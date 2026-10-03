---
name: context
description: How the hexapod servo package is layered, where it runs, and the hardware facts and rules any change has to respect
kind: context
---

# Context

<!-- map: generated — edit the note, not this; after a manual edit run `agent remap` -->

| section | line |
|---|---|
| Layers | 23 |
| Machines | 36 |
| Hardware | 42 |
| Rules | 50 |

<!-- /map -->


The package drives the Freenove hexapod's 18 servos (Gerry) from ROS 2 Jazzy: `sensor_msgs/JointState` commands on `joint_commands` go to a node that converts joint angles to servo angles and writes them to two PCA9685 boards over I²C.

## Layers

| File | Role |
|---|---|
| `servo_driver.py` | one PCA9685 chip; no ROS imports. Auto-increment on, one block write per channel. Bus is injectable, `shutdown()` relaxes all 16 channels and closes the bus if it opened it |
| `joints.py` | 6×3 layout (row = leg, column = joint 0–2), joint names `leg{L}_joint{J}`, the kit's default board addresses and servo map, `SERVO_AT_REST`, `STAND_POSE`; `joint_to_servo` applies calibration, per-side sign flips and the rest offset, then clips to the servo range |
| `config/hexapod.yaml` | Gerry's `board_addresses`, `servo_map` and `calibration` as servo_controller parameters; flat leg-major lists, calibration must keep decimal points (double array) |
| `servo_controller.py` | node: params `dry_run`, `board_addresses`, `servo_map`, `calibration` (kit values as defaults); both boards on one shared bus; subscribes `joint_commands` and keeps the last command per joint in `joint_radians` (NaN = never commanded; a joint left out or sent as NaN keeps its command); writes only joints that changed; drives GPIO 4; `destroy_node` relaxes |
| `utilities.py` | `run_node` (init, spin, Ctrl-C, destroy, shutdown) and `FakeBus`, which emulates auto-increment |
| `servo_publisher.py` | test: steps all 18 joints from the assembly pose to `STAND_POSE`, then bounces the joint 1s ±5° |
| `servo_test.py` | hardware-only script, no ROS |
| `launch/servo_test.launch.py` | controller (with `config/hexapod.yaml`) + publisher, `dry_run` launch argument |

## Machines

- sparky is the dev machine: always `dry_run:=true`. It has no `smbus2` on purpose, so a run without `dry_run` fails on import instead of writing to sparky's own I²C buses.
- The Pi runs Debian 13; ROS runs in Docker via `compose.yaml` at the repo root, with `/dev/i2c-1` and `/dev/gpiochip0` passed in.
- Code reaches the Pi through git. The Pi's deploy key is read-only, so edit and commit on sparky.

## Hardware

- GPIO 4 gates servo power: low = on.
- Board `0x41` holds kit servos 0–15, `0x40` holds 16–31 at channel − 16. Legs (kit numbers): 0 = 15, 14, 13; 1 = 12, 11, 10; 2 = 9, 8, 31; 3 = 22, 23, 27; 4 = 19, 20, 21; 5 = 16, 17, 18.
- Joint 2 is mounted mirrored: at rest its servo sits at 10° on legs 0–2 and 170° on legs 3–5, not 90°. Channel 15 on `0x41` is the safe test servo.
- Servo angle 0 to π maps to 500–2500 µs at 50 Hz. That range is the kit's assumption and has not been measured on Gerry.
- Other I²C devices: `0x48` ADC (battery), `0x68` MPU6050 IMU. `0x70` is the PCA9685 all-call address, not a device.

## Rules

- Keep the driver free of ROS so it can be tested with a fake bus.
- Every exit path relaxes the servos.
- Stop the Freenove server before running anything; it drives the same boards and pin.
- Frames follow ROS REP 103: x forward, y left, z up. Joint 0 rotates about z.
- Joints are numbered 0–2 from the body outwards; never by anatomy names.
- All angles are radians, joint angles with 0 at the kit's assembly pose; use `np.degrees` only to display them.
- `joint_commands` carries targets in; `joint_states` is reserved for the robot's current pose out.
