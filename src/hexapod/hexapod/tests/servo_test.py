"""Hardware smoke test: moves channel 15 on board 0x41 through 90, 80, 100, 90 degrees without ROS.

Only for the Pi with the servo boards attached; run with `python3 -m hexapod.tests.servo_test`.

Author: Marco Cassar (@Ocramaru)
"""
import math
import time

from hexapod.drivers.servo import ServoDriver

if __name__ == '__main__':
  from gpiozero import OutputDevice
  power = OutputDevice(4, active_high=False)  # GPIO 4 gates servo power and is active low, so on() powers the servos
  power.on()

  with ServoDriver(0x41) as servo:
    for angle in (math.pi / 2, 4 * math.pi / 9, 5 * math.pi / 9, math.pi / 2):
      servo.set_angle(15, angle)
      time.sleep(2)
