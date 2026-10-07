"""ROS node that stands in for gscam in dry runs, publishing random noise as JPEG images with a placeholder camera_info.

It takes gscam's node name and topics, so anything that consumes the camera runs unchanged on sparky. Like gscam in
jpeg mode it publishes only the compressed image; consumers decode it themselves.

Author: Marco Cassar (@Ocramaru)
"""
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, CompressedImage
from std_msgs.msg import Header

from hexapod.utilities import run_node


class FakeCamera(Node):
  def __init__(self):
    super().__init__('camera')
    self.declare_parameter('width', 640)
    self.declare_parameter('height', 480)
    self.declare_parameter('frame_id', 'camera_optical')
    self.declare_parameter('period', 0.1)
    self.width = self.get_parameter('width').value
    self.height = self.get_parameter('height').value
    self.frame_id = self.get_parameter('frame_id').value

    self.rng = np.random.default_rng()
    self.info = self.camera_info()
    self.compressed_publisher = self.create_publisher(CompressedImage, 'camera/image_raw/compressed', 10)
    self.info_publisher = self.create_publisher(CameraInfo, 'camera/camera_info', 10)
    self.create_timer(self.get_parameter('period').value, self.publish_frame)

    self.get_logger().info(f'Fake Camera Node has been started at {self.width}x{self.height}.')

  def camera_info(self):
    """Pinhole model with a 90 degree horizontal field of view and no distortion."""
    focal = self.width / 2  # tan(45 degrees) is 1, so half the width spans 45 degrees
    cx, cy = self.width / 2, self.height / 2
    return CameraInfo(width=self.width, height=self.height, distortion_model='plumb_bob', d=[0.0] * 5,
                      k=[focal, 0.0, cx, 0.0, focal, cy, 0.0, 0.0, 1.0],
                      r=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                      p=[focal, 0.0, cx, 0.0, 0.0, focal, cy, 0.0, 0.0, 0.0, 1.0, 0.0])

  def publish_frame(self):
    pixels = self.rng.integers(0, 256, (self.height, self.width, 3), dtype=np.uint8)
    header = Header(stamp=self.get_clock().now().to_msg(), frame_id=self.frame_id)
    _, jpeg = cv2.imencode('.jpg', pixels)
    self.info.header = header
    self.compressed_publisher.publish(CompressedImage(header=header, format='jpeg', data=jpeg.tobytes()))
    self.info_publisher.publish(self.info)


def main():
  with run_node(FakeCamera) as node:
    rclpy.spin(node)
