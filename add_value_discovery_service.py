#!/usr/bin/env python3
"""
ШАГ 6: Добавляем Value Discovery Service с Causal Inference
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 6: Добавляем Value Discovery Service                   ║
║  с причинно-следственным анализом                           ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Value Discovery Service
os.makedirs("backend/services/value-service/src", exist_ok=True)

# 2. Устанавливаем зависимости для causal inference
print("📦 Установка зависимостей...")
run("pip install numpy pandas scipy scikit-learn statsmodels")

# 3. Создаём рабочий Value Discovery Service
with open("backend/services/value-service/src/main.py", "w") as f:
    f.write("""# Value Discovery Service with Causal Inference
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import asyncpg
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import uuid
import os
import logging
import json
from enum import Enum
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Value Discovery Service", version="1.0.0")

# Database connection
db_pool = None

# Enums
class ValueType(str, Enum):
    EFFICIENCY = "efficiency"
    REVENUE = "revenue"
    COST_SAVING = "cost_saving"
    TIME_SAVING = "time_saving"
    QUALITY = "quality"
    INNOVATION = "innovation"
    SYNERGY = "synergy"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Models
class Interaction(BaseModel):
    id: str
    agent_a: str
    agent_b: str
    interaction_type: str
    duration: float
    resources_used: Dict
    outcomes: Dict
    timestamp: datetime
    metadata: Dict = {}

class ValueStream(BaseModel):
    id: str
    name: str
    description: str
    value_type: ValueType
    value_amount: float
    confidence: float
    confidence_level: ConfidenceLevel
    causal_factors: List[str]
    affected_agents: List[str]
    discovered_at: datetime
    implemented: bool = False
    actual_value: Optional[float] = None

class CausalGraph(BaseModel):
    nodes: List[str]
    edges: List[Dict[str, str]]
    strengths: Dict[str, float]

class CorrelationResult(BaseModel):
    variable_a: str
    variable_b: str
    correlation: float
    p_value: float
    significant: bool

