"""ROS node that turns JointState commands into leg and head servo positions on the hexapod's two PCA9685 boards.

Commands arrive as joint radians on `joint_commands`; only joints that change are written, and an
angle is kept only once its I2C write succeeded, so a failed write is retried by the next command.
With `dry_run` the boards sit on a FakeBus and nothing touches I2C or GPIO.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib
import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from hexapod.drivers.servo import ServoDriver
from hexapod.joints import (BOARD_ADDRESSES, JOINT_INDEX, JOINT_NAMES, joint_to_servo, REST_POSE, servo_address_channel,
                            SERVO_LIMITS, SERVO_MAP)
from hexapod.tests.fake_bus import FakeBus
from hexapod.utilities import run_node


class ServoController(Node):
  def __init__(self):
    super().__init__('servo_controller')
    self.declare_parameter('dry_run', False)
    self.declare_parameter('board_addresses', list(BOARD_ADDRESSES))
    self.declare_parameter('servo_map', SERVO_MAP.tolist())
    self.declare_parameter('calibration', [0.0] * len(JOINT_NAMES))
    self.declare_parameter('state_period', 0.05)
    self.declare_parameter('log_bus', False)  # dry run only: print every I2C write
    for name in JOINT_NAMES:  # one servo_limits.<joint> parameter each, so the YAML only lists exceptions
      self.declare_parameter(f'servo_limits.{name}', list(SERVO_LIMITS.get(name, (0.0, np.pi))))
    self.dry_run = self.get_parameter('dry_run').value
    self.board_addresses = list(self.get_parameter('board_addresses').value)

    # per-joint maps, each in JOINT_NAMES order
    per_joint_maps = {name: np.array(self.get_parameter(name).value) for name in ('servo_map', 'calibration')}
    for name, values in per_joint_maps.items():
      if len(values) != len(JOINT_NAMES): raise ValueError(f'{name} has {len(values)} entries, expected {len(JOINT_NAMES)}')
    self.servo_map, self.calibration = per_joint_maps.values()
    self.servo_min, self.servo_max = np.array([self.get_parameter(f'servo_limits.{name}').value for name in JOINT_NAMES]).T

    # one bus shared by both boards
    if self.dry_run:
      self.bus = FakeBus(verbose=self.get_parameter('log_bus').value)
    else:
      from smbus2 import SMBus
      self.bus = SMBus(1)

    self.drivers = {address: ServoDriver(address=address, bus=self.bus) for address in self.board_addresses}

    # last command per joint, NaN = never commanded
    self.joint_radians = np.full(len(JOINT_NAMES), np.nan)

    self.power_pin = None
    if not self.dry_run:
      from gpiozero import OutputDevice
      self.power_pin = OutputDevice(pin=4, active_high=False)  # GPIO 4 gates servo power and is active low, so on() powers the servos
      self.power_pin.on()

    # joint commands from the publisher (later the policy)
    self.create_subscription(JointState, 'joint_commands', self.callback, 10)
    # the commanded pose, for robot_state_publisher; the servos report no position of their own
    self.state_publisher = self.create_publisher(JointState, 'joint_states', 10)
    self.create_timer(self.get_parameter('state_period').value, self.publish_state)

    mode = ' in dry run mode' if self.dry_run else ''
    self.get_logger().info(f'Servo Controller Node has been started on addresses {[hex(address) for address in self.drivers]}{mode}.')

  def write_joints(self, commands):
    """Write `commands`, a {joint index: radians} dict, keeping only the angles that reached the servos."""
    target = self.joint_radians.copy()
    for index, position in commands.items():
      target[index] = position
    servo_angles = joint_to_servo(target, self.calibration, self.servo_min, self.servo_max)
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
        self.get_logger().warning(f'Unknown joint {name!r} ignored')
        continue
      if np.isnan(position) or self.joint_radians[index] == position: continue  # no command, or already there
      commands[index] = position
    self.write_joints(commands)

  def publish_state(self):
    commanded = ~np.isnan(self.joint_radians)  # joint used (bool)
    msg = JointState(name=[name for name, known in zip(JOINT_NAMES, commanded) if known], position=self.joint_radians[commanded].tolist())
    msg.header.stamp = self.get_clock().now().to_msg()
    self.state_publisher.publish(msg)

  def lie_down(self, duration=1.0, steps=20):
    """Ramp every commanded joint to REST_POSE, so a standing robot lowers itself before power is cut."""
    commanded = np.flatnonzero(~np.isnan(self.joint_radians))
    start = self.joint_radians[commanded]
    for fraction in np.linspace(0, 1, steps + 1)[1:]:
      self.write_joints(dict(zip(commanded, start + fraction * (REST_POSE[commanded] - start))))
      time.sleep(duration / steps)

  def destroy_node(self):
    with contextlib.ExitStack() as cleanup:  # runs last-registered first: lie down, power off, relax, close
      cleanup.callback(super().destroy_node)
      cleanup.callback(self.bus.close)
      for driver in self.drivers.values():
        cleanup.callback(driver.shutdown)
      if self.power_pin is not None:
        cleanup.callback(self.power_pin.close)
        cleanup.callback(self.power_pin.off)
      cleanup.callback(self.lie_down)


def main():
  with run_node(ServoController) as node:
    rclpy.spin(node)
