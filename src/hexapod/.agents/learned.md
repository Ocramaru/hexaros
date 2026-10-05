---
name: learned
description: Traps that already cost time in the hexapod package — node-name YAML keys, ROS libcamera on the Pi, uncalibrated legs, the kit's startup pose, rclpy shutdown, launch output buffering, scripted SIGINT tests
kind: learned
---

# Learned

## Traps

- **A YAML key that misses the node's name is silently ignored.** `imu_filter_madgwick`'s node is `imu_filter_madgwick`, not `imu_filter`; under the wrong key it kept `use_mag: true` and waited forever on `imu/mag`. Check with `ros2 node list`.
- **ROS's `ros-jazzy-libcamera` cannot drive the Pi camera.** Its `ipa_rpi_vc4.so` signature is invalid, so libcamera isolates it in a proxy process, which crashes in 0.7.2 (`A list of V4L2 controls requires a ControlInfoMap`). Before that, the container needs `/run/udev` to see the camera, and Docker's seccomp answers libcamera's `clone3` with ENOSYS. Hence the host's `rpicam-vid` streams to `gscam` instead.
- **Uncalibrated legs differ by tens of millimetres at the foot.** At one commanded pose, leg 4 hovered where the other five touched; leg 3 was next highest.
- **The kit's startup pose `[140, 0, 0]` lifts the feet to hip height.** It is a lying pose with legs held out, not a rest; ramping into it then cutting power lets the legs fall.
- **`SignalHandlerOptions.NO` makes the node unkillable.** Tested on Jazzy: `spin` then ignores SIGINT.
- **ROS logging fails during Ctrl-C cleanup.** rclpy invalidates the context before `except`/`finally` run, so logger calls print `Failed to publish log message to rosout`. Use `print` there.
- **`print()` under `ros2 launch` arrives in bursts.** Stdout is block-buffered; use `flush=True`.
- **Backgrounded `&` processes in a non-interactive shell ignore SIGINT.** Scripted Ctrl-C tests never reach the node.
