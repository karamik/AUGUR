#!/usr/bin/env python3
"""
ШАГ 5: Добавляем Conflict Resolution Service с теорией игр
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 5: Добавляем Conflict Resolution Service               ║
║  с теорией игр и предсказанием конфликтов                   ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Conflict Resolution Service
os.makedirs("backend/services/conflict-service/src", exist_ok=True)

# 2. Устанавливаем зависимости для теории игр
print("📦 Установка зависимостей...")
run("pip install numpy scipy networkx")

# 3. Создаём рабочий Conflict Resolution Service
with open("backend/services/conflict-service/src/main.py", "w") as f:
    f.write("""# Conflict Resolution Service with Game Theory
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import asyncpg
import numpy as np
import uuid
import os
import logging
import json
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Conflict Resolution Service", version="1.0.0")

# Database connection
db_pool = None

# Enums
class ConflictType(str, Enum):
    RESOURCE = "resource"
    GOAL = "goal"
    PRIORITY = "priority"
    INFORMATION = "information"
    COORDINATION = "coordination"

class ConflictStatus(str, Enum):
    PREDICTED = "predicted"
    ACTIVE = "active"
    RESOLVED = "resolved"
    PREVENTED = "prevented"

class ResolutionStrategy(str, Enum):
    NEGOTIATION = "negotiation"
    COMPROMISE = "compromise"
    COOPERATION = "cooperation"
    COMPETITION = "competition"
    AVOIDANCE = "avoidance"

# Models
class Agent(BaseModel):
    id: str
    type: str
    capabilities: List[str]
    preferences: Dict
    current_goal: Optional[str] = None
    resources: Dict = {}

class Interaction(BaseModel):
    id: str
    agent_a: str
    agent_b: str
    type: str
    context: Dict
    timestamp: datetime

class Conflict(BaseModel):
    id: str
    agent_a: str
    agent_b: str
    type: ConflictType
    status: ConflictStatus
    probability: float
    severity: float
    description: str
    context: Dict
    predicted_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_strategy: Optional[ResolutionStrategy] = None

class GameMatrix(BaseModel):
    agent_a_id: str
    agent_b_id: str
    strategies_a: List[str]
    strategies_b: List[str]
    payoffs: List[List[Tuple[float, float]]]  # [(a_payoff, b_payoff), ...]

class NashEquilibrium(BaseModel):
    exists: bool
    strategy_a: Optional[str] = None
    strategy_b: Optional[str] = None
    payoff_a: Optional[float] = None
    payoff_b: Optional[float] = None
    pareto_optimal: bool = False

