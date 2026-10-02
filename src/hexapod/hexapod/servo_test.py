# This should only run on the hardware

import time

from hexapod.servo_driver import ServoDriver

if __name__ == '__main__':
    from gpiozero import OutputDevice
    power = OutputDevice(4)  # kit: GPIO 4 gates servo power, low = on
    power.off()

    with ServoDriver(0x41) as servo:
        for angle in (90, 80, 100, 90):
            servo.set_angle(15, angle)
            time.sleep(2)
