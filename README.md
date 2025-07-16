# DroneSwarp - Drone Simulation System

A sophisticated multi-drone simulation system with advanced AI behaviors, missile systems, and real-time monitoring capabilities built with PyQt5.

## 🚁 Overview

DroneSwarp is a comprehensive drone simulation platform that features intelligent swarm behavior, multiple mission modes, advanced pathfinding, and a sophisticated missile combat system. The simulation supports various operational modes from reconnaissance to search-and-destroy missions.

## ✨ Key Features

### Core Systems
- **Multi-Drone Management**: Coordinate multiple drones with intelligent swarm behavior
- **Advanced AI**: A* pathfinding, boids flocking, and dynamic obstacle avoidance
- **Mission Modes**: 8 different operational modes (Normal, Reconnaissance, Search & Destroy, etc.)
- **Sophisticated Missile System**: 4 missile types with realistic physics and explosion effects
- **Real-time Monitoring**: Performance metrics, statistics, and debug information

### Simulation Capabilities
- **Dynamic Environments**: Moving targets, obstacles, and bases
- **Radar Systems**: Configurable radar detection with sweep visualization
- **State Management**: Comprehensive drone and mission state tracking
- **Save/Load System**: Complete simulation state persistence
- **Performance Optimization**: Real-time CPU and memory monitoring

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- PyQt5
- NumPy
- psutil (for performance monitoring)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/droneswarp.git
cd droneswarp

# Install dependencies
pip install PyQt5 numpy psutil

# Run the simulation
python main.py
```

## 🎮 Usage

### Starting the Simulation
```bash
python main.py
```

### Controls
- **Start/Pause**: Space bar or Start button
- **Reset**: R key or Reset button
- **Quick Save**: F5
- **Quick Load**: F9
- **Save Simulation**: Ctrl+S
- **Load Simulation**: Ctrl+O

### Interface Elements
- **Control Panel**: Start/pause, reset, mode selection, speed control
- **Visualization**: Real-time drone positions, paths, missiles, and effects
- **Status Panels**: Performance metrics, statistics, debug information
- **Radar Display**: Configurable radar sweep with target detection

## 🎯 Mission Modes

| Mode | Description | Special Features |
|------|-------------|------------------|
| **Normal** | Standard operations | Balanced settings, explosive missiles |
| **Reconnaissance** | Stealth surveillance | Limited weapons, radar required for targets |
| **Search & Destroy** | Aggressive hunting | Fast radar, high missile capacity |
| **Escort** | Protection missions | Formation flying, defensive positioning |
| **Defensive** | Base protection | Enhanced radar, strategic positioning |
| **Bombing Run** | Precision strikes | Heavy explosives, fast radar |
| **Patrol** | Area monitoring | Continuous radar, patrol patterns |
| **Search & Rescue** | Recovery operations | Fast radar, homing missiles |

## 🚀 Missile System

### Missile Types
- **Standard**: Balanced speed and damage
- **Explosive**: High damage, large blast radius
- **Homing**: Target-seeking with maneuverability
- **Piercing**: High-speed, focused damage

### Features
- Realistic physics simulation
- Trail effects and explosion animations
- Collision detection with obstacles
- Target prediction algorithms

## 📊 Monitoring & Analysis

### Performance Panel
- Real-time CPU and memory usage
- Frame rate monitoring
- System resource tracking

### Statistics Panel
- Mission progress and completion metrics
- Drone status and activity
- Combat effectiveness ratings

### Debug Panel
- Real-time system information
- Drone state visualization
- Performance diagnostics

## 🏗️ Architecture

### Core Components
```
DroneSystem/
├── Core/           # Drone classes and configurations
├── AI/             # Behavior and decision systems
├── Combat/         # Missile and weapon systems
├── Movement/       # Navigation and pathfinding
└── States/         # State management

GUI/
├── Windows/        # Main interface windows
├── Panels/         # Information displays
├── Renderer/       # Visualization systems
└── Components/     # UI elements

Utils/
├── SaveLoadManager # Simulation persistence
└── Various utilities
```

### Design Patterns
- **Factory Pattern**: For creating drones, targets, and obstacles
- **State Pattern**: For drone and missile state management
- **Observer Pattern**: For UI updates and event handling
- **Strategy Pattern**: For different AI behaviors and mission modes

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
# or
python tests/test_core_functionality.py
```

### Test Coverage
- ✅ Drone functionality and movement
- ✅ Missile system mechanics
- ✅ Pathfinding algorithms
- ✅ Save/Load operations
- ✅ Performance benchmarks
- ✅ Explosion effects

## 💾 Save System

### Save Files
- **Location**: `saves/` directory
- **Format**: JSON with timestamp
- **Quick Save**: `quicksave.sim`
- **Auto-backup**: Timestamped saves

### Saved Data
- Drone positions and states
- Mission progress
- Configuration settings
- Target and obstacle layouts

## 🎨 Customization

### Configuration Files
- `Config/SimulationConfig.py`: Main simulation parameters
- Mode handlers for mission-specific settings
- Missile configuration presets

### Extensibility
- Plugin system for AI behaviors
- Custom mission mode creation
- Configurable UI themes
- Modular renderer system

## 📈 Performance

### Optimization Features
- Efficient grid-based collision detection
- Optimized pathfinding algorithms
- Frame rate limiting and smoothing
- Memory usage monitoring

### Benchmarks
- Supports 10+ drones simultaneously
- Real-time performance at 60 FPS
- Memory usage under 100MB
- CPU usage optimized for multi-core systems

## 🐛 Known Issues

- Performance panel button needs connection
- Statistics panel button needs connection
- Convoy target spawning not implemented
- Some save loading edge cases

## 🛣️ Roadmap

### Immediate (v1.1)
- [ ] Fix remaining UI button connections
- [ ] Implement convoy target spawning
- [ ] Resolve save loading issues
- [ ] Add zoom functionality

### Short-term (v1.2)
- [ ] Formation flying patterns
- [ ] Sound effects system
- [ ] Scenario editor
- [ ] Mission replay system

### Long-term (v2.0)
- [ ] 3D visualization option
- [ ] Machine learning integration
- [ ] Multiplayer support
- [ ] Weather effects

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions, bug reports, or feature requests:
- Create an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the TodoList.md for known issues and progress

## 🙏 Acknowledgments

- PyQt5 development team for the GUI framework
- NumPy community for mathematical operations
- Open source pathfinding algorithm implementations
- Beta testers and contributors

---

**Project Status**: 92% Complete | **Last Updated**: July 2025

*DroneSwarp - Where artificial intelligence meets aerial coordination.*