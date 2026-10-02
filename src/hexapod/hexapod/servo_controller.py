import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from hexapod.servo_driver import ServoDriver
from hexapod.utilities import FakeBus, run_node


class ServoController(Node):
    def __init__(self):
        super().__init__('servo_controller')

        self.declare_parameter('address', 0x41)
        self.declare_parameter('channel', 15)
        self.declare_parameter('dry_run', False)

        self.address = self.get_parameter('address').value
        self.channel = self.get_parameter('channel').value
        self.dry_run = self.get_parameter('dry_run').value

        self.bus = FakeBus() if self.dry_run else None
        self.servo_driver = ServoDriver(address=self.address, bus=self.bus)

        self.power_pin = None
        if not self.dry_run:
            from gpiozero import OutputDevice
            self.power_pin = OutputDevice(pin=4)
            self.power_pin.off()
        
        self.create_subscription(Float32, 'servo/target_angle', self.servo_callback, 10)

        self.get_logger().info(f'Servo Controller Node has been started on address: {self.address} over channel: {self.channel} in mode dry_run:{self.dry_run}')

    def servo_callback(self, msg):
        angle = float(np.clip(msg.data, self.servo_driver.SERVO.MIN_ANGLE, self.servo_driver.SERVO.MAX_ANGLE))
        self.get_logger().info(f'Received: {msg.data} -> Clipped: {angle}')
        try:
            self.servo_driver.set_angle(self.channel, angle)
        except ValueError as e:
            self.get_logger().error(f'ValueError occurred: {e}')

    def destroy_node(self):
        self.servo_driver.shutdown()
        if self.power_pin is not None:
            self.power_pin.close()
        super().destroy_node()

def main():
    with run_node(ServoController) as node:
        rclpy.spin(node)