"""State management for the simulation"""
from enum import Enum
from typing import Dict, Any, List
import json
import time

class SimulationState(Enum):
    """Possible simulation states"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    RESETTING = "resetting"
    ERROR = "error"

class StateManager:
    """Manages the overall state of the simulation"""
    
    def __init__(self):
        self.current_state = SimulationState.STOPPED
        self.previous_state = SimulationState.STOPPED
        self.state_history = []
        self.state_data = {}
        self.listeners = {}
        self.start_time = None
        self.pause_time = None
        self.total_paused_time = 0
    
    def set_state(self, new_state: SimulationState, data: Dict[str, Any] = None):
        """Change the simulation state"""
        old_state = self.current_state
        self.previous_state = old_state
        self.current_state = new_state
        
        # Record state change
        state_change = {
            'timestamp': time.time(),
            'from_state': old_state.value,
            'to_state': new_state.value,
            'data': data or {}
        }
        self.state_history.append(state_change)
        
        # Handle specific state transitions
        if new_state == SimulationState.RUNNING:
            if old_state == SimulationState.STOPPED:
                self.start_time = time.time()
                self.total_paused_time = 0
            elif old_state == SimulationState.PAUSED and self.pause_time:
                self.total_paused_time += time.time() - self.pause_time
                self.pause_time = None
        
        elif new_state == SimulationState.PAUSED:
            self.pause_time = time.time()
        
        elif new_state == SimulationState.STOPPED:
            self.start_time = None
            self.pause_time = None
            self.total_paused_time = 0
        
        # Update state data
        if data:
            self.state_data.update(data)
        
        # Notify listeners
        self._notify_listeners(old_state, new_state, data)
    
    def get_state(self) -> SimulationState:
        """Get current simulation state"""
        return self.current_state
    
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.current_state == SimulationState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.current_state == SimulationState.PAUSED
    
    def is_stopped(self) -> bool:
        """Check if simulation is stopped"""
        return self.current_state == SimulationState.STOPPED
    
    def get_runtime(self) -> float:
        """Get total runtime in seconds (excluding paused time)"""
        if not self.start_time:
            return 0.0
        
        current_time = time.time()
        total_time = current_time - self.start_time
        
        # Subtract paused time
        paused_time = self.total_paused_time
        if self.pause_time:  # Currently paused
            paused_time += current_time - self.pause_time
        
        return max(0.0, total_time - paused_time)
    
    def add_state_listener(self, listener_id: str, callback):
        """Add a listener for state changes"""
        self.listeners[listener_id] = callback
    
    def remove_state_listener(self, listener_id: str):
        """Remove a state change listener"""
        if listener_id in self.listeners:
            del self.listeners[listener_id]
    
    def _notify_listeners(self, old_state: SimulationState, new_state: SimulationState, data: Dict[str, Any]):
        """Notify all listeners of state change"""
        for listener_id, callback in self.listeners.items():
            try:
                callback(old_state, new_state, data)
            except Exception as e:
                print(f"Error in state listener {listener_id}: {e}")
    
    def get_state_data(self, key: str = None):
        """Get state data"""
        if key:
            return self.state_data.get(key)
        return self.state_data.copy()
    
    def set_state_data(self, key: str, value: Any):
        """Set state data"""
        self.state_data[key] = value
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get history of state changes"""
        return self.state_history.copy()
    
    def clear_history(self):
        """Clear state history"""
        self.state_history.clear()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state"""
        return {
            'current_state': self.current_state.value,
            'previous_state': self.previous_state.value,
            'runtime': self.get_runtime(),
            'total_state_changes': len(self.state_history),
            'data_keys': list(self.state_data.keys())
        }