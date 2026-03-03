# Quadruped Semantic Navigation

Vision-based indoor navigation and obstacle avoidance for quadruped robot (RPi + YOLOv5 + SLAM + Patch management).

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd quadruped-semantic-navigation

# One-click setup
chmod +x scripts/setup_rpi.sh
./scripts/setup_rpi.sh

# Run YOLOv5 demo
./scripts/run_yolo_demo.sh
```

**Prerequisites**: Raspberry Pi 4 (8GB+) with Pi Camera module, Raspberry Pi OS Bookworm

## Repository Structure

```
├── docs/          # Documentation (overview, quickstart, hardware, etc.)
├── upstream/      # Upstream version tracking (no source code)
├── patches/       # Replayable patches for upstream projects
├── scripts/       # One-click setup and execution scripts
├── demos/         # Runnable demo applications
├── src/           # Core algorithm implementations
└── configs/       # Configuration files (RPi4, TB3, etc.)
```


## Features

- **Patch Management**: Clean separation of upstream patches from core code
- **One-Click Setup**: Automated scripts for environment setup
- **Modular Architecture**: Well-organized source code with clear module boundaries
- **Platform Support**: Raspberry Pi 4, TurtleBot3 simulation, Unitree Go2 (planned)

## License

MIT License - see [LICENSE](LICENSE) file for details.
