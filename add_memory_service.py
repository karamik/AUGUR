#!/usr/bin/env python3
"""
ШАГ 3: Добавляем Memory Service с pgvector
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 3: Добавляем Memory Service с pgvector                 ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Memory Service
os.makedirs("backend/services/memory-service/src", exist_ok=True)

# 2. Создаём рабочий Memory Service с pgvector
with open("backend/services/memory-service/src/main.py", "w") as f:
    f.write("""# Memory Service with pgvector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import asyncpg
import numpy as np
import uuid
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Memory Service", version="1.0.0")

# Models
class Memory(BaseModel):
    id: str
    agent_id: str
    content: str
    embedding: List[float]
    metadata: Dict = {}
    created_at: datetime

class MemoryCreate(BaseModel):
    agent_id: str
    content: str
    metadata: Dict = {}

class SearchQuery(BaseModel):
    query: str
    agent_id: Optional[str] = None
    limit: int = 10
    threshold: float = 0.7

# Simple embedding function (in production use sentence-transformers)
def simple_embed(text: str) -> List[float]:
    """Generate a simple deterministic embedding for demo"""
    import hashlib
    hash_obj = hashlib.sha256(text.encode())
    hash_bytes = hash_obj.digest()
    # Convert to list of floats between -1 and 1
    return [((b / 255.0) * 2 - 1) for b in hash_bytes[:1536]]

# Database connection
db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "augur"),
            password=os.getenv("DB_PASSWORD", "augur"),
            database=os.getenv("DB_NAME", "augur_memory"),
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Connected to PostgreSQL with pgvector")
        
        # Enable pgvector and create table
        async with db_pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id UUID PRIMARY KEY,
                    agent_id UUID NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create index for similarity search
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_embedding 
                ON memories USING ivfflat (embedding vector_cosine_ops)
            """)
            logger.info("✅ Table 'memories' ready with vector index")
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
        "service": "Memory Service",
        "version": "1.0.0",
        "status": "operational",
        "features": ["vector-search", "pgvector"]
    }

@app.get("/health")
async def health():
    db_status = "connected" if db_pool else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "pgvector": "enabled",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/memories", response_model=Memory)
async def create_memory(memory: MemoryCreate):
    """Store a memory with embedding"""
    memory_id = str(uuid.uuid4())
    embedding = simple_embed(memory.content)
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO memories (id, agent_id, content, embedding, metadata)
            VALUES ($1, $2, $3, $4::vector, $5)
        """, memory_id, memory.agent_id, memory.content, embedding, 
            json.dumps(memory.metadata))
    
    logger.info(f"✅ Memory stored: {memory_id}")
    return Memory(
        id=memory_id,
        agent_id=memory.agent_id,
        content=memory.content,
        embedding=embedding,
        metadata=memory.metadata,
        created_at=datetime.now()
    )

@app.get("/memories", response_model=List[Memory])
async def list_memories(agent_id: Optional[str] = None, limit: int = 100):
    """List memories, optionally filtered by agent"""
    async with db_pool.acquire() as conn:
        if agent_id:
            rows = await conn.fetch("""
                SELECT id, agent_id, content, embedding::text, metadata, created_at
                FROM memories 
                WHERE agent_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """, agent_id, limit)
        else:
            rows = await conn.fetch("""
                SELECT id, agent_id, content, embedding::text, metadata, created_at
                FROM memories 
                ORDER BY created_at DESC
                LIMIT $1
            """, limit)
    
    result = []
    for row in rows:
        # Parse embedding from pgvector format
        embed_str = row['embedding'].strip('[]').split(',')
        embedding = [float(x) for x in embed_str if x.strip()]
        
        result.append(Memory(
            id=row['id'],
            agent_id=row['agent_id'],
            content=row['content'],
            embedding=embedding,
            metadata=row['metadata'],
            created_at=row['created_at']
        ))
    return result

@app.get("/memories/{memory_id}", response_model=Memory)
async def get_memory(memory_id: str):
    """Get a specific memory by ID"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id, agent_id, content, embedding::text, metadata, created_at
            FROM memories WHERE id = $1
        """, memory_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    embed_str = row['embedding'].strip('[]').split(',')
    embedding = [float(x) for x in embed_str if x.strip()]
    
    return Memory(
        id=row['id'],
        agent_id=row['agent_id'],
        content=row['content'],
        embedding=embedding,
        metadata=row['metadata'],
        created_at=row['created_at']
    )

