from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'hexapod'

setup(
  name=package_name,
  version='0.0.0',
  packages=find_packages(exclude=['test']),
  data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
  ],
  install_requires=['setuptools'],
  zip_safe=True,
  maintainer='marcocassar',
  maintainer_email='dev@marcocassar.info',
  description='TODO: Package description',
  license='MIT-0',
  extras_require={
    'test': [
      'pytest',
    ],
  },
  entry_points={
    'console_scripts': [
      'servo_controller = hexapod.motion.servo_controller:main',
      'servo_publisher = hexapod.motion.servo_publisher:main',
      'battery_monitor = hexapod.sensors.battery_monitor:main',
      'imu_sensor = hexapod.sensors.imu_sensor:main',
      'ultrasonic_sensor = hexapod.sensors.ultrasonic_sensor:main',
      'fake_camera = hexapod.tests.fake_camera:main',
    ],
  },
)
