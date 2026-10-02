import os

from launch.actions import DeclareLaunchArgument
from launch.substitutions import FileContent, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from launch import LaunchDescription


def generate_launch_description():
    # copied from dummy robot launch file | eventually I want a urdf
    # pkg_share = FindPackageShare('hexapod').find('hexapod')
    # urdf_file = os.path.join(pkg_share, 'launch', 'single_rrbot.urdf')
    # robot_desc = FileContent(urdf_file)
    # rsp_params = {'robot_description': robot_desc}

    return LaunchDescription([
        DeclareLaunchArgument('dry_run', default_value='false'),
        Node(package='hexapod', executable='servo_controller', output='screen', parameters=[{'dry_run': LaunchConfiguration('dry_run')}]),
        Node(package='hexapod', executable='servo_publisher', output='screen'),
    ])
