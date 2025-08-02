# Architecture

## Modular Design
- Each major logic area is handled by a dedicated manager class.
- The MainController delegates to these managers, keeping orchestration clean.

## Event System
- The `EventManager` allows decoupled communication between components.
- Example: When a drone is destroyed, emit a `drone_destroyed` event. Listeners (e.g., AlertManager) can respond.

## Mission Management
- The `MissionManager` encapsulates mission objectives and win/loss logic.
- New missions can be added by subclassing or registering with the manager.

## Configuration
- The `ConfigManager` loads simulation parameters from JSON files.
- Use it to centralize and validate all tunable parameters.

## Extending the System
- Add new managers for new logic areas.
- Use the event system for new types of events.
- Keep business logic out of GUI code.