# Causal Inference Engine
class CausalInferenceEngine:
    def __init__(self):
        self.interaction_history = []
        self.value_patterns = []
        self.causal_graph = {}
    
    def add_interaction(self, interaction: Dict):
        """Add interaction to history"""
        self.interaction_history.append(interaction)
        
        # Keep only last 10000 interactions for performance
        if len(self.interaction_history) > 10000:
            self.interaction_history = self.interaction_history[-10000:]
    
    def calculate_correlations(self, variables: List[str]) -> List[CorrelationResult]:
        """Calculate correlations between variables"""
        if len(self.interaction_history) < 10:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(self.interaction_history)
        
        results = []
        for i in range(len(variables)):
            for j in range(i+1, len(variables)):
                var_a = variables[i]
                var_b = variables[j]
                
                if var_a in df.columns and var_b in df.columns:
                    # Select numeric columns only
                    if pd.api.types.is_numeric_dtype(df[var_a]) and pd.api.types.is_numeric_dtype(df[var_b]):
                        corr, p_value = stats.pearsonr(
                            df[var_a].fillna(0), 
                            df[var_b].fillna(0)
                        )
                        
                        results.append(CorrelationResult(
                            variable_a=var_a,
                            variable_b=var_b,
                            correlation=float(corr),
                            p_value=float(p_value),
                            significant=p_value < 0.05
                        ))
        
        return results
    
    def discover_causal_relationships(self) -> CausalGraph:
        """Discover causal relationships using linear regression"""
        if len(self.interaction_history) < 20:
            return CausalGraph(nodes=[], edges=[], strengths={})
        
        df = pd.DataFrame(self.interaction_history)
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        nodes = list(numeric_cols)
        edges = []
        strengths = {}
        
        for target in numeric_cols:
            # Use other variables as predictors
            predictors = [col for col in numeric_cols if col != target]
            
            if len(predictors) > 0:
                X = df[predictors].fillna(0).values
                y = df[target].fillna(0).values
                
                # Linear regression for causal strength
                model = LinearRegression()
                model.fit(X, y)
                
                for i, pred in enumerate(predictors):
                    strength = abs(model.coef_[i])
                    if strength > 0.1:  # Threshold for significance
                        edges.append({
                            "from": pred,
                            "to": target,
                            "strength": float(strength)
                        })
                        strengths[f"{pred}->{target}"] = float(strength)
        
        return CausalGraph(
            nodes=list(nodes),
            edges=edges,
            strengths=strengths
        )
    
    def identify_value_streams(self, agent_id: Optional[str] = None) -> List[ValueStream]:
        """Identify potential value streams from interactions"""
        if len(self.interaction_history) < 5:
            return []
        
        df = pd.DataFrame(self.interaction_history)
        
        if agent_id:
            df = df[(df['agent_a'] == agent_id) | (df['agent_b'] == agent_id)]
        
        value_streams = []
        
        # Look for patterns that create value
        
        # 1. Efficiency gains (reduced duration over time)
        if 'duration' in df.columns and len(df) > 5:
            recent = df.tail(5)['duration'].mean()
            historical = df.head(5)['duration'].mean()
            
            if historical > 0 and recent < historical * 0.8:  # 20% improvement
                value_streams.append(ValueStream(
                    id=str(uuid.uuid4()),
                    name="Efficiency Improvement",
                    description="Agents becoming more efficient over time",
                    value_type=ValueType.EFFICIENCY,
                    value_amount=float(historical - recent),
                    confidence=0.7,
                    confidence_level=ConfidenceLevel.MEDIUM,
                    causal_factors=["learning", "optimization"],
                    affected_agents=list(df['agent_a'].unique()) + list(df['agent_b'].unique()),
                    discovered_at=datetime.now()
                ))
        
        # 2. Synergy detection (when two agents work better together)
        if len(df) > 10:
            agent_pairs = df.groupby(['agent_a', 'agent_b']).size().reset_index(name='count')
            
            for _, row in agent_pairs.iterrows():
                a, b = row['agent_a'], row['agent_b']
                pair_df = df[(df['agent_a'] == a) & (df['agent_b'] == b)]
                
                if len(pair_df) >= 3:
                    # Check if they produce better outcomes together
                    if 'outcome_quality' in pair_df.columns:
                        avg_quality = pair_df['outcome_quality'].mean()
                        
                        # Compare with individual performances
                        a_alone = df[(df['agent_a'] == a) & (df['agent_b'].isna())]
                        b_alone = df[(df['agent_a'] == b) & (df['agent_b'].isna())]
                        
                        if not a_alone.empty and not b_alone.empty:
                            a_avg = a_alone['outcome_quality'].mean()
                            b_avg = b_alone['outcome_quality'].mean()
                            
                            if avg_quality > max(a_avg, b_avg) * 1.2:  # 20% synergy bonus
                                value_streams.append(ValueStream(
                                    id=str(uuid.uuid4()),
                                    name=f"Synergy: {a} + {b}",
                                    description="Agents create synergy when working together",
                                    value_type=ValueType.SYNERGY,
                                    value_amount=float(avg_quality - max(a_avg, b_avg)),
                                    confidence=0.8,
                                    confidence_level=ConfidenceLevel.HIGH,
                                    causal_factors=["collaboration", "complementary_skills"],
                                    affected_agents=[a, b],
                                    discovered_at=datetime.now()
                                ))
        
        # 3. Cost savings detection
        if 'resources_used' in df.columns:
            # Extract cost-related metrics
            costs = []
            for idx, row in df.iterrows():
                if isinstance(row['resources_used'], dict):
                    total_cost = sum(row['resources_used'].values())
                    costs.append(total_cost)
            
            if costs:
                avg_cost = np.mean(costs)
                min_cost = np.min(costs)
                
                if min_cost < avg_cost * 0.7:  # 30% cost saving opportunity
                    value_streams.append(ValueStream(
                        id=str(uuid.uuid4()),
                        name="Cost Optimization Opportunity",
                        description="Potential for significant cost savings",
                        value_type=ValueType.COST_SAVING,
                        value_amount=float(avg_cost - min_cost),
                        confidence=0.6,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        causal_factors=["resource_allocation", "efficiency"],
                        affected_agents=list(df['agent_a'].unique()),
                        discovered_at=datetime.now()
                    ))
        
        return value_streams
    
    def estimate_value_impact(self, value_stream: ValueStream, 
                            implementation_cost: float) -> Dict:
        """Estimate ROI of implementing a value stream"""
        
        # Base ROI calculation
        annual_value = value_stream.value_amount * 365  # Assuming daily value
        roi = (annual_value - implementation_cost) / implementation_cost if implementation_cost > 0 else float('inf')
        
        # Adjust for confidence
        adjusted_roi = roi * value_stream.confidence
        
        # Time to realize
        if value_stream.value_type == ValueType.EFFICIENCY:
            time_to_realize = 7  # days
        elif value_stream.value_type == ValueType.SYNERGY:
            time_to_realize = 30
        elif value_stream.value_type == ValueType.COST_SAVING:
            time_to_realize = 14
        else:
            time_to_realize = 21
        
        return {
            "value_stream_id": value_stream.id,
            "annual_value": float(annual_value),
            "implementation_cost": implementation_cost,
            "roi": float(roi),
            "adjusted_roi": float(adjusted_roi),
            "time_to_realize_days": time_to_realize,
            "confidence": value_stream.confidence,
            "recommendation": "highly_recommended" if adjusted_roi > 2 else 
                             "recommended" if adjusted_roi > 1 else 
                             "consider" if adjusted_roi > 0.5 else "low_priority"
        }

