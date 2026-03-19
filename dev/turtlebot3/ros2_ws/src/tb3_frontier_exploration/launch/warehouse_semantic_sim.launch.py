"""
Gazebo Classic + TurtleBot3 in warehouse_semantic.world.
Requires: gazebo_ros, turtlebot3_gazebo. Set TURTLEBOT3_MODEL before launch.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    pkg_tb3_fe = get_package_share_directory("tb3_frontier_exploration")
    world = os.path.join(pkg_tb3_fe, "worlds", "warehouse_semantic.world")

    pkg_gazebo_ros = get_package_share_directory("gazebo_ros")
    launch_tb3 = os.path.join(get_package_share_directory("turtlebot3_gazebo"), "launch")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    x_pose = LaunchConfiguration("x_pose", default="-2.5")
    y_pose = LaunchConfiguration("y_pose", default="-3.0")

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": world}.items(),
    )
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzclient.launch.py")
        ),
    )
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_tb3, "robot_state_publisher.launch.py")
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )
    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_tb3, "spawn_turtlebot3.launch.py")
        ),
        launch_arguments={"x_pose": x_pose, "y_pose": y_pose}.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true"),
        DeclareLaunchArgument("x_pose", default_value="-2.5"),
        DeclareLaunchArgument("y_pose", default_value="-3.0"),
        gzserver,
        gzclient,
        rsp,
        spawn,
    ])
