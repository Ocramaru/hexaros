"""Helpers shared by the hexapod nodes: a context manager that runs a node, and a fake I2C bus for dry runs.

FakeBus stores register writes and emulates the PCA9685's auto-increment, so dry runs catch a missing MODE1 setup.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib

import rclpy
from rclpy.node import Node


@contextlib.contextmanager
def run_node(node_class: type[Node]):
  with contextlib.ExitStack() as cleanup:  # unwinds last-first: destroy the node, then shut rclpy down
    rclpy.init()
    cleanup.callback(rclpy.try_shutdown)
    node = node_class()
    cleanup.callback(node.destroy_node)
    with contextlib.suppress(KeyboardInterrupt):  # Ctrl-C ends the node quietly
      yield node


class FakeBus:
  def __init__(self, read_byte_value=0):
    self.registers = {}
    self.read_byte_value = read_byte_value  # what a bare read_byte returns, e.g. an ADC reading

  def write_byte(self, address, value):
    if not 0 <= value <= 255: raise ValueError('Value must be between 0 and 255')
    print(f'write addr:0x{address:02x}, command: 0x{value:02x}', flush=True)

  def read_byte(self, address):
    return self.read_byte_value

  def write_byte_data(self, address, register, value):
    if not 0 <= value <= 255: raise ValueError('Value must be between 0 and 255')
    self.registers[(address, register)] = value
    print(f'write addr:0x{address:02x}, register: 0x{register:02x}, value:{value}', flush=True)

  def write_i2c_block_data(self, address, register, values):
    if not all(0 <= v <= 255 for v in values): raise ValueError('Value must be between 0 and 255')
    auto_increment = self.registers.get((address, 0x00), 0) & 0x20  # like the chip: without MODE1 AI, every byte hits one register
    for offset, value in enumerate(values):
      self.registers[(address, register + (offset if auto_increment else 0))] = value
    print(f'block addr:0x{address:02x}, register: 0x{register:02x}, values:{list(values)}', flush=True)

  def read_byte_data(self, address, register):
    return self.registers.get((address, register), 0)

  def close(self):
    pass
