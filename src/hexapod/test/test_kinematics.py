"""Check Pinocchio's reading of the URDF against an independent chain of 4x4 transforms, and the leg geometry.

Author: Marco Cassar (@Ocramaru) and Claude
"""
import xml.etree.ElementTree as ET

import numpy as np
import pytest
import xacro

from hexapod.joints import JOINT_INDEX, JOINT_NAMES, STAND_POSE
from hexapod.kinematics import END_EFFECTORS, Kinematics, URDF_PATH


@pytest.fixture(scope='module')
def urdf():
  return xacro.process_file(str(URDF_PATH)).toxml()


@pytest.fixture(scope='module')
def kinematics(urdf):
  return Kinematics(urdf)


def rotation(axis, angle):
  x, y, z = axis
  cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
  transform = np.eye(4)
  transform[:3, :3] = np.eye(3) + np.sin(angle) * cross + (1 - np.cos(angle)) * cross @ cross
  return transform


def chain_transform(urdf, frame, angles):
  """Multiply origin then rotation down the URDF's joints from base_link to `frame`."""
  parent_joint = {joint.find('child').get('link'): joint for joint in ET.fromstring(urdf).iter('joint')}
  steps = []
  while frame in parent_joint:
    joint = parent_joint[frame]
    origin = joint.find('origin')
    xyz = [float(v) for v in (origin.get('xyz', '0 0 0') if origin is not None else '0 0 0').split()]
    roll, pitch, yaw = [float(v) for v in (origin.get('rpy', '0 0 0') if origin is not None else '0 0 0').split()]
    step = rotation((0, 0, 1), yaw) @ rotation((0, 1, 0), pitch) @ rotation((1, 0, 0), roll)
    step[:3, 3] = xyz
    if joint.get('type') != 'fixed':
      step = step @ rotation([float(v) for v in joint.find('axis').get('xyz').split()], angles[JOINT_INDEX[joint.get('name')]])
    steps.append(step)
    frame = joint.find('parent').get('link')
  transform = np.eye(4)
  for step in reversed(steps): transform = transform @ step
  return transform


def test_matches_an_independent_chain(urdf, kinematics):
  rng = np.random.default_rng(0)
  for _ in range(20):
    angles = rng.uniform(-1.0, 1.0, len(JOINT_NAMES))
    for frame in END_EFFECTORS + ['camera_optical', 'head_link1']:
      np.testing.assert_allclose(kinematics.transform(frame, angles), chain_transform(urdf, frame, angles), atol=1e-9)


def test_left_and_right_mirror(kinematics):
  feet = kinematics.end_effectors(STAND_POSE)
  for right, left in ((0, 5), (1, 4), (2, 3)):
    np.testing.assert_allclose(feet[left], feet[right] * [1, -1, 1], atol=1e-9)


def test_inverse_kinematics_recovers_the_angles(kinematics):
  rng = np.random.default_rng(1)
  checked = 0
  while checked < 200:
    angles = np.zeros(len(JOINT_NAMES))
    for leg in range(6):  # joint 2 bent past straight, the branch the inverse picks
      angles[[JOINT_INDEX[f'leg{leg}_joint{j}'] for j in range(3)]] = rng.uniform([-0.6, -1.2, 0.3], [0.6, 1.0, 2.6])
    feet = kinematics.end_effectors(angles)
    if any(leg.mount.actInv(foot)[0] < 0.04 for leg, foot in zip(kinematics.legs, feet)): continue  # under the hip, where joint 0 is ambiguous
    np.testing.assert_allclose(kinematics.inverse_kinematics(feet), angles, atol=1e-9)
    checked += 1


def test_joint0_turns_the_foot_about_its_axis(kinematics):
  turned = STAND_POSE.copy()
  turned[JOINT_INDEX['leg0_joint0']] += 0.3
  axis = kinematics.transform('leg0_link0', STAND_POSE)[:3, 3]
  before, after = kinematics.end_effectors(STAND_POSE)[0] - axis, kinematics.end_effectors(turned)[0] - axis
  assert after[2] == pytest.approx(before[2])
  assert np.hypot(*after[:2]) == pytest.approx(np.hypot(*before[:2]))
  assert np.arctan2(after[1], after[0]) - np.arctan2(before[1], before[0]) == pytest.approx(0.3)
