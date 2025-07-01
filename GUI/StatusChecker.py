import numpy as np

class StatusChecker:
    def __init__(self):
        self.check_counter = 0

    def check_drone_states(self, drones):
        """Check and report drone states"""
        alive_count = 0
        landed_count = 0
        destroyed_count = 0
        
        for drone in drones:
            if hasattr(drone, 'has_landed') and drone.has_landed:
                landed_count += 1
            elif drone.alive:
                alive_count += 1
            else:
                destroyed_count += 1
        
        print(f"Drone Status: {alive_count} Active, {landed_count} Landed, {destroyed_count} Destroyed")
        return alive_count, landed_count, destroyed_count

    def check_mission_progress(self, drones):
        """Check mission completion status"""
        total_missiles_fired = sum(drone.missiles_fired for drone in drones)
        total_missiles_available = sum(drone.max_missiles for drone in drones)
        drones_attacked = sum(1 for drone in drones if drone.has_attacked)
        
        print(f"Mission Progress: {total_missiles_fired}/{total_missiles_available} missiles fired, {drones_attacked}/{len(drones)} drones attacked")
        
        mission_complete = all(drone.has_attacked and drone.has_landed or not drone.alive for drone in drones)
        
        if mission_complete:
            print("🎯 MISSION COMPLETE! All drones have completed their attacks.")
            return True
        return False

    def check_system_performance(self, drones, obstacles):
        """Check for system issues and performance"""
        collisions_detected = 0
        pathfinding_active = 0
        stuck_drones = 0
        
        for drone in drones:
            if not drone.alive:
                continue
                
            # Check for collisions with obstacles
            for obs in obstacles:
                if obs.contains(int(drone.position[0]), int(drone.position[1])):
                    collisions_detected += 1
            
            # Check if drone has active pathfinding
            if hasattr(drone, 'current_path') and drone.current_path:
                pathfinding_active += 1
            
            # Check if drone is stuck (very low velocity for extended time)
            if hasattr(drone, 'velocity') and np.linalg.norm(drone.velocity) < 0.1:
                if not hasattr(drone, 'stuck_timer'):
                    drone.stuck_timer = 0
                drone.stuck_timer += 1
                if drone.stuck_timer > 100:  # Stuck for 100 frames
                    stuck_drones += 1
            else:
                if hasattr(drone, 'stuck_timer'):
                    drone.stuck_timer = 0
        
        if collisions_detected > 0:
            print(f"⚠️ WARNING: {collisions_detected} collision(s) detected!")
        if stuck_drones > 0:
            print(f"⚠️ WARNING: {stuck_drones} drone(s) appear stuck!")
        
        print(f"System Status: {pathfinding_active} drones pathfinding, {stuck_drones} stuck")
        return collisions_detected, pathfinding_active, stuck_drones

    def run_periodic_checks(self, drones, obstacles, toggle_simulation_callback):
        """Run all periodic status checks"""
        self.check_counter += 1
        
        if self.check_counter % 20 == 0:  # Every second at 50ms intervals
            self.check_drone_states(drones)
            mission_complete = self.check_mission_progress(drones)
            performance_issues = self.check_system_performance(drones, obstacles)
            
            # Check if target is destroyed
            target_destroyed = hasattr(self, 'target') and self.target and self.target.is_destroyed()
            
            if target_destroyed and mission_complete:
                print("🎯 MISSION COMPLETE: Target destroyed and all drones processed!")
                return True, False, performance_issues
            elif target_destroyed:
                print("🎯 Target destroyed! Waiting for drones to return to base...")
        
        return False, False, False