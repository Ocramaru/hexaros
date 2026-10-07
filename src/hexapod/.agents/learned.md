---
name: learned
description: Traps that already cost time in the hexapod package — node-name YAML keys, ROS libcamera on the Pi, uncalibrated legs, the kit's startup pose, rclpy shutdown, launch output buffering, scripted SIGINT tests
kind: learned
---

# Learned

## Traps

- **pack0 reads high while the servos draw current.** Calibrated at 8.35 V at rest, it read 8.59 V with Gerry standing, where a loaded pack should sag; likely servo current shifting the ADC's ground, so under load pack0 looks healthier than it is.
- **Sparky's dry runs drive the real Gerry.** Both sit on ROS domain 0, so an orphaned `servo_publisher` from a closed dry-run launch stood Gerry up the moment his controller started; check `ros2 node list` before powering servos.
- **rclpy throttles per logger object.** A fresh `get_child(name)` each call never throttles; create child loggers once.
- **`-p robot_description:="$(xacro ...)"` parses the URDF as YAML.** A `: ` in an XML comment breaks it; launch files with `ParameterValue(..., value_type=str)` are safe.
- **The VS Code URDF extension resolves xacro macros by name alone.** A macro named like a URDF element (`inertia`) recurses there; real xacro is fine.
- **Raw camera frames do not cross Wi-Fi.** 640x480 `rgb8` at 28 fps is about 25 MB/s; with gscam decoding to raw, nothing reached Foxglove on sparky. `image_transport_plugins` also re-encodes every frame per subscribed transport, and `compressedDepth` fails on colour images every frame. Publish the JPEGs (`image_encoding: jpeg`), about 12 KB a frame.
- **A YAML key that misses the node's name is silently ignored.** `imu_filter_madgwick`'s node is `imu_filter_madgwick`, not `imu_filter`; under the wrong key it kept `use_mag: true` and waited forever on `imu/mag`. Check with `ros2 node list`.
- **ROS's `ros-jazzy-libcamera` cannot drive the Pi camera.** Its `ipa_rpi_vc4.so` signature is invalid, so libcamera isolates it in a proxy process, which crashes in 0.7.2 (`A list of V4L2 controls requires a ControlInfoMap`). Before that, the container needs `/run/udev` to see the camera, and Docker's seccomp answers libcamera's `clone3` with ENOSYS. Hence the host's `rpicam-vid` streams to `gscam` instead.
- **Uncalibrated legs differ by tens of millimetres at the foot.** At one commanded pose, leg 4 hovered where the other five touched; leg 3 was next highest.
- **The kit's startup pose `[140, 0, 0]` lifts the feet to hip height.** It is a lying pose with legs held out, not a rest; ramping into it then cutting power lets the legs fall.
- **`SignalHandlerOptions.NO` makes the node unkillable.** Tested on Jazzy: `spin` then ignores SIGINT.
- **ROS logging fails during Ctrl-C cleanup.** rclpy invalidates the context before `except`/`finally` run, so logger calls print `Failed to publish log message to rosout`. Use `print` there.
- **`print()` under `ros2 launch` arrives in bursts.** Stdout is block-buffered; use `flush=True`.
- **Backgrounded `&` processes in a non-interactive shell ignore SIGINT.** Scripted Ctrl-C tests never reach the node.
