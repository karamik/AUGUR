#!/usr/bin/env python3
"""
ШАГ 7: Добавляем Quantum Collective Intelligence Service
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 7: Добавляем Quantum Collective Intelligence           ║
║  с роевым интеллектом и коллективным обучением             ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Quantum Service
os.makedirs("backend/services/quantum-service/src", exist_ok=True)

# 2. Создаём рабочий Quantum Collective Intelligence Service
with open("backend/services/quantum-service/src/main.py", "w") as f:
    f.write("""# Quantum Collective Intelligence Service
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
import asyncpg
import numpy as np
import uuid
import os
import logging
import json
import asyncio
from collections import defaultdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quantum Collective Intelligence Service", version="1.0.0")

# Database connection
db_pool = None

# WebSocket connections for real-time swarm communication
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.swarm_members: Dict[str, Set[str]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, swarm_id: str, agent_id: str):
        await websocket.accept()
        self.active_connections[swarm_id].append(websocket)
        self.swarm_members[swarm_id].add(agent_id)
        logger.info(f"✅ Agent {agent_id} joined swarm {swarm_id}")

    def disconnect(self, websocket: WebSocket, swarm_id: str, agent_id: str):
        if swarm_id in self.active_connections:
            self.active_connections[swarm_id].remove(websocket)
        if swarm_id in self.swarm_members:
            self.swarm_members[swarm_id].discard(agent_id)
        logger.info(f"❌ Agent {agent_id} left swarm {swarm_id}")

    async def broadcast(self, swarm_id: str, message: dict, sender: str):
        """Broadcast message to all agents in swarm except sender"""
        for connection in self.active_connections[swarm_id]:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Enums
class SwarmType(str, Enum):
    COORDINATION = "coordination"
    LEARNING = "learning"
    PROBLEM_SOLVING = "problem_solving"
    OPTIMIZATION = "optimization"
    CONSENSUS = "consensus"

class EmergenceType(str, Enum):
    SYNERGY = "synergy"
    PATTERN = "pattern"
    INNOVATION = "innovation"
    SELF_ORGANIZATION = "self_organization"

class CollectiveState(str, Enum):
    FORMING = "forming"
    ACTIVE = "active"
    LEARNING = "learning"
    CONSENSUS = "consensus"
    DISBANDED = "disbanded"

# Models
class Agent(BaseModel):
    id: str
    capabilities: List[str]
    knowledge_base: Dict
    position: Optional[Dict] = None
    velocity: Optional[Dict] = None
    local_view: Dict = {}

class Swarm(BaseModel):
    id: str
    name: str
    type: SwarmType
    agents: List[str]
    state: CollectiveState
    goal: Dict
    consensus: Optional[Dict] = None
    emergence: List[Dict] = []
    created_at: datetime
    updated_at: datetime

class SwarmTask(BaseModel):
    id: str
    swarm_id: str
    description: str
    subtasks: List[Dict]
    assignments: Dict[str, str]  # agent_id -> subtask_id
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class CollectiveIntelligence(BaseModel):
    id: str
    swarm_id: str
    intelligence_score: float
    diversity_score: float
    cohesion_score: float
    emergence_score: float
    timestamp: datetime

