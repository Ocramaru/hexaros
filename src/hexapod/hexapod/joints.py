"""Joint layout of the Freenove hexapod: which servo drives each joint, and joint-to-servo angle conversion.

Every per-joint array is flat in JOINT_NAMES order: the 18 leg joints, leg-major with joints 0-2 from the body outwards
(the order the kit's control.py uses), then head joint 0 (pan) and joint 1 (tilt). Joint angles are radians, with 0 at
the kit's assembly pose.

Author: Marco Cassar (@Ocramaru)
"""

import numpy as np

# joint names for sensor_msgs/JointState; the URDF must use these
JOINT_NAMES = [f'leg{leg}_joint{joint}' for leg in range(6) for joint in range(3)] + ['head_joint0', 'head_joint1']
JOINT_INDEX = {name: index for index, name in enumerate(JOINT_NAMES)}
LEGS = slice(0, 18)
HEAD = slice(18, 20)

# the kit's defaults; Gerry's values come from config/hexapod.yaml
BOARD_ADDRESSES = (0x41, 0x40)  # servos 0-15 on the first board, 16-31 on the second
SERVO_MAP = np.array([  # kit servo numbers, from the kit's control.py and server.py
  15, 14, 13, 12, 11, 10, 9, 8, 31,  # legs 0-2
  22, 23, 27, 19, 20, 21, 16, 17, 18,  # legs 3-5
  0, 1,  # head
])
SERVO_LIMITS = {'head_joint0': (0.873, np.pi)}  # pan (50, 180) degrees, the kit's limits; others use the full 0 to pi

SIGNS = np.array([1, -1, 1] * 3 + [1, 1, -1] * 3 + [1, 1])
# servo angles at rest (joint angle 0) | (90, 90, 10) legs 0-2, (90, 90, 170) legs 3-5, (90, 90) head
SERVO_AT_REST = np.array([np.pi / 2, np.pi / 2, np.pi / 18] * 3 + [np.pi / 2, np.pi / 2, 17 * np.pi / 18] * 3 + [np.pi / 2, np.pi / 2])

STAND_POSE = np.array([0.0, -0.492, 1.634] * 6 + [0.0, 0.0])  # the kit's highest stance
REST_POSE = np.array([0.0, -0.529, 1.244] * 6 + [0.0, 0.0])  # belly down, feet out on the floor


def servo_address_channel(servo: int, board_addresses=BOARD_ADDRESSES) -> tuple[int, int]:
  """Convert a kit servo number to its board address and channel; each board has 16 channels."""
  return (board_addresses[servo // 16], servo % 16)


def joint_to_servo(angles: np.ndarray, calibration: np.ndarray, servo_min=0.0, servo_max=np.pi) -> np.ndarray:
  """Convert joint angles to servo angles, clipped to each servo's limits.

  Calibration is per-joint offsets in joint space, so they flip with the joint and mean the same direction on both sides.
  """
  return np.clip(SIGNS * (angles + calibration) + SERVO_AT_REST, servo_min, servo_max)
