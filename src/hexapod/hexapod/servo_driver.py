import time


# Raspi PCA9685 16-Channel PWM Servo Driver
class ServoDriver:
    class CHIP:
        name = "PCA9685"

        # registers
        MODE1 = 0x00
        PRESCALE = 0xFE
        LED0_ON_L = 0x06

        # layout
        REGISTERS_PER_CHANNEL = 4

        # clock
        OSCILLATOR_HZ = 25_000_000
        COUNTER_SIZE = 4096

        # bit masks
        SLEEP = 0x10
        RESTART = 0x80
        FULL_OFF = 0x10

    class SERVO:
        MIN_PULSE = 500
        MAX_PULSE = 2500
        RANGE_PULSE = MAX_PULSE - MIN_PULSE
        MIN_ANGLE = 0
        MAX_ANGLE = 180

    def __init__(self, address, bus=None, bus_number=1, frequency=50):
        self.address = address
        self.frequency = frequency
        self.period = 1_000_000 / frequency

        self.created_bus = False

        if bus is None:
            from smbus2 import SMBus
            self.bus = SMBus(bus_number)
            self.created_bus = True
        else:    
            self.bus=bus

        self._write(self.CHIP.MODE1, 0x00)
        self.set_pwm_frequency(self.frequency)

    def _read(self, register):
        """Read an unsigned byte from the I2C device."""
        return self.bus.read_byte_data(self.address, register)

    def _write(self, register, value):
        """Writes an 8-bit value to the specified register/address."""
        self.bus.write_byte_data(self.address, register, value)

    def set_pwm_frequency(self, frequency):
        """Sets the PWM frequency."""
        prescale = round(self.CHIP.OSCILLATOR_HZ / (self.CHIP.COUNTER_SIZE * frequency)) - 1
        old_mode = self._read(self.CHIP.MODE1)
        new_mode = (old_mode & 0x7F) | self.CHIP.SLEEP  # 0x10
        self._write(self.CHIP.MODE1, new_mode)
        self._write(self.CHIP.PRESCALE, prescale)
        self._write(self.CHIP.MODE1, old_mode)
        time.sleep(0.005)
        self._write(self.CHIP.MODE1, old_mode | self.CHIP.RESTART)  # 0x80

    def angle_to_pulse_count(self, angle):
        pulse = self.SERVO.MIN_PULSE + (angle / self.SERVO.MAX_ANGLE) * self.SERVO.RANGE_PULSE
        count = pulse / self.period * self.CHIP.COUNTER_SIZE
        return int(count)

    def set_angle(self, channel, angle):
        count = self.angle_to_pulse_count(angle)
        base = self.CHIP.LED0_ON_L + channel * self.CHIP.REGISTERS_PER_CHANNEL
        self._write(base, 0)
        self._write(base + 1, 0)
        self._write(base + 2, count & 0xFF)
        self._write(base + 3, (count >> 8) & 0xFF)

    def relax(self, channel):
        base = self.CHIP.LED0_ON_L + channel * self.CHIP.REGISTERS_PER_CHANNEL
        self._write(base, 0)
        self._write(base + 1, 0)
        self._write(base + 2, 0)
        self._write(base + 3, self.CHIP.FULL_OFF)

    def close(self):
        """Close the I2C bus."""
        if not self.created_bus: return
        self.bus.close()

    def shutdown(self):
        try:
            for channel in range(16):
                self.relax(channel)
        except KeyboardInterrupt: pass
        finally:
            self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()