# Initialize engine
engine = CausalInferenceEngine()

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "augur"),
            password=os.getenv("DB_PASSWORD", "augur"),
            database=os.getenv("DB_NAME", "augur_value"),
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Connected to Value Database")
        
        # Create tables
        async with db_pool.acquire() as conn:
            # Interactions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id UUID PRIMARY KEY,
                    agent_a UUID,
                    agent_b UUID,
                    interaction_type VARCHAR(50),
                    duration FLOAT,
                    resources_used JSONB,
                    outcomes JSONB,
                    metadata JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Value streams table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS value_streams (
                    id UUID PRIMARY KEY,
                    name VARCHAR(255),
                    description TEXT,
                    value_type VARCHAR(50),
                    value_amount FLOAT,
                    confidence FLOAT,
                    confidence_level VARCHAR(20),
                    causal_factors JSONB,
                    affected_agents JSONB,
                    discovered_at TIMESTAMP,
                    implemented BOOLEAN DEFAULT FALSE,
                    actual_value FLOAT,
                    implementation_cost FLOAT,
                    implemented_at TIMESTAMP
                )
            """)
            
            # Metrics table for time-series data
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id UUID PRIMARY KEY,
                    agent_id UUID,
                    metric_name VARCHAR(100),
                    metric_value FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_time ON interactions(timestamp)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_agents ON interactions(agent_a, agent_b)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_value_streams_type ON value_streams(value_type)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_agent_time ON metrics(agent_id, timestamp)")
            
            logger.info("✅ Value tables ready")
            
            # Load recent interactions into engine
            rows = await conn.fetch("""
                SELECT * FROM interactions 
                ORDER BY timestamp DESC 
                LIMIT 1000
            """)
            
            for row in rows:
                engine.add_interaction(dict(row))
            
            logger.info(f"✅ Loaded {len(rows)} interactions into engine")
            
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
        "service": "Value Discovery Service",
        "version": "1.0.0",
        "features": ["causal-inference", "value-discovery", "roi-analysis"],
        "interactions_loaded": len(engine.interaction_history)
    }

@app.get("/health")
async def health():
    db_status = "connected" if db_pool else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "causal_inference": "enabled",
        "interactions_in_memory": len(engine.interaction_history),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/interactions")
async def record_interaction(interaction: Interaction):
    """Record agent interaction for analysis"""
    
    # Store in database
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO interactions 
            (id, agent_a, agent_b, interaction_type, duration, 
             resources_used, outcomes, metadata, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, interaction.id, interaction.agent_a, interaction.agent_b,
            interaction.interaction_type, interaction.duration,
            json.dumps(interaction.resources_used),
            json.dumps(interaction.outcomes),
            json.dumps(interaction.metadata),
            interaction.timestamp)
    
    # Add to engine
    engine.add_interaction(interaction.dict())
    
    logger.info(f"✅ Interaction recorded: {interaction.id}")
    return {"message": "Interaction recorded", "id": interaction.id}

@app.post("/interactions/batch")
async def record_interactions_batch(interactions: List[Interaction]):
    """Record multiple interactions at once"""
    
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            for interaction in interactions:
                await conn.execute("""
                    INSERT INTO interactions 
                    (id, agent_a, agent_b, interaction_type, duration, 
                     resources_used, outcomes, metadata, timestamp)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, interaction.id, interaction.agent_a, interaction.agent_b,
                    interaction.interaction_type, interaction.duration,
                    json.dumps(interaction.resources_used),
                    json.dumps(interaction.outcomes),
                    json.dumps(interaction.metadata),
                    interaction.timestamp)
                
                engine.add_interaction(interaction.dict())
    
    logger.info(f"✅ Batch recorded: {len(interactions)} interactions")
    return {"message": f"Recorded {len(interactions)} interactions"}

