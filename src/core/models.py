from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4

class ModuleType(str, Enum):
    CHAT = "chat"
    TASKS = "tasks"
    INSIGHTS = "insights"
    AUTOMATION = "automation"
    THIRD_PARTY = "third_party"

class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    INSIGHT_GENERATED = "insight_generated"
    USER_ACTIVITY = "user_activity"
    MODULE_REGISTERED = "module_registered"
    INTELLIGENCE_RESPONSE = "intelligence_response"

class ModuleRegistration(BaseModel):
    module_id: UUID = Field(default_factory=uuid4)
    name: str
    module_type: ModuleType
    version: str
    description: str
    endpoint: str 
    capabilities: List[str]
    metadata: Dict[str, Any] = {}

class IntelligenceEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    source_module: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any]
    context: Dict[str, Any] = {}

class ModuleResponse(BaseModel):
    module_id: UUID
    module_name: str
    response: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class IntelligenceResponse(BaseModel):
    request_id: UUID
    original_event: IntelligenceEvent
    module_responses: List[ModuleResponse]
    core_insights: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)