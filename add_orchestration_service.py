#!/usr/bin/env python3
"""
ШАГ 2: Добавляем Orchestration Service с Redis
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 2: Добавляем Orchestration Service с Redis             ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Orchestration Service
os.makedirs("backend/services/orchestration-service/src", exist_ok=True)

# 2. Создаём рабочий Orchestration Service
with open("backend/services/orchestration-service/src/main.py", "w") as f:
    f.write("""# Orchestration Service with Redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import redis.asyncio as redis
import asyncio
import uuid
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Orchestration Service", version="1.0.0")

# Redis connection
redis_client = None

# Models
class Task(BaseModel):
    id: str
    name: str
    agent_id: str
    status: str = "pending"
    input_data: Dict = {}
    output_data: Optional[Dict] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskCreate(BaseModel):
    name: str
    agent_id: str
    input_data: Dict = {}

class Workflow(BaseModel):
    id: str
    name: str
    tasks: List[str]
    status: str = "pending"
    created_at: datetime

@app.on_event("startup")
async def startup():
    global redis_client
    try:
        redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://redis:6379"),
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Connected to Redis")
        
        # Create task queue
        await redis_client.delete("task_queue")
        logger.info("✅ Task queue initialized")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()
        logger.info("🔌 Redis disconnected")

@app.get("/")
async def root():
    return {
        "service": "Orchestration Service",
        "version": "1.0.0",
        "status": "operational",
        "redis": "connected" if redis_client else "disconnected"
    }

@app.get("/health")
async def health():
    redis_status = "connected" if redis_client and await redis_client.ping() else "disconnected"
    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task and add to queue"""
    task_id = str(uuid.uuid4())
    task_data = Task(
        id=task_id,
        name=task.name,
        agent_id=task.agent_id,
        input_data=task.input_data,
        created_at=datetime.now()
    )
    
    # Store task in Redis
    await redis_client.set(
        f"task:{task_id}",
        task_data.json(),
        ex=3600  # 1 hour TTL
    )
    
    # Add to queue
    await redis_client.lpush("task_queue", task_id)
    
    logger.info(f"✅ Task created: {task_id}")
    return task_data

@app.get("/tasks", response_model=List[Task])
async def list_tasks(limit: int = 100):
    """List all tasks from Redis"""
    keys = await redis_client.keys("task:*")
    tasks = []
    for key in keys[:limit]:
        task_data = await redis_client.get(key)
        if task_data:
            tasks.append(Task.parse_raw(task_data))
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get task by ID"""
    task_data = await redis_client.get(f"task:{task_id}")
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task.parse_raw(task_data)

@app.post("/tasks/{task_id}/start")
async def start_task(task_id: str):
    """Mark task as started"""
    task_data = await redis_client.get(f"task:{task_id}")
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = Task.parse_raw(task_data)
    task.status = "running"
    task.started_at = datetime.now()
    
    await redis_client.set(f"task:{task_id}", task.json())
    logger.info(f"▶ Task started: {task_id}")
    return task

@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, output: Dict):
    """Mark task as completed"""
    task_data = await redis_client.get(f"task:{task_id}")
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = Task.parse_raw(task_data)
    task.status = "completed"
    task.completed_at = datetime.now()
    task.output_data = output
    
    await redis_client.set(f"task:{task_id}", task.json())
    
    # Remove from queue if still there
    await redis_client.lrem("task_queue", 0, task_id)
    
    logger.info(f"✅ Task completed: {task_id}")
    return task

@app.get("/queue/next")
async def get_next_task():
    """Get next task from queue (for workers)"""
    task_id = await redis_client.rpop("task_queue")
    if not task_id:
        return {"message": "No tasks in queue"}
    
    task_data = await redis_client.get(f"task:{task_id}")
    if not task_data:
        return {"message": "Task data not found"}
    
    return Task.parse_raw(task_data)

@app.get("/queue/status")
async def queue_status():
    """Get queue status"""
    queue_length = await redis_client.llen("task_queue")
    return {
        "queue_length": queue_length,
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete task"""
    result = await redis_client.delete(f"task:{task_id}")
    if result == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove from queue if present
    await redis_client.lrem("task_queue", 0, task_id)
    
    logger.info(f"✅ Task deleted: {task_id}")
    return {"message": "Task deleted"}
""")

# 3. Создаём Dockerfile для Orchestration Service
with open("backend/services/orchestration-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN pip install fastapi uvicorn redis aioredis pydantic

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
""")

# 4. Обновляем docker-compose.yml (добавляем Redis и Orchestration)
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""services:
  postgres:""", """services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - augur-net

  orchestration-service:
    build: ./backend/services/orchestration-service
    ports:
      - "8002:8002"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - augur-net

  postgres:""")

new_compose = new_compose.replace("volumes:\n  postgres-data:", """volumes:
  postgres-data:
  redis-data:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 5. Создаём тест для нового сервиса
with open("test_orchestration.py", "w") as f:
    f.write("""import requests
import time
import json

print("🧪 Testing Orchestration Service...\\n")

base = "http://localhost:8002"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Redis: {data['redis']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Create task
print("\\n2️⃣ Creating task...")
task_data = {
    "name": "Test Task",
    "agent_id": "agent-123",
    "input_data": {"command": "test", "params": {"a": 1, "b": 2}}
}

try:
    resp = requests.post(f"{base}/tasks", json=task_data)
    if resp.status_code == 200:
        task = resp.json()
        task_id = task['id']
        print(f"   ✅ Task created: {task_id}")
        print(f"   📋 Status: {task['status']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. List tasks
print("\\n3️⃣ Listing tasks...")
try:
    resp = requests.get(f"{base}/tasks")
    if resp.status_code == 200:
        tasks = resp.json()
        print(f"   ✅ Found {len(tasks)} tasks")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Check queue
print("\\n4️⃣ Queue status...")
try:
    resp = requests.get(f"{base}/queue/status")
    if resp.status_code == 200:
        queue = resp.json()
        print(f"   ✅ Queue length: {queue['queue_length']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Orchestration Service test complete")
print("="*50)
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 2 ВЫПОЛНЕН                                           ║
║  Добавлен Orchestration Service с Redis                      ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Orchestration Service (порт 8002)
   • Redis (порт 6379)
   • Task queue
   • Background jobs

🚀 Что делать дальше:
   make build
   make up
   python test_orchestration.py

📊 Новые endpoints:
   POST /tasks      - создать задачу
   GET /tasks       - список задач
   GET /queue/next  - взять следующую задачу
   GET /queue/status- статус очереди
""")
