from typing import Dict, Any
from uuid import uuid4
from datetime import datetime
import asyncio

from src.core.models import ModuleRegistration, IntelligenceEvent, EventType, ModuleType
from src.core.service import CoreIntelligenceService
from src.events.bus import EventBus

class ChatModule:
    """Mock Chat Module with event-based communication"""
    
    def __init__(self, event_bus: EventBus, core_service: CoreIntelligenceService):
        self.event_bus = event_bus
        self.core_service = core_service
        self.module_id = None
        self.name = "Smart Chat Assistant"
        self.version = "1.0.0"
        self.conversations_db = {}
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Setup event handlers for this module"""
        self.event_bus.subscribe(EventType.MESSAGE_RECEIVED, self._handle_message)
        self.event_bus.subscribe(EventType.INTELLIGENCE_RESPONSE, self._handle_intelligence_response)

    async def register(self):
        """Register this module with the core service"""
        registration = ModuleRegistration(
            name=self.name,
            module_type=ModuleType.CHAT,
            version=self.version,
            description="AI-powered chat with context awareness and event-driven architecture",
            endpoint="chat-module/internal/events",
            capabilities=["chat", "sentiment_analysis", "context_awareness", "response_suggestion"]
        )
        registered_module = await self.core_service.register_module(registration)
        self.module_id = registered_module.module_id
        print(f"Chat Module registered with ID: {self.module_id}")
        return registered_module

    async def start_listening(self):
        """Start listening for events"""
        print("Chat Module started listening for events...")

    async def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message and publish event"""
        message_id = str(uuid4())
        conversation_id = message_data.get("conversation_id", str(uuid4()))
        
        message = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "content": message_data["content"],
            "sender": message_data.get("sender", "user"),
            "timestamp": datetime.now().isoformat(),
            "metadata": message_data.get("metadata", {})
        }
        
        if conversation_id not in self.conversations_db:
            self.conversations_db[conversation_id] = []
        self.conversations_db[conversation_id].append(message)
        
        event = IntelligenceEvent(
            event_type=EventType.MESSAGE_RECEIVED,
            source_module=self.module_id,
            payload=message,
            context={
                "user_id": message_data.get("user_id"),
                "conversation_context": self._get_conversation_context(conversation_id)
            }
        )
        
        await self.event_bus.publish(event)
        print(f"Chat Module published MESSAGE_RECEIVED event: {message_id}")
        
        return {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "status": "sent",
            "event_id": str(event.event_id)
        }

    async def _handle_message(self, event: IntelligenceEvent):
        """Handle incoming message events"""
        if event.source_module != self.module_id:
            message_data = event.payload
            print(f"Chat Module processing external message: {message_data.get('message_id')}")
            
            await asyncio.sleep(0.1)
            
            response_event = IntelligenceEvent(
                event_type=EventType.MESSAGE_SENT,
                source_module=self.module_id,
                payload={
                    "response_to": message_data.get("message_id"),
                    "content": "I understand your message. Let me help you with that.",
                    "sender": "assistant",
                    "conversation_id": message_data.get("conversation_id")
                }
            )
            await self.event_bus.publish(response_event)

    async def _handle_intelligence_response(self, event: IntelligenceEvent):
        """Handle responses from core intelligence service"""
        response_data = event.payload
        print(f"Chat Module received intelligence response")
        
        insights = response_data.get('core_insights', {})
        if 'synthesized_insights' in insights:
            print(f"Chat insights: {insights['synthesized_insights']}")

    def _get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """Get context for a conversation"""
        if conversation_id in self.conversations_db:
            messages = self.conversations_db[conversation_id][-5:]
            return {
                "message_count": len(messages),
                "recent_senders": list(set(msg['sender'] for msg in messages)),
                "last_activity": messages[-1]['timestamp'] if messages else None
            }
        return {}

    def get_chat_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        total_messages = sum(len(conv) for conv in self.conversations_db.values())
        return {
            "total_conversations": len(self.conversations_db),
            "total_messages": total_messages,
            "module_id": str(self.module_id),
            "module_name": self.name
        }