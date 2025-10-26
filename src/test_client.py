import asyncio
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def test_event_based_flow():
    """Test the event-based intelligence hub"""
    
    print("🚀 Testing Event-Based Universal Intelligence Hub\n")
    
    # 1. Check health
    print("1. Checking service health...")
    response = requests.get("http://localhost:8000/health")
    print(f"   Health: {response.json()}\n")
    
    # 2. Get module statistics
    print("2. Checking module registrations...")
    response = requests.get(f"{BASE_URL}/modules/stats")
    stats = response.json()
    print(f"   Module Stats: {stats}\n")
    
    # 3. Simulate task creation (triggers event flow)
    print("3. Simulating task creation event...")
    response = requests.post("http://localhost:8000/simulate/task-creation")
    result = response.json()
    print(f"   Task Creation Result: {result}\n")
    
    # 4. Check event statistics
    print("4. Checking event flow statistics...")
    response = requests.get(f"{BASE_URL}/events/stats")
    event_stats = response.json()
    print(f"   Event Stats: {event_stats}\n")
    
    # 5. Check context statistics
    print("5. Checking shared context...")
    response = requests.get(f"{BASE_URL}/context/stats")
    context_stats = response.json()
    print(f"   Context Stats: {context_stats}\n")
    
    # 6. Check individual module stats
    print("6. Checking individual module states...")
    modules_response = requests.get(f"{BASE_URL}/modules")
    modules = modules_response.json()
    print(f"   Registered Modules:")
    for module in modules:
        print(f"     - {module['name']} ({module['module_type']})")
    
    print("\n✅ Event flow test completed! Check logs for event processing details.")

if __name__ == "__main__":
    test_event_based_flow()