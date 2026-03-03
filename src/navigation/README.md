# Navigation Module

This module contains navigation algorithms for the quadruped robot.

## Structure

- `astar/`: A* path planning implementation
- `local_planner/`: Local path planning and obstacle avoidance

## Input/Output Conventions

### Path Planning
- **Input**: Start pose, goal pose, occupancy map
- **Output**: Path as list of waypoints

### Local Planner
- **Input**: Current pose, target waypoint, sensor data
- **Output**: Velocity commands (linear, angular)

## Usage

See individual subdirectory READMEs for detailed usage.
