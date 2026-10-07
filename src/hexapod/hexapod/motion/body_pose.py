"""Holds the feet where STAND_POSE plants them and moves the body to the pose in its parameters, through inverse kinematics.

Stands up first by stepping the joints from the assembly pose, like the test publisher; then each tick moves the body
toward x, y, z, roll, pitch and yaw at no more than `speed` and `turn_speed`, solves the joint angles that keep every
foot on its foothold, and sends them on `joint_commands`. The world frame's floor is z = 0 under the footholds, and
world -> base_link goes to TF, so Foxglove shows the feet planted while the body moves. A pose a leg cannot reach is
logged and skipped, and the body holds its last good pose.

Author: Marco Cassar (@Ocramaru)
"""
from geometry_msgs.msg import TransformStamped
import numpy as np
import pinocchio as pin
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster

from hexapod.joints import JOINT_NAMES, STAND_POSE
from hexapod.kinematics import body_pose, Kinematics
from hexapod.utilities import run_node

AXES = ('x', 'y', 'z', 'roll', 'pitch', 'yaw')


class BodyPose(Node):
  def __init__(self):
    super().__init__('body_pose')
    self.kinematics = Kinematics()
    stance = self.kinematics.end_effectors(STAND_POSE)
    stand_height = -stance[:, 2].min()
    self.footholds = stance + [0.0, 0.0, stand_height]  # the floor is z = 0 under the feet

    for axis in AXES: self.declare_parameter(axis, stand_height if axis == 'z' else 0.0)
    self.declare_parameter('speed', 0.02)  # m/s
    self.declare_parameter('turn_speed', 0.3)  # rad/s
    self.declare_parameter('period', 0.05)
    self.period = self.get_parameter('period').value

    self.pose = np.array([0.0, 0.0, stand_height, 0.0, 0.0, 0.0])  # the body's current x, y, z, roll, pitch, yaw
    self.joint_angles = np.zeros(len(JOINT_NAMES))  # stepping up to STAND_POSE from the assembly pose
    self.standing = False

    self.publisher = self.create_publisher(JointState, 'joint_commands', 10)
    self.tf = TransformBroadcaster(self)
    self.create_timer(self.period, self.tick)

    self.get_logger().info(f'Body Pose Node has been started; standing height {stand_height * 1000:.1f} mm.')

  def tick(self):
    if self.standing: self.move_body()
    else: self.stand_up()
    self.publish()

  def stand_up(self):
    diff = STAND_POSE - self.joint_angles
    step = np.radians(2)
    self.joint_angles = np.where(np.abs(diff) <= step, STAND_POSE, self.joint_angles + np.sign(diff) * step)
    self.standing = np.array_equal(self.joint_angles, STAND_POSE)

  def move_body(self):
    target = np.array([self.get_parameter(axis).value for axis in AXES])
    speeds = np.array([self.get_parameter('speed').value] * 3 + [self.get_parameter('turn_speed').value] * 3)
    pose = self.pose + np.clip(target - self.pose, -speeds * self.period, speeds * self.period)
    try:
      self.joint_angles = self.kinematics.body_inverse_kinematics(body_pose(*pose), self.footholds)
    except ValueError as e:
      self.get_logger().warning(f'body pose {np.round(pose, 3).tolist()} not reachable: {e}', throttle_duration_sec=2.0)
      return
    self.pose = pose

  def publish(self):
    stamp = self.get_clock().now().to_msg()
    self.publisher.publish(JointState(name=JOINT_NAMES, position=self.joint_angles.tolist()))
    body = body_pose(*self.pose)
    transform = TransformStamped()
    transform.header.stamp, transform.header.frame_id, transform.child_frame_id = stamp, 'world', 'base_link'
    transform.transform.translation.x, transform.transform.translation.y, transform.transform.translation.z = body.translation
    rotation = transform.transform.rotation
    rotation.x, rotation.y, rotation.z, rotation.w = pin.Quaternion(body.rotation).coeffs()
    self.tf.sendTransform(transform)


def main():
  with run_node(BodyPose) as node:
    rclpy.spin(node)
