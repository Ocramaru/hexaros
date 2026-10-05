"""Driver for the MPU6050 accelerometer and gyro on the hexapod's board.

No ROS imports, so it can be tested with a fake bus. Readings are SI units in the chip's own axes; placing the chip
on the body is the URDF's job.

Author: Marco Cassar (@Ocramaru)
"""
import time

import numpy as np


class ImuDriver:
  # registers
  CONFIG = 0x1A
  GYRO_CONFIG = 0x1B
  ACCEL_CONFIG = 0x1C
  ACCEL_XOUT_H = 0x3B
  PWR_MGMT_1 = 0x6B

  # register values
  CLOCK_GYRO_X = 0x01  # PWR_MGMT_1: awake, clocked from the gyro's PLL, steadier than the internal oscillator
  LOW_PASS_44HZ = 0x03  # CONFIG: digital low-pass at 44 Hz accel, 42 Hz gyro, against servo vibration
  GYRO_500_DPS = 0x08
  ACCEL_4G = 0x08

  # scale at those ranges
  GYRO_LSB_PER_DPS = 65.5
  ACCEL_LSB_PER_G = 8192
  GRAVITY = 9.80665
  START_SECONDS = 0.05  # the gyro needs 30 ms to start (datasheet 6.1)

  DATA_LENGTH = 14  # accel x, y, z, temperature, gyro x, y, z, each a big-endian int16

  def __init__(self, address=0x68, bus=None, bus_number=1):
    self.address = address
    self.created_bus = False

    if bus is None:
      from smbus2 import SMBus
      self.bus = SMBus(bus_number)
      self.created_bus = True
    else:
      self.bus = bus

    self._write(self.PWR_MGMT_1, self.CLOCK_GYRO_X)
    time.sleep(self.START_SECONDS)
    self._write(self.CONFIG, self.LOW_PASS_44HZ)
    self._write(self.GYRO_CONFIG, self.GYRO_500_DPS)
    self._write(self.ACCEL_CONFIG, self.ACCEL_4G)

  def _write(self, register, value):
    self.bus.write_byte_data(self.address, register, value)

  def read(self):
    """Read acceleration in m/s^2 and angular velocity in rad/s, each an (x, y, z) array."""
    data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, self.DATA_LENGTH)
    raw = np.frombuffer(bytes(data), dtype='>i2')
    accel = raw[0:3] / self.ACCEL_LSB_PER_G * self.GRAVITY
    gyro = np.radians(raw[4:7] / self.GYRO_LSB_PER_DPS)
    return accel, gyro

  def close(self):
    if not self.created_bus: return
    self.bus.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()
