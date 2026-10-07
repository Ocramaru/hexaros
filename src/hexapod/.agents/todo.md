---
name: todo
description: Open work for the hexapod ROS package — joint calibration, URDF limits in the controller, poses from footholds, gait, the null space, merging with ml/hexai, battery monitoring, camera calibration, outputs
kind: todo
---

# Todo

<!-- map: generated. Edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 21 |
| Sensors | 30 |
| Outputs | 35 |
| Practice | 39 |

<!-- /map -->


## Motion

- Per-joint calibration procedure, writing `calibration` in `config/calibration.yaml`. Leg 4 is furthest off, then leg 3.
- `servo_controller` takes its joint limits from the URDF instead of repeating them in `servo_limits`.
- `STAND_POSE` and `REST_POSE` as footholds through the IK, so rest truly puts the belly down.
- Tripod gait: turn in place first, then walk from `cmd_vel`.
- Body pose from joint angles (height, roll, pitch from the planted feet) and the null space of body motions, with `world_model`.
- Merge with ml/hexai: this URDF replaces hexai's `hexapod.xml` (moving joint 0's servos and the pan servo onto the links they turn with), and the kinematics move there. Gerry showed joint 0 swinging clockwise at positive angles on both sides, against hexai's note.

## Sensors

- Always-on battery monitoring: start `battery_monitor` at boot on its own, independent of test launches; at critical voltage lie down, cut servo power and shut the Pi down cleanly.
- Camera lens calibration with `camera_calibration` and a checkerboard, replacing the nominal `config/ov5647.yaml`.

## Outputs

- LED and buzzer nodes.

## Practice

Work to review by hand.

- Review `kinematics.py` and work through the inverse kinematics with pen and paper.
