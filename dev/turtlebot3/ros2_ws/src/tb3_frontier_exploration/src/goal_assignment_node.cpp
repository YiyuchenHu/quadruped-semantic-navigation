#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2/time.hpp>

#include <mutex>
#include <atomic>
#include <cmath>
#include <optional>

namespace tb3_frontier_exploration
{

enum class State { IDLE, NAVIGATING };

class GoalAssignmentNode : public rclcpp::Node
{
public:
  using NavigateToPose = nav2_msgs::action::NavigateToPose;
  using GoalHandle = rclcpp_action::ClientGoalHandle<NavigateToPose>;

  GoalAssignmentNode()
  : Node("goal_assignment_node"),
    state_(State::IDLE)
  {
    declare_parameter<std::string>("frontiers_topic", "/frontiers");
    declare_parameter<std::string>("odom_topic", "/odometry/filtered");
    declare_parameter<std::string>("navigate_to_pose_action", "navigate_to_pose");
    declare_parameter<std::string>("frame_id", "map");
    declare_parameter<std::string>("robot_base_frame", "base_link");
    declare_parameter<double>("goal_timeout", 60.0);
    declare_parameter<double>("rate", 1.0);
    declare_parameter<double>("min_frontier_distance", 0.5);
    declare_parameter<double>("failed_goal_avoidance_radius", 1.0);
    declare_parameter<double>("exploration_complete_log_interval", 5.0);

    std::string frontiers_topic = get_parameter("frontiers_topic").as_string();
    std::string odom_topic = get_parameter("odom_topic").as_string();
    std::string action_name = get_parameter("navigate_to_pose_action").as_string();

    tf_buffer_ = std::make_shared<tf2_ros::Buffer>(get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    frontiers_sub_ = create_subscription<geometry_msgs::msg::PoseArray>(
      frontiers_topic, 10, std::bind(&GoalAssignmentNode::frontiersCallback, this, std::placeholders::_1));
    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      odom_topic, 10, std::bind(&GoalAssignmentNode::odomCallback, this, std::placeholders::_1));

    nav_client_ = rclcpp_action::create_client<NavigateToPose>(this, action_name);

    double rate_hz = get_parameter("rate").as_double();
    timer_ = create_wall_timer(
      std::chrono::duration<double>(1.0 / rate_hz),
      std::bind(&GoalAssignmentNode::timerCallback, this));

    RCLCPP_INFO(get_logger(),
      "[goal_assignment] Started: frontiers=%s, action=%s, min_frontier_dist=%.2f, failed_avoid_radius=%.2f, goal_timeout=%.1fs",
      frontiers_topic.c_str(), action_name.c_str(),
      get_parameter("min_frontier_distance").as_double(),
      get_parameter("failed_goal_avoidance_radius").as_double(),
      get_parameter("goal_timeout").as_double());
  }

private:
  void frontiersCallback(const geometry_msgs::msg::PoseArray::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lock(frontiers_mutex_);
    latest_frontiers_ = msg;
    RCLCPP_DEBUG(get_logger(), "[frontiers] Received %zu centroids", msg->poses.size());
  }

  void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
  {
    (void)msg;
  }

  bool getRobotPoseInMap(double & rx, double & ry)
  {
    std::string frame_id = get_parameter("frame_id").as_string();
    std::string robot_frame = get_parameter("robot_base_frame").as_string();
    try {
      geometry_msgs::msg::TransformStamped t = tf_buffer_->lookupTransform(
        frame_id, robot_frame, tf2::TimePointZero, tf2::durationFromSec(0.5));
      rx = t.transform.translation.x;
      ry = t.transform.translation.y;
      return true;
    } catch (const std::exception & e) {
      RCLCPP_DEBUG(get_logger(), "[TF] Lookup failed: %s", e.what());
      return false;
    }
  }

