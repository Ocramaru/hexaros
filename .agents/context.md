---
name: context
description: The ros2_jazzy workspace for Gerry — which machine runs what, Docker on the Pi, and how code reaches it
kind: context
---

# Context

ROS 2 Jazzy workspace for Gerry, a Freenove hexapod; packages live in `src/`.

- sparky is the dev machine: always `dry_run:=true`. It has no `smbus2` on purpose, so a run without `dry_run` fails on import instead of writing to sparky's own I²C buses.
- The Pi runs Debian 13; ROS runs in Docker via `compose.yaml` here, with `/dev/i2c-1` and `/dev/gpiochip0` passed in. A `package.xml` dependency change needs `docker compose build`.
- Code reaches the Pi through git. The Pi's deploy key is read-only, so edit and commit on sparky.
