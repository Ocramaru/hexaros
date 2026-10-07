"""Kinematics of Gerry from urdf/hexapod.urdf.xacro, through Pinocchio.

Two models share the URDF: `model` measures everything from base_link, so only the joints move; `world_model` joins
base_link to the world through a free six degree of freedom joint, so the body's own pose is part of the state too.
Each has a data object Pinocchio fills with results. Joint angles are in JOINT_NAMES order; Pinocchio orders its
configuration by its own walk of the tree, so `configuration` maps one onto the other.

Inverse kinematics is closed form, with every length read from the model's placements. Joints 1 and 2 turn about
the leg's y axis, so they move the foot only in x and z: the foot sits a fixed distance to the side of joint 0's
line, and joint 0 (atan2) sets where that line points. In the leg's vertical plane, link 2's offset to the foot folds
into one straight segment, leaving a triangle whose angles (law of cosines) give joints 1 and 2, joint 2 raised.

Author: Marco Cassar (@Ocramaru)
"""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
import numpy as np
import pinocchio as pin
import xacro

from hexapod.joints import JOINT_INDEX, JOINT_NAMES

END_EFFECTORS = [f'leg{leg}_foot' for leg in range(6)]


class Leg:
  """One leg's geometry for closed-form inverse kinematics, read from the model."""

  def __init__(self, model, leg):
    joint0, joint1, joint2 = (model.getJointId(f'leg{leg}_joint{j}') for j in range(3))
    end_effector = model.frames[model.getFrameId(f'leg{leg}_foot')].placement  # relative to joint 2
    self.mount = model.jointPlacements[joint0]  # joint 0 in base_link
    self.joint1 = model.jointPlacements[joint1].translation  # joint 1 from joint 0
    self.link1_length = model.jointPlacements[joint2].translation[0]
    rotation = model.jointPlacements[joint2].rotation
    self.joint2_offset = np.arctan2(rotation[0, 2], rotation[0, 0])  # link 2's bend below link 1 at joint 2 = 0
    self.side_offset = self.joint1[1] + end_effector.translation[1]  # the foot's distance to the side of joint 0's line
    self.end_effector_length = np.hypot(end_effector.translation[0], end_effector.translation[2])  # joint 2 to the foot, as one segment
    self.end_effector_angle = np.arctan2(-end_effector.translation[2], end_effector.translation[0])  # that segment's angle below link 2
    self.angle_index = [JOINT_INDEX[f'leg{leg}_joint{j}'] for j in range(3)]
    self.lower_limits = model.lowerPositionLimit[[model.joints[joint].idx_q for joint in (joint0, joint1, joint2)]]

  def inverse(self, target):
    """Joint 0-2 angles that put the foot at `target` in base_link; ValueError if it is out of reach."""
    x, y, z = self.mount.actInv(np.asarray(target, dtype=float))  # into joint 0's frame
    along = np.sqrt(max(x**2 + y**2 - self.side_offset**2, 0.0))  # the foot's distance along joint 0's line
    angle0 = np.arctan2(y, x) - np.arctan2(self.side_offset, along)
    reach, depth = along - self.joint1[0], self.joint1[2] - z  # from joint 1, depth positive down
    span = np.hypot(reach, depth)  # joint 1 to the foot
    if not abs(self.link1_length - self.end_effector_length) < span < self.link1_length + self.end_effector_length:
      raise ValueError(f'{np.round(target, 4).tolist()} is out of reach')
    link1_to_span = np.arccos((self.link1_length**2 + span**2 - self.end_effector_length**2) / (2 * self.link1_length * span))
    angle1 = np.arctan2(depth, reach) - link1_to_span
    segment = np.arctan2(depth - self.link1_length * np.sin(angle1), reach - self.link1_length * np.cos(angle1))
    angle2 = segment - angle1 - self.joint2_offset - self.end_effector_angle
    # each joint's range is under a full turn, so [lower, lower + 2pi) holds exactly one copy of any reachable angle
    return (np.array([angle0, angle1, angle2]) - self.lower_limits) % (2 * np.pi) + self.lower_limits


try:
  URDF_PATH = Path(get_package_share_directory('hexapod')) / 'urdf' / 'hexapod.urdf.xacro'
except PackageNotFoundError:
  URDF_PATH = Path(__file__).resolve().parents[1] / 'urdf' / 'hexapod.urdf.xacro'  # the source tree, before a build


class Kinematics:
  def __init__(self, urdf=None):
    """Build both models; `urdf` is URDF XML, or None to expand the package's xacro."""
    xml = urdf if urdf is not None else xacro.process_file(str(URDF_PATH)).toxml()
    self.model = pin.buildModelFromXML(xml)
    self.world_model = pin.buildModelFromXML(xml, pin.JointModelFreeFlyer())
    self.model_data = self.model.createData()
    self.world_data = self.world_model.createData()
    self.configuration_index = np.array([self.model.joints[self.model.getJointId(name)].idx_q for name in JOINT_NAMES])
    self.end_effector_ids = [self.model.getFrameId(name) for name in END_EFFECTORS]
    self.legs = [Leg(self.model, leg) for leg in range(6)]
    self.lower_limits, self.upper_limits = (limits[self.configuration_index] for limits in
                                            (self.model.lowerPositionLimit, self.model.upperPositionLimit))

  def configuration(self, angles):
    """Rearrange joint `angles` from JOINT_NAMES order into Pinocchio's configuration."""
    configuration = pin.neutral(self.model)
    configuration[self.configuration_index] = angles
    return configuration

  def update_poses(self, angles):
    """Compute the pose of every frame in base_link for joint `angles`."""
    pin.framesForwardKinematics(self.model, self.model_data, self.configuration(angles))

  def transform(self, frame, angles):
    """Pose of `frame` in base_link, as a 4x4 homogeneous transform."""
    self.update_poses(angles)
    return self.model_data.oMf[self.model.getFrameId(frame)].homogeneous

  def end_effectors(self, angles):
    """Positions of the six feet in base_link, (6, 3)."""
    self.update_poses(angles)
    return np.array([self.model_data.oMf[i].translation for i in self.end_effector_ids])

  def inverse_kinematics(self, end_effectors, head=(0.0, 0.0)):
    """Joint angles in JOINT_NAMES order that put the six feet at `end_effectors`, (6, 3) in base_link.

    Raises ValueError if a foot is out of reach or an angle falls outside the URDF's joint limits.
    """
    angles = np.zeros(len(JOINT_NAMES))
    for leg, target in zip(self.legs, end_effectors):
      angles[leg.angle_index] = leg.inverse(target)
    angles[[JOINT_INDEX['head_joint0'], JOINT_INDEX['head_joint1']]] = head
    outside = (angles < self.lower_limits - 1e-9) | (angles > self.upper_limits + 1e-9)
    if outside.any(): raise ValueError(f'outside joint limits: {[JOINT_NAMES[i] for i in np.flatnonzero(outside)]}')
    return angles

  def body_inverse_kinematics(self, body, footholds, head=(0.0, 0.0)):
    """Joint angles that hold the body at `body` while the feet stay on `footholds`, (6, 3), both in the world frame."""
    return self.inverse_kinematics([body.actInv(foothold) for foothold in footholds], head)


def body_pose(x=0.0, y=0.0, z=0.0, roll=0.0, pitch=0.0, yaw=0.0):
  """Build the body's pose in the world from a position and roll, pitch, yaw about the world's fixed x, y, z axes."""
  return pin.SE3(pin.rpy.rpyToMatrix(roll, pitch, yaw), np.array([x, y, z]))