  // Returns index of best valid frontier, or nullopt if none valid.
  std::optional<size_t> selectBestFrontier(
    const geometry_msgs::msg::PoseArray & frontiers,
    double rx, double ry,
    std::string & frame_id)
  {
    const double min_dist = get_parameter("min_frontier_distance").as_double();
    const double min_dist_sq = min_dist * min_dist;
    const double avoid_radius = get_parameter("failed_goal_avoidance_radius").as_double();
    const double avoid_radius_sq = avoid_radius * avoid_radius;

    size_t best = 0;
    double best_dist_sq = 1e30;
    bool found = false;

    for (size_t i = 0; i < frontiers.poses.size(); i++) {
      double gx = frontiers.poses[i].position.x;
      double gy = frontiers.poses[i].position.y;
      double dx = gx - rx;
      double dy = gy - ry;
      double d2 = dx * dx + dy * dy;

      if (d2 < min_dist_sq) {
        RCLCPP_DEBUG(get_logger(), "[select] Frontier [%zu] (%.2f, %.2f) skipped: too close (%.2f m)",
          i, gx, gy, std::sqrt(d2));
        continue;
      }
      if (last_failed_goal_) {
        double fdx = gx - last_failed_goal_->x;
        double fdy = gy - last_failed_goal_->y;
        if (fdx * fdx + fdy * fdy < avoid_radius_sq) {
          RCLCPP_DEBUG(get_logger(), "[select] Frontier [%zu] (%.2f, %.2f) skipped: near last failed goal",
            i, gx, gy);
          continue;
        }
      }

      if (d2 < best_dist_sq) {
        best_dist_sq = d2;
        best = i;
        found = true;
      }
    }

    if (!found) return std::nullopt;
    if (frame_id.empty()) frame_id = frontiers.header.frame_id;
    return best;
  }

  void timerCallback()
  {
    const double goal_timeout = get_parameter("goal_timeout").as_double();

    if (state_ == State::NAVIGATING) {
      if (current_goal_handle_ && goal_sent_time_) {
        double elapsed = (now() - *goal_sent_time_).seconds();
        if (elapsed >= goal_timeout) {
          RCLCPP_WARN(get_logger(), "[timeout] Goal stalled for %.1fs (limit %.1fs), canceling",
            elapsed, goal_timeout);
          auto handle = current_goal_handle_;
          current_goal_handle_.reset();
          goal_sent_time_.reset();
          recordFailedGoal(current_goal_x_, current_goal_y_);
          state_ = State::IDLE;
          if (handle) {
            nav_client_->async_cancel_goal(handle);
          }
        }
      }
      return;
    }

    if (!nav_client_->action_server_is_ready()) {
      RCLCPP_DEBUG(get_logger(), "[idle] Action server not ready");
      return;
    }

    geometry_msgs::msg::PoseArray::SharedPtr frontiers;
    {
      std::lock_guard<std::mutex> lock(frontiers_mutex_);
      frontiers = latest_frontiers_;
    }

    if (!frontiers || frontiers->poses.empty()) {
      logExplorationCompleteIfDue();
      return;
    }

    double rx, ry;
    if (!getRobotPoseInMap(rx, ry)) return;

    std::string frame_id = get_parameter("frame_id").as_string();
    std::optional<size_t> best_opt = selectBestFrontier(*frontiers, rx, ry, frame_id);

    if (!best_opt) {
      RCLCPP_DEBUG(get_logger(), "[select] No valid frontier after filters (min_dist=%.2f, avoid_radius=%.2f)",
        get_parameter("min_frontier_distance").as_double(),
        get_parameter("failed_goal_avoidance_radius").as_double());
      logExplorationCompleteIfDue();
      return;
    }

    size_t best = *best_opt;
    double gx = frontiers->poses[best].position.x;
    double gy = frontiers->poses[best].position.y;
    double dist = std::sqrt(
      (gx - rx) * (gx - rx) + (gy - ry) * (gy - ry));

    RCLCPP_INFO(get_logger(), "[goal] Selected [%zu] (%.2f, %.2f) dist=%.2f m",
      best, gx, gy, dist);

    {
      std::lock_guard<std::mutex> lock(frontiers_mutex_);
      if (latest_frontiers_ && best < latest_frontiers_->poses.size()) {
        latest_frontiers_->poses.erase(latest_frontiers_->poses.begin() + best);
      }
    }

    NavigateToPose::Goal goal;
    goal.pose.header.stamp = now();
    goal.pose.header.frame_id = frame_id;
    goal.pose.pose.position.x = gx;
    goal.pose.pose.position.y = gy;
    goal.pose.pose.position.z = 0.0;
    goal.pose.pose.orientation.w = 1.0;
    goal.pose.pose.orientation.x = 0.0;
    goal.pose.pose.orientation.y = 0.0;
    goal.pose.pose.orientation.z = 0.0;

    current_goal_x_ = gx;
    current_goal_y_ = gy;

    auto send_opts = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
    send_opts.goal_response_callback = [this](typename GoalHandle::SharedPtr gh) {
      if (gh) {
        RCLCPP_INFO(get_logger(), "[action] Goal accepted");
        current_goal_handle_ = gh;
        goal_sent_time_ = now();
        state_ = State::NAVIGATING;
      } else {
        RCLCPP_WARN(get_logger(), "[action] Goal rejected");
        recordFailedGoal(current_goal_x_, current_goal_y_);
        state_ = State::IDLE;
      }
    };
    send_opts.result_callback = [this](const GoalHandle::WrappedResult & result) {
      current_goal_handle_.reset();
      goal_sent_time_.reset();
      state_ = State::IDLE;

      switch (result.code) {
        case rclcpp_action::ResultCode::SUCCEEDED:
          RCLCPP_INFO(get_logger(), "[result] SUCCEEDED");
          last_failed_goal_.reset();
          break;
        case rclcpp_action::ResultCode::ABORTED:
          RCLCPP_WARN(get_logger(), "[result] ABORTED");
          recordFailedGoal(current_goal_x_, current_goal_y_);
          break;
        case rclcpp_action::ResultCode::CANCELED:
          RCLCPP_WARN(get_logger(), "[result] CANCELED");
          recordFailedGoal(current_goal_x_, current_goal_y_);
          break;
        default:
          RCLCPP_WARN(get_logger(), "[result] Unknown code");
          recordFailedGoal(current_goal_x_, current_goal_y_);
      }
    };

    state_ = State::NAVIGATING;
    nav_client_->async_send_goal(goal, send_opts);
  }

