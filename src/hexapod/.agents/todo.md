---
name: todo
description: Open features for the hexapod ROS package — safe shutdown, calibration, body poses, URDF and TF, and ROS pipelines for the kit's sensors
kind: todo
---

# Todo

<!-- map: generated. Edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 20 |
| Sensors | 28 |
| Outputs | 36 |

<!-- /map -->


## Motion

- Safe shutdown: lie down into `REST_POSE`, cut servo power through GPIO 4, then relax every servo. Built; confirm on Gerry.
- Check joint directions on Gerry: positive head pan turns left, positive tilt tips down, and joint 0 swings every foot counterclockwise from above. Joint 0 has never been driven.
- Per-joint calibration procedure, writing `calibration` in `config/calibration.yaml`. Leg 4 is furthest off, then leg 3.
- Body poses (height, tilt, offset) from closed-form leg IK.
- URDF, `joint_states` from the controller, and `robot_state_publisher`.

## Sensors

- IMU pipeline (MPU6050, `0x68`). Raw data, gyro bias and Madgwick work; still find the chip's axes by tilting Gerry and watching `imu/data_raw`.
- Battery voltage pipeline (ADC, `0x48`).
- Always-on battery monitoring: start `battery_monitor` at boot on its own, independent of test launches; at critical voltage lie down, cut servo power and shut the Pi down cleanly. Needs pack0's divider recalibrated first; it reads 9.09 V on a 2S pack.
- Camera pipeline. Confirm the JPEG stream shows in Foxglove; then calibrate the lens with `camera_calibration` and a checkerboard, and point gscam's `camera_info_url` at the result so Rectify works.
- Ultrasonic pipeline.

## Outputs

- LED and buzzer nodes.
