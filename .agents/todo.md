---
name: todo
description: Open workspace-wide work — moving the Pi to hexaros and Lyrical, the gscam binary check-in, and shipping only changed image layers
kind: todo
---

# Todo

- On the Pi: rename `~/workspace/ros2_jazzy` to `~/workspace/hexaros`, `git remote set-url origin git@github.com:Ocramaru/hexaros.git`, then `make ship` from sparky for its first Lyrical image.
- Check in on gscam now and then: once `ros-lyrical-gscam` installs (its build farm job was failing in October 2026), drop the source build and `--skip-keys gscam` from the Dockerfile.
- Ship only changed layers: push the Pi's image to a local `registry:2` on sparky and point the `hexapod` service's `image` at it, with the Pi's Docker trusting the registry (`insecure-registries` or a Tailscale cert); `make ship` sends the whole image every time. Nothing in the image may be compiled with `-march=native`, since sparky's CPU is newer than the Pi 4's Cortex-A72.