# Game Theory Engine
class GameTheoryEngine:
    @staticmethod
    def create_payoff_matrix(agent_a: Agent, agent_b: Agent, context: Dict) -> GameMatrix:
        """Create payoff matrix based on agent preferences and context"""
        
        # Define possible strategies based on agent capabilities
        strategies = ["cooperate", "defect", "compromise", "compete"]
        
        # Filter strategies based on agent capabilities
        strategies_a = [s for s in strategies if s in agent_a.capabilities]
        strategies_b = [s for s in strategies if s in agent_b.capabilities]
        
        if not strategies_a:
            strategies_a = ["cooperate", "defect"]
        if not strategies_b:
            strategies_b = ["cooperate", "defect"]
        
        # Calculate payoffs based on preferences and context
        payoffs = []
        for s_a in strategies_a:
            row = []
            for s_b in strategies_b:
                # Base payoffs from game theory classic games
                if s_a == "cooperate" and s_b == "cooperate":
                    a_payoff = 3 + agent_a.preferences.get("cooperation_bonus", 0)
                    b_payoff = 3 + agent_b.preferences.get("cooperation_bonus", 0)
                elif s_a == "cooperate" and s_b == "defect":
                    a_payoff = 0
                    b_payoff = 5
                elif s_a == "defect" and s_b == "cooperate":
                    a_payoff = 5
                    b_payoff = 0
                elif s_a == "defect" and s_b == "defect":
                    a_payoff = 1
                    b_payoff = 1
                else:
                    # Custom strategies
                    a_payoff = agent_a.preferences.get(s_a, 2)
                    b_payoff = agent_b.preferences.get(s_b, 2)
                
                # Apply context modifiers
                resource_scarcity = context.get("resource_scarcity", 1.0)
                a_payoff *= resource_scarcity
                b_payoff *= resource_scarcity
                
                row.append((float(a_payoff), float(b_payoff)))
            payoffs.append(row)
        
        return GameMatrix(
            agent_a_id=agent_a.id,
            agent_b_id=agent_b.id,
            strategies_a=strategies_a,
            strategies_b=strategies_b,
            payoffs=payoffs
        )
    
    @staticmethod
    def find_nash_equilibrium(matrix: GameMatrix) -> List[NashEquilibrium]:
        """Find Nash Equilibria in the game matrix"""
        equilibria = []
        n_a = len(matrix.strategies_a)
        n_b = len(matrix.strategies_b)
        
        for i in range(n_a):
            for j in range(n_b):
                a_payoff, b_payoff = matrix.payoffs[i][j]
                
                # Check if this is a Nash Equilibrium
                is_nash = True
                
                # Check if any player can improve by changing strategy
                for k in range(n_a):
                    if k != i:
                        if matrix.payoffs[k][j][0] > a_payoff:
                            is_nash = False
                            break
                
                if is_nash:
                    for l in range(n_b):
                        if l != j:
                            if matrix.payoffs[i][l][1] > b_payoff:
                                is_nash = False
                                break
                
                if is_nash:
                    # Check if Pareto optimal
                    pareto = True
                    for k in range(n_a):
                        for l in range(n_b):
                            if (k != i or l != j):
                                if (matrix.payoffs[k][l][0] >= a_payoff and 
                                    matrix.payoffs[k][l][1] >= b_payoff and
                                    (matrix.payoffs[k][l][0] > a_payoff or 
                                     matrix.payoffs[k][l][1] > b_payoff)):
                                    pareto = False
                                    break
                    
                    equilibria.append(NashEquilibrium(
                        exists=True,
                        strategy_a=matrix.strategies_a[i],
                        strategy_b=matrix.strategies_b[j],
                        payoff_a=float(a_payoff),
                        payoff_b=float(b_payoff),
                        pareto_optimal=pareto
                    ))
        
        return equilibria if equilibria else [NashEquilibrium(exists=False)]
    
    @staticmethod
    def predict_conflict_probability(agent_a: Agent, agent_b: Agent, context: Dict) -> float:
        """Predict probability of conflict based on game theory"""
        
        # Get payoff matrix
        matrix = GameTheoryEngine.create_payoff_matrix(agent_a, agent_b, context)
        
        # Find Nash Equilibria
        equilibria = GameTheoryEngine.find_nash_equilibrium(matrix)
        
        # If there's a Pareto optimal Nash Equilibrium, low conflict probability
        for eq in equilibria:
            if eq.exists and eq.pareto_optimal:
                return 0.2
        
        # If multiple equilibria, medium conflict probability
        if len([e for e in equilibria if e.exists]) > 1:
            return 0.6
        
        # If no equilibrium, high conflict probability
        if not any(e.exists for e in equilibria):
            return 0.9
        
        return 0.5
    
    @staticmethod
    def suggest_resolution(agent_a: Agent, agent_b: Agent, context: Dict) -> ResolutionStrategy:
        """Suggest resolution strategy based on game type"""
        
        matrix = GameTheoryEngine.create_payoff_matrix(agent_a, agent_b, context)
        equilibria = GameTheoryEngine.find_nash_equilibrium(matrix)
        
        # Analyze game type and suggest strategy
        if any(e.pareto_optimal for e in equilibria if e.exists):
            return ResolutionStrategy.COOPERATION
        
        # Check if it's a zero-sum game
        is_zero_sum = True
        for i in range(len(matrix.payoffs)):
            for j in range(len(matrix.payoffs[i])):
                a_pay, b_pay = matrix.payoffs[i][j]
                if abs(a_pay + b_pay) > 0.1:
                    is_zero_sum = False
                    break
        
        if is_zero_sum:
            return ResolutionStrategy.COMPETITION
        
        # Check resource scarcity
        if context.get("resource_scarcity", 1.0) > 1.5:
            return ResolutionStrategy.COMPROMISE
        
        return ResolutionStrategy.NEGOTIATION

