class Debug:

    def __init__(self, sim_manager, canvas):
        self.sim_manager = sim_manager
        self.canvas = canvas

    def debug_simulation_state(self):
        """Debug current simulation state"""
        print("=== SIMULATION DEBUG ===")
        print(f"Drones: {len(self.sim_manager.drones)}")
        for i, drone in enumerate(self.sim_manager.drones):
            print(f"  Drone {i}: pos={drone.position}, alive={getattr(drone, 'alive', True)}")
        
        print(f"Target: {self.sim_manager.target}")
        if self.sim_manager.target:
            print(f"  Target pos: {getattr(self.sim_manager.target, 'position', 'No position')}")
        
        print(f"Obstacles: {len(self.sim_manager.obstacles)}")
        for i, obs in enumerate(self.sim_manager.obstacles[:3]):  # First 3 only
            print(f"  Obstacle {i}: x={obs.x()}, y={obs.y()}, w={obs.width()}, h={obs.height()}")
        
        print(f"Base: {self.sim_manager.base}")
        print(f"Canvas size: {self.canvas.size()}")
        print(f"Canvas visible: {self.canvas.isVisible()}")
        print("========================")