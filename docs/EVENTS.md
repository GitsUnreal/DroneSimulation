# Event System Usage

## Subscribing to Events
```python
from DroneSystem.Events.EventManager import EventManager

def on_drone_destroyed(drone_id):
    print(f"Drone {drone_id} destroyed!")

em = EventManager()
em.subscribe('drone_destroyed', on_drone_destroyed)
```

## Emitting Events
```python
em.emit('drone_destroyed', drone_id=42)
```

## Recommended Events
- `drone_destroyed`
- `missile_fired`
- `mission_complete`
- `alert_triggered`

Use events to decouple logic and keep modules independent.