# Initialize Game Theory Engine
gt_engine = GameTheoryEngine()

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "augur"),
            password=os.getenv("DB_PASSWORD", "augur"),
            database=os.getenv("DB_NAME", "augur_conflict"),
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Connected to Conflict Database")
        
        # Create tables
        async with db_pool.acquire() as conn:
            # Agents cache table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_profiles (
                    id UUID PRIMARY KEY,
                    type VARCHAR(50),
                    capabilities JSONB,
                    preferences JSONB,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Interactions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id UUID PRIMARY KEY,
                    agent_a UUID,
                    agent_b UUID,
                    type VARCHAR(50),
                    context JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Conflicts table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conflicts (
                    id UUID PRIMARY KEY,
                    agent_a UUID,
                    agent_b UUID,
                    type VARCHAR(50),
                    status VARCHAR(20),
                    probability FLOAT,
                    severity FLOAT,
                    description TEXT,
                    context JSONB,
                    predicted_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    resolution_strategy VARCHAR(50)
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflicts_agents ON conflicts(agent_a, agent_b)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_conflicts_status ON conflicts(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_agents ON interactions(agent_a, agent_b)")
            
            logger.info("✅ Conflict tables ready")
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
        "service": "Conflict Resolution Service",
        "version": "1.0.0",
        "features": ["game-theory", "nash-equilibrium", "conflict-prediction"]
    }

@app.get("/health")
async def health():
    db_status = "connected" if db_pool else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "game-theory": "enabled",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agents/profile")
async def register_agent_profile(agent: Agent):
    """Register or update agent profile for game theory analysis"""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO agent_profiles (id, type, capabilities, preferences, last_updated)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO UPDATE SET
                type = EXCLUDED.type,
                capabilities = EXCLUDED.capabilities,
                preferences = EXCLUDED.preferences,
                last_updated = EXCLUDED.last_updated
        """, agent.id, agent.type, json.dumps(agent.capabilities),
            json.dumps(agent.preferences), datetime.now())
    
    logger.info(f"✅ Agent profile registered: {agent.id}")
    return {"message": "Agent profile registered", "agent_id": agent.id}

@app.post("/interactions")
async def record_interaction(interaction: Interaction):
    """Record agent interaction for conflict analysis"""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO interactions (id, agent_a, agent_b, type, context)
            VALUES ($1, $2, $3, $4, $5)
        """, interaction.id, interaction.agent_a, interaction.agent_b,
            interaction.type, json.dumps(interaction.context))
    
    logger.info(f"✅ Interaction recorded: {interaction.id}")
    return {"message": "Interaction recorded"}

@app.post("/predict/{agent_a_id}/{agent_b_id}")
async def predict_conflict(agent_a_id: str, agent_b_id: str, context: Dict):
    """Predict conflict probability between two agents"""
    
    # Get agent profiles
    async with db_pool.acquire() as conn:
        agent_a_row = await conn.fetchrow(
            "SELECT * FROM agent_profiles WHERE id = $1",
            agent_a_id
        )
        agent_b_row = await conn.fetchrow(
            "SELECT * FROM agent_profiles WHERE id = $1",
            agent_b_id
        )
    
    if not agent_a_row or not agent_b_row:
        raise HTTPException(status_code=404, detail="One or both agents not found")
    
    # Create agent objects
    agent_a = Agent(
        id=agent_a_row['id'],
        type=agent_a_row['type'],
        capabilities=agent_a_row['capabilities'],
        preferences=agent_a_row['preferences']
    )
    agent_b = Agent(
        id=agent_b_row['id'],
        type=agent_b_row['type'],
        capabilities=agent_b_row['capabilities'],
        preferences=agent_b_row['preferences']
    )
    
    # Predict conflict
    conflict_prob = gt_engine.predict_conflict_probability(agent_a, agent_b, context)
    resolution = gt_engine.suggest_resolution(agent_a, agent_b, context)
    
    # Determine conflict type based on context
    conflict_type = ConflictType.RESOURCE
    if "goal" in context:
        conflict_type = ConflictType.GOAL
    elif "priority" in context:
        conflict_type = ConflictType.PRIORITY
    
    # Calculate severity based on probability and context
    severity = conflict_prob * context.get("importance", 1.0)
    
    # Create conflict record if probability > threshold
    conflict_id = None
    if conflict_prob > 0.5:
        conflict_id = str(uuid.uuid4())
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO conflicts 
                (id, agent_a, agent_b, type, status, probability, severity, 
                 description, context, predicted_at, resolution_strategy)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """, conflict_id, agent_a_id, agent_b_id, conflict_type.value,
                ConflictStatus.PREDICTED.value, conflict_prob, severity,
                f"Potential {conflict_type.value} conflict detected",
                json.dumps(context), datetime.now(), resolution.value)
        
        logger.info(f"⚠️ Conflict predicted: {conflict_id} with probability {conflict_prob}")
    
    return {
        "prediction": {
            "conflict_probability": conflict_prob,
            "severity": severity,
            "conflict_type": conflict_type,
            "suggested_resolution": resolution,
            "conflict_id": conflict_id
        },
        "game_analysis": {
            "has_nash_equilibrium": gt_engine.find_nash_equilibrium(
                gt_engine.create_payoff_matrix(agent_a, agent_b, context)
            )[0].exists
        }
    }

@app.get("/conflicts", response_model=List[Conflict])
async def list_conflicts(
    status: Optional[ConflictStatus] = None,
    agent_id: Optional[str] = None,
    limit: int = 100
):
    """List conflicts with optional filters"""
    async with db_pool.acquire() as conn:
        if status and agent_id:
            rows = await conn.fetch("""
                SELECT * FROM conflicts 
                WHERE status = $1 AND (agent_a = $2 OR agent_b = $2)
                ORDER BY predicted_at DESC
                LIMIT $3
            """, status.value, agent_id, limit)
        elif status:
            rows = await conn.fetch("""
                SELECT * FROM conflicts 
                WHERE status = $1
                ORDER BY predicted_at DESC
                LIMIT $2
            """, status.value, limit)
        elif agent_id:
            rows = await conn.fetch("""
                SELECT * FROM conflicts 
                WHERE agent_a = $1 OR agent_b = $1
                ORDER BY predicted_at DESC
                LIMIT $2
            """, agent_id, limit)
        else:
            rows = await conn.fetch("""
                SELECT * FROM conflicts 
                ORDER BY predicted_at DESC
                LIMIT $1
            """, limit)
    
    return [dict(row) for row in rows]

@app.get("/conflicts/{conflict_id}", response_model=Conflict)
async def get_conflict(conflict_id: str):
    """Get specific conflict by ID"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM conflicts WHERE id = $1",
            conflict_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Conflict not found")
    
    return dict(row)

