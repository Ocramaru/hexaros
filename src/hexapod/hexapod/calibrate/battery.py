"""Calibrate the battery voltage dividers from multimeter readings and offer to save them to config/calibration.yaml.

Measure each pack at rest, then run on the Pi with one reading per pack, in `channels` order:
  python3 -m hexapod.calibrate.battery 8.14 8.10

Author: Marco Cassar (@Ocramaru)
"""
import argparse
from pathlib import Path
import statistics

import yaml

from hexapod.drivers.adc import AdcDriver

CONFIG_DIR = Path(__file__).resolve().parents[2] / 'config'
SAMPLES = 20
MIN_PIN_VOLTS = 0.1  # below this the pack is switched off or disconnected
HEADER = '# Written by the hexapod.calibrate scripts; loaded after hexapod.yaml, so these values win.\n'


def main():
  parser = argparse.ArgumentParser(description='Calibrate the battery voltage dividers.')
  parser.add_argument('volts', type=float, nargs='+', help='multimeter reading per pack, in channels order')
  parser.add_argument('--config-dir', type=Path, default=CONFIG_DIR)
  args = parser.parse_args()

  params = yaml.safe_load((args.config_dir / 'hexapod.yaml').read_text())['battery_monitor']['ros__parameters']
  channels, names = params['channels'], params['names']
  if len(args.volts) != len(channels): parser.error(f'expected {len(channels)} readings, one per pack: {names}')

  with AdcDriver(address=params['adc_address']) as adc:
    pins = [statistics.mean(adc.read_pin_volts(channel) for _ in range(SAMPLES)) for channel in channels]
  for name, pin in zip(names, pins):
    if pin < MIN_PIN_VOLTS: parser.error(f'{name} reads {pin:.3f} V at the ADC; is its switch on?')

  calibration_file = args.config_dir / 'calibration.yaml'
  calibration = yaml.safe_load(calibration_file.read_text()) if calibration_file.exists() else {}
  battery = calibration.setdefault('battery_monitor', {}).setdefault('ros__parameters', {})
  old = battery.get('dividers', ['unset'] * len(channels))
  dividers = [round(meter / pin, 3) for meter, pin in zip(args.volts, pins)]
  for name, meter, pin, before, after in zip(names, args.volts, pins, old, dividers):
    print(f'{name}: meter {meter:.2f} V, ADC pin {pin:.3f} V, divider {before} -> {after}')

  if input(f'Save to {calibration_file}? [y/N] ').strip().lower() != 'y': return
  battery['dividers'] = dividers
  calibration_file.write_text(HEADER + yaml.safe_dump(calibration, default_flow_style=None, sort_keys=False, width=4096))
  print('Saved. If this is the Pi, copy the values into calibration.yaml on sparky and commit there; the Pi cannot push.')


if __name__ == '__main__':
  main()
