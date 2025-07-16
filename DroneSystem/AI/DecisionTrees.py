from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import numpy as np

class DecisionResult(Enum):
    CONTINUE_SEARCH = "continue_search"
    ENGAGE_TARGET = "engage_target"
    RETURN_TO_BASE = "return_to_base"
    AVOID_OBSTACLE = "avoid_obstacle"
    FORM_UP = "form_up"
    SUPPORT_ALLY = "support_ally"
    ABORT_MISSION = "abort_mission"

class DecisionNode:
    def __init__(self, condition: Callable, true_action: Any, false_action: Any, name: str = ""):
        self.condition = condition
        self.true_action = true_action
        self.false_action = false_action
        self.name = name
    
    def evaluate(self, context: Dict) -> Any:
        """Evaluate the decision node and return the appropriate action"""
        if self.condition(context):
            if isinstance(self.true_action, DecisionNode):
                return self.true_action.evaluate(context)
            return self.true_action
        else:
            if isinstance(self.false_action, DecisionNode):
                return self.false_action.evaluate(context)
            return self.false_action

class DecisionTrees:
    def __init__(self):
        self.combat_tree = self._build_combat_decision_tree()
        self.search_tree = self._build_search_decision_tree()
        self.survival_tree = self._build_survival_decision_tree()
        self.formation_tree = self._build_formation_decision_tree()
    
    def make_combat_decision(self, drone, target, obstacles: List, other_drones: List) -> DecisionResult:
        """Make combat-related decisions"""
        context = {
            'drone': drone,
            'target': target,
            'obstacles': obstacles,
            'other_drones': other_drones,
            'distance_to_target': self._distance_to_target(drone, target),
            'fuel_level': getattr(drone, 'fuel', 100),
            'missiles_remaining': drone.max_missiles - drone.missiles_fired,
            'health': 100 if drone.alive else 0
        }
        
        return self.combat_tree.evaluate(context)
    
    def make_search_decision(self, drone, target, simulation_step: int) -> DecisionResult:
        """Make search-related decisions"""
        context = {
            'drone': drone,
            'target': target,
            'simulation_step': simulation_step,
            'target_visible': target and not getattr(target, 'hidden', False),
            'target_in_radar': target and getattr(target, 'spotted_by_radar', False),
            'search_time': getattr(drone, 'search_time', 0)
        }
        
        return self.search_tree.evaluate(context)
    
    def make_survival_decision(self, drone, threats: List, obstacles: List) -> DecisionResult:
        """Make survival/evasion decisions"""
        context = {
            'drone': drone,
            'threats': threats,
            'obstacles': obstacles,
            'health': 100 if drone.alive else 0,
            'nearest_threat_distance': self._get_nearest_threat_distance(drone, threats),
            'escape_routes': self._count_escape_routes(drone, obstacles)
        }
        
        return self.survival_tree.evaluate(context)
    
    def make_formation_decision(self, drone, other_drones: List, leader=None) -> DecisionResult:
        """Make formation flying decisions"""
        context = {
            'drone': drone,
            'other_drones': other_drones,
            'leader': leader,
            'is_leader': leader is None or drone == leader,
            'formation_integrity': self._calculate_formation_integrity(drone, other_drones),
            'distance_to_leader': self._distance_to_leader(drone, leader) if leader else 0
        }
        
        return self.formation_tree.evaluate(context)
    
    def _build_combat_decision_tree(self) -> DecisionNode:
        """Build the combat decision tree"""
        
        # Leaf nodes (final decisions)
        engage_target = DecisionResult.ENGAGE_TARGET
        return_to_base = DecisionResult.RETURN_TO_BASE
        avoid_obstacle = DecisionResult.AVOID_OBSTACLE
        continue_search = DecisionResult.CONTINUE_SEARCH
        
        # Decision nodes
        missiles_available = DecisionNode(
            condition=lambda ctx: ctx['missiles_remaining'] > 0,
            true_action=engage_target,
            false_action=return_to_base,
            name="missiles_available"
        )
        
        in_attack_range = DecisionNode(
            condition=lambda ctx: ctx['distance_to_target'] < 100,
            true_action=missiles_available,
            false_action=continue_search,
            name="in_attack_range"
        )
        
        target_visible = DecisionNode(
            condition=lambda ctx: ctx['target'] and not getattr(ctx['target'], 'hidden', False),
            true_action=in_attack_range,
            false_action=continue_search,
            name="target_visible"
        )
        
        drone_healthy = DecisionNode(
            condition=lambda ctx: ctx['health'] > 20,
            true_action=target_visible,
            false_action=return_to_base,
            name="drone_healthy"
        )
        
        return drone_healthy
    
    def _build_search_decision_tree(self) -> DecisionNode:
        """Build the search decision tree"""
        
        engage_target = DecisionResult.ENGAGE_TARGET
        continue_search = DecisionResult.CONTINUE_SEARCH
        return_to_base = DecisionResult.RETURN_TO_BASE
        
        search_timeout = DecisionNode(
            condition=lambda ctx: ctx['search_time'] < 500,  # Max search time
            true_action=continue_search,
            false_action=return_to_base,
            name="search_timeout"
        )
        
        target_spotted = DecisionNode(
            condition=lambda ctx: ctx['target_visible'] or ctx['target_in_radar'],
            true_action=engage_target,
            false_action=search_timeout,
            name="target_spotted"
        )
        
        return target_spotted
    
    def _build_survival_decision_tree(self) -> DecisionNode:
        """Build the survival decision tree"""
        
        avoid_obstacle = DecisionResult.AVOID_OBSTACLE
        abort_mission = DecisionResult.ABORT_MISSION
        continue_search = DecisionResult.CONTINUE_SEARCH
        
        escape_available = DecisionNode(
            condition=lambda ctx: ctx['escape_routes'] > 0,
            true_action=avoid_obstacle,
            false_action=abort_mission,
            name="escape_available"
        )
        
        immediate_danger = DecisionNode(
            condition=lambda ctx: ctx['nearest_threat_distance'] < 30,
            true_action=escape_available,
            false_action=continue_search,
            name="immediate_danger"
        )
        
        health_critical = DecisionNode(
            condition=lambda ctx: ctx['health'] > 10,
            true_action=immediate_danger,
            false_action=abort_mission,
            name="health_critical"
        )
        
        return health_critical
    
    def _build_formation_decision_tree(self) -> DecisionNode:
        """Build the formation flying decision tree"""
        
        form_up = DecisionResult.FORM_UP
        support_ally = DecisionResult.SUPPORT_ALLY
        continue_search = DecisionResult.CONTINUE_SEARCH
        
        formation_broken = DecisionNode(
            condition=lambda ctx: ctx['formation_integrity'] > 0.6,
            true_action=continue_search,
            false_action=form_up,
            name="formation_broken"
        )
        
        too_far_from_leader = DecisionNode(
            condition=lambda ctx: ctx['distance_to_leader'] < 100,
            true_action=formation_broken,
            false_action=form_up,
            name="too_far_from_leader"
        )
        
        is_leader_check = DecisionNode(
            condition=lambda ctx: ctx['is_leader'],
            true_action=formation_broken,
            false_action=too_far_from_leader,
            name="is_leader_check"
        )
        
        return is_leader_check
    
    def _distance_to_target(self, drone, target) -> float:
        """Calculate distance to target"""
        if not target:
            return float('inf')
        return np.linalg.norm(
            np.array([target.position[0], target.position[1]]) - drone.position
        )
    
    def _distance_to_leader(self, drone, leader) -> float:
        """Calculate distance to formation leader"""
        if not leader:
            return 0
        return np.linalg.norm(drone.position - leader.position)
    
    def _get_nearest_threat_distance(self, drone, threats: List) -> float:
        """Get distance to nearest threat"""
        if not threats:
            return float('inf')
        
        min_distance = float('inf')
        for threat in threats:
            if hasattr(threat, 'position'):
                distance = np.linalg.norm(
                    np.array(threat.position) - drone.position
                )
                min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _count_escape_routes(self, drone, obstacles: List) -> int:
        """Count available escape routes"""
        escape_routes = 0
        directions = [
            np.array([1, 0]),   # Right
            np.array([-1, 0]),  # Left
            np.array([0, 1]),   # Down
            np.array([0, -1])   # Up
        ]
        
        for direction in directions:
            # Check if path is clear in this direction
            test_pos = drone.position + direction * 50
            blocked = False
            
            for obstacle in obstacles:
                if hasattr(obstacle, 'contains') and obstacle.contains(
                    int(test_pos[0]), int(test_pos[1])
                ):
                    blocked = True
                    break
            
            if not blocked:
                escape_routes += 1
        
        return escape_routes
    
    def _calculate_formation_integrity(self, drone, other_drones: List) -> float:
        """Calculate how well the formation is maintained"""
        if not other_drones:
            return 1.0
        
        total_distance = 0
        count = 0
        ideal_distance = 40  # Ideal spacing between drones
        
        for other_drone in other_drones:
            if other_drone != drone and other_drone.alive:
                distance = np.linalg.norm(drone.position - other_drone.position)
                # Score based on how close to ideal distance
                score = max(0, 1 - abs(distance - ideal_distance) / ideal_distance)
                total_distance += score
                count += 1
        
        return total_distance / count if count > 0 else 1.0
    
    def get_decision_explanation(self, result: DecisionResult, context: Dict) -> str:
        """Get human-readable explanation of the decision"""
        explanations = {
            DecisionResult.CONTINUE_SEARCH: "Target not found, continuing search pattern",
            DecisionResult.ENGAGE_TARGET: f"Target detected at distance {context.get('distance_to_target', 'unknown')}, engaging",
            DecisionResult.RETURN_TO_BASE: "Mission complete or low resources, returning to base",
            DecisionResult.AVOID_OBSTACLE: "Obstacle detected, taking evasive action",
            DecisionResult.FORM_UP: "Formation broken, reforming with team",
            DecisionResult.SUPPORT_ALLY: "Team member needs assistance",
            DecisionResult.ABORT_MISSION: "Critical situation, aborting mission"
        }
        
        return explanations.get(result, "Unknown decision")
    
    def get_tree_visualization(self, tree_name: str) -> Dict:
        """Get a visualization of the decision tree structure"""
        trees = {
            'combat': self.combat_tree,
            'search': self.search_tree,
            'survival': self.survival_tree,
            'formation': self.formation_tree
        }
        
        if tree_name not in trees:
            return {}
        
        def visualize_node(node, depth=0):
            if isinstance(node, DecisionResult):
                return {'type': 'result', 'value': node.value, 'depth': depth}
            
            return {
                'type': 'decision',
                'name': node.name,
                'depth': depth,
                'true_branch': visualize_node(node.true_action, depth + 1),
                'false_branch': visualize_node(node.false_action, depth + 1)
            }
        
        return visualize_node(trees[tree_name])