@app.get("/interactions", response_model=List[Interaction])
async def list_interactions(
    agent_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List interactions with optional filters"""
    async with db_pool.acquire() as conn:
        if agent_id:
            rows = await conn.fetch("""
                SELECT * FROM interactions 
                WHERE agent_a = $1 OR agent_b = $1
                ORDER BY timestamp DESC
                LIMIT $2 OFFSET $3
            """, agent_id, limit, offset)
        else:
            rows = await conn.fetch("""
                SELECT * FROM interactions 
                ORDER BY timestamp DESC
                LIMIT $1 OFFSET $2
            """, limit, offset)
    
    return [dict(row) for row in rows]

@app.get("/discover/value-streams", response_model=List[ValueStream])
async def discover_value_streams(agent_id: Optional[str] = None):
    """Discover potential value streams from interactions"""
    
    value_streams = engine.identify_value_streams(agent_id)
    
    # Store discovered streams in database
    async with db_pool.acquire() as conn:
        for vs in value_streams:
            await conn.execute("""
                INSERT INTO value_streams 
                (id, name, description, value_type, value_amount, confidence,
                 confidence_level, causal_factors, affected_agents, discovered_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (id) DO NOTHING
            """, vs.id, vs.name, vs.description, vs.value_type.value,
                vs.value_amount, vs.confidence, vs.confidence_level.value,
                json.dumps(vs.causal_factors), json.dumps(vs.affected_agents),
                vs.discovered_at)
    
    logger.info(f"🔍 Discovered {len(value_streams)} value streams")
    return value_streams

@app.get("/value-streams", response_model=List[ValueStream])
async def list_value_streams(
    value_type: Optional[ValueType] = None,
    implemented: Optional[bool] = None,
    limit: int = 100
):
    """List discovered value streams"""
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM value_streams WHERE 1=1"
        params = []
        
        if value_type:
            query += f" AND value_type = ${len(params) + 1}"
            params.append(value_type.value)
        
        if implemented is not None:
            query += f" AND implemented = ${len(params) + 1}"
            params.append(implemented)
        
        query += " ORDER BY value_amount DESC LIMIT $" + str(len(params) + 1)
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
    
    return [dict(row) for row in rows]

@app.get("/value-streams/{stream_id}", response_model=ValueStream)
async def get_value_stream(stream_id: str):
    """Get specific value stream by ID"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM value_streams WHERE id = $1",
            stream_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Value stream not found")
    
    return dict(row)

@app.post("/value-streams/{stream_id}/analyze-roi")
async def analyze_roi(stream_id: str, implementation_cost: float):
    """Analyze ROI for implementing a value stream"""
    
    # Get value stream
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM value_streams WHERE id = $1",
            stream_id
        )
    
    if not row:
        raise HTTPException(status_code=404, detail="Value stream not found")
    
    value_stream = ValueStream(**dict(row))
    
    # Calculate ROI
    roi_analysis = engine.estimate_value_impact(value_stream, implementation_cost)
    
    return roi_analysis

@app.post("/value-streams/{stream_id}/implement")
async def implement_value_stream(
    stream_id: str,
    implementation_cost: float,
    notes: Optional[str] = None
):
    """Mark a value stream as implemented"""
    
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE value_streams 
            SET implemented = TRUE, 
                implementation_cost = $1,
                implemented_at = $2
            WHERE id = $3
        """, implementation_cost, datetime.now(), stream_id)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Value stream not found")
    
    logger.info(f"✅ Value stream implemented: {stream_id}")
    return {"message": "Value stream marked as implemented", "id": stream_id}

@app.get("/correlations", response_model=List[CorrelationResult])
async def analyze_correlations(variables: Optional[List[str]] = None):
    """Analyze correlations between variables"""
    
    if not variables:
        # Use default variables from recent interactions
        if engine.interaction_history:
            df = pd.DataFrame(engine.interaction_history[-100:])
            variables = list(df.select_dtypes(include=[np.number]).columns)
        else:
            return []
    
    results = engine.calculate_correlations(variables)
    return results

@app.get("/causal-graph", response_model=CausalGraph)
async def get_causal_graph():
    """Get the current causal graph from interactions"""
    return engine.discover_causal_relationships()

@app.get("/analytics/summary")
async def get_value_analytics():
    """Get analytics summary for value discovery"""
    
    async with db_pool.acquire() as conn:
        # Total value streams
        total = await conn.fetchval("SELECT COUNT(*) FROM value_streams")
        
        # By type
        type_counts = await conn.fetch("""
            SELECT value_type, COUNT(*) as count 
            FROM value_streams 
            GROUP BY value_type
        """)
        
        # Total potential value
        total_value = await conn.fetchval("""
            SELECT SUM(value_amount) FROM value_streams 
            WHERE implemented = FALSE
        """) or 0
        
        # Implemented value
        implemented_value = await conn.fetchval("""
            SELECT SUM(actual_value) FROM value_streams 
            WHERE implemented = TRUE
        """) or 0
        
        # Average confidence
        avg_confidence = await conn.fetchval("""
            SELECT AVG(confidence) FROM value_streams
        """) or 0
        
        # Total interactions
        total_interactions = await conn.fetchval(
            "SELECT COUNT(*) FROM interactions"
        ) or 0
    
    return {
        "total_value_streams": total,
        "by_type": {row['value_type']: row['count'] for row in type_counts},
        "total_potential_value": float(total_value),
        "implemented_value": float(implemented_value),
        "average_confidence": float(avg_confidence),
        "total_interactions_analyzed": total_interactions,
        "interactions_in_memory": len(engine.interaction_history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/agents/{agent_id}/value-profile")
async def get_agent_value_profile(agent_id: str):
    """Get value profile for a specific agent"""
    
    # Get interactions for this agent
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM interactions 
            WHERE agent_a = $1 OR agent_b = $1
            ORDER BY timestamp DESC
            LIMIT 100
        """, agent_id)
    
    if not rows:
        return {"message": "No interactions found for this agent"}
    
    interactions = [dict(row) for row in rows]
    
    # Calculate agent metrics
    durations = [i.get('duration', 0) for i in interactions if i.get('duration')]
    avg_duration = np.mean(durations) if durations else 0
    
    # Count interactions by type
    interaction_types = {}
    for i in interactions:
        itype = i.get('interaction_type', 'unknown')
        interaction_types[itype] = interaction_types.get(itype, 0) + 1
    
    # Find value streams involving this agent
    value_streams = engine.identify_value_streams(agent_id)
    
    return {
        "agent_id": agent_id,
        "total_interactions": len(interactions),
        "average_duration": float(avg_duration),
        "interaction_type_breakdown": interaction_types,
        "discovered_value_streams": [vs.dict() for vs in value_streams],
        "estimated_annual_value": sum(vs.value_amount for vs in value_streams) * 365,
        "last_active": interactions[0]['timestamp'] if interactions else None
    }
