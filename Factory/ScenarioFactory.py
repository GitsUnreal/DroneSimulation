"""
ScenarioFactory.py
Creates full simulation scenarios (obstacles, targets, drones, etc) from config or presets.
"""
from Factory.ObstacleFactory import ObstacleFactory
from Factory.TargetFactory import TargetFactory
from Factory.DroneFactory import DroneFactory

class ScenarioFactory:
    @staticmethod
    def create_scenario(config):
        """
        Create a scenario from a config dict. Example config:
        {
            'obstacles': {...},
            'targets': {...},
            'drones': {...},
            ...
        }
        """
        obstacles = ObstacleFactory.create_obstacle_field(**config.get('obstacles', {}))
        targets = [TargetFactory.create_random_target(obstacles) for _ in range(config.get('targets', {}).get('count', 1))]
        drones = DroneFactory.create_drones(**config.get('drones', {})) if 'drones' in config else []
        return {
            'obstacles': obstacles,
            'targets': targets,
            'drones': drones
        }

    @staticmethod
    def create_default_scenario():
        config = {
            'obstacles': {'count': 5},
            'targets': {'count': 2},
            'drones': {'count': 3}
        }
        return ScenarioFactory.create_scenario(config)
