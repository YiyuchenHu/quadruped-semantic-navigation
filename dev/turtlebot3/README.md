# TurtleBot3 Integration

This directory contains code and scripts for TurtleBot3 robot platform integration.

## Purpose

Code in this directory is used for:
- TurtleBot3-specific implementations
- ROS 2 integration scripts
- Navigation and control algorithms adapted for TurtleBot3
- Testing and validation on TurtleBot3 hardware

## Structure

- `ros2_ws/` — ROS 2 workspace (build and run from here for Phase 2).
- `docs/` — Phase 1 baseline and planning docs.

## Dependencies

- ROS 2 Humble
- TurtleBot3 packages (Gazebo, Navigation2)
- See main project `requirements.txt` for Python dependencies

---

## Phase 2: SLAM + Frontier Exploration (Simulation)

This phase verifies **autonomous exploration in simulation** using:
- **TurtleBot3 Gazebo** — robot and world
- **Nav2 with SLAM enabled** — mapping and navigation
- **tb3_frontier_exploration** — frontier detection and goal assignment

### Completed

- Gazebo simulation with TurtleBot3 (waffle_pi)
- Nav2 running in SLAM mode
- Frontier exploration pipeline (frontier_detection_node + goal_assignment_node)
- Tested in multiple Gazebo worlds

### Tested Gazebo Worlds

The system was tested in:

- `turtlebot3_world.launch.py`
- `turtlebot3_dqn_stage2.launch.py`
- `turtlebot3_house.launch.py`

**Launch only one world at a time** in Terminal 1.

### Reproduction Steps

Use three terminals. All commands that need the workspace run from `ros2_ws`; run `./build_tb3_frontier.sh` once if you have not built the workspace (see [build note](#build-note) below).

---

**Terminal 1 — Gazebo world**

Starts the simulation; choose one of the three worlds.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi

# Pick one:
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
# ros2 launch turtlebot3_gazebo turtlebot3_dqn_stage2.launch.py
# ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

---

**Terminal 2 — Nav2 + SLAM**

Provides mapping and navigation; uses the map from SLAM.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export TURTLEBOT3_MODEL=waffle_pi

ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True slam:=True
```

---

**Terminal 3 — Frontier exploration**

Runs frontier detection and goal assignment; sends goals to Nav2.

```bash
cd ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch tb3_frontier_exploration exploration.launch.py use_sim_time:=true
```

---

### Expected Behavior

After all three are running:

- Robot appears in Gazebo.
- SLAM builds the map (map topic and RViz).
- Frontier exploration selects goals and sends them to Nav2.
- Robot autonomously explores unknown space.

### Build note

To build the `tb3_frontier_exploration` package (e.g. after cloning or pulling), from `ros2_ws` run:

```bash
./build_tb3_frontier.sh
source install/setup.bash
```

---

## Phase 1 Baseline

**Phase 1 (slam_toolbox + explore_lite):** See [docs/phase1_baseline.md](docs/phase1_baseline.md) for the validated Gazebo + slam_toolbox + Nav2 + explore_lite setup, run order, and verification.
