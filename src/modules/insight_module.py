from typing import Dict, Any
from uuid import uuid4
from datetime import datetime
import asyncio

from src.core.models import ModuleRegistration, IntelligenceEvent, EventType, ModuleType
from src.core.service import CoreIntelligenceService
from src.events.bus import EventBus

class InsightModule:
    """Mock Insight Module with event-based communication"""
    
    def __init__(self, event_bus: EventBus, core_service: CoreIntelligenceService):
        self.event_bus = event_bus
        self.core_service = core_service
        self.module_id = None
        self.name = "Insight Generator"
        self.version = "2.1.0"
        self.insights_db = {}
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers for this module"""
        self.event_bus.subscribe(EventType.TASK_CREATED, self._handle_task_event)
        self.event_bus.subscribe(EventType.MESSAGE_RECEIVED, self._handle_message_event)
        self.event_bus.subscribe(EventType.USER_ACTIVITY, self._handle_user_activity)

    async def register(self):
        """Register this module with the core service"""
        registration = ModuleRegistration(
            name=self.name,
            module_type=ModuleType.INSIGHTS,
            version=self.version,
            description="Pattern recognition and insight generation with event-driven architecture",
            endpoint="insight-module/internal/events",
            capabilities=["insights", "pattern_recognition", "analytics", "trend_analysis"]
        )
        registered_module = await self.core_service.register_module(registration)
        self.module_id = registered_module.module_id
        print(f"Insight Module registered with ID: {self.module_id}")
        return registered_module

    async def start_listening(self):
        """Start listening for events"""
        print("Insight Module started listening for events...")

    async def _handle_task_event(self, event: IntelligenceEvent):
        """Handle task-related events to generate insights"""
        task_data = event.payload
        print(f"Insight Module analyzing task: {task_data.get('task_id')}")
        
        await asyncio.sleep(0.2)
        
        insight_id = str(uuid4())
        insight = {
            "insight_id": insight_id,
            "type": "task_pattern",
            "source_event": str(event.event_id),
            "patterns": ["High-priority task created", "Similar tasks completed in 2-3 hours"],
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }
        self.insights_db[insight_id] = insight
        
        insight_event = IntelligenceEvent(
            event_type=EventType.INSIGHT_GENERATED,
            source_module=self.module_id,
            payload=insight,
            context={"original_event_id": str(event.event_id)}
        )
        await self.event_bus.publish(insight_event)

    async def _handle_message_event(self, event: IntelligenceEvent):
        """Handle message events to generate insights"""
        message_data = event.payload
        print(f"Insight Module analyzing message: {message_data.get('message_id')}")
        
        await asyncio.sleep(0.1)
        
        insight_id = str(uuid4())
        insight = {
            "insight_id": insight_id,
            "type": "communication_pattern",
            "source_event": str(event.event_id),
            "patterns": ["User seeking assistance", "Common support topic"],
            "sentiment": "neutral",
            "confidence": 0.78,
            "timestamp": datetime.now().isoformat()
        }
        self.insights_db[insight_id] = insight
        
        insight_event = IntelligenceEvent(
            event_type=EventType.INSIGHT_GENERATED,
            source_module=self.module_id,
            payload=insight
        )
        await self.event_bus.publish(insight_event)

    async def _handle_user_activity(self, event: IntelligenceEvent):
        """Handle user activity events"""
        activity_data = event.payload
        print(f"Insight Module analyzing user activity: {activity_data.get('user_id')}")
        
        insight_id = str(uuid4())
        insight = {
            "insight_id": insight_id,
            "type": "user_behavior",
            "user_id": activity_data.get('user_id'),
            "patterns": ["Active during business hours", "Prefers task-based workflow"],
            "recommendations": ["Schedule important tasks in morning"],
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
        self.insights_db[insight_id] = insight
        
        insight_event = IntelligenceEvent(
            event_type=EventType.INSIGHT_GENERATED,
            source_module=self.module_id,
            payload=insight
        )
        await self.event_bus.publish(insight_event)

    def get_insight_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        insight_types = {}
        for insight in self.insights_db.values():
            insight_type = insight.get('type', 'unknown')
            insight_types[insight_type] = insight_types.get(insight_type, 0) + 1
            
        return {
            "total_insights": len(self.insights_db),
            "insights_by_type": insight_types,
            "module_id": str(self.module_id),
            "module_name": self.name
        }