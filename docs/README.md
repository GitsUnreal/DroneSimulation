# DroneSimulation Documentation

## Overview
This project simulates autonomous drones with modular AI, movement, combat, and mission logic. The codebase is organized for maintainability and scalability.

## Key Modules
- **MainController**: Orchestrates the simulation, delegates to managers for movement, attack, state, alerts, etc.
- **MovementManager**: Handles drone movement logic.
- **AttackManager**: Handles missile firing and attack logic.
- **AlertManager**: Handles alerts and notifications.
- **PathfindingManager**: Handles pathfinding logic.
- **CollisionManager**: Handles drone-to-drone collision avoidance.
- **StateManager**: Handles drone state transitions.
- **MissionManager**: Handles mission objectives and win/loss conditions.
- **EventManager**: Decouples simulation events.
- **ConfigManager**: Loads and manages simulation configuration.

## How to Run
1. Install dependencies (see `requirements.txt` if present).
2. Run `main.py` to start the simulation.
3. Use the GUI to interact with and observe the simulation.

## Adding a New Mission
- Implement a new mission class and register it with `MissionManager`.

## Event System
- Subscribe to events using `EventManager.subscribe(event_type, callback)`.
- Emit events using `EventManager.emit(event_type, *args, **kwargs)`.

## Configuration
- Place configuration files in `Config/` and load them with `ConfigManager`.

## Contributing
- Follow modularization patterns.
- Add docstrings and comments to new modules.
- Add tests for new features in `tests/`.
