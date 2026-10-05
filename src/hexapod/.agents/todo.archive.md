---
name: todo.archive
description: Finished features of the hexapod ROS package, newest first
kind: todo.archive
---

# Todo archive

## Motion

- Head pan/tilt control. Done as `head_joint0` and `head_joint1` on `joint_commands`, sharing the flat 20-joint maps with the legs; `servo_limits` caps pan at the kit's 50°.
- Extend `servo_controller` to drive all 18 servos across both boards. Done with JointState commands on `joint_commands`, both PCA9685 boards on one bus, radians throughout.
