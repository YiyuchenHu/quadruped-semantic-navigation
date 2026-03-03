# Quadruped Semantic Navigation

Vision-based indoor navigation and obstacle avoidance for quadruped robot (RPi + YOLOv5 + SLAM + Patch management).

## 🎯 Project Overview

This repository implements a complete navigation system for quadruped robots, featuring:
- **Real-time object detection** using YOLOv5 on Raspberry Pi
- **SLAM-based mapping** with LiDAR and camera sensors
- **Path planning** with A* and local obstacle avoidance
- **Clean patch management** for upstream dependencies

## 📁 Repository Structure

This repository follows a clear separation between **upstream dependencies** (patches) and **core implementation**:

```
quadruped-semantic-navigation/
├── docs/              # Comprehensive documentation
│   ├── 00-overview.md
│   ├── 01-quickstart.md
│   ├── 02-hardware.md
│   ├── 03-software-stack.md
│   ├── 04-troubleshooting.md
│   └── patches/       # Patch documentation
├── upstream/          # Upstream version tracking (no source code)
│   ├── picamera2.version
│   └── yolov5-demo.version
├── patches/           # Replayable patches for upstream projects
│   └── picamera2/
├── scripts/           # One-click setup and execution scripts
│   ├── setup_rpi.sh
│   ├── fetch_picamera2.sh
│   ├── apply_patches_picamera2.sh
│   └── run_yolo_demo.sh
├── demos/             # Runnable demo applications
│   └── rpi_yolov5_tflite/
├── src/               # Core algorithm implementations
│   ├── navigation/    # Path planning algorithms
│   ├── mapping/       # SLAM and mapping
│   ├── perception/    # Object detection and tracking
│   └── utils/         # Common utilities
└── configs/           # Configuration files for different platforms
    ├── rpi4_bookworm_aarch64.yaml
    └── sim_tb3.yaml
```

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi 4 (8GB recommended) running Raspberry Pi OS Bookworm
- Camera module (Pi Camera v2 or v3)
- Optional: TurtleBot3 or Unitree Go2 for full navigation stack

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd quadruped-semantic-navigation
   ```

2. **Run one-click setup**:
   ```bash
   chmod +x scripts/setup_rpi.sh
   ./scripts/setup_rpi.sh
   ```

3. **Run YOLOv5 demo**:
   ```bash
   ./scripts/run_yolo_demo.sh
   ```

For detailed instructions, see [Quick Start Guide](docs/01-quickstart.md).

## 📚 Documentation

- **[Overview](docs/00-overview.md)** - Project overview and architecture
- **[Quick Start](docs/01-quickstart.md)** - Installation and first steps
- **[Hardware Setup](docs/02-hardware.md)** - Hardware requirements and configuration
- **[Software Stack](docs/03-software-stack.md)** - Dependencies and versions
- **[Troubleshooting](docs/04-troubleshooting.md)** - Common issues and solutions

## 🔧 Key Features

### Patch Management
- Clean separation of upstream patches from core code
- Version tracking for all upstream dependencies
- Replayable patches for easy maintenance

### One-Click Setup
- Automated scripts for cloning upstream repos
- Automatic patch application
- Environment configuration

### Modular Architecture
- Well-organized source code with clear module boundaries
- Input/output conventions documented
- Easy to extend and maintain

### Platform Support
- Raspberry Pi 4 (primary platform)
- TurtleBot3 simulation
- Unitree Go2 (planned)

## 🏗️ Development

### Adding New Algorithms

1. Create module directory in `src/`:
   ```bash
   mkdir -p src/your_module
   ```

2. Add README with input/output conventions
3. Implement your algorithm
4. Add tests/demos if applicable

### Adding New Patches

1. Update upstream version in `upstream/`
2. Create patch file in `patches/`
3. Document in `docs/patches/`
4. Update scripts if needed

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows the repository structure conventions
- Documentation is updated
- Patches are properly documented
- Tests pass (if applicable)

## 📧 Contact

For questions or issues, please open an issue on the repository.
