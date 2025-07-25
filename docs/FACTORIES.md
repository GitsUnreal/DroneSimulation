# FACTORIES.md

## Overview
This document describes the factory system for object creation in the simulation.

### Key Files
- `BaseFactory.py`: Abstract base class for all factories.
- `FactoryRegistry.py`: Central registry for registering and retrieving factories.
- `ScenarioFactory.py`: Creates full simulation scenarios (obstacles, targets, etc).
- `ObstacleFactory.py`, `TargetFactory.py`: Factories for specific object types.

## Extending the Factory System
- To add a new object type, create a new factory inheriting from `BaseFactory`.
- Register it in `FactoryRegistry` for easy access.
- Use `ScenarioFactory` to compose scenarios from multiple factories.

## Example Usage
```python
from Factory.FactoryRegistry import FactoryRegistry
from Factory.ScenarioFactory import ScenarioFactory

# Register factories
FactoryRegistry.register_factory('obstacle', ObstacleFactory)
FactoryRegistry.register_factory('target', TargetFactory)

# Create a scenario
scenario = ScenarioFactory.create_default_scenario()
```

## Design Principles
- **Modularity:** Each factory handles one object type or pattern.
- **Extensibility:** Add new factories without changing existing code.
- **Config-Driven:** Factories can create objects from config dicts for flexibility.
