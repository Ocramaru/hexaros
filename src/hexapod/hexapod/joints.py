"""Leg layout of the Freenove hexapod: which servo drives each joint, and joint-to-servo angle conversion.

Rows are legs 0-5, columns are joints 0-2 from the body outwards, the order the kit's control.py uses.
Joint angles are radians, with 0 at the kit's assembly pose.

Author: Marco Cassar (@Ocramaru)
"""

import numpy as np

from hexapod.servo_driver import ServoDriver

# the kit's defaults; Gerry's values come from config/hexapod.yaml
BOARD_ADDRESSES = (0x41, 0x40)  # servos 0-15 on the first board, 16-31 on the second
SERVO_MAP = np.array([  # kit servo number for each [leg][joint], from the kit's control.py
  (15, 14, 13),
  (12, 11, 10),
  (9, 8, 31),
  (22, 23, 27),
  (19, 20, 21),
  (16, 17, 18),
])

# joint names for sensor_msgs/JointState, same [leg][joint] layout; the URDF must use these
JOINT_NAMES = np.array([[f'leg{leg}_joint{joint}' for joint in range(3)] for leg in range(6)])
JOINT_INDEX = {name: index for index, name in np.ndenumerate(JOINT_NAMES)}

# standing pose in joint radians: the kit's move_position(0, 0, 0), feet at [140, 0, -44] mm in each leg frame
STAND_POSE = np.array([[0.0, -0.716, 1.745]] * 6)

flip_signs = np.array([[1, -1, 1]] * 3 + [[1, 1, -1]] * 3)
# servo angles for all joints at resting position (0) | (90, 90, 10) legs 0-2, (90, 90, 170) legs 3-5
SERVO_AT_REST = np.array([[np.pi / 2, np.pi / 2, np.pi / 18]] * 3 + [[np.pi / 2, np.pi / 2, 17 * np.pi / 18]] * 3)


def servo_address_channel(servo: int, board_addresses=BOARD_ADDRESSES) -> tuple[int, int]:
  """Convert a kit servo number to its board address and channel; each board has 16 channels."""
  return (board_addresses[servo // 16], servo % 16)


def joint_to_servo(joint_matrix: np.ndarray, calibration: np.ndarray) -> np.ndarray:
  """Convert 6x3 joint angles to 6x3 servo angles, clipped to the servo range.

  Calibration is per-joint offsets in joint space, so they flip with the joint and mean the same direction on both sides.
  """
  servo = flip_signs * (joint_matrix + calibration) + SERVO_AT_REST
  return np.clip(servo, ServoDriver.SERVO.MIN_ANGLE, ServoDriver.SERVO.MAX_ANGLE)
