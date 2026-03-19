import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("tb3_frontier_exploration")
    default_goals = os.path.join(pkg_share, "config", "semantic_goals.yaml")

    use_sim_time = LaunchConfiguration("use_sim_time", default="true")
    user_command_topic = LaunchConfiguration("user_command_topic", default="user_command")
    semantic_cmd_result_topic = LaunchConfiguration(
        "semantic_cmd_result_topic", default="semantic_cmd_result"
    )
    navigate_to_pose_action = LaunchConfiguration(
        "navigate_to_pose_action", default="navigate_to_pose"
    )
    semantic_goals_file = LaunchConfiguration(
        "semantic_goals_file", default=default_goals
    )
    frame_id = LaunchConfiguration("frame_id", default="map")

    return LaunchDescription([
        DeclareLaunchArgument("use_sim_time", default_value="true",
                             description="Use simulation time"),
        DeclareLaunchArgument("user_command_topic", default_value="user_command",
                             description="Topic for text commands"),
        DeclareLaunchArgument("semantic_cmd_result_topic",
                             default_value="semantic_cmd_result",
                             description="Topic for result/feedback messages"),
        DeclareLaunchArgument("navigate_to_pose_action",
                             default_value="navigate_to_pose",
                             description="Nav2 action name"),
        DeclareLaunchArgument("semantic_goals_file", default_value=default_goals,
                             description="Path to semantic_goals.yaml"),
        DeclareLaunchArgument("frame_id", default_value="map",
                             description="Frame for goal poses"),

        Node(
            package="tb3_frontier_exploration",
            executable="fake_semantic_navigation_node.py",
            name="fake_semantic_navigation_node",
            parameters=[{
                "use_sim_time": use_sim_time,
                "user_command_topic": user_command_topic,
                "semantic_cmd_result_topic": semantic_cmd_result_topic,
                "navigate_to_pose_action": navigate_to_pose_action,
                "semantic_goals_file": semantic_goals_file,
                "frame_id": frame_id,
            }],
            output="screen",
        ),
    ])