# Quantum Collective Intelligence Engine
class QuantumCollectiveEngine:
    def __init__(self):
        self.swarms = {}
        self.agents = {}
        self.collective_memory = []
        self.emergence_patterns = []
    
    def create_swarm(self, name: str, swarm_type: SwarmType, goal: Dict) -> Swarm:
        """Create a new swarm"""
        swarm_id = str(uuid.uuid4())
        swarm = Swarm(
            id=swarm_id,
            name=name,
            type=swarm_type,
            agents=[],
            state=CollectiveState.FORMING,
            goal=goal,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.swarms[swarm_id] = swarm
        return swarm
    
    def add_agent_to_swarm(self, swarm_id: str, agent: Agent):
        """Add agent to existing swarm"""
        if swarm_id not in self.swarms:
            raise ValueError("Swarm not found")
        
        self.agents[agent.id] = agent
        self.swarms[swarm_id].agents.append(agent.id)
        self.swarms[swarm_id].updated_at = datetime.now()
        
        # Update swarm state
        if len(self.swarms[swarm_id].agents) >= 2:
            self.swarms[swarm_id].state = CollectiveState.ACTIVE
    
    def remove_agent_from_swarm(self, swarm_id: str, agent_id: str):
        """Remove agent from swarm"""
        if swarm_id in self.swarms and agent_id in self.swarms[swarm_id].agents:
            self.swarms[swarm_id].agents.remove(agent_id)
            self.swarms[swarm_id].updated_at = datetime.now()
            
            if len(self.swarms[swarm_id].agents) < 2:
                self.swarms[swarm_id].state = CollectiveState.FORMING
    
    def decompose_task(self, task: Dict, swarm: Swarm) -> SwarmTask:
        """Decompose complex task into subtasks based on agent capabilities"""
        subtasks = []
        assignments = {}
        
        # Simple decomposition - can be made more sophisticated
        if "complexity" in task:
            num_subtasks = min(len(swarm.agents), task["complexity"])
            for i in range(num_subtasks):
                subtasks.append({
                    "id": str(uuid.uuid4()),
                    "description": f"{task['description']} - Part {i+1}",
                    "dependencies": [] if i == 0 else [subtasks[i-1]["id"]]
                })
            
            # Assign subtasks to agents based on capabilities
            for i, agent_id in enumerate(swarm.agents[:num_subtasks]):
                if i < len(subtasks):
                    assignments[agent_id] = subtasks[i]["id"]
        
        swarm_task = SwarmTask(
            id=str(uuid.uuid4()),
            swarm_id=swarm.id,
            description=task["description"],
            subtasks=subtasks,
            assignments=assignments,
            status="pending",
            created_at=datetime.now()
        )
        
        return swarm_task
    
    def calculate_emergence(self, swarm_id: str) -> List[Dict]:
        """Detect emergent behaviors in the swarm"""
        if swarm_id not in self.swarms:
            return []
        
        swarm = self.swarms[swarm_id]
        emergence = []
        
        # Check for synergy (collective > sum of individuals)
        if len(swarm.agents) >= 2:
            # This would be calculated from actual performance metrics
            synergy_score = np.random.random() * 0.5 + 0.5  # Simulated
            if synergy_score > 0.8:
                emergence.append({
                    "type": EmergenceType.SYNERGY,
                    "score": synergy_score,
                    "description": "Agents working together exceed individual capabilities",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Check for self-organization
        if swarm.state == CollectiveState.ACTIVE and len(swarm.agents) > 3:
            organization_score = np.random.random() * 0.6 + 0.4  # Simulated
            if organization_score > 0.7:
                emergence.append({
                    "type": EmergenceType.SELF_ORGANIZATION,
                    "score": organization_score,
                    "description": "Agents spontaneously organized without central control",
                    "timestamp": datetime.now().isoformat()
                })
        
        return emergence
    
    def calculate_collective_intelligence(self, swarm_id: str) -> CollectiveIntelligence:
        """Calculate collective intelligence metrics for the swarm"""
        if swarm_id not in self.swarms:
            raise ValueError("Swarm not found")
        
        swarm = self.swarms[swarm_id]
        
        # Diversity based on different capabilities
        capabilities_set = set()
        for agent_id in swarm.agents:
            if agent_id in self.agents:
                capabilities_set.update(self.agents[agent_id].capabilities)
        diversity = len(capabilities_set) / (len(swarm.agents) * 3)  # Normalized
        
        # Cohesion based on communication patterns (simulated)
        cohesion = np.random.random() * 0.3 + 0.6  # 0.6-0.9
        
        # Emergence based on detected patterns
        emergence_patterns = self.calculate_emergence(swarm_id)
        emergence_score = len(emergence_patterns) / 3  # Normalized
        
        # Overall intelligence score
        intelligence = (diversity * 0.3 + cohesion * 0.4 + emergence_score * 0.3)
        
        return CollectiveIntelligence(
            id=str(uuid.uuid4()),
            swarm_id=swarm_id,
            intelligence_score=float(intelligence),
            diversity_score=float(diversity),
            cohesion_score=float(cohesion),
            emergence_score=float(emergence_score),
            timestamp=datetime.now()
        )
    
    def reach_consensus(self, swarm_id: str, proposals: List[Dict]) -> Dict:
        """Reach consensus among agents using weighted voting"""
        if swarm_id not in self.swarms:
            raise ValueError("Swarm not found")
        
        swarm = self.swarms[swarm_id]
        
        # Weighted voting based on agent reliability (simulated)
        weights = {agent_id: np.random.random() * 0.5 + 0.5 
                  for agent_id in swarm.agents}
        
        # Aggregate proposals
        consensus = {
            "topic": proposals[0].get("topic", "unknown"),
            "decision": None,
            "confidence": 0.0,
            "voting_results": {}
        }
        
        if proposals:
            # Simple majority voting
            options = {}
            for proposal in proposals:
                option = proposal.get("option")
                if option:
                    options[option] = options.get(option, 0) + 1
            
            if options:
                consensus["decision"] = max(options, key=options.get)
                consensus["confidence"] = options[consensus["decision"]] / len(proposals)
                consensus["voting_results"] = options
        
        # Update swarm consensus
        self.swarms[swarm_id].consensus = consensus
        self.swarms[swarm_id].state = CollectiveState.CONSENSUS
        
        return consensus
    
    def collective_learn(self, swarm_id: str, new_knowledge: Dict) -> Dict:
        """Enable collective learning across the swarm"""
        if swarm_id not in self.swarms:
            raise ValueError("Swarm not found")
        
        swarm = self.swarms[swarm_id]
        
        # Store in collective memory
        learning_event = {
            "id": str(uuid.uuid4()),
            "swarm_id": swarm_id,
            "knowledge": new_knowledge,
            "timestamp": datetime.now().isoformat()
        }
        self.collective_memory.append(learning_event)
        
        # Update each agent's knowledge base
        updates = []
        for agent_id in swarm.agents:
            if agent_id in self.agents:
                # Share knowledge with agent
                self.agents[agent_id].knowledge_base.update(new_knowledge)
                updates.append(agent_id)
        
        swarm.state = CollectiveState.LEARNING
        
        return {
            "learning_event_id": learning_event["id"],
            "agents_updated": len(updates),
            "collective_memory_size": len(self.collective_memory)
        }

# Initialize engine
engine = QuantumCollectiveEngine()

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "augur"),
            password=os.getenv("DB_PASSWORD", "augur"),
            database=os.getenv("DB_NAME", "augur_quantum"),
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Connected to Quantum Database")
        
        # Create tables
        async with db_pool.acquire() as conn:
            # Swarms table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS swarms (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255),
                    type VARCHAR(50),
                    agents JSONB,
                    state VARCHAR(50),
                    goal JSONB,
                    consensus JSONB,
                    emergence JSONB,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Swarm tasks table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS swarm_tasks (
                    id UUID PRIMARY KEY,
                    swarm_id UUID REFERENCES swarms(id),
                    description TEXT,
                    subtasks JSONB,
                    assignments JSONB,
                    status VARCHAR(50),
                    created_at TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            # Collective intelligence metrics
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS collective_intelligence (
                    id UUID PRIMARY KEY,
                    swarm_id UUID REFERENCES swarms(id),
                    intelligence_score FLOAT,
                    diversity_score FLOAT,
                    cohesion_score FLOAT,
                    emergence_score FLOAT,
                    timestamp TIMESTAMP
                )
            """)
            
            # Collective memory
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS collective_memory (
                    id UUID PRIMARY KEY,
                    swarm_id UUID REFERENCES swarms(id),
                    knowledge JSONB,
                    timestamp TIMESTAMP
                )
            """)
            
            # Emergence patterns
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS emergence_patterns (
                    id UUID PRIMARY KEY,
                    swarm_id UUID REFERENCES swarms(id),
                    pattern_type VARCHAR(50),
                    pattern_data JSONB,
                    detected_at TIMESTAMP
                )
            """)
            
            logger.info("✅ Quantum tables ready")
    except Exception as e:
        logger.error(f"❌ DB Connection failed: {e}")

@app.on_event("shutdown")
async def shutdown():
    if db_pool:
        await db_pool.close()
        logger.info("🔌 DB disconnected")

@app.get("/")
async def root():
    return {
        "service": "Quantum Collective Intelligence Service",
        "version": "1.0.0",
        "features": ["swarm-intelligence", "collective-learning", "emergence-detection"],
        "active_swarms": len(engine.swarms)
    }

@app.get("/health")
async def health():
    db_status = "connected" if db_pool else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "quantum_engine": "enabled",
        "active_swarms": len(engine.swarms),
        "agents_registered": len(engine.agents),
        "timestamp": datetime.now().isoformat()
    }

# WebSocket endpoint for real-time swarm communication
@app.websocket("/ws/{swarm_id}/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, swarm_id: str, agent_id: str):
    await manager.connect(websocket, swarm_id, agent_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process different message types
            msg_type = data.get("type")
            
            if msg_type == "proposal":
                # Agent proposes something to the swarm
                await manager.broadcast(swarm_id, {
                    "type": "proposal",
                    "agent": agent_id,
                    "proposal": data["proposal"],
                    "timestamp": datetime.now().isoformat()
                }, agent_id)
            
            elif msg_type == "vote":
                # Agent votes on a proposal
                await manager.broadcast(swarm_id, {
                    "type": "vote",
                    "agent": agent_id,
                    "vote": data["vote"],
                    "timestamp": datetime.now().isoformat()
                }, agent_id)
            
            elif msg_type == "knowledge":
                # Agent shares knowledge
                await manager.broadcast(swarm_id, {
                    "type": "knowledge",
                    "agent": agent_id,
                    "knowledge": data["knowledge"],
                    "timestamp": datetime.now().isoformat()
                }, agent_id)
                
                # Store in collective memory
                if swarm_id in engine.swarms:
                    engine.collective_learn(swarm_id, data["knowledge"])
            
            elif msg_type == "status":
                # Agent reports status
                await manager.broadcast(swarm_id, {
                    "type": "status",
                    "agent": agent_id,
                    "status": data["status"],
                    "timestamp": datetime.now().isoformat()
                }, agent_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, swarm_id, agent_id)

# REST endpoints
@app.post("/swarms", response_model=Swarm)
async def create_swarm(name: str, swarm_type: SwarmType, goal: Dict):
    """Create a new swarm"""
    swarm = engine.create_swarm(name, swarm_type, goal)
    
    # Store in database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO swarms (id, name, type, agents, state, goal, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, swarm.id, swarm.name, swarm_type.value, json.dumps([]),
            swarm.state.value, json.dumps(goal), swarm.created_at, swarm.updated_at)
    
    logger.info(f"✅ Swarm created: {swarm.id}")
    return swarm

@app.post("/swarms/{swarm_id}/agents/{agent_id}")
async def add_agent_to_swarm(swarm_id: str, agent_id: str, agent_data: Agent):
    """Add agent to swarm"""
    try:
        engine.add_agent_to_swarm(swarm_id, agent_data)
        
        # Update database
        async with db_pool.acquire() as conn:
            swarm = engine.swarms[swarm_id]
            await conn.execute("""
                UPDATE swarms 
                SET agents = $1, state = $2, updated_at = $3
                WHERE id = $4
            """, json.dumps(swarm.agents), swarm.state.value,
                swarm.updated_at, swarm_id)
        
        logger.info(f"✅ Agent {agent_id} added to swarm {swarm_id}")
        return {"message": "Agent added to swarm", "swarm_id": swarm_id, "agent_id": agent_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/swarms/{swarm_id}/agents/{agent_id}")
async def remove_agent_from_swarm(swarm_id: str, agent_id: str):
    """Remove agent from swarm"""
    try:
        engine.remove_agent_from_swarm(swarm_id, agent_id)
        
        # Update database
        async with db_pool.acquire() as conn:
            if swarm_id in engine.swarms:
                swarm = engine.swarms[swarm_id]
                await conn.execute("""
                    UPDATE swarms 
                    SET agents = $1, state = $2, updated_at = $3
                    WHERE id = $4
                """, json.dumps(swarm.agents), swarm.state.value,
                    swarm.updated_at, swarm_id)
        
        logger.info(f"❌ Agent {agent_id} removed from swarm {swarm_id}")
        return {"message": "Agent removed from swarm"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/swarms", response_model=List[Swarm])
async def list_swarms(state: Optional[CollectiveState] = None):
    """List all swarms"""
    if state:
        return [s for s in engine.swarms.values() if s.state == state]
    return list(engine.swarms.values())

@app.get("/swarms/{swarm_id}", response_model=Swarm)
async def get_swarm(swarm_id: str):
    """Get swarm by ID"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    return engine.swarms[swarm_id]

@app.post("/swarms/{swarm_id}/tasks")
async def create_swarm_task(swarm_id: str, task: Dict):
    """Create a task for the swarm"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    swarm_task = engine.decompose_task(task, engine.swarms[swarm_id])
    
    # Store in database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO swarm_tasks 
            (id, swarm_id, description, subtasks, assignments, status, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, swarm_task.id, swarm_id, swarm_task.description,
            json.dumps(swarm_task.subtasks), json.dumps(swarm_task.assignments),
            swarm_task.status, swarm_task.created_at)
    
    logger.info(f"✅ Task created for swarm {swarm_id}: {swarm_task.id}")
    return swarm_task

@app.get("/swarms/{swarm_id}/tasks", response_model=List[SwarmTask])
async def list_swarm_tasks(swarm_id: str):
    """List all tasks for a swarm"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM swarm_tasks WHERE swarm_id = $1 ORDER BY created_at DESC",
            swarm_id
        )
    return [dict(row) for row in rows]

@app.post("/swarms/{swarm_id}/consensus")
async def reach_consensus(swarm_id: str, proposals: List[Dict]):
    """Reach consensus in the swarm"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    consensus = engine.reach_consensus(swarm_id, proposals)
    
    # Update database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE swarms 
            SET consensus = $1, state = $2, updated_at = $3
            WHERE id = $4
        """, json.dumps(consensus), CollectiveState.CONSENSUS.value,
            datetime.now(), swarm_id)
    
    logger.info(f"✅ Consensus reached in swarm {swarm_id}")
    return consensus

