class AlertManager:
    @staticmethod
    def handle_alerts(drones, alert_system):
        for drone in drones:
            if not drone.alive and not hasattr(drone, '_destruction_alerted'):
                alert_system.show_drone_destroyed_alert(drone.drone_id)
                drone._destruction_alerted = True
            if drone.missiles_fired >= drone.max_missiles and not hasattr(drone, '_missiles_alerted'):
                alert_system.show_all_missiles_fired_alert(drone.drone_id)
                drone._missiles_alerted = True
            if hasattr(drone, 'has_landed') and drone.has_landed and not hasattr(drone, '_landing_alerted'):
                alert_system.show_drone_landed_alert(drone.drone_id)
                drone._landing_alerted = True
    @staticmethod
    def handle_mission_complete(drones, alert_system, mission_complete_alerted):
        if (all(hasattr(drone, 'has_landed') and drone.has_landed for drone in drones)
            and not mission_complete_alerted):
            alert_system.show_mission_complete_alert(drones)
            return True
        return mission_complete_alerted