""")

# 4. Создаём Dockerfile для Value Service
with open("backend/services/value-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install fastapi uvicorn asyncpg numpy pandas scipy scikit-learn statsmodels

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
""")

# 5. Создаём SQL для Value Service
with open("infra/postgres/init/05-value.sql", "w") as f:
    f.write("""-- Create value database
CREATE DATABASE augur_value;

\\c augur_value;

-- Interactions table
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY,
    agent_a UUID,
    agent_b UUID,
    interaction_type VARCHAR(50),
    duration FLOAT,
    resources_used JSONB,
    outcomes JSONB,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Value streams table
CREATE TABLE IF NOT EXISTS value_streams (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    value_type VARCHAR(50),
    value_amount FLOAT,
    confidence FLOAT,
    confidence_level VARCHAR(20),
    causal_factors JSONB,
    affected_agents JSONB,
    discovered_at TIMESTAMP,
    implemented BOOLEAN DEFAULT FALSE,
    actual_value FLOAT,
    implementation_cost FLOAT,
    implemented_at TIMESTAMP
);

-- Metrics table for time-series data
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY,
    agent_id UUID,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_interactions_time ON interactions(timestamp);
CREATE INDEX idx_interactions_agents ON interactions(agent_a, agent_b);
CREATE INDEX idx_interactions_type ON interactions(interaction_type);
CREATE INDEX idx_value_streams_type ON value_streams(value_type);
CREATE INDEX idx_value_streams_value ON value_streams(value_amount DESC);
CREATE INDEX idx_metrics_agent_time ON metrics(agent_id, timestamp);
CREATE INDEX idx_metrics_name_time ON metrics(metric_name, timestamp);

-- Create hypertable for time-series if using TimescaleDB
-- SELECT create_hypertable('metrics', 'timestamp');
""")

