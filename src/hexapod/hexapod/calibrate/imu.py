"""Measure the gyro bias with the robot still and offer to save it to config/calibration.yaml.

Keep the robot still, then run on the Pi from the workspace root:
  python3 -m hexapod.calibrate.imu

Author: Marco Cassar (@Ocramaru)
"""
import argparse
from pathlib import Path
import time

import numpy as np
import yaml

from hexapod.drivers.imu import ImuDriver

CONFIG_DIR = Path('src/hexapod/config')  # the source config from the workspace root, not the installed copy colcon rebuilds over
PERIOD = 0.01
MAX_GYRO_SPREAD = np.radians(0.5)  # a standard deviation above this rad/s means the robot moved
HEADER = '# Written by the hexapod.calibrate scripts; loaded after hexapod.yaml, so these values win.\n'


def main():
  parser = argparse.ArgumentParser(description='Measure the gyro bias.')
  parser.add_argument('--samples', type=int, default=500)
  parser.add_argument('--config-dir', type=Path, default=CONFIG_DIR)
  args = parser.parse_args()

  params = yaml.safe_load((args.config_dir / 'hexapod.yaml').read_text())['imu_sensor']['ros__parameters']
  print(f'Sampling for {args.samples * PERIOD:.0f} s; keep the robot still.')
  readings = []
  with ImuDriver(address=params['address']) as imu:
    for _ in range(args.samples):
      readings.append(imu.read())
      time.sleep(PERIOD)
  accel, gyro = (np.array(axis) for axis in zip(*readings))
  if gyro.std(axis=0).max() > MAX_GYRO_SPREAD: parser.error('the gyro saw motion; keep the robot still and run again')

  calibration_file = args.config_dir / 'calibration.yaml'
  calibration = yaml.safe_load(calibration_file.read_text()) if calibration_file.exists() else {}
  imu_params = calibration.setdefault('imu_sensor', {}).setdefault('ros__parameters', {})
  bias = [round(float(value), 5) for value in gyro.mean(axis=0)]
  print(f'gravity {np.linalg.norm(accel.mean(axis=0)):.2f} m/s^2 (expect about 9.81)')
  print(f'gyro bias {imu_params.get("gyro_bias", "unset")} -> {bias} rad/s ({np.degrees(bias).round(2).tolist()} deg/s)')

  if input(f'Save to {calibration_file}? [y/N] ').strip().lower() != 'y': return
  imu_params['gyro_bias'] = bias
  calibration_file.write_text(HEADER + yaml.safe_dump(calibration, default_flow_style=None, sort_keys=False, width=4096))
  print('Saved. If this is the Pi, copy the values into calibration.yaml on sparky and commit there; the Pi cannot push.')


if __name__ == '__main__':
  main()
