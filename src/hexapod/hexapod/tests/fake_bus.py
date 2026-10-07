"""A fake I2C bus with smbus2's interface, for dry runs and driver tests.

It stores register writes and emulates the PCA9685's auto-increment, so dry runs catch a missing MODE1 setup.
With `verbose` it prints every write.

Author: Marco Cassar (@Ocramaru)
"""


class FakeBus:
  def __init__(self, read_byte_value=0, verbose=False):
    self.registers = {}
    self.read_byte_value = read_byte_value  # what a bare read_byte returns, e.g. an ADC reading
    self.verbose = verbose

  def log(self, text):
    if self.verbose: print(text, flush=True)

  def write_byte(self, address, value):
    if not 0 <= value <= 255: raise ValueError('Value must be between 0 and 255')
    self.log(f'write addr:0x{address:02x}, command: 0x{value:02x}')

  def read_byte(self, address):
    return self.read_byte_value

  def write_byte_data(self, address, register, value):
    if not 0 <= value <= 255: raise ValueError('Value must be between 0 and 255')
    self.registers[(address, register)] = value
    self.log(f'write addr:0x{address:02x}, register: 0x{register:02x}, value:{value}')

  def write_i2c_block_data(self, address, register, values):
    if not all(0 <= v <= 255 for v in values): raise ValueError('Value must be between 0 and 255')
    auto_increment = self.registers.get((address, 0x00), 0) & 0x20  # like the chip: without MODE1 AI, every byte hits one register
    for offset, value in enumerate(values):
      self.registers[(address, register + (offset if auto_increment else 0))] = value
    self.log(f'block addr:0x{address:02x}, register: 0x{register:02x}, values:{list(values)}')

  def read_byte_data(self, address, register):
    return self.registers.get((address, register), 0)

  def read_i2c_block_data(self, address, register, length):
    return [self.registers.get((address, register + offset), 0) for offset in range(length)]

  def close(self):
    pass
