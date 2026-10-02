---
name: learned
description: Traps that already cost time in the hexapod package — rclpy shutdown behaviour, launch output buffering, scripted SIGINT tests
kind: learned
---

# Learned

## Traps

- **`SignalHandlerOptions.NO` makes the node unkillable.** Tested on Jazzy: `spin` then ignores SIGINT.
- **ROS logging fails during Ctrl-C cleanup.** rclpy invalidates the context before `except`/`finally` run, so logger calls print `Failed to publish log message to rosout`. Use `print` there.
- **`print()` under `ros2 launch` arrives in bursts.** Stdout is block-buffered; use `flush=True`.
- **Backgrounded `&` processes in a non-interactive shell ignore SIGINT.** Scripted Ctrl-C tests never reach the node.