@app.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    conflict_id: str,
    strategy: ResolutionStrategy,
    outcome: Dict
):
    """Mark conflict as resolved"""
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE conflicts 
            SET status = $1, resolved_at = $2, resolution_strategy = $3
            WHERE id = $4
        """, ConflictStatus.RESOLVED.value, datetime.now(), strategy.value, conflict_id)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Conflict not found")
    
    logger.info(f"✅ Conflict resolved: {conflict_id} using {strategy.value}")
    return {"message": "Conflict resolved", "strategy": strategy, "outcome": outcome}

@app.get("/game/matrix/{agent_a_id}/{agent_b_id}")
async def get_game_matrix(agent_a_id: str, agent_b_id: str, context: Dict):
    """Get game theory matrix for two agents"""
    
    # Get agent profiles
    async with db_pool.acquire() as conn:
        agent_a_row = await conn.fetchrow(
            "SELECT * FROM agent_profiles WHERE id = $1",
            agent_a_id
        )
        agent_b_row = await conn.fetchrow(
            "SELECT * FROM agent_profiles WHERE id = $1",
            agent_b_id
        )
    
    if not agent_a_row or not agent_b_row:
        raise HTTPException(status_code=404, detail="One or both agents not found")
    
    agent_a = Agent(
        id=agent_a_row['id'],
        type=agent_a_row['type'],
        capabilities=agent_a_row['capabilities'],
        preferences=agent_a_row['preferences']
    )
    agent_b = Agent(
        id=agent_b_row['id'],
        type=agent_b_row['type'],
        capabilities=agent_b_row['capabilities'],
        preferences=agent_b_row['preferences']
    )
    
    # Create game matrix
    matrix = gt_engine.create_payoff_matrix(agent_a, agent_b, context)
    equilibria = gt_engine.find_nash_equilibrium(matrix)
    
    return {
        "matrix": matrix.dict(),
        "nash_equilibria": [e.dict() for e in equilibria]
    }

@app.get("/analytics/summary")
async def get_conflict_analytics():
    """Get conflict analytics summary"""
    async with db_pool.acquire() as conn:
        # Total conflicts
        total = await conn.fetchval("SELECT COUNT(*) FROM conflicts")
        
        # By status
        predicted = await conn.fetchval(
            "SELECT COUNT(*) FROM conflicts WHERE status = $1",
            ConflictStatus.PREDICTED.value
        )
        resolved = await conn.fetchval(
            "SELECT COUNT(*) FROM conflicts WHERE status = $1",
            ConflictStatus.RESOLVED.value
        )
        
        # Average probability
        avg_prob = await conn.fetchval(
            "SELECT AVG(probability) FROM conflicts"
        ) or 0
        
        # Most common conflict type
        type_stats = await conn.fetch("""
            SELECT type, COUNT(*) as count 
            FROM conflicts 
            GROUP BY type 
            ORDER BY count DESC 
            LIMIT 1
        """)
        
        most_common_type = type_stats[0]['type'] if type_stats else None
        
        # Most common resolution
        resolution_stats = await conn.fetch("""
            SELECT resolution_strategy, COUNT(*) as count 
            FROM conflicts 
            WHERE resolution_strategy IS NOT NULL
            GROUP BY resolution_strategy 
            ORDER BY count DESC 
            LIMIT 1
        """)
        
        most_common_resolution = resolution_stats[0]['resolution_strategy'] if resolution_stats else None
    
    return {
        "total_conflicts": total,
        "by_status": {
            "predicted": predicted,
            "resolved": resolved
        },
        "average_probability": float(avg_prob),
        "most_common_type": most_common_type,
        "most_common_resolution": most_common_resolution,
        "timestamp": datetime.now().isoformat()
    }
""")

