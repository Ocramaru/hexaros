"""ROS node that reads the battery packs through the ADS7830 and publishes BatteryState on `battery/<name>`.

Percentage is estimated from smoothed voltage; current and charge are NaN, since the board has no current sensor.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib
import dataclasses
import math

import numpy as np
import rclpy
from rclpy.impl.rcutils_logger import RcutilsLogger
from rclpy.node import Node
from rclpy.publisher import Publisher
from sensor_msgs.msg import BatteryState

from hexapod.drivers.adc import AdcDriver
from hexapod.tests.fake_bus import FakeBus
from hexapod.utilities import run_node

# typical Li-ion resting voltage per cell and charge percent
CELL_CURVE_VOLTS = [3.0, 3.3, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2]
CELL_CURVE_PERCENT = [0, 5, 15, 25, 45, 60, 70, 80, 90, 100]


def cell_percentage(cell_volts):
  """Estimate charge on BatteryState's 0-1 scale from one cell's voltage."""
  return float(np.interp(cell_volts, CELL_CURVE_VOLTS, CELL_CURVE_PERCENT)) / 100


@dataclasses.dataclass
class Pack:
  channel: int
  name: str
  divider: float
  publisher: Publisher
  logger: RcutilsLogger  # kept, since rclpy's throttle state lives on the logger object
  smoothed: float | None = None


class BatteryMonitor(Node):
  def __init__(self):
    super().__init__('battery_monitor')
    self.declare_parameter('dry_run', False)
    self.declare_parameter('adc_address', 0x48)
    self.declare_parameter('channels', [0, 4])
    self.declare_parameter('names', ['pack0', 'pack1'])
    self.declare_parameter('dividers', [3.0, 3.0])
    self.declare_parameter('cells_in_series', 2)
    self.declare_parameter('warn_cell_volts', 3.3)
    self.declare_parameter('critical_cell_volts', 3.0)
    self.declare_parameter('design_capacity', 3.5)
    self.declare_parameter('smoothing', 0.2)
    self.declare_parameter('period', 1.0)

    dry_run = self.get_parameter('dry_run').value
    channels = self.get_parameter('channels').value
    names = self.get_parameter('names').value
    dividers = self.get_parameter('dividers').value
    if not len(channels) == len(names) == len(dividers): raise ValueError('channels, names and dividers must be the same length')
    self.cells = self.get_parameter('cells_in_series').value
    self.warn_volts = self.get_parameter('warn_cell_volts').value
    self.critical_volts = self.get_parameter('critical_cell_volts').value
    self.design_capacity = self.get_parameter('design_capacity').value
    self.smoothing = self.get_parameter('smoothing').value

    bus = FakeBus(read_byte_value=140) if dry_run else None  # a healthy 3.5-4.1 V per cell through either divider
    self.adc = AdcDriver(address=self.get_parameter('adc_address').value, bus=bus)
    self.packs = [
      Pack(channel, name, divider, self.create_publisher(BatteryState, f'battery/{name}', 10), self.get_logger().get_child(name))
      for channel, name, divider in zip(channels, names, dividers)
    ]
    self.create_timer(self.get_parameter('period').value, self.publish_batteries)

    mode = ' in dry run mode' if dry_run else ''
    self.get_logger().info(f'Battery Monitor Node has been started for {list(names)}{mode}.')

  def publish_batteries(self):
    for pack in self.packs:
      try:
        volts = self.adc.read_pin_volts(pack.channel) * pack.divider
      except OSError as e:
        self.get_logger().error(f'{pack.name} not read: {e}')
        continue
      pack.smoothed = volts if pack.smoothed is None else pack.smoothed + self.smoothing * (volts - pack.smoothed)  # exponential smoothing against load spikes
      cell_volts = pack.smoothed / self.cells

      msg = BatteryState()
      msg.header.stamp = self.get_clock().now().to_msg()
      msg.voltage = volts
      msg.percentage = cell_percentage(cell_volts)
      msg.design_capacity = self.design_capacity
      msg.current = msg.charge = msg.capacity = math.nan
      msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LION
      msg.present = True
      msg.location = pack.name
      pack.publisher.publish(msg)

      if cell_volts < self.critical_volts:
        pack.logger.error(f'critical: {pack.smoothed:.2f} V ({cell_volts:.2f} V per cell)', throttle_duration_sec=10.0)
      elif cell_volts < self.warn_volts:
        pack.logger.warning(f'low: {pack.smoothed:.2f} V ({cell_volts:.2f} V per cell)', throttle_duration_sec=10.0)

  def destroy_node(self):
    with contextlib.ExitStack() as cleanup:  # every step runs even if one raises; the error re-raises after
      cleanup.callback(super().destroy_node)
      cleanup.callback(self.adc.close)


def main():
  with run_node(BatteryMonitor) as node:
    rclpy.spin(node)
