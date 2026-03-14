#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <geometry_msgs/msg/point.hpp>

#include <vector>
#include <set>
#include <queue>
#include <mutex>
#include <cstdint>

namespace tb3_frontier_exploration
{

using Cell = std::pair<int, int>;
using Cluster = std::vector<Cell>;

class FrontierDetectionNode : public rclcpp::Node
{
public:
  FrontierDetectionNode()
  : Node("frontier_detection_node")
  {
    declare_parameter<std::string>("map_topic", "/map");
    declare_parameter<std::string>("costmap_topic", "/global_costmap/costmap");
    declare_parameter<std::string>("frontiers_topic", "/frontiers");
    declare_parameter<std::string>("frontiers_markers_topic", "/frontiers_markers");
    declare_parameter<std::string>("frame_id", "map");
    declare_parameter<int>("min_cluster_size", 5);
    declare_parameter<int>("cost_threshold", 128);
    declare_parameter<bool>("use_costmap_filter", true);
    declare_parameter<bool>("publish_raw_markers", true);
    declare_parameter<bool>("publish_rejected_markers", true);
    declare_parameter<bool>("verbose_frontier_logging", false);

    std::string map_topic = get_parameter("map_topic").as_string();
    std::string costmap_topic = get_parameter("costmap_topic").as_string();
    std::string frontiers_topic = get_parameter("frontiers_topic").as_string();
    std::string markers_topic = get_parameter("frontiers_markers_topic").as_string();

    map_sub_ = create_subscription<nav_msgs::msg::OccupancyGrid>(
      map_topic, 10, std::bind(&FrontierDetectionNode::mapCallback, this, std::placeholders::_1));
    costmap_sub_ = create_subscription<nav_msgs::msg::OccupancyGrid>(
      costmap_topic, 10, std::bind(&FrontierDetectionNode::costmapCallback, this, std::placeholders::_1));

    frontiers_pub_ = create_publisher<geometry_msgs::msg::PoseArray>(frontiers_topic, 10);
    markers_pub_ = create_publisher<visualization_msgs::msg::MarkerArray>(markers_topic, 10);

    RCLCPP_INFO(get_logger(), "frontier_detection: map=%s, costmap=%s, frontiers=%s",
      map_topic.c_str(), costmap_topic.c_str(), frontiers_topic.c_str());
  }

private:
  static constexpr int8_t FREE = 0;
  static constexpr int8_t OCCUPIED = 100;

  static bool isFree(int8_t value) { return value == FREE; }
  static bool isUnknown(int8_t value) { return value < 0 || value > OCCUPIED; }

  bool isFrontierCell(const nav_msgs::msg::OccupancyGrid & grid, int mx, int my) const
  {
    const int w = static_cast<int>(grid.info.width);
    const int h = static_cast<int>(grid.info.height);
    if (mx < 0 || mx >= w || my < 0 || my >= h) return false;
    const size_t idx = static_cast<size_t>(my) * grid.info.width + static_cast<size_t>(mx);
    if (!isFree(grid.data[idx])) return false;
    const int dx[] = {-1, -1, -1,  0,  0,  1,  1,  1};
    const int dy[] = {-1,  0,  1, -1,  1, -1,  0,  1};
    for (int i = 0; i < 8; i++) {
      int nx = mx + dx[i], ny = my + dy[i];
      if (nx < 0 || nx >= w || ny < 0 || ny >= h) continue;
      size_t nidx = static_cast<size_t>(ny) * grid.info.width + static_cast<size_t>(nx);
      if (isUnknown(grid.data[nidx])) return true;
    }
    return false;
  }

  void gridToWorld(const nav_msgs::msg::OccupancyGrid & grid, int gx, int gy,
                   double & wx, double & wy) const
  {
    wx = grid.info.origin.position.x + (static_cast<double>(gx) + 0.5) * grid.info.resolution;
    wy = grid.info.origin.position.y + (static_cast<double>(gy) + 0.5) * grid.info.resolution;
  }