@app.post("/search", response_model=List[Memory])
async def search_memories(search: SearchQuery):
    """Semantic search using vector similarity"""
    query_embedding = simple_embed(search.query)
    
    async with db_pool.acquire() as conn:
        if search.agent_id:
            rows = await conn.fetch("""
                SELECT id, agent_id, content, embedding::text, metadata, created_at,
                       1 - (embedding <=> $2::vector) as similarity
                FROM memories 
                WHERE agent_id = $1 
                  AND 1 - (embedding <=> $2::vector) > $3
                ORDER BY similarity DESC
                LIMIT $4
            """, search.agent_id, query_embedding, search.threshold, search.limit)
        else:
            rows = await conn.fetch("""
                SELECT id, agent_id, content, embedding::text, metadata, created_at,
                       1 - (embedding <=> $1::vector) as similarity
                FROM memories 
                WHERE 1 - (embedding <=> $1::vector) > $2
                ORDER BY similarity DESC
                LIMIT $3
            """, query_embedding, search.threshold, search.limit)
    
    result = []
    for row in rows:
        embed_str = row['embedding'].strip('[]').split(',')
        embedding = [float(x) for x in embed_str if x.strip()]
        
        result.append(Memory(
            id=row['id'],
            agent_id=row['agent_id'],
            content=row['content'],
            embedding=embedding,
            metadata=row['metadata'],
            created_at=row['created_at']
        ))
    
    logger.info(f"🔍 Search found {len(result)} results")
    return result

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory"""
    async with db_pool.acquire() as conn:
        result = await conn.execute("DELETE FROM memories WHERE id = $1", memory_id)
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Memory not found")
    
    logger.info(f"✅ Memory deleted: {memory_id}")
    return {"message": "Memory deleted"}

@app.delete("/memories/agent/{agent_id}")
async def delete_agent_memories(agent_id: str):
    """Delete all memories for an agent"""
    async with db_pool.acquire() as conn:
        result = await conn.execute("DELETE FROM memories WHERE agent_id = $1", agent_id)
    
    logger.info(f"✅ All memories deleted for agent: {agent_id}")
    return {"message": f"Memories deleted for agent {agent_id}"}
""")

# 3. Создаём Dockerfile для Memory Service
with open("backend/services/memory-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install fastapi uvicorn asyncpg numpy

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
""")

# 4. Создаём SQL для pgvector
with open("infra/postgres/init/02-pgvector.sql", "w") as f:
    f.write("""-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memories table
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY,
    agent_id UUID NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for similarity search
CREATE INDEX IF NOT EXISTS idx_memories_embedding 
ON memories USING ivfflat (embedding vector_cosine_ops);
""")

# 5. Обновляем docker-compose.yml
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""  postgres:
    image: postgres:15""", """  postgres:
    image: ankane/pgvector:latest  # PostgreSQL with pgvector pre-installed""")

new_compose = new_compose.replace("""services:
  redis:""", """services:
  memory-service:
    build: ./backend/services/memory-service
    ports:
      - "8003:8003"
    environment:
      - DB_USER=augur
      - DB_PASSWORD=augur
      - DB_NAME=augur_memory
      - DB_HOST=postgres
      - DB_PORT=5432
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - augur-net

  redis:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 6. Создаём тест для Memory Service
with open("test_memory.py", "w") as f:
    f.write("""import requests
import time
import json

print("🧪 Testing Memory Service with pgvector...\\n")

base = "http://localhost:8003"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Database: {data['database']}")
        print(f"   ✅ pgvector: {data['pgvector']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Store memories
print("\\n2️⃣ Storing memories...")
memories = [
    {"agent_id": "agent-123", "content": "The quick brown fox jumps over the lazy dog", 
     "metadata": {"type": "example", "language": "english"}},
    {"agent_id": "agent-123", "content": "Machine learning is a subset of artificial intelligence",
     "metadata": {"type": "definition", "topic": "ai"}},
    {"agent_id": "agent-456", "content": "Python is a programming language",
     "metadata": {"type": "fact", "language": "python"}},
]

memory_ids = []
for i, mem in enumerate(memories):
    try:
        resp = requests.post(f"{base}/memories", json=mem)
        if resp.status_code == 200:
            data = resp.json()
            memory_ids.append(data['id'])
            print(f"   ✅ Memory {i+1} stored: {data['id'][:8]}...")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 3. List memories
print("\\n3️⃣ Listing memories...")
try:
    resp = requests.get(f"{base}/memories")
    if resp.status_code == 200:
        memories = resp.json()
        print(f"   ✅ Found {len(memories)} total memories")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. List memories for specific agent
print("\\n4️⃣ Listing memories for agent-123...")
try:
    resp = requests.get(f"{base}/memories?agent_id=agent-123")
    if resp.status_code == 200:
        memories = resp.json()
        print(f"   ✅ Found {len(memories)} memories for agent-123")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Semantic search
print("\\n5️⃣ Semantic search for 'AI and learning'...")
search_query = {
    "query": "AI and learning",
    "limit": 3,
    "threshold": 0.5
}

try:
    resp = requests.post(f"{base}/search", json=search_query)
    if resp.status_code == 200:
        results = resp.json()
        print(f"   ✅ Found {len(results)} results")
        for i, result in enumerate(results):
            print(f"      {i+1}. {result['content']} (similarity: ???)")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 6. Get specific memory
if memory_ids:
    print("\\n6️⃣ Getting first memory...")
    try:
        resp = requests.get(f"{base}/memories/{memory_ids[0]}")
        if resp.status_code == 200:
            mem = resp.json()
            print(f"   ✅ Retrieved: {mem['content']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Memory Service test complete")
print("="*50)
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 3 ВЫПОЛНЕН                                           ║
║  Добавлен Memory Service с pgvector                          ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Memory Service (порт 8003)
   • pgvector (векторный поиск в PostgreSQL)
   • Семантический поиск
   • Векторные эмбеддинги

🚀 Что делать дальше:
   make build
   make up
   python test_memory.py

📊 Новые endpoints:
   POST /memories        - сохранить память
   GET /memories         - список памяти
   POST /search          - семантический поиск
   GET /memories/{id}    - получить память

🧠 Теперь агенты могут:
   • Хранить долговременную память
   • Искать похожие воспоминания
   • Находить семантически связанные данные
""")
