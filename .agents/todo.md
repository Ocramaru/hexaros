---
name: todo
description: Open workspace-wide work — building the Docker image on sparky and shipping it to the Pi
kind: todo
---

# Todo

- Build the image on sparky and have the Pi pull it, instead of building on the Pi. Both are aarch64, so sparky builds natively; push to a local `registry:2` on sparky so the Pi pulls only changed layers, with `compose.yaml` pointing at that image and the Pi's Docker trusting the registry (`insecure-registries` or a Tailscale cert). `docker save | zstd | ssh rpi4b docker load` works with no setup in the meantime. Nothing in the image may be compiled with `-march=native`, since sparky's CPU is newer than the Pi 4's Cortex-A72.
