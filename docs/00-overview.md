# Overview

## Project Description

This repository contains vision-based indoor navigation and obstacle avoidance system for quadruped robots, specifically designed for Raspberry Pi with YOLOv5, SLAM, and patch management capabilities.

## Repository Structure

This repository follows a clear separation between **upstream dependencies** (patches) and **core implementation**:

```
quadruped-semantic-navigation/
├── docs/              # Documentation
├── upstream/          # Upstream version tracking (no source code)
├── patches/           # Replayable patches for upstream projects
├── scripts/           # One-click setup and execution scripts
├── demos/             # Runnable demo applications
├── src/               # Core algorithm implementations
└── configs/           # Configuration files for different platforms
```

## Key Features

- **Patch Management**: Clean separation of upstream patches from core code
- **One-Click Setup**: Automated scripts for cloning upstream repos, applying patches, and running demos
- **Modular Architecture**: Well-organized source code with clear module boundaries
- **Platform Support**: Configurations for RPi4, TB3, Go2, and simulation environments

## Quick Links

- [Quick Start Guide](01-quickstart.md)
- [Hardware Requirements](02-hardware.md)
- [Software Stack](03-software-stack.md)
- [Troubleshooting](04-troubleshooting.md)
