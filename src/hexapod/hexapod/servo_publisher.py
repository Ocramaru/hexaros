"""Test publisher: walks all 18 joints from the assembly pose to the standing pose, then bounces joint 1.

Sends full JointState commands on `joint_commands` at 20 Hz; the controller skips joints that did not change.

Author: Marco Cassar (@Ocramaru)
"""
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

from hexapod.joints import JOINT_NAMES, LEGS, STAND_POSE
from hexapod.utilities import run_node


class ServoPublisher(Node):
  def __init__(self):
    super().__init__('servo_publisher')

    # all 18 joints in radians, stepping from the assembly pose (0) to the standing pose, then bouncing joint 1 on every leg
    self.joint_angles = np.zeros(len(JOINT_NAMES))
    bounce = np.zeros(len(JOINT_NAMES))
    bounce[LEGS][1::3] = np.radians(5)  # joint 1 of every leg
    self.targets = [STAND_POSE, STAND_POSE + bounce, STAND_POSE - bounce]
    self.target_index = 0
    self.step_size = np.radians(2)

    self.publisher = self.create_publisher(JointState, 'joint_commands', 10)
    self.timer = self.create_timer(0.05, self.publish_joints)

    self.get_logger().info('Servo Publisher Node has been started.')

  def step_joints(self):
    # each joint moves towards its target by at most one step, and lands exactly on it
    target = self.targets[self.target_index]
    diff = target - self.joint_angles
    self.joint_angles = np.where(np.abs(diff) <= self.step_size, target, self.joint_angles + np.sign(diff) * self.step_size)
    # stand first, then alternate between bounce up (1) and bounce down (2)
    if np.array_equal(self.joint_angles, target):
      self.target_index = 2 if self.target_index == 1 else 1

  def publish_joints(self):
    self.step_joints()
    msg = JointState()
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.name = JOINT_NAMES
    msg.position = self.joint_angles.tolist()
    self.publisher.publish(msg)


def main():
  with run_node(ServoPublisher) as node:
    rclpy.spin(node)
