---
name: context
description: How the hexapod package's nodes, URDF and kinematics fit together, its two config files, hardware facts, and the rules changes must respect
kind: context
---

# Context

<!-- map: generated. Edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Layout | 23 |
| Config | 36 |
| Hardware | 41 |
| Rules | 48 |

<!-- /map -->


The package drives Gerry's 18 leg servos and 2 head servos, and reads its batteries. `sensor_msgs/JointState` commands on `joint_commands` go to `servo_controller`, which converts joint angles to servo angles and writes them to two PCA9685 boards over I²C; `battery_monitor` publishes `BatteryState` on `battery/<name>` from the ADS7830 ADC; `imu_sensor` publishes raw `Imu` on `imu/data_raw` from the MPU6050, and `imu_filter_madgwick` adds orientation on `imu/data`; `ultrasonic_sensor` publishes `Range` on `ultrasonic/range`; `gscam` forwards the Pi host's `rpicam-vid` JPEGs on `camera/image_raw/compressed`, with no raw image (`deploy/rpicam-stream.service`), with `fake_camera` standing in on dry runs. `servo_controller` also publishes the commanded angles on `joint_states`, which `robot_state_publisher` turns into TF from `urdf/hexapod.urdf.xacro`; `body_pose` moves the body over planted feet through the leg IK in `kinematics.py`.

## Layout

| folder | holds |
|---|---|
| `hexapod/drivers/` | ROS-free hardware access, one file per chip |
| `hexapod/motion/` | nodes that move the robot |
| `hexapod/sensors/` | nodes that publish sensor readings |
| `hexapod/calibrate/` | `python3 -m` scripts that write `config/calibration.yaml` |
| `hexapod/tests/` | dry-run stand-ins (`FakeBus`, `fake_camera`) and hardware smoke tests |
| `hexapod/` | `joints.py` (joint names and servo maps), `kinematics.py` (Pinocchio forward and closed-form inverse kinematics) and `utilities.py` (`run_node`) |
| `urdf/` | `hexapod.urdf.xacro`, the robot's only geometry |
| `test/` | ament lint tests and pytest, run by `colcon test` |

## Config

- `config/hexapod.yaml` is hand-written; `config/calibration.yaml` holds measured values, is written only by `python3 -m hexapod.calibrate.<name>` scripts, and loads after it, so it wins.
- Every per-joint map is one flat list of 20 in `JOINT_NAMES` order: legs leg-major (`leg0_joint0, leg0_joint1, …`), then `head_joint0` (pan) and `head_joint1` (tilt); `LEGS` and `HEAD` slice them. Double arrays keep their decimal points.

## Hardware

- Joint 2 is mounted mirrored: at rest its servo sits at 10° on legs 0–2 and 170° on legs 3–5. Channel 15 on `0x41` is the safe test servo.
- Servo angle 0 to π maps to 500–2500 µs at 50 Hz, the kit's assumption, not yet measured on Gerry.
- `0x70` on the I²C bus is the PCA9685 all-call address, not a device.
- IMU readings are in the chip's own axes in `imu`; how the chip sits on the body belongs in the URDF.

## Rules

- Use an existing package (`imu_filter_madgwick`, `gscam`, gpiozero's `DistanceSensor`) over writing our own; write one only for hardware no package covers.
- Drivers stay free of ROS, so they test against `FakeBus`.
- Every exit path relaxes the servos.
- Stop the Freenove server before running anything; it drives the same boards and pin.
- Frames follow ROS REP 103: x forward, y left, z up. Joint 0 rotates about z. Image data is stamped `camera_optical` (z out of the lens), never `camera`.
- Joints are named by number from the body outwards: `leg{L}_joint{J}` and `head_joint{J}`. Attached parts are fixed joints named `<part>_mount`.
- Lengths, offsets and joint limits live only in the URDF; code reads them through Pinocchio rather than copying numbers.
- All angles are radians, joint angles with 0 at the kit's assembly pose; degrees only for display.
- `joint_commands` carries targets in; `joint_states` is reserved for the robot's current pose out.
