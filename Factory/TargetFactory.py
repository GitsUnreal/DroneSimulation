import random
import numpy as np
from EnemyAI.Target import target
from Utils.PositionUtils import PositionUtils

class TargetFactory:
    @staticmethod
    def create_random_target(obstacles, target_id=1):
        """Create a random type of target in a valid position"""
        target_type = random.choice(["static", "linear", "circular", "waypoint", "random"])
        
        # Find valid position for target
        valid_position = PositionUtils.find_valid_position(obstacles, width=20, height=20, margin=40)
        
        if target_type == "static":
            new_target = target(target_id=target_id, position=valid_position, height=20, width=20)
        elif target_type == "linear":
            new_target = target(target_id=target_id, position=valid_position, height=20, width=20, is_moving_target=True)
            new_target.set_linear_movement(direction=[1, 0.5], speed=3.0)
        elif target_type == "circular":
            # For circular targets, make sure the circle doesn't intersect obstacles
            center_pos = PositionUtils.find_valid_position(obstacles, width=160, height=160, margin=80)
            new_target = target(target_id=target_id, position=center_pos, height=20, width=20, is_moving_target=True)
            new_target.set_circular_movement(center=center_pos, radius=60, angular_speed=0.03)
        elif target_type == "waypoint":
            new_target = target(target_id=target_id, position=valid_position, height=20, width=20, is_moving_target=True)
            # Generate valid waypoints
            TargetFactory._set_valid_waypoints(new_target, obstacles, num_waypoints=6)
        elif target_type == "random":
            new_target = target(target_id=target_id, position=valid_position, height=20, width=20, is_moving_target=True)
            new_target.set_random_movement(direction_change_interval=2.0, speed=2.5)
        
        print(f"Created {target_type} target at safe position {valid_position}")
        return new_target

    @staticmethod
    def _set_valid_waypoints(target_obj, obstacles, num_waypoints=6):
        """Generate valid waypoints that don't intersect obstacles"""
        valid_waypoints = []
        
        for _ in range(num_waypoints):
            waypoint_pos = PositionUtils.find_valid_position(obstacles, width=20, height=20, margin=30)
            valid_waypoints.append(np.array(waypoint_pos, dtype=float))
        
        target_obj.movement_pattern = "waypoint"
        target_obj.waypoints = valid_waypoints
        target_obj.current_waypoint_index = 0
        target_obj.path_complete = False
        
        print(f"Target {target_obj.target_id} valid waypoints: {valid_waypoints}")