# 4. Создаём Dockerfile для Conflict Service
with open("backend/services/conflict-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install fastapi uvicorn asyncpg numpy scipy networkx

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]
""")

# 5. Создаём SQL для Conflict Service
with open("infra/postgres/init/04-conflict.sql", "w") as f:
    f.write("""-- Create conflict database
CREATE DATABASE augur_conflict;

\\c augur_conflict;

-- Agent profiles cache
CREATE TABLE IF NOT EXISTS agent_profiles (
    id UUID PRIMARY KEY,
    type VARCHAR(50),
    capabilities JSONB,
    preferences JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interactions history
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY,
    agent_a UUID,
    agent_b UUID,
    type VARCHAR(50),
    context JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conflicts table
CREATE TABLE IF NOT EXISTS conflicts (
    id UUID PRIMARY KEY,
    agent_a UUID,
    agent_b UUID,
    type VARCHAR(50),
    status VARCHAR(20),
    probability FLOAT,
    severity FLOAT,
    description TEXT,
    context JSONB,
    predicted_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_strategy VARCHAR(50)
);

-- Indexes for performance
CREATE INDEX idx_conflicts_agents ON conflicts(agent_a, agent_b);
CREATE INDEX idx_conflicts_status ON conflicts(status);
CREATE INDEX idx_conflicts_type ON conflicts(type);
CREATE INDEX idx_conflicts_probability ON conflicts(probability);
CREATE INDEX idx_interactions_agents ON interactions(agent_a, agent_b);
CREATE INDEX idx_interactions_time ON interactions(timestamp);
""")

# 6. Обновляем docker-compose.yml
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""services:
  governance-service:""", """services:
  conflict-service:
    build: ./backend/services/conflict-service
    ports:
      - "8005:8005"
    environment:
      - DB_USER=augur
      - DB_PASSWORD=augur
      - DB_NAME=augur_conflict
      - DB_HOST=postgres
      - DB_PORT=5432
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - augur-net

  governance-service:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 7. Создаём тест для Conflict Service
with open("test_conflict.py", "w") as f:
    f.write("""import requests
import time
import json
import uuid

print("🧪 Testing Conflict Resolution Service with Game Theory...\\n")

base = "http://localhost:8005"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Database: {data['database']}")
        print(f"   ✅ Game Theory: {data['game-theory']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Register agent profiles
print("\\n2️⃣ Registering agent profiles...")
agent_ids = []

agent_types = [
    {"type": "cooperative", "preferences": {"cooperation_bonus": 2, "cooperate": 5, "defect": 1}},
    {"type": "competitive", "preferences": {"cooperation_bonus": 0, "cooperate": 1, "defect": 5}},
    {"type": "balanced", "preferences": {"cooperation_bonus": 1, "cooperate": 3, "defect": 3}}
]

for i, agent_type in enumerate(agent_types):
    agent_data = {
        "id": str(uuid.uuid4()),
        "type": agent_type["type"],
        "capabilities": ["cooperate", "defect", "compromise", "compete"],
        "preferences": agent_type["preferences"],
        "current_goal": f"goal_{i}",
        "resources": {"cpu": 100, "memory": 512}
    }
    agent_ids.append(agent_data["id"])
    
    try:
        resp = requests.post(f"{base}/agents/profile", json=agent_data)
        if resp.status_code == 200:
            print(f"   ✅ Agent {i+1} registered: {agent_type['type']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 3. Predict conflicts between agents
print("\\n3️⃣ Predicting conflicts...")
context = {
    "resource_scarcity": 1.5,
    "importance": 0.8,
    "goal": "complete_task"
}

for i in range(len(agent_ids)):
    for j in range(i+1, len(agent_ids)):
        try:
            resp = requests.post(
                f"{base}/predict/{agent_ids[i]}/{agent_ids[j]}",
                json=context
            )
            if resp.status_code == 200:
                prediction = resp.json()
                prob = prediction['prediction']['conflict_probability']
                resolution = prediction['prediction']['suggested_resolution']
                print(f"   ✅ Agents {i+1}-{j+1}: conflict prob={prob:.2f}, resolution={resolution}")
                if prediction['prediction'].get('conflict_id'):
                    print(f"      Conflict ID: {prediction['prediction']['conflict_id']}")
            else:
                print(f"   ❌ Failed: {resp.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

# 4. Get game theory matrix
print("\\n4️⃣ Getting game theory matrix...")
try:
    resp = requests.get(
        f"{base}/game/matrix/{agent_ids[0]}/{agent_ids[1]}",
        json=context
    )
    if resp.status_code == 200:
        matrix_data = resp.json()
        matrix = matrix_data['matrix']
        print(f"   ✅ Game matrix created")
        print(f"      Strategies A: {matrix['strategies_a']}")
        print(f"      Strategies B: {matrix['strategies_b']}")
        print(f"      Nash Equilibria: {len(matrix_data['nash_equilibria'])}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. List conflicts
print("\\n5️⃣ Listing conflicts...")
try:
    resp = requests.get(f"{base}/conflicts?limit=10")
    if resp.status_code == 200:
        conflicts = resp.json()
        print(f"   ✅ Found {len(conflicts)} conflicts")
        for i, conflict in enumerate(conflicts):
            print(f"      {i+1}. Type: {conflict['type']}, Prob: {conflict['probability']:.2f}, Status: {conflict['status']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Get analytics
print("\\n6️⃣ Getting conflict analytics...")
try:
    resp = requests.get(f"{base}/analytics/summary")
    if resp.status_code == 200:
        analytics = resp.json()
        print(f"   ✅ Total conflicts: {analytics['total_conflicts']}")
        print(f"      Predicted: {analytics['by_status']['predicted']}")
        print(f"      Resolved: {analytics['by_status']['resolved']}")
        print(f"      Avg probability: {analytics['average_probability']:.2f}")
        print(f"      Most common type: {analytics['most_common_type']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Record an interaction
print("\\n7️⃣ Recording agent interaction...")
interaction = {
    "id": str(uuid.uuid4()),
    "agent_a": agent_ids[0],
    "agent_b": agent_ids[1],
    "type": "negotiation",
    "context": {"topic": "resource_allocation", "duration": 30}
}

try:
    resp = requests.post(f"{base}/interactions", json=interaction)
    if resp.status_code == 200:
        print(f"   ✅ Interaction recorded")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Conflict Resolution Service test complete")
print("="*50)
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 5 ВЫПОЛНЕН                                           ║
║  Добавлен Conflict Resolution Service с теорией игр         ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Conflict Resolution Service (порт 8005)
   • Game Theory Engine
   • Nash Equilibrium calculation
   • Conflict prediction
   • Resolution strategies
   • Agent profiling

🚀 Что делать дальше:
   make build
   make up
   python test_conflict.py

📊 Новые endpoints:
   POST /agents/profile                    - регистрация агента
   POST /predict/{a}/{b}                    - предсказание конфликта
   GET /game/matrix/{a}/{b}                  - матрица игры
   GET /conflicts                            - список конфликтов
   POST /conflicts/{id}/resolve               - разрешить конфликт
   GET /analytics/summary                     - аналитика

🎮 Возможности теории игр:
   • Матрицы выплат (payoff matrices)
   • Поиск равновесий Нэша
   • Парето-оптимальные решения
   • Предсказание конфликтов
   • Стратегии разрешения
""")
