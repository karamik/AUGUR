import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "AUGUR API"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_agent():
    agent_data = {
        "name": "test-agent",
        "agent_type": "test",
        "environment": "testing",
        "metadata": {"test": True}
    }
    
    response = client.post("/api/v1/agents/", json=agent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-agent"
    assert "id" in data

def test_list_agents():
    response = client.get("/api/v1/agents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
