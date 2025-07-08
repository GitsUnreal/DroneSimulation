"""Status checking utilities for GUI"""

class StatusChecker:
    """Checks status of various system components"""
    
    def __init__(self):
        self.last_check_time = 0
        self.status_cache = {}
    
    def check_system_status(self):
        """Check overall system status"""
        return {
            'gui_status': 'OK',
            'simulation_status': 'OK',
            'drone_status': 'OK'
        }
    
    def check_drone_status(self, drones):
        """Check status of drones"""
        active_count = len([d for d in drones if getattr(d, 'alive', True)])
        return {
            'total_drones': len(drones),
            'active_drones': active_count,
            'status': 'OK' if active_count > 0 else 'WARNING'
        }