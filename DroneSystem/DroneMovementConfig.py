from dataclasses import dataclass

@dataclass
class DroneMovementConfig:
    speed: float = 5.0  # Add this line (choose a default value)
    # ...other config attributes...