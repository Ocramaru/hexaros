---
name: todo.archive
description: Finished features of the hexapod ROS package, newest first
kind: todo.archive
---

# Todo archive

<!-- map: generated. Edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Motion | 19 |
| Sensors | 27 |

<!-- /map -->


## Motion

- Body poses from leg IK. Done as `body_pose`; dry run only.
- Closed-form leg IK. Done in `kinematics.py` on Pinocchio, limits from the URDF.
- URDF, `joint_states` and `robot_state_publisher`. Done as `urdf/hexapod.urdf.xacro`, geometry from the CAD.
- Head pan/tilt control. Done as `head_joint0` and `head_joint1` on `joint_commands`, sharing the flat 20-joint maps with the legs; `servo_limits` caps pan at the kit's 50°.
- Extend `servo_controller` to drive all 18 servos across both boards. Done with JointState commands on `joint_commands`, both PCA9685 boards on one bus, radians throughout.

## Sensors

- Ultrasonic pipeline. Done as `ultrasonic_sensor`; tested on Gerry.
- Battery voltage pipeline. Done as `battery_monitor`; dividers still need recalibrating.
