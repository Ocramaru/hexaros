---
name: context
description: How the hexapod package's servo and battery nodes fit together, its two config files, hardware facts, and the rules changes must respect
kind: context
---

# Context

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Config | 22 |
| Hardware | 27 |
| Rules | 33 |

<!-- /map -->


The package drives Gerry's 18 leg servos and 2 head servos, and reads its batteries. `sensor_msgs/JointState` commands on `joint_commands` go to `servo_controller`, which converts joint angles to servo angles and writes them to two PCA9685 boards over I²C; `battery_monitor` publishes `BatteryState` on `battery/<name>` from the ADS7830 ADC.

## Config

- `config/hexapod.yaml` is hand-written; `config/calibration.yaml` holds measured values, is written only by `python3 -m hexapod.calibrate.<name>` scripts, and loads after it, so it wins.
- Every per-joint map is one flat list of 20 in `JOINT_NAMES` order: legs leg-major (`leg0_joint0, leg0_joint1, …`), then `head_joint0` (pan) and `head_joint1` (tilt); `LEGS` and `HEAD` slice them. Double arrays keep their decimal points.

## Hardware

- Joint 2 is mounted mirrored: at rest its servo sits at 10° on legs 0–2 and 170° on legs 3–5. Channel 15 on `0x41` is the safe test servo.
- Servo angle 0 to π maps to 500–2500 µs at 50 Hz, the kit's assumption, not yet measured on Gerry.
- Other I²C devices: `0x68` MPU6050 IMU. `0x70` is the PCA9685 all-call address, not a device.

## Rules

- Drivers (`servo_driver.py`, `adc_driver.py`) stay free of ROS, so they test against `FakeBus`.
- Every exit path relaxes the servos.
- Stop the Freenove server before running anything; it drives the same boards and pin.
- Frames follow ROS REP 103: x forward, y left, z up. Joint 0 rotates about z.
- Joints are named by number from the body outwards: `leg{L}_joint{J}` and `head_joint{J}`.
- All angles are radians, joint angles with 0 at the kit's assembly pose; degrees only for display.
- `joint_commands` carries targets in; `joint_states` is reserved for the robot's current pose out.
