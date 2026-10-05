---
name: todo
description: Open features for the hexapod ROS package — safe shutdown, calibration, body poses, URDF and TF, and ROS pipelines for the kit's sensors
kind: todo
---

# Todo

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 20 |
| Sensors | 27 |
| Outputs | 34 |

<!-- /map -->


## Motion

- Safe shutdown: sit down, cut servo power through GPIO 4, then relax every servo.
- Per-joint calibration procedure, writing `calibration` in `config/calibration.yaml`.
- Body poses (height, tilt, offset) from closed-form leg IK.
- URDF, `joint_states` from the controller, and `robot_state_publisher`.

## Sensors

- IMU pipeline (MPU6050, `0x68`).
- Battery voltage pipeline (ADC, `0x48`).
- Camera pipeline.
- Ultrasonic pipeline.

## Outputs

- LED and buzzer nodes.
