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
| Sensors | 29 |

<!-- /map -->


## Motion

- Check every joint on Gerry. Leg order matched; joint 0's sign and the head's channels and tilt sign were fixed in `joints.py`.
- Safe shutdown into `REST_POSE`. Confirmed on Gerry.
- Body poses from leg IK. Done as `body_pose`; roll, pitch, yaw and height confirmed on Gerry.
- Closed-form leg IK. Done in `kinematics.py` on Pinocchio, limits from the URDF.
- URDF, `joint_states` and `robot_state_publisher`. Done as `urdf/hexapod.urdf.xacro`, geometry from the CAD.
- Head pan/tilt control. Done as `head_joint0` and `head_joint1` on `joint_commands`, sharing the flat 20-joint maps with the legs; the kit's 50° `servo_limits` entry turned out to be tilt's.
- Extend `servo_controller` to drive all 18 servos across both boards. Done with JointState commands on `joint_commands`, both PCA9685 boards on one bus, radians throughout.

## Sensors

- Camera pipeline. Done as rpicam-vid on the host into gscam, JPEG at 15 Hz in `camera_optical`; shown in Foxglove.
- IMU pipeline. Done as `imu_sensor` and Madgwick; the chip's axes are in the URDF's `imu_mount`.
- Ultrasonic pipeline. Done as `ultrasonic_sensor`; tested on Gerry.
- Battery voltage pipeline. Done as `battery_monitor`, dividers calibrated at 8.35 V.
