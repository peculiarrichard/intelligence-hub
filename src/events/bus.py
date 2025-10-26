from typing import Dict, List, Callable, Any
from src.core.models import IntelligenceEvent


class EventBus:
    """Lightweight mock event bus for inter-module communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[IntelligenceEvent] = []
        self.max_history = 1000

    async def publish(self, event: IntelligenceEvent):
        """Publish an event to all subscribers"""
        print(f"Event published: {event.event_type} from {event.source_module}")
        
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        event_type = event.event_type.value
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    await callback(event)
                except Exception as e:
                    print(f"Error in event subscriber: {e}")

    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to events of a specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from events"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)

    def get_recent_events(self, limit: int = 10) -> List[IntelligenceEvent]:
        """Get recent events for debugging/monitoring"""
        return self.event_history[-limit:]

    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about event flow"""
        event_counts = {}
        for event in self.event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "events_by_type": event_counts,
            "active_subscribers": {
                event_type: len(callbacks) 
                for event_type, callbacks in self.subscribers.items()
            }
        }
    

def get_event_bus() -> EventBus:
    return EventBus()