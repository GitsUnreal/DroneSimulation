"""
Event coordination and dispatching system
"""
from typing import Dict, List, Callable
from .UIEvents import UIEvent, UIEventType

class EventDispatcher:
    def __init__(self):
        self.listeners: Dict[UIEventType, List[Callable]] = {}
    
    def subscribe(self, event_type: UIEventType, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: UIEventType, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)
    
    def dispatch(self, event: UIEvent):
        """Dispatch an event to all listeners"""
        if event.event_type in self.listeners:
            for callback in self.listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
