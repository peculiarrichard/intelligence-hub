from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from src.core.service import CoreIntelligenceService
from src.modules.router import router as modules_router
from src.events.bus import EventBus
from src.modules.task_module import TaskModule
from src.modules.chat_module import ChatModule
from src.modules.insight_module import InsightModule

event_bus = EventBus()
core_service = CoreIntelligenceService(event_bus)

task_module = TaskModule(event_bus, core_service)
chat_module = ChatModule(event_bus, core_service)
insight_module = InsightModule(event_bus, core_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await core_service.initialize()
    
    await task_module.register()
    await chat_module.register() 
    await insight_module.register()
    
    asyncio.create_task(task_module.start_listening())
    asyncio.create_task(chat_module.start_listening())
    asyncio.create_task(insight_module.start_listening())
    
    print("Core Intelligence Service started with 3 mock modules!")
    yield
    print("Core Intelligence Service stopped!")

app = FastAPI(
    title="Universal Intelligence Hub",
    description="Event-driven backend for modular intelligence orchestration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_core_service() -> CoreIntelligenceService:
    return core_service

def get_event_bus() -> EventBus:
    return event_bus

app.include_router(modules_router, prefix="/api/v1", tags=["modules"])

@app.get("/")
async def root():
    return {
        "message": "Universal Intelligence Hub API",
        "version": "1.0.0",
        "status": "operational",
        "architecture": "event-driven"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "core_intelligence"}

@app.post("/simulate/task-creation")
async def simulate_task_creation():
    """Endpoint to simulate task creation and event flow"""
    return await task_module.create_task({
        "title": "Test Task from API",
        "description": "This task was created via API call",
        "priority": "high",
        "user_id": "api_user_123"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)