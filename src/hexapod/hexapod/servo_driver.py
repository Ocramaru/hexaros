"""Driver for one PCA9685 16-channel PWM board driving hobby servos over I2C.

No ROS imports, so it can be tested with a fake bus. CHIP holds the PCA9685's register map and
SERVO the servo's pulse range; angles are radians, 0 to pi across the servo's travel.

Author: Marco Cassar (@Ocramaru)
"""
import math
import time


class ServoDriver:
  class CHIP:
    name = 'PCA9685'
    CHANNELS = 16

    # registers
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06

    # layout
    REGISTERS_PER_CHANNEL = 4

    # clock
    OSCILLATOR_HZ = 25_000_000
    COUNTER_SIZE = 4096
    FREQUENCY_RANGE = (24, 1525)  # Hz the prescale register can reach: 255 gives 23.8, 3 gives 1525.9 (datasheet 7.3.5)

    # bit masks
    SLEEP = 0x10
    RESTART = 0x80
    AUTO_INCREMENT = 0x20  # MODE1 bit 5: block writes fill consecutive registers
    FULL_OFF = 0x10

  class SERVO:
    MIN_PULSE = 500
    MAX_PULSE = 2500
    RANGE_PULSE = MAX_PULSE - MIN_PULSE
    MIN_ANGLE = 0.0  # radians; the servo's 500-2500 us spans 0 to pi
    MAX_ANGLE = math.pi

  def __init__(self, address, bus=None, bus_number=1, frequency=50):
    self.address = address
    self.created_bus = False

    if bus is None:
      from smbus2 import SMBus
      self.bus = SMBus(bus_number)
      self.created_bus = True
    else:
      self.bus = bus

    self._write(self.CHIP.MODE1, self.CHIP.AUTO_INCREMENT)
    self.set_pwm_frequency(frequency)

  def _read(self, register):
    return self.bus.read_byte_data(self.address, register)

  def _write(self, register, value):
    self.bus.write_byte_data(self.address, register, value)

  def _write_channel(self, channel, on, off):
    """Write a channel's ON and OFF counts in one I2C transaction (needs auto-increment)."""
    if not 0 <= channel < self.CHIP.CHANNELS: raise ValueError(f'channel {channel} is outside 0-{self.CHIP.CHANNELS - 1}')
    base = self.CHIP.LED0_ON_L + channel * self.CHIP.REGISTERS_PER_CHANNEL
    self.bus.write_i2c_block_data(self.address, base, [on & 0xFF, on >> 8, off & 0xFF, off >> 8])

  def set_pwm_frequency(self, frequency):
    """Set the PWM frequency; the chip only accepts a new prescale while asleep, so sleep, write, wake, restart."""
    low, high = self.CHIP.FREQUENCY_RANGE
    if not low <= frequency <= high: raise ValueError(f'{frequency} Hz is outside the PCA9685 range {low}-{high} Hz')

    prescale = round(self.CHIP.OSCILLATOR_HZ / (self.CHIP.COUNTER_SIZE * frequency)) - 1
    if 1_000_000 / frequency <= self.SERVO.MAX_PULSE: raise ValueError(f'{frequency} Hz period is shorter than the {self.SERVO.MAX_PULSE} us pulse')

    old_mode = self._read(self.CHIP.MODE1)
    self._write(self.CHIP.MODE1, (old_mode & 0x7F) | self.CHIP.SLEEP)
    self._write(self.CHIP.PRESCALE, prescale)
    self._write(self.CHIP.MODE1, old_mode)
    time.sleep(0.005)
    self._write(self.CHIP.MODE1, old_mode | self.CHIP.RESTART)
    self.frequency = frequency
    self.period = 1_000_000 / frequency

  def angle_to_pulse_count(self, angle):
    angle = min(max(angle, self.SERVO.MIN_ANGLE), self.SERVO.MAX_ANGLE)
    fraction = (angle - self.SERVO.MIN_ANGLE) / (self.SERVO.MAX_ANGLE - self.SERVO.MIN_ANGLE)  # normalize
    pulse = self.SERVO.MIN_PULSE + fraction * self.SERVO.RANGE_PULSE
    return int(pulse / self.period * self.CHIP.COUNTER_SIZE)

  def set_angle(self, channel, angle):
    self._write_channel(channel, 0, self.angle_to_pulse_count(angle))

  def relax(self, channel):
    self._write_channel(channel, 0, self.CHIP.FULL_OFF << 8)  # full-OFF bit lands in OFF_H

  def close(self):
    if not self.created_bus: return
    self.bus.close()

  def shutdown(self):
    try:
      for channel in range(self.CHIP.CHANNELS):
        self.relax(channel)
    finally:
      self.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.shutdown()
