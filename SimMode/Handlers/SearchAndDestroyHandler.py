from SimMode.ModeHandler import ModeHandler

class SearchAndDestroyHandler(ModeHandler):
    def __init__(self):
        super().__init__("Search and Destroy")
    
    def configure_drones(self, drones):
        for drone in drones:
            drone.detection_range = 80  # Reduced range
            drone.attack_range = 80
            drone.max_missiles = 4  # More missiles
    
    def configure_target(self, target):
        target.hidden = True  # Target starts hidden
    
    def get_movement_parameters(self):
        return {
            'separation_weight': 1.5,  # Closer formation
            'alignment_weight': 0.2,   # More coordinated
            'cohesion_weight': 0.3,    # Stay together
            'target_weight': 2.0       # Aggressive pursuit
        }
    
    def should_show_target(self):
        return False  # Hidden until detected