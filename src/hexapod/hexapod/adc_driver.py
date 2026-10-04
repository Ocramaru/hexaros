"""Driver for the ADS7830 8-channel, 8-bit ADC that measures the hexapod's battery voltages.

No ROS imports, so it can be tested with a fake bus. Voltages are at the chip's input pin; scaling back up through
the board's voltage dividers is the caller's job, since each pack has its own.

Author: Marco Cassar (@Ocramaru)
"""


class AdcDriver:
  COMMAND = 0x84  # single-ended input with the converter on, as the kit's adc.py sends it
  CHANNELS = 8
  FULL_SCALE = 255
  REFERENCE_VOLTS = 5.0
  STABLE_READ_ATTEMPTS = 5

  def __init__(self, address=0x48, bus=None, bus_number=1):
    self.address = address
    self.created_bus = False

    if bus is None:
      from smbus2 import SMBus
      self.bus = SMBus(bus_number)
      self.created_bus = True
    else:
      self.bus = bus

  def read_raw(self, channel):
    """Read one channel's 8-bit value, accepting it once two consecutive reads agree."""
    if not 0 <= channel < self.CHANNELS: raise ValueError(f'channel {channel} is outside 0-{self.CHANNELS - 1}')
    select = ((channel << 2) | (channel >> 1)) & 0x07  # the ADS7830 numbers single-ended inputs in interleaved order
    self.bus.write_byte(self.address, self.COMMAND | select << 4)
    value = self.bus.read_byte(self.address)
    for _ in range(self.STABLE_READ_ATTEMPTS):
      previous, value = value, self.bus.read_byte(self.address)
      if value == previous: break
    return value

  def read_pin_volts(self, channel):
    return self.read_raw(channel) / self.FULL_SCALE * self.REFERENCE_VOLTS

  def close(self):
    if not self.created_bus: return
    self.bus.close()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.close()
