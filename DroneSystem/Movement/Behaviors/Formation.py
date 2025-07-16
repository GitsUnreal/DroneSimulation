import numpy as np
from typing import List, Dict, Optional

class FormationType:
    V_FORMATION = "v_formation"
    LINE_FORMATION = "line_formation"
    DIAMOND_FORMATION = "diamond_formation"
    CIRCLE_FORMATION = "circle_formation"
    WEDGE_FORMATION = "wedge_formation"

class Formation:
    def __init__(self, formation_type: str = FormationType.V_FORMATION, spacing: float = 30.0):
        self.formation_type = formation_type
        self.spacing = spacing
        self.leader = None
        self.members = []
        self.target_positions = {}
    
    def set_leader(self, drone):
        """Set formation leader"""
        self.leader = drone
        if drone not in self.members:
            self.members.append(drone)
    
    def add_member(self, drone):
        """Add drone to formation"""
        if drone not in self.members:
            self.members.append(drone)
    
    def remove_member(self, drone):
        """Remove drone from formation"""
        if drone in self.members:
            self.members.remove(drone)
        if self.leader == drone and self.members:
            self.leader = self.members[0]  # Promote first member to leader
    
    def update_formation(self) -> Dict:
        """Update formation positions for all members"""
        if not self.leader or not self.members:
            return {}
        
        # Calculate target positions based on formation type
        if self.formation_type == FormationType.V_FORMATION:
            positions = self._calculate_v_formation()
        elif self.formation_type == FormationType.LINE_FORMATION:
            positions = self._calculate_line_formation()
        elif self.formation_type == FormationType.DIAMOND_FORMATION:
            positions = self._calculate_diamond_formation()
        elif self.formation_type == FormationType.CIRCLE_FORMATION:
            positions = self._calculate_circle_formation()
        elif self.formation_type == FormationType.WEDGE_FORMATION:
            positions = self._calculate_wedge_formation()
        else:
            positions = self._calculate_v_formation()  # Default
        
        # Update target positions
        for i, member in enumerate(self.members):
            if i < len(positions):
                self.target_positions[member.drone_id] = positions[i]
        
        return self.target_positions
    
    def get_formation_force(self, drone) -> np.ndarray:
        """Get force vector to maintain formation position"""
        if drone.drone_id not in self.target_positions:
            return np.zeros(2)
        
        target_pos = np.array(self.target_positions[drone.drone_id])
        current_pos = drone.position
        
        # Calculate force towards target position
        to_target = target_pos - current_pos
        distance = np.linalg.norm(to_target)
        
        if distance < 5:  # Close enough to target
            return np.zeros(2)
        
        # Proportional force - stronger when farther from target
        force_magnitude = min(distance * 0.1, 2.0)  # Cap maximum force
        force_direction = to_target / (distance + 1e-6)
        
        return force_direction * force_magnitude
    
    def _calculate_v_formation(self) -> List[np.ndarray]:
        """Calculate V-formation positions"""
        positions = []
        leader_pos = self.leader.position
        
        for i, member in enumerate(self.members):
            if member == self.leader:
                positions.append(leader_pos.copy())
            else:
                # Determine which side of the V
                side = 1 if (i - 1) % 2 == 0 else -1
                rank = (i - 1) // 2 + 1
                
                offset = np.array([
                    -rank * self.spacing * 0.8,  # Behind leader
                    side * rank * self.spacing    # To the side
                ])
                
                positions.append(leader_pos + offset)
        
        return positions
    
    def _calculate_line_formation(self) -> List[np.ndarray]:
        """Calculate line formation positions"""
        positions = []
        leader_pos = self.leader.position
        
        for i, member in enumerate(self.members):
            offset = np.array([0, (i - len(self.members) // 2) * self.spacing])
            positions.append(leader_pos + offset)
        
        return positions
    
    def _calculate_diamond_formation(self) -> List[np.ndarray]:
        """Calculate diamond formation positions"""
        positions = []
        leader_pos = self.leader.position
        
        diamond_positions = [
            np.array([0, 0]),                    # Leader (front)
            np.array([-self.spacing, self.spacing/2]),     # Left
            np.array([self.spacing, self.spacing/2]),      # Right
            np.array([0, self.spacing]),         # Rear
            np.array([-self.spacing/2, self.spacing*1.5]), # Rear-left
            np.array([self.spacing/2, self.spacing*1.5])   # Rear-right
        ]
        
        for i, member in enumerate(self.members):
            if i < len(diamond_positions):
                positions.append(leader_pos + diamond_positions[i])
            else:
                # Additional drones in extended line
                extra_offset = np.array([0, self.spacing * (1.5 + (i - len(diamond_positions)))])
                positions.append(leader_pos + extra_offset)
        
        return positions
    
    def _calculate_circle_formation(self) -> List[np.ndarray]:
        """Calculate circle formation positions"""
        positions = []
        leader_pos = self.leader.position
        radius = self.spacing * 1.5
        
        for i, member in enumerate(self.members):
            if member == self.leader:
                positions.append(leader_pos.copy())
            else:
                angle = 2 * np.pi * (i - 1) / max(len(self.members) - 1, 1)
                offset = np.array([
                    radius * np.cos(angle),
                    radius * np.sin(angle)
                ])
                positions.append(leader_pos + offset)
        
        return positions
    
    def _calculate_wedge_formation(self) -> List[np.ndarray]:
        """Calculate wedge formation positions"""
        positions = []
        leader_pos = self.leader.position
        
        for i, member in enumerate(self.members):
            if member == self.leader:
                positions.append(leader_pos.copy())
            else:
                # Create wedge shape - wider at the back
                rank = (i - 1) // 2 + 1
                side = 1 if (i - 1) % 2 == 0 else -1
                
                offset = np.array([
                    -rank * self.spacing * 0.6,      # Behind leader
                    side * rank * self.spacing * 1.2  # Wider spread
                ])
                
                positions.append(leader_pos + offset)
        
        return positions
    
    def get_formation_integrity(self) -> float:
        """Calculate how well the formation is maintained (0-1)"""
        if len(self.members) < 2:
            return 1.0
        
        total_error = 0.0
        count = 0
        
        for member in self.members:
            if member.drone_id in self.target_positions:
                target_pos = np.array(self.target_positions[member.drone_id])
                actual_pos = member.position
                error = np.linalg.norm(target_pos - actual_pos)
                
                # Normalize error (perfect = 0, terrible = spacing distance)
                normalized_error = min(error / self.spacing, 1.0)
                total_error += normalized_error
                count += 1
        
        if count == 0:
            return 1.0
        
        # Return integrity score (1 = perfect, 0 = terrible)
        return max(0.0, 1.0 - (total_error / count))
    
    def change_formation(self, new_formation_type: str):
        """Change formation type"""
        self.formation_type = new_formation_type
        self.update_formation()  # Recalculate positions
    
    def get_formation_status(self) -> Dict:
        """Get detailed formation status"""
        return {
            'type': self.formation_type,
            'leader_id': self.leader.drone_id if self.leader else None,
            'member_count': len(self.members),
            'member_ids': [m.drone_id for m in self.members],
            'integrity': self.get_formation_integrity(),
            'spacing': self.spacing
        }