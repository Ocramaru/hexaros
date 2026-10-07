import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
  share = get_package_share_directory('hexapod')
  config_dir = os.path.join(share, 'config')
  urdf = os.path.join(share, 'urdf', 'hexapod.urdf.xacro')
  parameters = [  # later entries override earlier ones
    os.path.join(config_dir, 'hexapod.yaml'),
    os.path.join(config_dir, 'calibration.yaml'),
    {'dry_run': LaunchConfiguration('dry_run')},
  ]

  return LaunchDescription([
    DeclareLaunchArgument('dry_run', default_value='false'),
    Node(package='hexapod', executable='servo_controller', output='screen', parameters=parameters),
    Node(package='hexapod', executable='servo_publisher', output='screen'),
    Node(package='hexapod', executable='battery_monitor', output='screen', parameters=parameters),
    Node(package='hexapod', executable='imu_sensor', output='screen', parameters=parameters),
    Node(package='imu_filter_madgwick', executable='imu_filter_madgwick_node', output='screen', parameters=parameters[:1]),
    Node(package='gscam', executable='gscam_node', name='camera', output='screen', parameters=parameters[:1],
         condition=UnlessCondition(LaunchConfiguration('dry_run'))),
    Node(package='hexapod', executable='fake_camera', name='camera', output='screen', parameters=parameters[:1],
         condition=IfCondition(LaunchConfiguration('dry_run'))),  # noise on gscam's topics, since sparky has no camera
    Node(package='hexapod', executable='ultrasonic_sensor', output='screen', parameters=parameters),
    Node(package='robot_state_publisher', executable='robot_state_publisher', output='screen',
         parameters=[{'robot_description': ParameterValue(Command(['xacro ', urdf]), value_type=str)}]),
  ])
