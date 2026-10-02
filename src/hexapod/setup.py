from setuptools import find_packages, setup

from glob import glob
import os

package_name = 'hexapod'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share/',package_name, 'launch'), glob('launch/*.launch.py')),
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
            'servo_controller = hexapod.servo_controller:main',
            'servo_publisher = hexapod.servo_publisher:main',
        ],
    },
)
