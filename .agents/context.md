---
name: context
description: The hexaros workspace for Gerry — ROS 2 Lyrical in Docker on sparky and the Pi, which machine runs what, and how code and images reach the Pi
kind: context
---

# Context

ROS 2 Lyrical workspace for Gerry, a Freenove hexapod; packages live in `src/`. ROS runs in Docker on both machines, from one Dockerfile: its `robot` stage is the Pi's (compose service `hexapod`, with `/dev/i2c-1` and `/dev/gpiochip0`), and `dev` adds the Foxglove bridge for sparky (service `dev`, no devices). Lyrical's packages need Ubuntu 26.04, which neither host runs.

- Build and run only inside the containers (`make shell`, then `make build`); sparky's host Jazzy and the containers' Lyrical would overwrite each other's `build/` and `install/`.
- sparky's shell is zsh, so host commands source `setup.zsh`; the containers use bash and `setup.bash`.
- sparky is the dev machine: always `dry_run:=true`. Its container gets no devices, so nothing there can reach sparky's own I²C buses.
- The Pi runs Debian 13 and never builds: `make ship` on sparky builds the Pi's image and loads it into the Pi's Docker. Ship again after a `package.xml` dependency change.
- Code reaches the Pi through git. The Pi's deploy key is read-only, so edit and commit on sparky.
- sparky and the Pi share ROS domain 0, so anything on sparky publishing `joint_commands` drives the real Gerry; check `ros2 node list` before his servos power up.
- `make record` on the Pi saves the stack into `bags/`; `make replay` with `just bridge-replay` on sparky plays it in Foxglove.
