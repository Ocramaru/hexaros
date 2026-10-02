---
name: todo
description: Open features for the hexapod ROS package — all 18 servos, calibration and standing, and ROS pipelines for the kit's sensors
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

- Extend `servo_controller` to drive all 18 servos across both boards.
- Per-joint calibration from the kit's `point.txt`, in a layer above the driver.
- Neutral and standing poses from leg kinematics.
- URDF and `robot_state_publisher`.

## Sensors

- IMU pipeline (MPU6050, `0x68`).
- Battery voltage pipeline (ADC, `0x48`).
- Camera pipeline.
- Ultrasonic pipeline.

## Outputs

- LED and buzzer nodes.