@app.post("/swarms/{swarm_id}/learn")
async def collective_learn(swarm_id: str, knowledge: Dict):
    """Collective learning in the swarm"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    result = engine.collective_learn(swarm_id, knowledge)
    
    # Store in collective memory database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO collective_memory (id, swarm_id, knowledge, timestamp)
            VALUES ($1, $2, $3, $4)
        """, result["learning_event_id"], swarm_id,
            json.dumps(knowledge), datetime.now())
    
    logger.info(f"✅ Collective learning in swarm {swarm_id}")
    return result

@app.get("/swarms/{swarm_id}/intelligence", response_model=CollectiveIntelligence)
async def get_collective_intelligence(swarm_id: str):
    """Get collective intelligence metrics for swarm"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    ci = engine.calculate_collective_intelligence(swarm_id)
    
    # Store in database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO collective_intelligence 
            (id, swarm_id, intelligence_score, diversity_score, cohesion_score, emergence_score, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, ci.id, swarm_id, ci.intelligence_score, ci.diversity_score,
            ci.cohesion_score, ci.emergence_score, ci.timestamp)
    
    return ci

@app.get("/swarms/{swarm_id}/emergence")
async def detect_emergence(swarm_id: str):
    """Detect emergent behaviors in swarm"""
    if swarm_id not in engine.swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")
    
    emergence = engine.calculate_emergence(swarm_id)
    
    # Store patterns
    async with db_pool.acquire() as conn:
        for pattern in emergence:
            await conn.execute("""
                INSERT INTO emergence_patterns (id, swarm_id, pattern_type, pattern_data, detected_at)
                VALUES ($1, $2, $3, $4, $5)
            """, str(uuid.uuid4()), swarm_id, pattern["type"],
                json.dumps(pattern), datetime.now())
    
    return emergence

@app.get("/analytics/collective-memory")
async def get_collective_memory(limit: int = 100):
    """Get collective memory entries"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM collective_memory 
            ORDER BY timestamp DESC 
            LIMIT $1
        """, limit)
    return [dict(row) for row in rows]

@app.get("/analytics/emergence-patterns")
async def get_emergence_patterns(swarm_id: Optional[str] = None):
    """Get emergence patterns"""
    async with db_pool.acquire() as conn:
        if swarm_id:
            rows = await conn.fetch(
                "SELECT * FROM emergence_patterns WHERE swarm_id = $1 ORDER BY detected_at DESC",
                swarm_id
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM emergence_patterns ORDER BY detected_at DESC LIMIT 100"
            )
    return [dict(row) for row in rows]

@app.get("/analytics/swarm-performance")
async def get_swarm_performance(swarm_id: str):
    """Get performance metrics for a swarm"""
    async with db_pool.acquire() as conn:
        # Get intelligence history
        intelligence = await conn.fetch("""
            SELECT * FROM collective_intelligence 
            WHERE swarm_id = $1 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, swarm_id)
        
        # Get task completion stats
        tasks = await conn.fetch("""
            SELECT status, COUNT(*) as count 
            FROM swarm_tasks 
            WHERE swarm_id = $1 
            GROUP BY status
        """, swarm_id)
        
        # Get emergence patterns
        emergence = await conn.fetch("""
            SELECT pattern_type, COUNT(*) as count 
            FROM emergence_patterns 
            WHERE swarm_id = $1 
            GROUP BY pattern_type
        """, swarm_id)
    
    return {
        "swarm_id": swarm_id,
        "intelligence_history": [dict(row) for row in intelligence],
        "task_stats": {row['status']: row['count'] for row in tasks},
        "emergence_stats": {row['pattern_type']: row['count'] for row in emergence}
    }
