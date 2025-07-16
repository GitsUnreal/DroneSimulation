import numpy as np

class TargetPredictor:
    def predict_position(self, target, time_ahead):
        """Predict where a moving target will be"""
        if not hasattr(target, 'velocity'):
            return (target.x(), target.y())
        
        current_pos = np.array([target.position[0], target.position[1]])
        velocity = np.array(target.velocity)
        predicted_pos = current_pos + velocity * time_ahead
        
        return tuple(predicted_pos)
    
    def get_intercept_point(self, drone_pos, missile_speed, target_pos, target_velocity):
        """Calculate optimal intercept point for a missile"""
        # Implementation of intercept calculation
        # This is a simplified version - you might want more sophisticated prediction
        relative_pos = np.array(target_pos) - np.array(drone_pos)
        distance = np.linalg.norm(relative_pos)
        time_to_target = distance / missile_speed
        
        intercept_pos = np.array(target_pos) + np.array(target_velocity) * time_to_target
        return tuple(intercept_pos)