  std::vector<Cluster> clusterByAdjacency(
    const std::vector<Cell> & cells,
    int width, int height) const
  {
    std::set<Cell> frontier_set(cells.begin(), cells.end());
    std::set<Cell> visited;
    std::vector<Cluster> clusters;
    const int dx[] = {-1, -1, -1,  0,  0,  1,  1,  1};
    const int dy[] = {-1,  0,  1, -1,  1, -1,  0,  1};

    for (const Cell & seed : cells) {
      if (visited.count(seed)) continue;
      Cluster cluster;
      std::queue<Cell> q;
      q.push(seed);
      visited.insert(seed);
      while (!q.empty()) {
        Cell c = q.front();
        q.pop();
        cluster.push_back(c);
        for (int i = 0; i < 8; i++) {
          Cell n(c.first + dx[i], c.second + dy[i]);
          if (n.first < 0 || n.first >= width || n.second < 0 || n.second >= height) continue;
          if (frontier_set.count(n) && !visited.count(n)) {
            visited.insert(n);
            q.push(n);
          }
        }
      }
      clusters.push_back(std::move(cluster));
    }
    return clusters;
  }

  void clusterCentroid(const nav_msgs::msg::OccupancyGrid & grid,
                       const Cluster & cluster, double & cx, double & cy) const
  {
    cx = 0.0;
    cy = 0.0;
    if (cluster.empty()) return;
    for (const Cell & c : cluster) {
      double wx, wy;
      gridToWorld(grid, c.first, c.second, wx, wy);
      cx += wx;
      cy += wy;
    }
    cx /= static_cast<double>(cluster.size());
    cy /= static_cast<double>(cluster.size());
  }

  int getCostAtWorld(double wx, double wy) const
  {
    int mx = 0, my = 0;
    return getCostAtWorldWithIndices(wx, wy, mx, my);
  }

  int getCostAtWorldWithIndices(double wx, double wy, int & out_mx, int & out_my) const
  {
    std::lock_guard<std::mutex> lock(costmap_mutex_);
    if (!current_costmap_) return -1;
    const auto & cm = *current_costmap_;
    const double ox = cm.info.origin.position.x;
    const double oy = cm.info.origin.position.y;
    const double res = cm.info.resolution;
    const int w = static_cast<int>(cm.info.width);
    const int h = static_cast<int>(cm.info.height);
    int gx = static_cast<int>(std::floor((wx - ox) / res));
    int gy = static_cast<int>(std::floor((wy - oy) / res));
    out_mx = gx;
    out_my = gy;
    if (gx < 0 || gx >= w || gy < 0 || gy >= h) return 255;
    size_t idx = static_cast<size_t>(gy) * cm.info.width + static_cast<size_t>(gx);
    return static_cast<int>(static_cast<unsigned char>(cm.data[idx]));
  }

  void costmapCallback(const nav_msgs::msg::OccupancyGrid::SharedPtr msg)
  {
    if (msg->info.width == 0 || msg->info.height == 0) return;
    std::lock_guard<std::mutex> lock(costmap_mutex_);
    current_costmap_ = msg;
  }

  void mapCallback(const nav_msgs::msg::OccupancyGrid::SharedPtr msg)
  {
    if (msg->info.width == 0 || msg->info.height == 0) {
      RCLCPP_WARN(get_logger(), "Received empty map");
      return;
    }

    const bool verbose = get_parameter("verbose_frontier_logging").as_bool();
#define FRONTIER_LOG(...) do { \
  if (verbose) RCLCPP_INFO(get_logger(), __VA_ARGS__); \
  else RCLCPP_DEBUG(get_logger(), __VA_ARGS__); \
} while (0)

    const int w = static_cast<int>(msg->info.width);
    const int h = static_cast<int>(msg->info.height);
    std::vector<Cell> frontier_cells;
    for (int my = 0; my < h; my++) {
      for (int mx = 0; mx < w; mx++) {
        if (isFrontierCell(*msg, mx, my)) {
          frontier_cells.emplace_back(mx, my);
        }
      }
    }

