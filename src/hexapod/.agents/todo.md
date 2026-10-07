---
name: todo
description: Open work for the hexapod ROS package — checks on Gerry, calibration, poses from footholds, gait, the null space, URDF limits in the controller, sensors, and merging with ml/hexai
kind: todo
---

# Todo

<!-- map: generated. Edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 21 |
| Sensors | 33 |
| Outputs | 39 |
| Practice | 43 |

<!-- /map -->


## Motion

- Safe shutdown: lie down into `REST_POSE`, cut servo power through GPIO 4, then relax every servo. Built; confirm on Gerry.
- Check joints on Gerry one at a time: which physical leg is leg 0 (the URDF uses hexai's order, leg 0 front right, clockwise), whether channel 0 is pan or tilt, and the directions (positive pan turns left, positive tilt tips down, joint 0 swings every foot counterclockwise from above).
- Try `body_pose.launch.py` on Gerry; it is tested in dry run only.
- Per-joint calibration procedure, writing `calibration` in `config/calibration.yaml`. Leg 4 is furthest off, then leg 3.
- `servo_controller` takes its joint limits from the URDF instead of `servo_limits`, once the head channels are settled; today the head's 50-180 degree servo limit and the URDF's disagree.
- `STAND_POSE` and `REST_POSE` as footholds through the IK, so rest truly puts the belly down.
- Tripod gait: turn in place first, then walk from `cmd_vel`.
- Body pose from joint angles (height, roll, pitch from the planted feet) and the null space of body motions, with `world_model`.
- Merge with ml/hexai: this URDF replaces hexai's `hexapod.xml` (moving joint 0's servos and the pan servo onto the links they turn with), and the kinematics move there.

## Sensors

- IMU pipeline (MPU6050, `0x68`). Raw data, gyro bias and Madgwick work; still find the chip's axes by tilting Gerry and watching `imu/data_raw`.
- Always-on battery monitoring: start `battery_monitor` at boot on its own, independent of test launches; at critical voltage lie down, cut servo power and shut the Pi down cleanly. Needs both dividers recalibrated first; pack0 reads 9.09 V on a 2S pack.
- Camera pipeline. Confirm the JPEG stream shows in Foxglove; then calibrate the lens with `camera_calibration` and a checkerboard, and point gscam's `camera_info_url` at the result so Rectify works.

## Outputs

- LED and buzzer nodes.

## Practice

Work to review by hand.

- Review `kinematics.py` and work through the inverse kinematics with pen and paper.