  void recordFailedGoal(double gx, double gy)
  {
    last_failed_goal_ = {gx, gy};
    RCLCPP_DEBUG(get_logger(), "[failed] Recorded (%.2f, %.2f) for avoidance", gx, gy);
  }

  void logExplorationCompleteIfDue()
  {
    double interval = get_parameter("exploration_complete_log_interval").as_double();
    auto now_t = now();
    if (!last_exploration_complete_log_time_ ||
        (now_t - *last_exploration_complete_log_time_).seconds() >= interval) {
      RCLCPP_INFO(get_logger(), "[exploration] No valid frontiers — exploration complete (will retry when new frontiers appear)");
      last_exploration_complete_log_time_ = now_t;
    }
  }

  rclcpp::Subscription<geometry_msgs::msg::PoseArray>::SharedPtr frontiers_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp_action::Client<NavigateToPose>::SharedPtr nav_client_;
  rclcpp::TimerBase::SharedPtr timer_;

  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

  geometry_msgs::msg::PoseArray::SharedPtr latest_frontiers_;
  std::mutex frontiers_mutex_;

  State state_;
  typename GoalHandle::SharedPtr current_goal_handle_;
  std::optional<rclcpp::Time> goal_sent_time_;
  double current_goal_x_{0.0};
  double current_goal_y_{0.0};

  struct Point { double x, y; };
  std::optional<Point> last_failed_goal_;
  std::optional<rclcpp::Time> last_exploration_complete_log_time_;
};

}  // namespace tb3_frontier_exploration

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<tb3_frontier_exploration::GoalAssignmentNode>());
  rclcpp::shutdown();
  return 0;
}
