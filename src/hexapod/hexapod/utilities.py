import contextlib

import rclpy
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.node import Node


@contextlib.contextmanager
def run_node(node_class: type[Node]):
    node = None
    try:
        rclpy.init()
        node = node_class()
        yield node
    except KeyboardInterrupt:
        pass
    finally:
        if node: node.destroy_node()
        rclpy.try_shutdown()


class FakeBus:
    def __init__(self):
        self.registers = {}

    def write_byte_data(self, address, register, value):
        if not 0 <= value <= 255: raise ValueError("Value must be between 0 and 255")
        self.registers[(address, register)] = value
        print(f'write addr:0x{address:02x}, register: 0x{register:02x}, value:{value}', flush=True)

    def read_byte_data(self, address, register):
        return self.registers.get((address, register), 0)

    def close(self):
        pass