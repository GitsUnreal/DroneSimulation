from typing import List, Dict, Optional, Tuple
from enum import Enum
import numpy as np
from .PatternGenerator import PatternGenerator, SearchPattern

class MissionPhase(Enum):
    PREPARATION = "preparation"
    DEPLOYMENT = "deployment"
    SEARCH = "search"
    ENGAGE = "engage"
    EXTRACTION = "extraction"
    COMPLETE = "complete"

class MissionObjective(Enum):
    SEARCH_AND_DESTROY = "search_and_destroy"
    RECONNAISSANCE = "reconnaissance"
    ESCORT = "escort"  # Add this line
    PATROL = "patrol"
    SEARCH_AND_RESCUE = "search_and_rescue"

class MissionPlanner:
    def __init__(self, pattern_generator: PatternGenerator = None):
        self.pattern_generator = pattern_generator or PatternGenerator()
        self.current_phase = MissionPhase.PREPARATION
        self.mission_objective = MissionObjective.SEARCH_AND_DESTROY
        self.phase_timers = {}
        self.mission_start_time = 0
        self.drone_assignments = {}
        
    def plan_mission(self, drones: List, target=None, mission_type: MissionObjective = None) -> Dict:
        """Create a comprehensive mission plan"""
        if mission_type:
            self.mission_objective = mission_type
            
        mission_plan = {
            'objective': self.mission_objective.value,
            'phases': self._create_phase_plan(),
            'drone_roles': self._assign_drone_roles(drones),
            'search_areas': self._divide_search_areas(drones),
            'coordination_points': self._plan_coordination_points(),
            'contingencies': self._plan_contingencies(drones)
        }
        
        return mission_plan
    
    def update_mission_phase(self, drones: List, target=None, simulation_step: int = 0) -> Dict:
        """Update current mission phase based on situation"""
        phase_changed = False
        old_phase = self.current_phase
        
        # Check phase transition conditions
        if self.current_phase == MissionPhase.PREPARATION:
            if all(drone.alive for drone in drones):
                self.current_phase = MissionPhase.DEPLOYMENT
                phase_changed = True
                
        elif self.current_phase == MissionPhase.DEPLOYMENT:
            if self._drones_deployed(drones):
                if target and getattr(target, 'hidden', False):
                    self.current_phase = MissionPhase.SEARCH
                else:
                    self.current_phase = MissionPhase.ENGAGE
                phase_changed = True
                
        elif self.current_phase == MissionPhase.SEARCH:
            if target and getattr(target, 'spotted_by_radar', False):
                self.current_phase = MissionPhase.ENGAGE
                phase_changed = True
                
        elif self.current_phase == MissionPhase.ENGAGE:
            if target and getattr(target, 'destroyed', False):
                self.current_phase = MissionPhase.EXTRACTION
                phase_changed = True
            elif all(drone.has_attacked for drone in drones if drone.alive):
                self.current_phase = MissionPhase.EXTRACTION
                phase_changed = True
                
        elif self.current_phase == MissionPhase.EXTRACTION:
            if all(getattr(drone, 'has_landed', False) for drone in drones if drone.alive):
                self.current_phase = MissionPhase.COMPLETE
                phase_changed = True
        
        # Update phase timer
        if phase_changed:
            self.phase_timers[old_phase.value] = simulation_step - self.phase_timers.get(old_phase.value, 0)
            self.phase_timers[self.current_phase.value] = simulation_step
        
        return {
            'current_phase': self.current_phase.value,
            'phase_changed': phase_changed,
            'previous_phase': old_phase.value if phase_changed else None,
            'phase_duration': simulation_step - self.phase_timers.get(self.current_phase.value, simulation_step)
        }
    
    def get_drone_orders(self, drone, target=None, simulation_step: int = 0) -> Dict:
        """Get specific orders for a drone based on current mission phase"""
        orders = {
            'phase': self.current_phase.value,
            'priority': 'normal',
            'action': 'hold',
            'target_position': None,
            'formation': None,
            'search_pattern': None
        }
        
        role = self.drone_assignments.get(drone.drone_id, 'assault')
        
        if self.current_phase == MissionPhase.DEPLOYMENT:
            orders.update(self._get_deployment_orders(drone, role))
            
        elif self.current_phase == MissionPhase.SEARCH:
            orders.update(self._get_search_orders(drone, role, simulation_step))
            
        elif self.current_phase == MissionPhase.ENGAGE:
            orders.update(self._get_engagement_orders(drone, target, role))
            
        elif self.current_phase == MissionPhase.EXTRACTION:
            orders.update(self._get_extraction_orders(drone, role))
        
        return orders
    
    def _create_phase_plan(self) -> Dict:
        """Create detailed phase plans based on mission objective"""
        base_phases = {
            MissionPhase.PREPARATION: {
                'description': 'Pre-mission checks and initialization',
                'duration_estimate': 50,
                'objectives': ['System checks', 'Route planning', 'Formation setup']
            },
            MissionPhase.DEPLOYMENT: {
                'description': 'Move to operational area',
                'duration_estimate': 100,
                'objectives': ['Reach deployment zone', 'Establish formation']
            },
            MissionPhase.SEARCH: {
                'description': 'Locate target',
                'duration_estimate': 200,
                'objectives': ['Systematic search', 'Target identification']
            },
            MissionPhase.ENGAGE: {
                'description': 'Engage target',
                'duration_estimate': 150,
                'objectives': ['Coordinate attack', 'Neutralize target']
            },
            MissionPhase.EXTRACTION: {
                'description': 'Return to base',
                'duration_estimate': 100,
                'objectives': ['Safe return', 'Mission debrief']
            }
        }
        
        # Modify based on mission type
        if self.mission_objective == MissionObjective.RECONNAISSANCE:
            base_phases[MissionPhase.ENGAGE]['description'] = 'Gather intelligence'
            base_phases[MissionPhase.ENGAGE]['objectives'] = ['Observe target', 'Collect data']
            
        return base_phases
    
    def _assign_drone_roles(self, drones: List) -> Dict:
        """Assign roles to drones based on mission and drone capabilities"""
        roles = {}
        
        if self.mission_objective == MissionObjective.SEARCH_AND_DESTROY:
            # Assign roles: leader, assault, support
            for i, drone in enumerate(drones):
                if i == 0:
                    roles[drone.drone_id] = 'leader'
                elif i < len(drones) * 0.7:
                    roles[drone.drone_id] = 'assault'
                else:
                    roles[drone.drone_id] = 'support'
                    
        elif self.mission_objective == MissionObjective.RECONNAISSANCE:
            # All drones as scouts
            for drone in drones:
                roles[drone.drone_id] = 'scout'
                
        elif self.mission_objective == MissionObjective.ESCORT:
            # Mixed roles for protection
            for i, drone in enumerate(drones):
                if i < 2:
                    roles[drone.drone_id] = 'escort'
                else:
                    roles[drone.drone_id] = 'guardian'
        
        self.drone_assignments = roles
        return roles
    
    def _divide_search_areas(self, drones: List) -> Dict:
        """Divide search area among drones"""
        search_areas = {}
        grid_size = int(np.sqrt(len(drones))) + 1
        
        for i, drone in enumerate(drones):
            grid_x = i % grid_size
            grid_y = i // grid_size
            
            area_width = 1080 // grid_size
            area_height = 720 // grid_size
            
            search_areas[drone.drone_id] = {
                'center': (grid_x * area_width + area_width/2, grid_y * area_height + area_height/2),
                'bounds': (grid_x * area_width, grid_y * area_height, area_width, area_height),
                'priority': 'normal'
            }
        
        return search_areas
    
    def _plan_coordination_points(self) -> List[Tuple[int, int]]:
        """Plan coordination waypoints for formation flying"""
        return [
            (270, 180),   # Formation point 1
            (540, 360),   # Center rally point
            (810, 540),   # Formation point 2
        ]
    
    def _plan_contingencies(self, drones: List) -> Dict:
        """Plan contingency responses"""
        return {
            'drone_loss': {
                'threshold': len(drones) * 0.5,
                'action': 'abort_mission'
            },
            'target_lost': {
                'action': 'expand_search'
            },
            'heavy_resistance': {
                'action': 'coordinate_attack'
            }
        }
    
    def _drones_deployed(self, drones: List) -> bool:
        """Check if all drones are deployed"""
        return all(np.linalg.norm(drone.position - np.array([540, 360])) < 200 for drone in drones if drone.alive)
    
    def _get_deployment_orders(self, drone, role: str) -> Dict:
        """Get deployment phase orders"""
        return {
            'action': 'move_to_formation',
            'target_position': (540, 360),  # Center of screen
            'priority': 'high',
            'formation': 'v_formation' if role == 'leader' else 'follow_leader'
        }
    
    def _get_search_orders(self, drone, role: str, simulation_step: int) -> Dict:
        """Get search phase orders"""
        if role == 'leader':
            pattern = SearchPattern.SPIRAL
        elif role == 'scout':
            pattern = SearchPattern.GRID
        else:
            pattern = SearchPattern.SWEEP
            
        return {
            'action': 'search',
            'search_pattern': pattern.value,
            'priority': 'normal',
            'target_position': tuple(self.pattern_generator.generate_search_pattern(pattern, drone, simulation_step))
        }
    
    def _get_engagement_orders(self, drone, target, role: str) -> Dict:
        """Get engagement phase orders"""
        if not target:
            return {'action': 'hold', 'priority': 'normal'}
            
        return {
            'action': 'attack',
            'target_position': (target.position[0], target.position[1]),
            'priority': 'high',
            'formation': 'attack_formation' if role in ['assault', 'leader'] else 'support_formation'
        }
    
    def _get_extraction_orders(self, drone, role: str) -> Dict:
        """Get extraction phase orders"""
        return {
            'action': 'return_to_base',
            'priority': 'high',
            'formation': 'return_formation'
        }
    
    def get_mission_status(self, drones: List, target=None) -> Dict:
        """Get comprehensive mission status"""
        active_drones = [d for d in drones if d.alive]
        landed_drones = [d for d in drones if getattr(d, 'has_landed', False)]
        
        return {
            'phase': self.current_phase.value,
            'objective': self.mission_objective.value,
            'drones_active': len(active_drones),
            'drones_total': len(drones),
            'drones_landed': len(landed_drones),
            'target_status': 'destroyed' if target and getattr(target, 'destroyed', False) else 'active',
            'mission_progress': self._calculate_mission_progress(drones, target),
            'estimated_completion': self._estimate_completion_time()
        }
    
    def _calculate_mission_progress(self, drones: List, target=None) -> float:
        """Calculate overall mission progress percentage"""
        phase_weights = {
            MissionPhase.PREPARATION: 0.1,
            MissionPhase.DEPLOYMENT: 0.2,
            MissionPhase.SEARCH: 0.3,
            MissionPhase.ENGAGE: 0.3,
            MissionPhase.EXTRACTION: 0.1
        }
        
        completed_weight = 0.0
        for phase in MissionPhase:
            if phase.value in [p.value for p in MissionPhase if p.value < self.current_phase.value]:
                completed_weight += phase_weights.get(phase, 0)
        
        # Add partial progress for current phase
        if self.current_phase == MissionPhase.EXTRACTION:
            landed_ratio = len([d for d in drones if getattr(d, 'has_landed', False)]) / len(drones)
            completed_weight += phase_weights[self.current_phase] * landed_ratio
        elif self.current_phase == MissionPhase.ENGAGE and target:
            if getattr(target, 'destroyed', False):
                completed_weight += phase_weights[self.current_phase]
        
        return min(completed_weight * 100, 100.0)
    
    def _estimate_completion_time(self) -> int:
        """Estimate remaining simulation steps to completion"""
        phase_estimates = {
            MissionPhase.PREPARATION: 50,
            MissionPhase.DEPLOYMENT: 100,
            MissionPhase.SEARCH: 200,
            MissionPhase.ENGAGE: 150,
            MissionPhase.EXTRACTION: 100,
            MissionPhase.COMPLETE: 0
        }
        
        remaining_time = 0
        current_found = False
        
        for phase in MissionPhase:
            if phase == self.current_phase:
                current_found = True
                remaining_time += phase_estimates.get(phase, 0) // 2  # Assume half completed
            elif current_found and phase != MissionPhase.COMPLETE:
                remaining_time += phase_estimates.get(phase, 0)
        
        return remaining_time