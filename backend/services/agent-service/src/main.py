from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

app = FastAPI(title="Agent Service")

# База данных в памяти (потом заменим на PostgreSQL)
agents_db = {}

class AgentCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class Agent(AgentCreate):
    id: str
    status: str = "inactive"
    created_at: datetime
    last_active: Optional[datetime] = None

@app.get("/")
async def root():
    return {
        "service": "Agent Service",
        "status": "running",
        "agents_count": len(agents_db)
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "agent-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents")
async def create_agent(agent: AgentCreate):
    agent_id = str(uuid.uuid4())
    new_agent = {
        "id": agent_id,
        "name": agent.name,
        "type": agent.type,
        "description": agent.description,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }
    agents_db[agent_id] = new_agent
    return new_agent

@app.get("/agents")
async def list_agents():
    return list(agents_db.values())

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id not in agents_db:
        return {"error": "Agent not found"}
    return agents_db[agent_id]
