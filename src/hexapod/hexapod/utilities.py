"""Helpers shared by the hexapod nodes: a context manager that runs a node.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib
import signal

import rclpy
from rclpy.node import Node


@contextlib.contextmanager
def run_node(node_class: type[Node]):
  with contextlib.ExitStack() as cleanup:  # unwinds last-first: destroy the node, then shut rclpy down
    rclpy.init()
    cleanup.callback(rclpy.try_shutdown)
    node = node_class()
    cleanup.callback(node.destroy_node)
    # Ctrl-C reaches every node twice, from the terminal and from ros2 launch; the second must not cut cleanup short
    cleanup.callback(signal.signal, signal.SIGINT, signal.SIG_IGN)
    with contextlib.suppress(KeyboardInterrupt):  # Ctrl-C ends the node quietly
      yield node
