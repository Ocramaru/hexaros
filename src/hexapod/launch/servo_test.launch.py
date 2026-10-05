import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  # copied from dummy robot launch file | eventually I want a urdf
  # pkg_share = FindPackageShare('hexapod').find('hexapod')
  # urdf_file = os.path.join(pkg_share, 'launch', 'single_rrbot.urdf')
  # robot_desc = FileContent(urdf_file)
  # rsp_params = {'robot_description': robot_desc}

  config_dir = os.path.join(get_package_share_directory('hexapod'), 'config')
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
    Node(package='camera_ros', executable='camera_node', name='camera', output='screen', parameters=parameters[:1],
         condition=UnlessCondition(LaunchConfiguration('dry_run'))),
    Node(package='hexapod', executable='fake_camera', name='camera', output='screen', parameters=parameters[:1],
         condition=IfCondition(LaunchConfiguration('dry_run'))),  # noise on camera_ros's topics, since sparky has no camera
  ])
