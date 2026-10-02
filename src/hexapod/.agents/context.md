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
| Machines | 34 |
| Hardware | 40 |
| Rules | 47 |

<!-- /map -->


The package drives the Freenove hexapod's servos (Gerry) from ROS 2 Jazzy: a topic carries a target angle, a node clips it, and a ROS-free driver writes it to a PCA9685 over I²C.

## Layers

| File | Role |
|---|---|
| `servo_driver.py` | one PCA9685 chip; no ROS imports. Bus is injectable, `shutdown()` relaxes all 16 channels and closes the bus if it opened it |
| `servo_controller.py` | node: params `address`, `channel`, `dry_run`; clips 0–180; drives GPIO 4; `destroy_node` relaxes |
| `utilities.py` | `run_node` (init, spin, Ctrl-C, destroy, shutdown) and `FakeBus` for dry runs |
| `servo_publisher.py` | test ramp between two angles |
| `servo_test.py` | hardware-only script, no ROS |
| `launch/servo_test.launch.py` | controller + publisher, `dry_run` launch argument |

## Machines

- sparky is the dev machine: always `dry_run:=true`. It has no `smbus2` on purpose, so a run without `dry_run` fails on import instead of writing to sparky's own I²C buses.
- The Pi runs Debian 13; ROS runs in Docker via `compose.yaml` at the repo root, with `/dev/i2c-1` and `/dev/gpiochip0` passed in.
- Code reaches the Pi through git. The Pi's deploy key is read-only, so edit and commit on sparky.

## Hardware

- GPIO 4 gates servo power: low = on.
- Board `0x41` holds kit servos 0–15, `0x40` holds 16–31 at channel − 16. Legs (kit numbers): 0 = 15, 14, 13; 1 = 12, 11, 10; 2 = 9, 8, 31; 3 = 22, 23, 27; 4 = 19, 20, 21; 5 = 16, 17, 18.
- Third joints are mounted mirrored: their neutral is 10° or 170°, not 90°. Channel 15 on `0x41` is the safe test servo.
- Other I²C devices: `0x48` ADC (battery), `0x68` MPU6050 IMU. `0x70` is the PCA9685 all-call address, not a device.

## Rules

- Keep the driver free of ROS so it can be tested with a fake bus.
- Every exit path relaxes the servos.
- Stop the Freenove server before running anything; it drives the same boards and pin.