    FRONTIER_LOG("[frontier] 1. raw frontier cells: %zu", frontier_cells.size());

    int min_size = get_parameter("min_cluster_size").as_int();
    std::vector<Cluster> clusters = clusterByAdjacency(frontier_cells, w, h);

    FRONTIER_LOG("[frontier] 2. total clusters: %zu (min_cluster_size=%d)", clusters.size(), min_size);

    std::vector<std::pair<double, double>> all_centroids;
    for (size_t ci = 0; ci < clusters.size(); ci++) {
      const Cluster & cl = clusters[ci];
      FRONTIER_LOG("[frontier] 3. cluster[%zu] size=%zu", ci, cl.size());
      if (static_cast<int>(cl.size()) < min_size) {
        FRONTIER_LOG("[frontier]    skipped (below min_cluster_size)");
        continue;
      }
      double cx, cy;
      clusterCentroid(*msg, cl, cx, cy);
      all_centroids.emplace_back(cx, cy);
      FRONTIER_LOG("[frontier] 4. cluster[%zu] centroid (representative): (%.3f, %.3f)", ci, cx, cy);
    }

    int cost_threshold = get_parameter("cost_threshold").as_int();
    bool use_filter = get_parameter("use_costmap_filter").as_bool();
    std::vector<std::pair<double, double>> safe_centroids;
    std::vector<std::pair<double, double>> rejected_centroids;
    for (size_t i = 0; i < all_centroids.size(); i++) {
      const auto & c = all_centroids[i];
      int cmx = 0, cmy = 0;
      int cost = getCostAtWorldWithIndices(c.first, c.second, cmx, cmy);
      FRONTIER_LOG("[frontier] 6. candidate[%zu] world=(%.3f, %.3f) costmap_idx=(%d, %d) cost=%d",
        i, c.first, c.second, cmx, cmy, cost);
      if (!use_filter || cost < 0) {
        safe_centroids.push_back(c);
        FRONTIER_LOG("[frontier] 8. candidate[%zu] ACCEPTED (no filter or cost<0)", i);
        continue;
      }
      if (cost <= cost_threshold) {
        safe_centroids.push_back(c);
        FRONTIER_LOG("[frontier] 8. candidate[%zu] ACCEPTED (cost %d <= threshold %d)", i, cost, cost_threshold);
      } else {
        rejected_centroids.push_back(c);
        FRONTIER_LOG("[frontier] 8. candidate[%zu] REJECTED (cost %d > threshold %d)", i, cost, cost_threshold);
      }
    }

    FRONTIER_LOG("[frontier] 9. final safe published frontiers: %zu", safe_centroids.size());
#undef FRONTIER_LOG

    std::string frame_id = get_parameter("frame_id").as_string();
    if (frame_id.empty()) frame_id = msg->header.frame_id;

    RCLCPP_INFO(get_logger(),
      "[frontier] raw=%zu clusters=%zu centroids=%zu safe=%zu rejected=%zu",
      frontier_cells.size(), clusters.size(), all_centroids.size(), safe_centroids.size(), rejected_centroids.size());

    geometry_msgs::msg::PoseArray pose_array;
    pose_array.header.stamp = msg->header.stamp;
    pose_array.header.frame_id = frame_id;
    pose_array.poses.resize(safe_centroids.size());
    for (size_t i = 0; i < safe_centroids.size(); i++) {
      pose_array.poses[i].position.x = safe_centroids[i].first;
      pose_array.poses[i].position.y = safe_centroids[i].second;
      pose_array.poses[i].position.z = 0.0;
      pose_array.poses[i].orientation.w = 1.0;
      pose_array.poses[i].orientation.x = 0.0;
      pose_array.poses[i].orientation.y = 0.0;
      pose_array.poses[i].orientation.z = 0.0;
    }
    frontiers_pub_->publish(pose_array);

