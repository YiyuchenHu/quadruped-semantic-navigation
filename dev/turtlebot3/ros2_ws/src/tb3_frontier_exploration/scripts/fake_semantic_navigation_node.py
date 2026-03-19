#!/usr/bin/env python3
"""
Minimal ROS2 node for fake semantic navigation.
Subscribes to a text command (e.g. "go to table"), parses the object label,
looks up the predefined pose from YAML, and sends a NavigateToPose goal to Nav2.
Optional map gating: only allow navigation to a goal if that map cell is explored (known).
No YOLO, no LLM.
"""

import os
import sys
import math
import yaml

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from nav2_msgs.action import NavigateToPose
from visualization_msgs.msg import Marker, MarkerArray


# Allow importing command_parser and map_gating when run via ros2 run (same install dir).
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
import command_parser  # noqa: E402
import map_gating  # noqa: E402


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    """Convert yaw (radians) to quaternion (x, y, z, w). Rotation around z."""
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


class FakeSemanticNavigationNode(Node):
    def __init__(self):
        super().__init__("fake_semantic_navigation_node")

        self.declare_parameter("user_command_topic", "user_command")
        self.declare_parameter("semantic_cmd_result_topic", "semantic_cmd_result")
        self.declare_parameter("semantic_goal_pose_topic", "semantic_goal_pose")
        self.declare_parameter("navigate_to_pose_action", "navigate_to_pose")
        self.declare_parameter("semantic_goals_file", "")  # default: from package share
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("map_topic", "map")
        self.declare_parameter("use_map_gating", True)

        self._goals, self._allowed_objects, self._frame_id = self._load_semantic_goals()

        if not self._goals:
            self.get_logger().error("No semantic goals loaded. Check semantic_goals_file.")
            return

        nav_action = self.get_parameter("navigate_to_pose_action").get_parameter_value().string_value
        cmd_topic = self.get_parameter("user_command_topic").get_parameter_value().string_value
        result_topic = self.get_parameter("semantic_cmd_result_topic").get_parameter_value().string_value
        goal_pose_topic = self.get_parameter("semantic_goal_pose_topic").get_parameter_value().string_value
        map_topic = self.get_parameter("map_topic").get_parameter_value().string_value
        self._use_map_gating = self.get_parameter("use_map_gating").get_parameter_value().bool_value

        self._latest_map = None  # OccupancyGrid or None
        self._object_order = sorted(self._goals.keys())  # stable order for marker ids

        self._action_client = ActionClient(self, NavigateToPose, nav_action)
        self._sub = self.create_subscription(
            String, cmd_topic, self._command_callback, 10
        )
        self._result_pub = self.create_publisher(String, result_topic, 10)
        self._goal_pose_pub = self.create_publisher(PoseStamped, goal_pose_topic, 10)
        self._marker_pub = self.create_publisher(MarkerArray, "semantic_object_markers", 10)
        if self._use_map_gating:
            self._map_sub = self.create_subscription(
                OccupancyGrid, map_topic, self._map_callback, 10
            )

        self.get_logger().info(
            "fake_semantic_navigation_node started. Supported objects: %s. Map gating: %s."
            % (", ".join(sorted(self._allowed_objects)), self._use_map_gating)
        )

    def _map_callback(self, msg: OccupancyGrid) -> None:
        """Store latest map for gating (last message wins); update semantic object markers."""
        self._latest_map = msg
        self._publish_semantic_markers()

    def _publish_semantic_markers(self) -> None:
        """Publish TEXT_VIEW_FACING + SPHERE markers for each object that is known in the current map."""
        if self._latest_map is None:
            return
        stamp = self.get_clock().now().to_msg()
        n = len(self._object_order)
        arr = MarkerArray()
        for marker_id, label in enumerate(self._object_order):
            pose_data = self._goals[label]
            x = float(pose_data.get("x", 0))
            y = float(pose_data.get("y", 0))
            known = map_gating.is_goal_known_in_map(self._latest_map, x, y)
            if not known:
                for mid in (marker_id, marker_id + n):
                    m = Marker()
                    m.header.frame_id = self._frame_id
                    m.header.stamp = stamp
                    m.ns = "semantic_objects"
                    m.id = mid
                    m.action = Marker.DELETE
                    arr.markers.append(m)
                continue
            # TEXT_VIEW_FACING: red text, z=0.5, scale.z=0.3
            mt = Marker()
            mt.header.frame_id = self._frame_id
            mt.header.stamp = stamp
            mt.ns = "semantic_objects"
            mt.id = marker_id
            mt.type = Marker.TEXT_VIEW_FACING
            mt.action = Marker.ADD
            mt.pose.position.x = x
            mt.pose.position.y = y
            mt.pose.position.z = 0.5
            mt.pose.orientation.w = 1.0
            mt.scale.z = 0.3
            mt.color.r = 1.0
            mt.color.g = 0.0
            mt.color.b = 0.0
            mt.color.a = 1.0
            mt.text = label
            arr.markers.append(mt)
            # SPHERE: blue, z=0.1, scale=0.15
            ms = Marker()
            ms.header.frame_id = self._frame_id
            ms.header.stamp = stamp
            ms.ns = "semantic_objects"
            ms.id = marker_id + n
            ms.type = Marker.SPHERE
            ms.action = Marker.ADD
            ms.pose.position.x = x
            ms.pose.position.y = y
            ms.pose.position.z = 0.1
            ms.pose.orientation.w = 1.0
            ms.scale.x = 0.15
            ms.scale.y = 0.15
            ms.scale.z = 0.15
            ms.color.r = 0.0
            ms.color.g = 0.0
            ms.color.b = 1.0
            ms.color.a = 1.0
            arr.markers.append(ms)
        if arr.markers:
            self._marker_pub.publish(arr)

    def _load_semantic_goals(self) -> tuple[dict, set, str]:
        """Load semantic_goals.yaml. Returns (goals dict, allowed_objects set, frame_id)."""
        path_param = self.get_parameter("semantic_goals_file").get_parameter_value().string_value
        path = path_param
        if not path or not os.path.isfile(path):
            try:
                from ament_index_python.packages import get_package_share_directory
                pkg_share = get_package_share_directory("tb3_frontier_exploration")
                path = os.path.join(pkg_share, "config", "semantic_goals.yaml")
            except Exception as e:
                self.get_logger().error("Package share not found: %s" % e)
                return {}, set(), "map"
        if not os.path.isfile(path):
            self.get_logger().error("Semantic goals file not found: %s" % path)
            return {}, set(), "map"
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.get_logger().error("Failed to load YAML %s: %s" % (path, e))
            return {}, set(), "map"
        raw_goals = data.get("semantic_goals") or {}
        goals = {str(k).lower(): raw_goals[k] for k in raw_goals}
        frame_id = data.get("frame_id", "map") or "map"
        return goals, set(goals.keys()), frame_id

    def _command_callback(self, msg: String) -> None:
        """Parse command, look up pose, send Nav2 goal or publish error."""
        raw = (msg.data or "").strip()
        self.get_logger().info("Command received: '%s'" % raw)

        success, object_label, error_message = command_parser.parse_command(
            raw, allowed_objects=self._allowed_objects
        )
        if not success:
            self.get_logger().warn("Command rejected: %s" % (error_message or "unknown"))
            self._publish_result(error_message or "Error")
            return
        self.get_logger().info("Object parsed: '%s'" % object_label)

        if object_label not in self._goals:
            err = "Unknown object '%s'." % object_label
            self.get_logger().warn(err)
            self._publish_result(err)
            return
        pose_data = self._goals[object_label]
        x = float(pose_data.get("x", 0))
        y = float(pose_data.get("y", 0))
        yaw = float(pose_data.get("yaw", 0))
        self.get_logger().info("Goal pose chosen: (x=%.2f, y=%.2f, yaw=%.2f)" % (x, y, yaw))

        if self._use_map_gating:
            if self._latest_map is None:
                self.get_logger().warn("Map gating: no map received yet.")
                self._publish_result("No map received yet.")
                return
            if not map_gating.is_goal_known_in_map(self._latest_map, x, y):
                self.get_logger().warn("Map gating: '%s' goal not in explored map yet." % object_label)
                self._publish_result("Object '%s' not in explored map yet." % object_label)
                return
            self.get_logger().info("Map gating: '%s' goal cell is known." % object_label)

        qx, qy, qz, qw = yaw_to_quaternion(yaw)

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.header.frame_id = self._frame_id
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = qx
        goal_msg.pose.pose.orientation.y = qy
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        if not self._action_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error("Nav2 action server not available.")
            self._publish_result("Nav2 not available.")
            return

        self.get_logger().info("Goal sent: %s -> (%.2f, %.2f)" % (object_label, x, y))
        self._goal_pose_pub.publish(goal_msg.pose)
        self._publish_result("Navigating to %s." % object_label)
        goal_future = self._action_client.send_goal_async(goal_msg)
        goal_future.add_done_callback(self._result_callback)

    def _result_callback(self, future) -> None:
        """Goal response callback: accepted or rejected by Nav2."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn("Goal rejected by Nav2.")
            self._publish_result("Goal rejected by Nav2.")
            return
        self.get_logger().info("Goal accepted by Nav2.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._nav2_result_done)

    def _nav2_result_done(self, future) -> None:
        """Navigation finished: log and publish success or failure."""
        response = future.result()
        status = getattr(response, "status", None)
        if hasattr(status, "status"):
            status = status.status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Navigation finished: succeeded.")
            self._publish_result("Navigation finished.")
        else:
            self.get_logger().warn("Navigation finished: failed (status=%s)." % status)
            self._publish_result("Navigation failed (status=%s)." % status)

    def _publish_result(self, text: str) -> None:
        msg = String()
        msg.data = text
        self._result_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FakeSemanticNavigationNode()
    if not node._goals:
        rclpy.shutdown()
        return 1
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
