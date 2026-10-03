import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  # copied from dummy robot launch file | eventually I want a urdf
  # pkg_share = FindPackageShare('hexapod').find('hexapod')
  # urdf_file = os.path.join(pkg_share, 'launch', 'single_rrbot.urdf')
  # robot_desc = FileContent(urdf_file)
  # rsp_params = {'robot_description': robot_desc}

  config = os.path.join(get_package_share_directory('hexapod'), 'config', 'hexapod.yaml')
  return LaunchDescription([
    DeclareLaunchArgument('dry_run', default_value='false'),
    Node(package='hexapod', executable='servo_controller', output='screen', parameters=[config, {'dry_run': LaunchConfiguration('dry_run')}]),
    Node(package='hexapod', executable='servo_publisher', output='screen'),
  ])
