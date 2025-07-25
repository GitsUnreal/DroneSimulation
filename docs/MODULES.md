# Module Overview

## DroneSystem
- **Controllers/**: MainController, MovementManager, AttackManager, AlertManager, EscortFormationManager
- **Movement/**: Navigation, Behaviors, PathfindingManager, CollisionManager
- **Combat/**: Weapons, MissileManager, MissileSystem
- **States/**: StateManager
- **Mission/**: MissionManager
- **Events/**: EventManager
- **Core/**: Drone, DroneConfig, DroneFactory, DroneTypes
- **AI/**: BehaviorEngine, DecisionTrees, MissionPlanner, PatternGenerator

## Config
- **ConfigManager**: Loads and manages simulation configuration files.

## Utils
- **MathUtils**: Vector math utilities.
- **DroneUtils**: Drone-specific helpers.

## How to Extend
- Add new managers for new logic areas.
- Use the event system to decouple features.
- Add new configuration files for new scenarios.
