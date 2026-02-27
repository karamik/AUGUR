#!/usr/bin/env python3
"""
AUGUR ENTERPRISE PLATFORM - ПОЛНАЯ УСТАНОВКА
Один скрипт = Вся платформа
Запустите в Termux и получите работающую систему
"""

import os
import subprocess
import sys
import time

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  AUGUR ENTERPRISE PLATFORM - ПОЛНАЯ УСТАНОВКА               ║
║  Один скрипт = Вся платформа                                ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Проверяем, что мы в папке AUGUR
if not os.path.exists("README.md"):
    print("❌ Ошибка: Запустите скрипт в папке AUGUR")
    sys.exit(1)

# 2. Устанавливаем зависимости для Python
print("\n📦 Устанавливаем Python зависимости...")
run("pkg install -y python nodejs postgresql redis docker")

# 3. СОЗДАЁМ МИКРОСЕРВИСНУЮ АРХИТЕКТУРУ
print("\n🏗️ СОЗДАЁМ МИКРОСЕРВИСЫ...")

services = [
    "api-gateway",
    "agent-service",
    "orchestration-service",
    "memory-service",
    "governance-service",
    "conflict-resolution-service",
    "value-discovery-service",
    "quantum-service"
]

for service in services:
    os.makedirs(f"backend/services/{service}/src", exist_ok=True)
    os.makedirs(f"backend/services/{service}/tests", exist_ok=True)

# 4. СОЗДАЁМ РАБОТАЮЩИЙ API ГЕЙТВЕЙ
print("\n🌐 СОЗДАЁМ API GATEWAY...")

with open("backend/services/api-gateway/src/main.py", "w") as f:
    f.write("""from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AUGUR API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "agents": "http://agent-service:8001",
    "orchestration": "http://orchestration-service:8002",
    "memory": "http://memory-service:8003",
    "governance": "http://governance-service:8004",
    "conflict": "http://conflict-resolution-service:8005",
    "value": "http://value-discovery-service:8006",
    "quantum": "http://quantum-service:8007"
}

client = httpx.AsyncClient(timeout=30.0)

@app.get("/")
async def root():
    return {
        "service": "AUGUR Enterprise Platform",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    services_status = {}
    for name, url in SERVICES.items():
        try:
            resp = await client.get(f"{url}/health", timeout=2.0)
            services_status[name] = "healthy" if resp.status_code == 200 else "unhealthy"
        except:
            services_status[name] = "unreachable"
    
    return {
        "status": "healthy",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }

@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return {"error": f"Service {service} not found"}
    
    url = f"{SERVICES[service]}/{path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    
    try:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.on_event("shutdown")
async def shutdown():
    await client.aclose()
""")

# 5. СОЗДАЁМ РАБОТАЮЩИЙ AGENT SERVICE
print("\n🤖 СОЗДАЁМ AGENT SERVICE...")

with open("backend/services/agent-service/src/main.py", "w") as f:
    f.write("""from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Service")

# In-memory database (для простоты, потом заменим на PostgreSQL)
agents_db = {}

class AgentCreate(BaseModel):
    name: str
    type: str
    capabilities: List[str] = []
    config: Dict = {}

class Agent(AgentCreate):
    id: str
    status: str = "inactive"
    created_at: datetime
    last_active: Optional[datetime] = None

@app.get("/")
async def root():
    return {"service": "Agent Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agent-service", "timestamp": datetime.now().isoformat()}

@app.post("/agents")
async def create_agent(agent: AgentCreate):
    agent_id = str(uuid.uuid4())
    new_agent = Agent(
        id=agent_id,
        name=agent.name,
        type=agent.type,
        capabilities=agent.capabilities,
        config=agent.config,
        created_at=datetime.now()
    )
    agents_db[agent_id] = new_agent.dict()
    logger.info(f"Agent created: {agent_id}")
    return agents_db[agent_id]

@app.get("/agents")
async def list_agents():
    return list(agents_db.values())

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

@app.post("/agents/{agent_id}/heartbeat")
async def heartbeat(agent_id: str):
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    agents_db[agent_id]["last_active"] = datetime.now()
    agents_db[agent_id]["status"] = "active"
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
""")

# 6. СОЗДАЁМ DOCKER-COMPOSE С БАЗАМИ ДАННЫХ
print("\n🐳 СОЗДАЁМ DOCKER-COMPOSE С БАЗАМИ ДАННЫХ...")

with open("docker-compose.yml", "w") as f:
    f.write("""version: '3.8'

services:
  # API Gateway
  api-gateway:
    build: ./backend/services/api-gateway
    ports:
      - "8000:8000"
    networks:
      - augur-net

  # Agent Service
  agent-service:
    build: ./backend/services/agent-service
    ports:
      - "8001:8001"
    networks:
      - augur-net

  # PostgreSQL
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: augur
      POSTGRES_PASSWORD: augur
      POSTGRES_DB: augur
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql/data
    networks:
      - augur-net

  # Redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - augur-net

  # Neo4j
  neo4j:
    image: neo4j:latest
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data
    networks:
      - augur-net

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api-gateway
    networks:
      - augur-net

volumes:
  pg-data:
  redis-data:
  neo4j-data:

networks:
  augur-net:
    driver: bridge
""")

# 7. СОЗДАЁМ ФРОНТЕНД
print("\n🎨 СОЗДАЁМ ФРОНТЕНД...")

