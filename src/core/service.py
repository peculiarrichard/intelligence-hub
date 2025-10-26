from typing import Dict, List, Optional
from uuid import UUID
import asyncio

from src.core.models import (
    ModuleRegistration, 
    IntelligenceEvent, 
    IntelligenceResponse,
    ModuleResponse,
    EventType
)
from src.events.bus import EventBus
from src.shared.context import SharedContext

class CoreIntelligenceService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.registered_modules: Dict[UUID, ModuleRegistration] = {}
        self.shared_context = SharedContext()
        self.event_handlers = {}

    async def initialize(self):
        """Initialize the core service and set up event handlers"""
        self._setup_event_handlers()
        for event_type in EventType:
            self.event_bus.subscribe(event_type, self._handle_incoming_event)

    def _setup_event_handlers(self):
        """Register event handlers for different event types"""
        self.event_handlers = {
            EventType.TASK_CREATED: self._handle_task_event,
            EventType.MESSAGE_RECEIVED: self._handle_message_event,
            EventType.INSIGHT_GENERATED: self._handle_insight_event,
            EventType.USER_ACTIVITY: self._handle_user_activity,
            EventType.MODULE_REGISTERED: self._handle_module_registration,
        }

    async def register_module(self, registration: ModuleRegistration) -> ModuleRegistration:
        """Register a new module with the core service"""
        self.registered_modules[registration.module_id] = registration
        
        event = IntelligenceEvent(
            event_type=EventType.MODULE_REGISTERED,
            source_module=registration.module_id,
            payload={
                "module_name": registration.name,
                "module_type": registration.module_type,
                "capabilities": registration.capabilities
            }
        )
        
        await self.event_bus.publish(event)
        print(f"Module registered: {registration.name} ({registration.module_type})")
        return registration

    async def _handle_incoming_event(self, event: IntelligenceEvent):
        """Handle incoming events from the event bus"""
        print(f"Core Service processing event: {event.event_type} from {event.source_module}")
        
        self.shared_context.update_from_event(event)
        
        response = await self.process_event(event)
        
        response_event = IntelligenceEvent(
            event_type=EventType.INTELLIGENCE_RESPONSE,
            source_module=event.source_module,
            payload=response.model_dump()
        )
        await self.event_bus.publish(response_event)
        
        print(f"Core Service completed processing event: {event.event_type}")

    async def process_event(self, event: IntelligenceEvent) -> IntelligenceResponse:
        """Process an incoming event and orchestrate module responses"""
        relevant_modules = self._get_relevant_modules(event)
        
        module_responses = await self._orchestrate_module_processing(event, relevant_modules)
        
        core_insights = await self._generate_core_insights(event, module_responses)
        
        return IntelligenceResponse(
            request_id=event.event_id,
            original_event=event,
            module_responses=module_responses,
            core_insights=core_insights
        )

    def _get_relevant_modules(self, event: IntelligenceEvent) -> List[ModuleRegistration]:
        """Determine which modules should process this event"""
        relevant_modules = []
        
        for module in self.registered_modules.values():
            if self._is_module_relevant(module, event):
                relevant_modules.append(module)
        
        return relevant_modules

    def _is_module_relevant(self, module: ModuleRegistration, event: IntelligenceEvent) -> bool:
        """Determine if a module is relevant for a given event"""
        if module.module_id == event.source_module:
            return False
            
        module_capabilities = set(module.capabilities)
        
        relevance_map = {
            EventType.TASK_CREATED: {"task_management", "automation", "analysis"},
            EventType.MESSAGE_RECEIVED: {"chat", "insights", "sentiment_analysis"},
            EventType.INSIGHT_GENERATED: {"insights", "knowledge_base", "analytics"},
            EventType.USER_ACTIVITY: {"analytics", "insights", "automation"},
        }
        
        relevant_capabilities = relevance_map.get(event.event_type, set())
        return bool(module_capabilities & relevant_capabilities)

    async def _orchestrate_module_processing(self, event: IntelligenceEvent, modules: List[ModuleRegistration]) -> List[ModuleResponse]:
        """Orchestrate parallel processing of event by relevant modules"""
        tasks = []
        for module in modules:
            task = self._process_with_module(event, module)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_responses = []
        for i, response in enumerate(responses):
            if not isinstance(response, Exception):
                successful_responses.append(response)
            else:
                print(f"Module {modules[i].name} failed: {response}")
        
        return successful_responses

    async def _process_with_module(self, event: IntelligenceEvent, module: ModuleRegistration) -> ModuleResponse:
        """Simulate processing an event with a specific module"""
        
        await asyncio.sleep(0.1)
        
        # Mock module intelligence based on module type
        mock_response = self._generate_mock_module_response(module, event)
        
        return ModuleResponse(
            module_id=module.module_id,
            module_name=module.name,
            response=mock_response
        )

    def _generate_mock_module_response(self, module: ModuleRegistration, event: IntelligenceEvent) -> Dict:
        """Generate mock responses based on module type and event"""
        base_response = {
            "processed": True,
            "confidence": 0.85,
            "context_used": list(self.shared_context.get_relevant_context(event).keys())[:3]
        }
        
        if module.module_type.value == "chat":
            return {
                **base_response,
                "suggested_responses": ["I understand your request.", "Let me help with that."],
                "sentiment": "positive",
                "urgency": "medium"
            }
        elif module.module_type.value == "tasks":
            return {
                **base_response,
                "estimated_completion_time": "2 hours",
                "priority": "high",
                "dependencies": []
            }
        elif module.module_type.value == "insights":
            return {
                **base_response,
                "key_insights": ["Pattern detected in user behavior", "Opportunity for automation"],
                "recommendations": ["Consider automating this workflow"],
                "correlation_strength": 0.75
            }
        
        return base_response

    async def _generate_core_insights(self, event: IntelligenceEvent, responses: List[ModuleResponse]) -> Dict:
        """Generate core insights by synthesizing module responses"""
        if not responses:
            return {"message": "No modules processed this event"}
        
        all_insights = []
        all_confidences = []
        
        for response in responses:
            if "key_insights" in response.response:
                all_insights.extend(response.response["key_insights"])
            if "confidence" in response.response:
                all_confidences.append(response.response["confidence"])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        return {
            "synthesized_insights": list(set(all_insights))[:5],
            "average_confidence": round(avg_confidence, 2),
            "modules_engaged": len(responses),
            "consensus_level": "high" if avg_confidence > 0.7 else "medium",
            "processing_time": "instant"
        }

    async def _handle_task_event(self, event: IntelligenceEvent):
        print(f"Core handling task event: {event.event_type}")

    async def _handle_message_event(self, event: IntelligenceEvent):
        print(f"Core handling message event: {event.event_type}")

    async def _handle_insight_event(self, event: IntelligenceEvent):
        print(f"Core handling insight event: {event.event_type}")

    async def _handle_user_activity(self, event: IntelligenceEvent):
        print(f"Core handling user activity: {event.event_type}")

    async def _handle_module_registration(self, event: IntelligenceEvent):
        print(f"New module registered: {event.payload.get('module_name')}")
    

    def get_module_stats(self) -> Dict:
        """Get statistics about registered modules"""
        return {
            "total_modules": len(self.registered_modules),
            "modules_by_type": {
                module_type.value: len([m for m in self.registered_modules.values() if m.module_type == module_type])
                for module_type in EventType
            },
            "active_capabilities": list(set(
                capability 
                for module in self.registered_modules.values() 
                for capability in module.capabilities
            ))
        }