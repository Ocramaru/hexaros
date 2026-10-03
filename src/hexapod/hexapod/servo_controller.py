"""ROS node that turns JointState commands into servo positions on the hexapod's two PCA9685 boards.

Commands arrive as joint radians on `joint_commands`; only joints that change are written, and an
angle is kept only once its I2C write succeeded, so a failed write is retried by the next command.
With `dry_run` the boards sit on a FakeBus and nothing touches I2C or GPIO.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from hexapod.joints import BOARD_ADDRESSES, JOINT_INDEX, JOINT_NAMES, joint_to_servo, servo_address_channel, SERVO_MAP
from hexapod.servo_driver import ServoDriver
from hexapod.utilities import FakeBus, run_node


class ServoController(Node):
  def __init__(self):
    super().__init__('servo_controller')
    self.declare_parameter('dry_run', False)
    self.declare_parameter('board_addresses', list(BOARD_ADDRESSES))
    self.declare_parameter('servo_map', SERVO_MAP.flatten().tolist())
    self.declare_parameter('calibration', [0.0] * SERVO_MAP.size)
    self.dry_run = self.get_parameter('dry_run').value
    self.board_addresses = list(self.get_parameter('board_addresses').value)
    self.servo_map = np.reshape(self.get_parameter('servo_map').value, JOINT_NAMES.shape)
    self.calibration = np.reshape(self.get_parameter('calibration').value, JOINT_NAMES.shape)

    # one bus shared by both boards
    if self.dry_run:
      self.bus = FakeBus()
    else:
      from smbus2 import SMBus
      self.bus = SMBus(1)

    self.drivers = {address: ServoDriver(address=address, bus=self.bus) for address in self.board_addresses}

    # last command per joint, NaN = never commanded
    self.joint_radians = np.full(JOINT_NAMES.shape, np.nan)

    self.power_pin = None
    if not self.dry_run:
      from gpiozero import OutputDevice
      self.power_pin = OutputDevice(pin=4, active_high=False)  # GPIO 4 gates servo power and is active low, so on() powers the servos
      self.power_pin.on()

    # joint commands from the publisher (later the policy)
    self.create_subscription(JointState, 'joint_commands', self.callback, 10)

    mode = ' in dry run mode' if self.dry_run else ''
    self.get_logger().info(f'Servo Controller Node has been started on addresses {[hex(address) for address in self.drivers]}{mode}.')

  def write_joints(self, commands):
    """Write `commands`, a {(leg, joint): radians} dict, keeping only the angles that reached the servos."""
    target = self.joint_radians.copy()
    for index, position in commands.items(): target[index] = position
    servo_angles = joint_to_servo(target, self.calibration)
    for index, position in commands.items():
      address, channel = servo_address_channel(self.servo_map[index], self.board_addresses)
      try:
        self.drivers[address].set_angle(channel, servo_angles[index])
      except (OSError, ValueError) as e:
        self.get_logger().error(f'{JOINT_NAMES[index]} not written: {e}')
        continue
      self.joint_radians[index] = position

  def callback(self, msg):
    # only the named joints change; leave a joint out, or send NaN, to keep its last command
    if len(msg.name) != len(msg.position): return self.get_logger().error('joint_commands names and positions differ in length; ignored')
    commands = {}
    for name, position in zip(msg.name, msg.position):
      index = JOINT_INDEX.get(name)
      if index is None:
        self.get_logger().warn(f'Unknown joint {name!r} ignored')
        continue
      if np.isnan(position) or self.joint_radians[index] == position: continue  # no command, or already there
      commands[index] = position
    self.write_joints(commands)

  def destroy_node(self):
    with contextlib.ExitStack() as cleanup:  # every step runs even if one raises; the error re-raises after
      cleanup.callback(super().destroy_node)
      cleanup.callback(self.bus.close)
      if self.power_pin is not None: cleanup.callback(self.power_pin.close)
      for driver in self.drivers.values(): cleanup.callback(driver.shutdown)


def main():
  with run_node(ServoController) as node:
    rclpy.spin(node)
