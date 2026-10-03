---
name: todo
description: Open features for the hexapod ROS package — calibration, body poses, URDF and TF, and ROS pipelines for the kit's sensors
kind: todo
---

# Todo

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 20 |
| Sensors | 26 |
| Outputs | 33 |

<!-- /map -->


## Motion

- Per-joint calibration procedure, writing `calibration` in `config/hexapod.yaml`.
- Body poses (height, tilt, offset) from closed-form leg IK.
- URDF, `joint_states` from the controller, and `robot_state_publisher`.

## Sensors

- IMU pipeline (MPU6050, `0x68`).
- Battery voltage pipeline (ADC, `0x48`).
- Camera pipeline.
- Ultrasonic pipeline.

## Outputs

- LED and buzzer nodes.