# 6. Обновляем docker-compose.yml
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""services:
  conflict-service:""", """services:
  value-service:
    build: ./backend/services/value-service
    ports:
      - "8006:8006"
    environment:
      - DB_USER=augur
      - DB_PASSWORD=augur
      - DB_NAME=augur_value
      - DB_HOST=postgres
      - DB_PORT=5432
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - augur-net

  conflict-service:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 7. Создаём тест для Value Service
with open("test_value.py", "w") as f:
    f.write("""import requests
import time
import json
import uuid
from datetime import datetime, timedelta

print("🧪 Testing Value Discovery Service with Causal Inference...\\n")

base = "http://localhost:8006"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Database: {data['database']}")
        print(f"   ✅ Causal Inference: {data['causal_inference']}")
        print(f"   ✅ Interactions in memory: {data['interactions_in_memory']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Create sample interactions
print("\\n2️⃣ Creating sample interactions...")

# Generate 20 interactions with patterns
interactions = []
agent_ids = [str(uuid.uuid4()) for _ in range(4)]

# Pattern 1: Efficiency improvement (duration decreasing over time)
for i in range(10):
    interactions.append({
        "id": str(uuid.uuid4()),
        "agent_a": agent_ids[0],
        "agent_b": agent_ids[1],
        "interaction_type": "collaboration",
        "duration": 100 - i * 5,  # Decreasing duration
        "resources_used": {"cpu": 50, "memory": 256},
        "outcomes": {"quality": 80 + i * 2, "success": True},
        "metadata": {"pattern": "efficiency"},
        "timestamp": (datetime.now() - timedelta(days=30-i)).isoformat()
    })

# Pattern 2: Synergy (two agents perform better together)
for i in range(5):
    interactions.append({
        "id": str(uuid.uuid4()),
        "agent_a": agent_ids[2],
        "agent_b": agent_ids[3],
        "interaction_type": "synergy",
        "duration": 50,
        "resources_used": {"cpu": 80, "memory": 512},
        "outcomes": {"quality": 95, "success": True},
        "metadata": {"pattern": "synergy"},
        "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
    })

# Pattern 3: Individual performances (baseline)
interactions.append({
    "id": str(uuid.uuid4()),
    "agent_a": agent_ids[2],
    "agent_b": "",
    "interaction_type": "solo",
    "duration": 30,
    "resources_used": {"cpu": 40, "memory": 128},
    "outcomes": {"quality": 70, "success": True},
    "metadata": {"pattern": "baseline"},
    "timestamp": datetime.now().isoformat()
})

interactions.append({
    "id": str(uuid.uuid4()),
    "agent_a": agent_ids[3],
    "agent_b": "",
    "interaction_type": "solo",
    "duration": 35,
    "resources_used": {"cpu": 45, "memory": 256},
    "outcomes": {"quality": 75, "success": True},
    "metadata": {"pattern": "baseline"},
    "timestamp": datetime.now().isoformat()
})

try:
    resp = requests.post(f"{base}/interactions/batch", json=interactions)
    if resp.status_code == 200:
        print(f"   ✅ Created {len(interactions)} interactions")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Discover value streams
print("\\n3️⃣ Discovering value streams...")
try:
    resp = requests.get(f"{base}/discover/value-streams")
    if resp.status_code == 200:
        streams = resp.json()
        print(f"   ✅ Discovered {len(streams)} value streams")
        for i, stream in enumerate(streams):
            print(f"      {i+1}. {stream['name']} - {stream['value_type']}: {stream['value_amount']:.2f} (confidence: {stream['confidence']:.2f})")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. List all value streams
print("\\n4️⃣ Listing all value streams...")
try:
    resp = requests.get(f"{base}/value-streams")
    if resp.status_code == 200:
        streams = resp.json()
        print(f"   ✅ Found {len(streams)} streams in database")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Analyze correlations
print("\\n5️⃣ Analyzing correlations...")
try:
    resp = requests.get(f"{base}/correlations")
    if resp.status_code == 200:
        correlations = resp.json()
        print(f"   ✅ Found {len(correlations)} correlations")
        for corr in correlations[:5]:  # Show first 5
            sig = "✓" if corr['significant'] else "✗"
            print(f"      {corr['variable_a']} ↔ {corr['variable_b']}: {corr['correlation']:.2f} (p={corr['p_value']:.3f}) {sig}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Get causal graph
print("\\n6️⃣ Getting causal graph...")
try:
    resp = requests.get(f"{base}/causal-graph")
    if resp.status_code == 200:
        graph = resp.json()
        print(f"   ✅ Nodes: {len(graph['nodes'])}")
        print(f"   ✅ Edges: {len(graph['edges'])}")
        for edge in graph['edges'][:5]:
            print(f"      {edge['from']} → {edge['to']} (strength: {edge['strength']:.2f})")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Get agent value profile
print("\\n7️⃣ Getting agent value profile...")
try:
    resp = requests.get(f"{base}/agents/{agent_ids[0]}/value-profile")
    if resp.status_code == 200:
        profile = resp.json()
        print(f"   ✅ Agent interactions: {profile['total_interactions']}")
        print(f"   ✅ Avg duration: {profile['average_duration']:.1f}")
        print(f"   ✅ Discovered streams: {len(profile['discovered_value_streams'])}")
        print(f"   ✅ Estimated annual value: ${profile['estimated_annual_value']:.2f}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 8. Get analytics summary
print("\\n8️⃣ Getting analytics summary...")
try:
    resp = requests.get(f"{base}/analytics/summary")
    if resp.status_code == 200:
        analytics = resp.json()
        print(f"   ✅ Total value streams: {analytics['total_value_streams']}")
        print(f"   ✅ Total potential value: ${analytics['total_potential_value']:.2f}")
        print(f"   ✅ Average confidence: {analytics['average_confidence']:.2f}")
        print(f"   ✅ Total interactions: {analytics['total_interactions_analyzed']}")
        print("   ✅ By type:")
        for vtype, count in analytics['by_type'].items():
            print(f"      {vtype}: {count}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Value Discovery Service test complete")
print("="*50)
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 6 ВЫПОЛНЕН                                           ║
║  Добавлен Value Discovery Service с Causal Inference        ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Value Discovery Service (порт 8006)
   • Causal Inference Engine
   • Корреляционный анализ
   • Причинно-следственные графы
   • Обнаружение ценностных потоков
   • ROI анализ
   • Агентские профили ценности

🚀 Что делать дальше:
   make build
   make up
   python test_value.py

📊 Новые endpoints:
   POST /interactions                    - запись взаимодействия
   POST /interactions/batch               - пакетная запись
   GET /discover/value-streams             - найти ценностные потоки
   GET /value-streams                      - список ценностных потоков
   POST /value-streams/{id}/analyze-roi    - анализ ROI
   POST /value-streams/{id}/implement      - отметить как реализованное
   GET /correlations                        - корреляционный анализ
   GET /causal-graph                        - причинно-следственный граф
   GET /agents/{id}/value-profile           - профиль ценности агента
   GET /analytics/summary                    - аналитика

💰 Новые возможности:
   • Обнаружение скрытых ценностей
   • Причинно-следственный анализ
   • Предсказание ROI
   • Оптимизация взаимодействий
   • Анализ эффективности агентов
""")