    visualization_msgs::msg::MarkerArray ma;
    visualization_msgs::msg::Marker centroid_marker;
    centroid_marker.header.stamp = msg->header.stamp;
    centroid_marker.header.frame_id = frame_id;
    centroid_marker.ns = "frontier_centroids_safe";
    centroid_marker.id = 0;
    centroid_marker.type = visualization_msgs::msg::Marker::SPHERE_LIST;
    centroid_marker.action = visualization_msgs::msg::Marker::ADD;
    double scale = msg->info.resolution * 2.0;
    centroid_marker.scale.x = scale;
    centroid_marker.scale.y = scale;
    centroid_marker.scale.z = scale;
    centroid_marker.color.r = 0.0f;
    centroid_marker.color.g = 1.0f;
    centroid_marker.color.b = 0.0f;
    centroid_marker.color.a = 0.9f;
    centroid_marker.points.resize(safe_centroids.size());
    for (size_t i = 0; i < safe_centroids.size(); i++) {
      centroid_marker.points[i].x = safe_centroids[i].first;
      centroid_marker.points[i].y = safe_centroids[i].second;
      centroid_marker.points[i].z = 0.0;
    }
    ma.markers.push_back(centroid_marker);

    if (get_parameter("publish_rejected_markers").as_bool() && !rejected_centroids.empty()) {
      visualization_msgs::msg::Marker rej_marker;
      rej_marker.header.stamp = msg->header.stamp;
      rej_marker.header.frame_id = frame_id;
      rej_marker.ns = "frontier_centroids_rejected";
      rej_marker.id = 1;
      rej_marker.type = visualization_msgs::msg::Marker::SPHERE_LIST;
      rej_marker.action = visualization_msgs::msg::Marker::ADD;
      rej_marker.scale.x = scale;
      rej_marker.scale.y = scale;
      rej_marker.scale.z = scale;
      rej_marker.color.r = 1.0f;
      rej_marker.color.g = 0.0f;
      rej_marker.color.b = 0.0f;
      rej_marker.color.a = 0.8f;
      rej_marker.points.resize(rejected_centroids.size());
      for (size_t i = 0; i < rejected_centroids.size(); i++) {
        rej_marker.points[i].x = rejected_centroids[i].first;
        rej_marker.points[i].y = rejected_centroids[i].second;
        rej_marker.points[i].z = 0.0;
      }
      ma.markers.push_back(rej_marker);
    }

    if (get_parameter("publish_raw_markers").as_bool()) {
      visualization_msgs::msg::Marker raw_marker;
      raw_marker.header.stamp = msg->header.stamp;
      raw_marker.header.frame_id = frame_id;
      raw_marker.ns = "frontier_cells";
      raw_marker.id = 2;
      raw_marker.type = visualization_msgs::msg::Marker::SPHERE_LIST;
      raw_marker.action = visualization_msgs::msg::Marker::ADD;
      double raw_scale = msg->info.resolution * 1.2;
      raw_marker.scale.x = raw_scale;
      raw_marker.scale.y = raw_scale;
      raw_marker.scale.z = raw_scale;
      raw_marker.color.r = 1.0f;
      raw_marker.color.g = 0.5f;
      raw_marker.color.b = 0.0f;
      raw_marker.color.a = 0.4f;
      raw_marker.points.resize(frontier_cells.size());
      for (size_t i = 0; i < frontier_cells.size(); i++) {
        double wx, wy;
        gridToWorld(*msg, frontier_cells[i].first, frontier_cells[i].second, wx, wy);
        raw_marker.points[i].x = wx;
        raw_marker.points[i].y = wy;
        raw_marker.points[i].z = 0.0;
      }
      ma.markers.push_back(raw_marker);
    }
    markers_pub_->publish(ma);
  }

  rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr map_sub_;
  rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr costmap_sub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseArray>::SharedPtr frontiers_pub_;
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr markers_pub_;

  nav_msgs::msg::OccupancyGrid::SharedPtr current_costmap_;
  mutable std::mutex costmap_mutex_;
};

}  // namespace tb3_frontier_exploration

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<tb3_frontier_exploration::FrontierDetectionNode>());
  rclcpp::shutdown();
  return 0;
}
