from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from src.core.service import CoreIntelligenceService
from src.core.models import (
    ModuleRegistration, 
    ModuleType
)
from src.events.bus import EventBus, get_event_bus

router = APIRouter()

def get_core_service() -> CoreIntelligenceService:
    from src.main import core_service
    return core_service

@router.post("/modules/register", response_model=ModuleRegistration)
async def register_module(
    registration: ModuleRegistration,
    core_service: CoreIntelligenceService = Depends(get_core_service)
):
    """Register a new module with the core intelligence service"""
    return await core_service.register_module(registration)

@router.get("/modules", response_model=List[ModuleRegistration])
async def list_modules(
    core_service: CoreIntelligenceService = Depends(get_core_service)
):
    """List all registered modules"""
    return list(core_service.registered_modules.values())

@router.get("/modules/stats")
async def get_module_stats(
    core_service: CoreIntelligenceService = Depends(get_core_service)
):
    """Get statistics about registered modules"""
    return core_service.get_module_stats()

@router.get("/events/stats")
async def get_event_stats(
    event_bus: EventBus = Depends(get_event_bus)
):
    """Get statistics about event flow"""
    return event_bus.get_event_stats()

@router.get("/context/stats")
async def get_context_stats(
    core_service: CoreIntelligenceService = Depends(get_core_service)
):
    """Get statistics about shared context"""
    return core_service.shared_context.get_context_stats()



# Pre-defined module examples
@router.post("/modules/register-examples")
async def register_example_modules(
    core_service: CoreIntelligenceService = Depends(get_core_service)
):
    """Register example modules for demonstration"""
    example_modules = [
        ModuleRegistration(
            name="Smart Chat Assistant",
            module_type=ModuleType.CHAT,
            version="1.0.0",
            description="AI-powered chat with context awareness",
            endpoint="https://chat-module.example.com/webhook",
            capabilities=["chat", "sentiment_analysis", "context_awareness"]
        ),
        ModuleRegistration(
            name="Task Intelligence Engine",
            module_type=ModuleType.TASKS,
            version="1.2.0",
            description="Smart task management and prioritization",
            endpoint="https://tasks-module.example.com/webhook",
            capabilities=["task_management", "prioritization", "automation"]
        ),
        ModuleRegistration(
            name="Insight Generator",
            module_type=ModuleType.INSIGHTS,
            version="2.1.0",
            description="Pattern recognition and insight generation",
            endpoint="https://insights-module.example.com/webhook",
            capabilities=["insights", "pattern_recognition", "analytics"]
        )
    ]
    
    registered = []
    for module in example_modules:
        result = await core_service.register_module(module)
        registered.append(result)
    
    return {"message": f"Registered {len(registered)} example modules", "modules": registered}