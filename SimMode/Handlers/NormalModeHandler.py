from SimMode.ModeHandler import ModeHandler

class NormalModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("Normal")
    
    def configure_drones(self, drones):
        for drone in drones:
            drone.detection_range = 100
            drone.attack_range = 100
            drone.max_missiles = 2
    
    def configure_target(self, target):
        target.hidden = False
    
    def get_movement_parameters(self):
        return {
            'separation_weight': 2.0,
            'alignment_weight': 0.1,
            'cohesion_weight': 0.1,
            'target_weight': 1.5
        }
    
    def should_show_target(self):
        return True