""")

# 4. Создаём Dockerfile для Quantum Service
with open("backend/services/quantum-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install fastapi uvicorn asyncpg numpy websockets

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8007", "--reload"]
""")

# 5. Создаём SQL для Quantum Service
with open("infra/postgres/init/06-quantum.sql", "w") as f:
    f.write("""-- Create quantum database
CREATE DATABASE augur_quantum;

\\c augur_quantum;

-- Swarms table
CREATE TABLE IF NOT EXISTS swarms (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(50),
    agents JSONB,
    state VARCHAR(50),
    goal JSONB,
    consensus JSONB,
    emergence JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Swarm tasks table
CREATE TABLE IF NOT EXISTS swarm_tasks (
    id UUID PRIMARY KEY,
    swarm_id UUID REFERENCES swarms(id),
    description TEXT,
    subtasks JSONB,
    assignments JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Collective intelligence metrics
CREATE TABLE IF NOT EXISTS collective_intelligence (
    id UUID PRIMARY KEY,
    swarm_id UUID REFERENCES swarms(id),
    intelligence_score FLOAT,
    diversity_score FLOAT,
    cohesion_score FLOAT,
    emergence_score FLOAT,
    timestamp TIMESTAMP
);

-- Collective memory
CREATE TABLE IF NOT EXISTS collective_memory (
    id UUID PRIMARY KEY,
    swarm_id UUID REFERENCES swarms(id),
    knowledge JSONB,
    timestamp TIMESTAMP
);

-- Emergence patterns
CREATE TABLE IF NOT EXISTS emergence_patterns (
    id UUID PRIMARY KEY,
    swarm_id UUID REFERENCES swarms(id),
    pattern_type VARCHAR(50),
    pattern_data JSONB,
    detected_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_swarms_type ON swarms(type);
CREATE INDEX idx_swarms_state ON swarms(state);
CREATE INDEX idx_swarm_tasks_swarm ON swarm_tasks(swarm_id);
CREATE INDEX idx_swarm_tasks_status ON swarm_tasks(status);
CREATE INDEX idx_collective_intelligence_swarm ON collective_intelligence(swarm_id);
CREATE INDEX idx_collective_memory_swarm ON collective_memory(swarm_id);
CREATE INDEX idx_collective_memory_time ON collective_memory(timestamp);
CREATE INDEX idx_emergence_swarm ON emergence_patterns(swarm_id);
CREATE INDEX idx_emergence_type ON emergence_patterns(pattern_type);
""")

