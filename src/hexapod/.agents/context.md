---
name: context
description: How the hexapod package's servo, battery and IMU nodes fit together, its two config files, hardware facts, and the rules changes must respect
kind: context
---

# Context

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Layout | 23 |
| Config | 35 |
| Hardware | 40 |
| Rules | 47 |

<!-- /map -->


The package drives Gerry's 18 leg servos and 2 head servos, and reads its batteries. `sensor_msgs/JointState` commands on `joint_commands` go to `servo_controller`, which converts joint angles to servo angles and writes them to two PCA9685 boards over I²C; `battery_monitor` publishes `BatteryState` on `battery/<name>` from the ADS7830 ADC; `imu_sensor` publishes raw `Imu` on `imu/data_raw` from the MPU6050, and `imu_filter_madgwick` adds orientation on `imu/data`.

## Layout

| folder | holds |
|---|---|
| `hexapod/drivers/` | ROS-free hardware access, one file per chip |
| `hexapod/motion/` | nodes that move the robot |
| `hexapod/sensors/` | nodes that publish sensor readings |
| `hexapod/calibrate/` | `python3 -m` scripts that write `config/calibration.yaml` |
| `hexapod/tests/` | dry-run stand-ins (`FakeBus`) and hardware smoke tests |
| `hexapod/` | `joints.py` (joint layout, shared by motion and the URDF) and `utilities.py` (`run_node`) |
| `test/` | ament lint tests run by `colcon test` |

## Config

- `config/hexapod.yaml` is hand-written; `config/calibration.yaml` holds measured values, is written only by `python3 -m hexapod.calibrate.<name>` scripts, and loads after it, so it wins.
- Every per-joint map is one flat list of 20 in `JOINT_NAMES` order: legs leg-major (`leg0_joint0, leg0_joint1, …`), then `head_joint0` (pan) and `head_joint1` (tilt); `LEGS` and `HEAD` slice them. Double arrays keep their decimal points.

## Hardware

- Joint 2 is mounted mirrored: at rest its servo sits at 10° on legs 0–2 and 170° on legs 3–5. Channel 15 on `0x41` is the safe test servo.
- Servo angle 0 to π maps to 500–2500 µs at 50 Hz, the kit's assumption, not yet measured on Gerry.
- `0x70` on the I²C bus is the PCA9685 all-call address, not a device.
- IMU readings are in the chip's own axes in `imu_link`; how the chip sits on the body belongs in the URDF.

## Rules

- Drivers stay free of ROS, so they test against `FakeBus`.
- Every exit path relaxes the servos.
- Stop the Freenove server before running anything; it drives the same boards and pin.
- Frames follow ROS REP 103: x forward, y left, z up. Joint 0 rotates about z.
- Joints are named by number from the body outwards: `leg{L}_joint{J}` and `head_joint{J}`.
- All angles are radians, joint angles with 0 at the kit's assembly pose; degrees only for display.
- `joint_commands` carries targets in; `joint_states` is reserved for the robot's current pose out.
