"""ROS node that reads the MPU6050 and publishes raw Imu messages on `imu/data_raw`.

Angular velocity has the calibrated gyro bias removed. Orientation is left to imu_filter_madgwick, which publishes
`imu/data`.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

from hexapod.drivers.imu import ImuDriver
from hexapod.tests.fake_bus import FakeBus
from hexapod.utilities import run_node


class ImuSensor(Node):
  def __init__(self):
    super().__init__('imu_sensor')
    self.declare_parameter('dry_run', False)
    self.declare_parameter('address', 0x68)
    self.declare_parameter('frame_id', 'imu')
    self.declare_parameter('period', 0.01)
    self.declare_parameter('gyro_bias', [0.0, 0.0, 0.0])

    dry_run = self.get_parameter('dry_run').value
    address = self.get_parameter('address').value
    self.frame_id = self.get_parameter('frame_id').value
    self.gyro_bias = np.array(self.get_parameter('gyro_bias').value)
    if len(self.gyro_bias) != 3: raise ValueError(f'gyro_bias has {len(self.gyro_bias)} entries, expected 3')

    bus = None
    if dry_run:
      bus = FakeBus()
      bus.registers[(address, ImuDriver.ACCEL_XOUT_H + 4)] = 0x20  # accel z high byte: 0x2000 is 1 g, a level robot at rest
    self.imu = ImuDriver(address=address, bus=bus)
    self.publisher = self.create_publisher(Imu, 'imu/data_raw', 10)
    self.create_timer(self.get_parameter('period').value, self.publish_imu)

    mode = ' in dry run mode' if dry_run else ''
    self.get_logger().info(f'IMU Sensor Node has been started on address {hex(address)}{mode}.')

  def publish_imu(self):
    try:
      accel, gyro = self.imu.read()
    except OSError as e:
      self.get_logger().error(f'IMU not read: {e}', throttle_duration_sec=1.0)
      return
    gyro = gyro - self.gyro_bias

    msg = Imu()
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.header.frame_id = self.frame_id
    msg.orientation_covariance[0] = -1.0  # no orientation estimate in this message
    msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z = gyro.tolist()
    msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z = accel.tolist()
    self.publisher.publish(msg)

  def destroy_node(self):
    with contextlib.ExitStack() as cleanup:  # every step runs even if one raises; the error re-raises after
      cleanup.callback(super().destroy_node)
      cleanup.callback(self.imu.close)


def main():
  with run_node(ImuSensor) as node:
    rclpy.spin(node)
