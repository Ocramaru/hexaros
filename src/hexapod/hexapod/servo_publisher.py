import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from hexapod.utilities import run_node


class ServoPublisher(Node):
    def __init__(self):
        super().__init__('servo_publisher')

        self.current_angle = 60.0
        self.angle_step_size = 2
        self.target_angle_arr = [45.0, 90.0]
        self.target_angle_index = 0

        self.publisher = self.create_publisher(Float32, 'servo/target_angle', 10)
        self.timer = self.create_timer(0.5, self.publish_target_angle)

        self.get_logger().info('Servo Publisher Node has been started.')

    def step_angle(self):
        if self.current_angle < self.target_angle_arr[self.target_angle_index]:
            self.current_angle += self.angle_step_size
        elif self.current_angle > self.target_angle_arr[self.target_angle_index]:
            self.current_angle -= self.angle_step_size

        if abs(self.target_angle_arr[self.target_angle_index] - self.current_angle) < self.angle_step_size:
            self.current_angle = self.target_angle_arr[self.target_angle_index]

        if self.current_angle == self.target_angle_arr[self.target_angle_index]:
            self.target_angle_index = (self.target_angle_index + 1) % len(self.target_angle_arr)

    def publish_target_angle(self):
        msg = Float32()
        self.step_angle()
        msg.data = self.current_angle
        self.publisher.publish(msg)

def main():
    with run_node(ServoPublisher) as node:
        rclpy.spin(node)