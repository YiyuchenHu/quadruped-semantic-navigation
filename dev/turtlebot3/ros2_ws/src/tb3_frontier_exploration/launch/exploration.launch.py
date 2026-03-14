import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("tb3_frontier_exploration")
    config = os.path.join(pkg_share, "config", "params.yaml")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true", description="Use simulation time"),
        Node(
            package="tb3_frontier_exploration",
            executable="frontier_detection_node",
            name="frontier_detection_node",
            parameters=[config, {"use_sim_time": use_sim_time}],
            output="screen",
        ),
        Node(
            package="tb3_frontier_exploration",
            executable="goal_assignment_node",
            name="goal_assignment_node",
            parameters=[config, {"use_sim_time": use_sim_time}],
            output="screen",
        ),
    ])
