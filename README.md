# Universal Intelligence Hub

A lightweight, event-driven backend service for modular intelligence orchestration.

Enable AI modules to communicate, share context, and collaborate through a central event bus

## Features

- Event-Driven Architecture - Pure event-based communication between modules
- Modular Intelligence - Independent AI modules with specialized capabilities
- Shared Context - Central intelligence state management across modules
- FastAPI Powered - High-performance async API with automatic OpenAPI docs
- Container Ready - Full Docker & Docker Compose support
- Real-time Monitoring - Built-in statistics and health checks
- Loose Coupling - Modules communicate without direct dependencies

## Architectural Decisions

### Hybrid Communication Pattern

- REST API for module registration and administrative tasks
- Event Bus for all inter-module communication and intelligence sharing

**Reasoning:** This approach provides optimal flexibility while maintaining clear separation of concerns.

### Modular Monolith with Event-Driven Core

- Single FastAPI application hosting all services
- Clear separation through dedicated classes and event boundaries
- Easy to extract into microservices when needed

**Benefits:**

- Reduced operational complexity
- Maintains clear domain boundaries
- Simplified testing and development
- Easy evolution to distributed architecture

## Module Registration & Event Flow

### Module Registration Process

**Module Initialization**
```python
task_module = TaskModule(event_bus, core_service)
```

**Automatic Registration**
```python
await task_module.register()
```

**Core Service Processing**

- Validates module capabilities
- Generates unique module ID
- Stores in module registry
- Broadcasts MODULE_REGISTERED event

### Supported Event Types

| Event Type | Source | Consumers | Purpose |
|------------|--------|-----------|---------|
| TASK_CREATED | Task Module | Core, Insights, Chat | New task notification |
| MESSAGE_RECEIVED | Chat Module | Core, Insights, Task | Incoming message processing |
| INSIGHT_GENERATED | Insight Module | Core, Task, Chat | Share generated insights |
| INTELLIGENCE_RESPONSE | Core Service | All Modules | Aggregated intelligence response |
| MODULE_REGISTERED | Core Service | All Modules | New module announcement |

## Service-to-Service Communication

### Event-Driven Communication Pattern

**Core Principle:** Modules never call each other directly. All communication happens through the event bus.

### Event Subscription Model
Each module subscribes to relevant event types:


### Intelligence Orchestration

The Core Service provides intelligent routing:

- Relevance Detection - Determines which modules should process each event
- Parallel Processing - Processes events through multiple modules concurrently
- Response Aggregation - Combines insights from all relevant modules
- Context Awareness - Maintains shared context across all interactions

### Fault Isolation

- Circuit Breaker Pattern - Modules process events independently
- Graceful Degradation - Failure in one module doesn't affect others
- Error Handling - Exceptions are caught and logged, not propagated

## Versioning & Scalability

### API Versioning Strategy

**Current Approach:** URL Path Versioning
```
/api/v1/modules/register
/api/v1/modules/stats
```

**Versioning Rules:**

- All breaking changes require a new version (v2, v3, etc.)
- Previous versions maintained during deprecation period
- Semantic versioning for module capabilities

### Scalability Strategy

#### 1. Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  intelligence-hub:
    scale: 3
    environment:
      - EVENT_BUS_TYPE=redis  # Switch to distributed event bus
```

#### 2. Event Bus Evolution

- Current: Mock in-memory event bus
- Stage 2: Redis Pub/Sub for distributed environments
- Stage 3: Apache Kafka for enterprise-scale deployments

#### 3. Database Scaling

- Module Data: Each module owns its database
- Shared Context: Redis Cluster for distributed caching
- Event Storage: Kafka with persistent log storage

#### 4. Performance Optimizations

- Async/await throughout the codebase
- Connection pooling for external services
- Cached context lookups
- Batched event processing

## Quick Start

### Prerequisites

- Python 3.11+ or Docker
- Git

### Local Development

**Clone and setup**
```bash
git clone <repository-url>
cd intelligence-hub

# Create virtual environment
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Run the service**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Access the application**

- API Server: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Docker Deployment

**Using Docker Compose**
```bash
docker-compose up -d
```

## API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/modules/register | POST | Register a new module |
| /api/v1/modules | GET | List all registered modules |
| /api/v1/modules/stats | GET | Get module statistics |
| /api/v1/events/stats | GET | Get event flow metrics |
| /api/v1/context/stats | GET | Get shared context information |
| /simulate/task-creation | POST | Simulate task creation event flow |


## Project Structure
```
intelligence-hub/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── service.py          # Core Intelligence Service
│   │   └── models.py           # Pydantic models
│   ├── modules/
│   │   ├── router.py           # Module REST API
│   │   ├── task_module.py      # Task management module
│   │   ├── chat_module.py      # Chat processing module
│   │   └── insight_module.py   # Insight generation module
│   ├── events/
│   │   ├── bus.py              # Mock event bus implementation
│   │   └── handlers.py         # Event handlers
│   └── shared/
│       └── context.py          # Shared intelligence context
├── tests/                      # Test suite
├── docker-compose.yml          # Multi-service setup
├── Dockerfile                  # Container definition
└── requirements.txt            # Python dependencies
```

## Testing

### Manual Testing

1. Start the service (see Quick Start)
2. Open API docs at http://localhost:8000/docs
3. Use the test endpoints to simulate event flows
4. Monitor logs to see event processing in real-time

## Docker Configuration

### Development
```bash
# Build and run with hot reload
docker-compose up --build

# View logs
docker-compose logs -f

## Monitoring & Observability

### Built-in Metrics

- Module Statistics: Registered modules and capabilities
- Event Flow: Event counts and processing times
- Context Metrics: Shared context size and usage
- Health Checks: Service status and dependencies

### Access Metrics
```bash
# Module statistics
curl http://localhost:8000/api/v1/modules/stats

# Event flow metrics
curl http://localhost:8000/api/v1/events/stats

# Context information
curl http://localhost:8000/api/v1/context/stats
```

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v1/modules/stats
```

## Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Documentation: This README and inline code comments
- Issues: GitHub Issues for bug reports and feature requests
- Discussion: GitHub Discussions for questions and ideas
- Examples: Test scripts and API examples included

---

Built using FastAPI and Event-Driven Architecture