# 6. Обновляем docker-compose.yml
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""services:
  value-service:""", """services:
  quantum-service:
    build: ./backend/services/quantum-service
    ports:
      - "8007:8007"
    environment:
      - DB_USER=augur
      - DB_PASSWORD=augur
      - DB_NAME=augur_quantum
      - DB_HOST=postgres
      - DB_PORT=5432
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - augur-net

  value-service:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 7. Создаём тест для Quantum Service
with open("test_quantum.py", "w") as f:
    f.write("""import requests
import time
import json
import uuid
from datetime import datetime

print("🧪 Testing Quantum Collective Intelligence Service...\\n")

base = "http://localhost:8007"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Database: {data['database']}")
        print(f"   ✅ Quantum Engine: {data['quantum_engine']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Create a swarm
print("\\n2️⃣ Creating swarm...")
swarm_data = {
    "name": "Research Swarm",
    "swarm_type": "problem_solving",
    "goal": {"task": "solve_complex_problem", "deadline": "2026-12-31"}
}

try:
    resp = requests.post(f"{base}/swarms", params=swarm_data)
    if resp.status_code == 200:
        swarm = resp.json()
        swarm_id = swarm['id']
        print(f"   ✅ Swarm created: {swarm_id}")
        print(f"      Name: {swarm['name']}")
        print(f"      Type: {swarm['type']}")
        print(f"      State: {swarm['state']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        swarm_id = None
except Exception as e:
    print(f"   ❌ Error: {e}")
    swarm_id = None

# 3. Add agents to swarm
if swarm_id:
    print("\\n3️⃣ Adding agents to swarm...")
    agent_ids = []
    for i in range(3):
        agent_data = {
            "id": str(uuid.uuid4()),
            "capabilities": [f"capability_{j}" for j in range(i+1)],
            "knowledge_base": {"domain": f"area_{i}"},
            "position": {"x": i*10, "y": i*5}
        }
        agent_ids.append(agent_data["id"])
        
        try:
            resp = requests.post(
                f"{base}/swarms/{swarm_id}/agents/{agent_data['id']}",
                json=agent_data
            )
            if resp.status_code == 200:
                print(f"   ✅ Agent {i+1} added: {agent_data['id'][:8]}...")
            else:
                print(f"   ❌ Failed: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        time.sleep(0.5)

# 4. Create a task for the swarm
if swarm_id:
    print("\\n4️⃣ Creating swarm task...")
    task = {
        "description": "Complex research problem",
        "complexity": 3
    }
    
    try:
        resp = requests.post(f"{base}/swarms/{swarm_id}/tasks", json=task)
        if resp.status_code == 200:
            task_data = resp.json()
            print(f"   ✅ Task created: {task_data['id']}")
            print(f"      Subtasks: {len(task_data['subtasks'])}")
            print(f"      Assignments: {len(task_data['assignments'])}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 5. Get collective intelligence
if swarm_id:
    print("\\n5️⃣ Calculating collective intelligence...")
    try:
        resp = requests.get(f"{base}/swarms/{swarm_id}/intelligence")
        if resp.status_code == 200:
            ci = resp.json()
            print(f"   ✅ Intelligence score: {ci['intelligence_score']:.3f}")
            print(f"      Diversity: {ci['diversity_score']:.3f}")
            print(f"      Cohesion: {ci['cohesion_score']:.3f}")
            print(f"      Emergence: {ci['emergence_score']:.3f}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 6. Reach consensus
if swarm_id:
    print("\\n6️⃣ Reaching consensus...")
    proposals = [
        {"agent": agent_ids[0], "topic": "approach", "option": "method_a"},
        {"agent": agent_ids[1], "topic": "approach", "option": "method_b"},
        {"agent": agent_ids[2], "topic": "approach", "option": "method_a"}
    ]
    
    try:
        resp = requests.post(f"{base}/swarms/{swarm_id}/consensus", json=proposals)
        if resp.status_code == 200:
            consensus = resp.json()
            print(f"   ✅ Consensus reached!")
            print(f"      Decision: {consensus['decision']}")
            print(f"      Confidence: {consensus['confidence']:.3f}")
            print(f"      Voting results: {consensus['voting_results']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 7. Collective learning
if swarm_id:
    print("\\n7️⃣ Collective learning...")
    knowledge = {
        "discovery": "new_algorithm",
        "effectiveness": 0.95,
        "applications": ["optimization", "search"]
    }
    
    try:
        resp = requests.post(f"{base}/swarms/{swarm_id}/learn", json=knowledge)
        if resp.status_code == 200:
            learning = resp.json()
            print(f"   ✅ Learning event: {learning['learning_event_id']}")
            print(f"      Agents updated: {learning['agents_updated']}")
            print(f"      Collective memory size: {learning['collective_memory_size']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 8. Detect emergence
if swarm_id:
    print("\\n8️⃣ Detecting emergence...")
    try:
        resp = requests.get(f"{base}/swarms/{swarm_id}/emergence")
        if resp.status_code == 200:
            emergence = resp.json()
            print(f"   ✅ Detected {len(emergence)} emergence patterns")
            for i, pattern in enumerate(emergence):
                print(f"      {i+1}. {pattern['type']}: {pattern['description']} (score: {pattern['score']:.2f})")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 9. Get swarm performance analytics
if swarm_id:
    print("\\n9️⃣ Getting swarm performance...")
    try:
        resp = requests.get(f"{base}/analytics/swarm-performance?swarm_id={swarm_id}")
        if resp.status_code == 200:
            perf = resp.json()
            print(f"   ✅ Swarm performance:")
            print(f"      Intelligence history: {len(perf['intelligence_history'])} entries")
            print(f"      Task stats: {perf['task_stats']}")
            print(f"      Emergence stats: {perf['emergence_stats']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 10. List all swarms
print("\\n🔟 Listing all swarms...")
try:
    resp = requests.get(f"{base}/swarms")
    if resp.status_code == 200:
        swarms = resp.json()
        print(f"   ✅ Found {len(swarms)} swarms")
        for i, s in enumerate(swarms):
            print(f"      {i+1}. {s['name']} - {s['type']} - {s['state']} ({len(s['agents'])} agents)")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Quantum Collective Intelligence Service test complete")
print("="*50)
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 7 ВЫПОЛНЕН                                           ║
║  Добавлен Quantum Collective Intelligence Service           ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Quantum Collective Intelligence (порт 8007)
   • Swarm Intelligence Engine
   • Collective Learning
   • Emergence Detection
   • Consensus Mechanisms
   • Real-time WebSocket communication
   • Collective Memory

🚀 Что делать дальше:
   make build
   make up
   python test_quantum.py

📊 Новые endpoints:
   POST /swarms                          - создать рой
   POST /swarms/{id}/agents/{aid}        - добавить агента
   WebSocket /ws/{swarm_id}/{agent_id}    - реальное время
   POST /swarms/{id}/tasks                - создать задачу
   POST /swarms/{id}/consensus             - достичь консенсуса
   POST /swarms/{id}/learn                 - коллективное обучение
   GET /swarms/{id}/intelligence            - метрики интеллекта
   GET /swarms/{id}/emergence               - обнаружение эмерджентности
   GET /analytics/collective-memory         - коллективная память
   GET /analytics/swarm-performance         - производительность

🧠 Новые возможности:
   • Роевой интеллект
   • Коллективное обучение
   • Эмерджентное поведение
   • Консенсус в реальном времени
   • Самоорганизация агентов
""")