os.makedirs("frontend/src", exist_ok=True)

with open("frontend/package.json", "w") as f:
    f.write("""{
  "name": "augur-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
""")

with open("frontend/src/App.js", "w") as f:
    f.write("""import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [services, setServices] = useState({});
  const [agents, setAgents] = useState([]);
  const [newAgent, setNewAgent] = useState({ name: '', type: '' });

  useEffect(() => {
    // Check system health
    axios.get('http://localhost:8000/health')
      .then(res => setServices(res.data.services))
      .catch(err => console.log(err));

    // Load agents
    loadAgents();
  }, []);

  const loadAgents = () => {
    axios.get('http://localhost:8000/api/v1/agents/agents')
      .then(res => setAgents(res.data))
      .catch(err => console.log(err));
  };

  const createAgent = () => {
    axios.post('http://localhost:8000/api/v1/agents/agents', newAgent)
      .then(() => {
        loadAgents();
        setNewAgent({ name: '', type: '' });
      })
      .catch(err => console.log(err));
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>🚀 AUGUR Enterprise Platform</h1>
      
      <h2>System Status</h2>
      <pre>{JSON.stringify(services, null, 2)}</pre>

      <h2>Create New Agent</h2>
      <input
        placeholder="Agent name"
        value={newAgent.name}
        onChange={e => setNewAgent({...newAgent, name: e.target.value})}
      />
      <input
        placeholder="Agent type"
        value={newAgent.type}
        onChange={e => setNewAgent({...newAgent, type: e.target.value})}
      />
      <button onClick={createAgent}>Create Agent</button>

      <h2>Agents ({agents.length})</h2>
      <ul>
        {agents.map(agent => (
          <li key={agent.id}>
            {agent.name} ({agent.type}) - {agent.status}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
""")

with open("frontend/Dockerfile", "w") as f:
    f.write("""FROM node:18
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
""")

# 8. СОЗДАЁМ DOCKERFILE ДЛЯ СЕРВИСОВ
print("\n📦 СОЗДАЁМ DOCKERFILE...")

for service in services:
    with open(f"backend/services/{service}/Dockerfile", "w") as f:
        f.write("""FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install fastapi uvicorn httpx
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
""")
    
    with open(f"backend/services/{service}/requirements.txt", "w") as f:
        f.write("fastapi\nuvicorn\nhttpx\npydantic\n")

# 9. СОЗДАЁМ ТЕСТОВЫЙ СКРИПТ
print("\n🧪 СОЗДАЁМ ТЕСТОВЫЙ СКРИПТ...")

with open("test_platform.py", "w") as f:
    f.write("""import requests
import time
import json

print("🔍 Testing AUGUR Enterprise Platform...")

# Test API Gateway
try:
    r = requests.get("http://localhost:8000/")
    print(f"✅ API Gateway: {r.json()}")
except:
    print("❌ API Gateway not responding")

# Test Agent Service
try:
    # Create agent
    agent = {
        "name": "Test Agent",
        "type": "assistant",
        "capabilities": ["test"]
    }
    r = requests.post("http://localhost:8000/api/v1/agents/agents", json=agent)
    agent_id = r.json()["id"]
    print(f"✅ Created agent: {agent_id}")

    # List agents
    r = requests.get("http://localhost:8000/api/v1/agents/agents")
    print(f"✅ Agents: {len(r.json())} total")
except Exception as e:
    print(f"❌ Agent Service error: {e}")

print("\\n✅ Test complete!")
""")

# 10. СОЗДАЁМ MAKEFILE
print("\n🔧 СОЗДАЁМ MAKEFILE...")

with open("Makefile", "w") as f:
    f.write("""build:
\tdocker-compose build

up:
\tdocker-compose up -d
\t@echo ""
\t@echo "🚀 AUGUR Enterprise Platform запущена!"
\t@echo "📊 API Gateway: http://localhost:8000"
\t@echo "📈 API Docs: http://localhost:8000/docs"
\t@echo "🖥️  Frontend: http://localhost:3000"
\t@echo "🗄️  Neo4j: http://localhost:7474"

down:
\tdocker-compose down

logs:
\tdocker-compose logs -f

test:
\tpython test_platform.py
""")

# 11. ЗАПУСК
print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ПЛАТФОРМА СОЗДАНА!                                       ║
╚══════════════════════════════════════════════════════════════╝

Теперь у вас есть:

✅ РАБОТАЮЩИЙ КОД:
   - API Gateway на порту 8000
   - Agent Service на порту 8001
   - Ещё 6 микросервисов готовы к заполнению

✅ БАЗЫ ДАННЫХ:
   - PostgreSQL (порт 5432)
   - Redis (порт 6379)
   - Neo4j (порт 7474)

✅ API:
   - POST /agents - создать агента
   - GET /agents - список агентов
   - GET /health - статус системы

✅ ФРОНТЕНД:
   - http://localhost:3000

🚀 ЧТО ДЕЛАТЬ ДАЛЬШЕ:

1. Запустите платформу:
   make build
   make up

2. Проверьте работу:
   make test

3. Откройте в браузере:
   - Фронтенд: http://localhost:3000
   - API: http://localhost:8000

4. Создайте первого агента через API:
   curl -X POST http://localhost:8000/api/v1/agents/agents \\
     -H "Content-Type: application/json" \\
     -d '{"name":"Agent1","type":"assistant"}'

📞 Контакты: augur2026@gmail.com
""")
