from typing import Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from src.core.models import ModuleRegistration, IntelligenceEvent, EventType, ModuleType
from src.core.service import CoreIntelligenceService
from src.events.bus import EventBus

class TaskModule:
    """Mock Task Management Module with event-based communication"""
    
    def __init__(self, event_bus: EventBus, core_service: CoreIntelligenceService):
        self.event_bus = event_bus
        self.core_service = core_service
        self.module_id = None
        self.name = "Task Intelligence Engine"
        self.version = "1.2.0"
        self.tasks_db = {}
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers for this module"""
        self.event_bus.subscribe(EventType.TASK_CREATED, self._handle_task_created)
        self.event_bus.subscribe(EventType.INTELLIGENCE_RESPONSE, self._handle_intelligence_response)
        self.event_bus.subscribe("task_analysis_complete", self._handle_task_analysis)

    async def register(self):
        """Register this module with the core service"""
        registration = ModuleRegistration(
            name=self.name,
            module_type=ModuleType.TASKS,
            version=self.version,
            description="Smart task management and prioritization with event-driven architecture",
            endpoint="task-module/internal/events",
            capabilities=["task_management", "prioritization", "automation", "analysis"]
        )
        registered_module = await self.core_service.register_module(registration)
        self.module_id = registered_module.module_id
        print(f"Task Module registered with ID: {self.module_id}")
        return registered_module

    async def start_listening(self):
        """Start listening for events (mock background process)"""
        print("Task Module started listening for events...")
        # In a real implementation, this would be a proper message consumer

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task and publish event (simulating internal module operation)"""
        task_id = str(uuid4())
        
        task = {
            "task_id": task_id,
            "title": task_data["title"],
            "description": task_data.get("description", ""),
            "priority": task_data.get("priority", "medium"),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "user_id": task_data.get("user_id", "unknown")
        }
        self.tasks_db[task_id] = task
        
        event = IntelligenceEvent(
            event_type=EventType.TASK_CREATED,
            source_module=self.module_id,
            payload=task,
            context={
                "user_id": task_data.get("user_id"),
                "source": "task_module"
            }
        )
        
        await self.event_bus.publish(event)
        print(f" Task Module published TASK_CREATED event for task: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "created",
            "message": "Task created and event published",
            "event_id": str(event.event_id)
        }

    async def _handle_task_created(self, event: IntelligenceEvent):
        """Handle task creation events (even from other modules)"""
        if event.source_module != self.module_id:
            task_data = event.payload
            print(f"🔄 Task Module processing external task: {task_data.get('task_id')}")
            
            await asyncio.sleep(0.1)
            
            analysis_event = IntelligenceEvent(
                event_type=EventType.INSIGHT_GENERATED,
                source_module=self.module_id,
                payload={
                    "type": "task_analysis",
                    "task_id": task_data.get("task_id"),
                    "insights": ["Task complexity: medium", "Estimated completion: 2 hours"],
                    "recommendations": ["Break into subtasks", "Set reminder for follow-up"]
                },
                context={"original_event_id": str(event.event_id)}
            )
            await self.event_bus.publish(analysis_event)

    async def _handle_intelligence_response(self, event: IntelligenceEvent):
        """Handle responses from core intelligence service"""
        response_data = event.payload
        original_event_id = response_data.get("original_event_id")
        
        print(f"Task Module received intelligence response for event {original_event_id}")
        print(f"Core insights: {response_data.get('core_insights', {})}")
        
        for task_id in self.tasks_db:
            if "task_analysis" in str(response_data.get('core_insights', {})):
                self.tasks_db[task_id]["last_insights"] = response_data.get('core_insights')

    async def _handle_task_analysis(self, event: IntelligenceEvent):
        """Handle custom task analysis events"""
        analysis_data = event.payload
        task_id = analysis_data.get("task_id")
        
        if task_id in self.tasks_db:
            self.tasks_db[task_id]["analysis"] = analysis_data
            print(f"Task Module updated analysis for task: {task_id}")

    def get_task_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        return {
            "total_tasks": len(self.tasks_db),
            "tasks_by_priority": {
                "high": len([t for t in self.tasks_db.values() if t.get("priority") == "high"]),
                "medium": len([t for t in self.tasks_db.values() if t.get("priority") == "medium"]),
                "low": len([t for t in self.tasks_db.values() if t.get("priority") == "low"])
            },
            "module_id": str(self.module_id),
            "module_name": self.name
        }