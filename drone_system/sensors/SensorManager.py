"""Sensor management system for drones"""
from typing import List, Dict, Any
import numpy as np

class SensorReading:
    """Represents a sensor reading"""
    
    def __init__(self, sensor_type: str, value: Any, timestamp: float):
        self.sensor_type = sensor_type
        self.value = value
        self.timestamp = timestamp
        self.confidence = 1.0

class SensorManager:
    """Manages sensors for drones"""
    
    def __init__(self, drone_id: int):
        self.drone_id = drone_id
        self.sensors = {}
        self.readings_history = []
        self.max_history = 100
    
    def add_sensor(self, sensor_type: str, sensor_config: dict = None):
        """Add a sensor to the drone"""
        self.sensors[sensor_type] = {
            'enabled': True,
            'config': sensor_config or {},
            'last_reading': None
        }
    
    def get_sensor_reading(self, sensor_type: str, drone_position: np.ndarray, environment_data: dict) -> SensorReading:
        """Get a reading from a specific sensor"""
        if sensor_type not in self.sensors or not self.sensors[sensor_type]['enabled']:
            return None
        
        # Simulate different sensor types
        if sensor_type == 'proximity':
            return self._get_proximity_reading(drone_position, environment_data)
        elif sensor_type == 'target_detection':
            return self._get_target_detection_reading(drone_position, environment_data)
        elif sensor_type == 'obstacle_detection':
            return self._get_obstacle_detection_reading(drone_position, environment_data)
        
        return None
    
    def _get_proximity_reading(self, position: np.ndarray, env_data: dict) -> SensorReading:
        """Get proximity sensor reading"""
        # Simple proximity detection
        nearby_objects = []
        if 'drones' in env_data:
            for other_drone in env_data['drones']:
                if other_drone.drone_id != self.drone_id:
                    distance = np.linalg.norm(position - other_drone.position)
                    if distance < 50:  # 50 pixel detection range
                        nearby_objects.append(('drone', distance, other_drone.drone_id))
        
        return SensorReading('proximity', nearby_objects, 0.0)
    
    def _get_target_detection_reading(self, position: np.ndarray, env_data: dict) -> SensorReading:
        """Get target detection reading"""
        if 'target' in env_data and env_data['target']:
            target = env_data['target']
            target_pos = np.array([target.x(), target.y()])
            distance = np.linalg.norm(position - target_pos)
            
            # Detection range and accuracy based on distance
            detection_range = 150
            if distance <= detection_range:
                accuracy = max(0.5, 1.0 - (distance / detection_range))
                return SensorReading('target_detection', {
                    'detected': True,
                    'distance': distance,
                    'direction': target_pos - position,
                    'accuracy': accuracy
                }, 0.0)
        
        return SensorReading('target_detection', {'detected': False}, 0.0)
    
    def _get_obstacle_detection_reading(self, position: np.ndarray, env_data: dict) -> SensorReading:
        """Get obstacle detection reading"""
        obstacles_detected = []
        if 'obstacles' in env_data:
            for obstacle in env_data['obstacles']:
                # Check if obstacle is within detection range
                obs_center = np.array([obstacle.x() + obstacle.width()/2, obstacle.y() + obstacle.height()/2])
                distance = np.linalg.norm(position - obs_center)
                
                if distance < 100:  # 100 pixel detection range
                    obstacles_detected.append({
                        'distance': distance,
                        'position': obs_center,
                        'size': (obstacle.width(), obstacle.height())
                    })
        
        return SensorReading('obstacle_detection', obstacles_detected, 0.0)
    
    def update_sensors(self, drone_position: np.ndarray, environment_data: dict):
        """Update all sensors and store readings"""
        current_time = 0.0  # In a real implementation, use actual time
        
        for sensor_type in self.sensors:
            reading = self.get_sensor_reading(sensor_type, drone_position, environment_data)
            if reading:
                reading.timestamp = current_time
                self.sensors[sensor_type]['last_reading'] = reading
                
                # Store in history
                self.readings_history.append(reading)
                if len(self.readings_history) > self.max_history:
                    self.readings_history.pop(0)
    
    def get_latest_reading(self, sensor_type: str) -> SensorReading:
        """Get the latest reading from a sensor"""
        if sensor_type in self.sensors:
            return self.sensors[sensor_type]['last_reading']
        return None
    
    def get_sensor_status(self) -> Dict[str, bool]:
        """Get status of all sensors"""
        return {sensor: data['enabled'] for sensor, data in self.sensors.items()}