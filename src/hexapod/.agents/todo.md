---
name: todo
description: Open features for the hexapod ROS package — head control, calibration, body poses, URDF and TF, and ROS pipelines for the kit's sensors
kind: todo
---

# Todo

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 20 |
| Sensors | 28 |
| Outputs | 35 |

<!-- /map -->


## Motion

- Head pan/tilt control: micro servos on kit channels 0 and 1 (`0x41`), with their own pulse range; the kit limits pan to 50-180°.
- Per-joint calibration procedure, writing `calibration` in `config/calibration.yaml`.
- Sit-down sequence before the servos relax, so shutdown doesn't drop a standing robot.
- Body poses (height, tilt, offset) from closed-form leg IK.
- URDF, `joint_states` from the controller, and `robot_state_publisher`.

## Sensors

- IMU pipeline (MPU6050, `0x68`).
- Battery voltage pipeline (ADC, `0x48`).
- Camera pipeline.
- Ultrasonic pipeline.

## Outputs

- LED and buzzer nodes.
