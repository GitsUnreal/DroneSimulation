from SimMode.ModeHandler import ModeHandler

class PatrolModeHandler(ModeHandler):
    def __init__(self):
        super().__init__("patrol")
    
    def configure_drones(self, drones):
        for drone in drones:
            drone.detection_range = 10
            drone.attack_range = 30
            drone.max_missiles = 6
            drone.missile_config = self.get_missile_parameters()
            drone.movement_config = self.get_movement_parameters()

    def drone_movement_parameters(self):
        return {
            'speed': 50,
            'turn_rate': 5
        }

    def configure_target(self, target):
        target.hidden = False
    
    def get_movement_parameters(self):
        return {
            'separation_weight': 2.0,
            'alignment_weight': 0.1,
            'cohesion_weight': 0.1,
            'target_weight': 1.5
        }
    
    def get_missile_parameters(self):
        return {
            'speed': 100,
            'lifetime': 5,
            'explosion_radius': 10,
            'misile_type': 'explosive'
        }
    
    def should_show_target(self):
        return True