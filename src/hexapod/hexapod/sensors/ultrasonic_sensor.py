"""ROS node that reads the HC-SR04 ultrasonic sensor through gpiozero and publishes Range on `ultrasonic/range`.

No echo within `max_range` is published as +inf, REP 117's no-detection value. With `dry_run` it publishes random
distances and touches no GPIO.

Author: Marco Cassar (@Ocramaru)
"""
import contextlib
import math

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range

from hexapod.utilities import run_node


class UltrasonicSensor(Node):

  def __init__(self):
    super().__init__('ultrasonic_sensor')
    self.declare_parameter('dry_run', False)
    self.declare_parameter('trigger_pin', 27)
    self.declare_parameter('echo_pin', 22)
    self.declare_parameter('min_range', 0.02)
    self.declare_parameter('max_range', 3.0)
    self.declare_parameter('field_of_view', 0.26)
    self.declare_parameter('frame_id', 'ultrasonic')
    self.declare_parameter('period', 0.1)

    dry_run = self.get_parameter('dry_run').value
    self.min_range = self.get_parameter('min_range').value
    self.max_range = self.get_parameter('max_range').value
    self.field_of_view = self.get_parameter('field_of_view').value
    self.frame_id = self.get_parameter('frame_id').value

    self.sensor = None
    self.rng = np.random.default_rng()
    if not dry_run:
      from gpiozero import DistanceSensor
      self.sensor = DistanceSensor(echo=self.get_parameter('echo_pin').value, trigger=self.get_parameter('trigger_pin').value,
                                   max_distance=self.max_range)
    self.publisher = self.create_publisher(Range, 'ultrasonic/range', 10)
    self.create_timer(self.get_parameter('period').value, self.publish_range)

    mode = ' in dry run mode' if dry_run else ''
    self.get_logger().info(f'Ultrasonic Sensor Node has been started{mode}.')

  def publish_range(self):
    if self.sensor is None:
      distance = self.rng.uniform(self.min_range, self.max_range)
    else:
      distance = self.sensor.distance  # metres, the median of gpiozero's recent echoes, capped at max_distance
    if distance >= self.max_range: distance = math.inf

    msg = Range()
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.header.frame_id = self.frame_id
    msg.radiation_type = Range.ULTRASOUND
    msg.field_of_view = self.field_of_view
    msg.min_range = self.min_range
    msg.max_range = self.max_range
    msg.range = float(distance)
    self.publisher.publish(msg)

  def destroy_node(self):
    with contextlib.ExitStack() as cleanup:  # every step runs even if one raises; the error re-raises after
      cleanup.callback(super().destroy_node)
      if self.sensor is not None:
        cleanup.callback(self.sensor.close)


def main():
  with run_node(UltrasonicSensor) as node:
    rclpy.spin(node)
