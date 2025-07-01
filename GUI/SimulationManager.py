import random
import numpy as np
from PyQt5.QtCore import QRect
from AI.Drone import Drone
from AI.MainController import MainController
from EnemyAI.Target import target

class SimulationManager:
    def __init__(self):
        self.drones = []
        self.obstacles = []
        self.target = None
        self.base = None
        self.movement_controller = None

    def init_simulation(self, num_drones=2):
        """Initialize simulation objects and controller."""
        self.drones = [
            Drone(
                [np.random.rand() * 500, np.random.rand() * 500],
                [np.random.rand() * 2 - 1, np.random.rand() * 2 - 1],
                i
            )
            for i in range(num_drones)
        ]

        self.obstacles = [
            QRect(200, 150, 100, 50),
            QRect(350, 300, 100, 50),
        ]
        # Create different types of targets
        target_type = random.choice(["static", "linear", "circular", "waypoint", "random"])
        
        if target_type == "static":
            self.target = target(target_id=1, position=(500, 400), height=20, width=20)
        elif target_type == "linear":
            self.target = target(target_id=1, position=(300, 300), height=20, width=20, is_moving_target=True)
            self.target.set_linear_movement(direction=[1, 0.5], speed=3.0)
        elif target_type == "circular":
            self.target = target(target_id=1, position=(400, 300), height=20, width=20, is_moving_target=True)
            self.target.set_circular_movement(center=[400, 300], radius=80, angular_speed=0.03)
        elif target_type == "waypoint":
            self.target = target(target_id=1, position=(200, 200), height=20, width=20, is_moving_target=True)
            self.target.set_random_path(num_waypoints=6)
        elif target_type == "random":
            self.target = target(target_id=1, position=(400, 300), height=20, width=20, is_moving_target=True)
            self.target.set_random_movement(direction_change_interval=2.0, speed=2.5)
        
        print(f"Created {target_type} target at {self.target.position}")
        
        self.base = QRect(50, 50, 20, 20)

        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)

    # def random_target(self):
    #     return QRect(random.randint(400, 800), random.randint(100, 500), 20, 20)

    def check_target_status(self):
        """Check if target has been destroyed"""
        if self.target and self.target.is_destroyed():
            return True
        return False

    def reset_simulation(self):
        """Reset all drones and create new target"""
        for i, drone in enumerate(self.drones):
            start_x = 50 + i * 40
            start_y = 50 + i * 30
            drone.position = np.array([start_x, start_y], dtype=float)
            drone.x, drone.y = start_x, start_y
            drone.velocity = np.zeros(2)
            drone.alive = True
            drone.has_attacked = False
            drone.has_landed = False
            if hasattr(drone, 'returning_to_base'):
                drone.returning_to_base = False

            drone.reset_missiles()
            drone.current_path = []
            drone.current_waypoint_index = 0
            if hasattr(drone, 'current_path_timer'):
                drone.current_path_timer = 0
            print(f"Reset drone {i} to position ({start_x}, {start_y})")

        # Reset target
        if self.target:
            self.target.destroyed = False  # Reset target destruction status

        self.target = target(target_id=0, position=(random.randint(400, 800), random.randint(100, 500)), height=20, width=20)
        print(f"New target at ({self.target.position[0]}, {self.target.position[1]})")
        self.movement_controller = MainController(self.drones, self.obstacles, self.target, self.base)

    def get_active_drones(self):
        """Get drones that are actively participating in simulation"""
        return [drone for drone in self.drones if drone.alive and not (hasattr(drone, 'has_landed') and drone.has_landed)]

    def get_landed_drones(self):
        """Get drones that have landed at base"""
        return [drone for drone in self.drones if hasattr(drone, 'has_landed') and drone.has_landed]

    def reactivate_all_landed_drones(self):
        """Reactivate all landed drones for a new mission"""
        landed_drones = self.get_landed_drones()
        for drone in landed_drones:
            drone.reactivate_from_base()
        
        if landed_drones:
            print(f"Reactivated {len(landed_drones)} drones from base")
        return len(landed_drones)

    def handle_collisions(self):
        """Handle drone collisions with obstacles and other drones - only for active drones"""
        active_drones = self.get_active_drones()
        
        for drone in active_drones:
            # Obstacle collisions
            for obs in self.obstacles:
                if obs.contains(int(drone.position[0]), int(drone.position[1])):
                    print(f"Drone {drone.drone_id} destroyed by obstacle at ({drone.position[0]:.1f}, {drone.position[1]:.1f})")
                    drone.destroy()
                    break

            # Drone-to-drone collisions (only with other active drones)
            for other in active_drones:
                if other is not drone:
                    dist = np.linalg.norm(drone.position - other.position)
                    if dist < 20:
                        direction = drone.position - other.position
                        if np.linalg.norm(direction) > 0:
                            direction /= np.linalg.norm(direction)
                            drone.position += direction * 2
                            other.position -= direction * 2

    def is_position_valid(self, position, width=20, height=20, margin=10):
        """Check if a position is valid (not inside obstacles with margin)"""
        x, y = position
        
        # Check bounds
        if x < 50 or x > 1000 or y < 100 or y > 600:
            return False
        
        # Check collision with obstacles
        for obstacle in self.obstacles:
            # Add margin around obstacles
            if (obstacle.x() - margin <= x <= obstacle.x() + obstacle.width() + margin and
                obstacle.y() - margin <= y <= obstacle.y() + obstacle.height() + margin):
                return False
        
        return True

    def find_valid_position(self, width=20, height=20, margin=10, max_attempts=50):
        """Find a valid spawn position that doesn't overlap with obstacles"""
        import random
        
        for _ in range(max_attempts):
            x = random.randint(50, 1000)
            y = random.randint(100, 600)
            
            if self.is_position_valid((x, y), width, height, margin):
                return (x, y)
        
        # Fallback to safe positions if no valid position found
        safe_positions = [
            (75, 125), (100, 150), (125, 175), (150, 200),  # Top-left area
            (900, 500), (850, 450), (800, 400), (750, 350)  # Bottom-right area
        ]
        
        for pos in safe_positions:
            if self.is_position_valid(pos, width, height, margin):
                return pos
        
        # Last resort - return a position far from obstacles
        return (75, 125)