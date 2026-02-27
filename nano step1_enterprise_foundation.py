#!/usr/bin/env python3
"""
AUGUR Enterprise Platform - Step 1: Foundation
Запустите этот скрипт в корневой папке проекта (рядом с README.md)
Он создаст полноценную микросервисную архитектуру для enterprise-платформы.
"""

import os
import sys
import subprocess
from pathlib import Path

# --- Цветной вывод для телефона ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"{Colors.OKBLUE}▶ {msg}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def run_cmd(cmd, cwd=None):
    """Безопасный запуск команд с выводом в консоль"""
    print_step(f"Executing: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Command failed: {cmd}")
        print(result.stderr)
        return False
    if result.stdout:
        print(result.stdout)
    return True

# --- Главная функция ---
def main():
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  AUGUR Enterprise Platform - Step 1: Foundation             ║")
    print("║  Превращаем репозиторий в реальную enterprise-платформу    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(Colors.ENDC)

    # Проверяем, что мы в корне репозитория AUGUR
    if not os.path.exists("README.md") or "AUGUR" not in open("README.md").read():
        print_error("Скрипт нужно запускать из корневой папки репозитория AUGUR (где лежит README.md)")
        sys.exit(1)

    # 1. Создаем структуру enterprise-микросервисов
    print_step("Создаём структуру микросервисов...")
    microservices = [
        "api-gateway",
        "agent-service",
        "orchestration-service",
        "memory-service",
        "governance-service",
        "conflict-resolution-service",
        "value-discovery-service",
        "quantum-collective-service"
    ]

    # Создаём папки для сервисов, перенося существующий код
    os.makedirs("backend/old", exist_ok=True)
    for item in os.listdir("backend"):
        if item not in ["services", "shared", "old"] and os.path.isfile(f"backend/{item}"):
            os.rename(f"backend/{item}", f"backend/old/{item}")

    os.makedirs("backend/services", exist_ok=True)
    os.makedirs("backend/shared", exist_ok=True)

    for service in microservices:
        service_path = f"backend/services/{service}"
        os.makedirs(f"{service_path}/src", exist_ok=True)
        os.makedirs(f"{service_path}/tests", exist_ok=True)
        print(f"  - {service}")

    # Переносим существующий fingerprint.py в новый сервис
    if os.path.exists("backend/fingerprint.py"):
        os.rename("backend/fingerprint.py", "backend/services/agent-service/src/fingerprint.py")
        print_step("Перенесён существующий fingerprint.py")

    # 2. Создаём корневой docker-compose.yml
    print_step("Создаём production-ready docker-compose.yml...")
    with open("docker-compose.yml", "w") as f:
        f.write("""version: '3.8'

x-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

services:
  # API Gateway
  api-gateway:
    build:
      context: ./backend/services/api-gateway
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur
      - REDIS_URL=redis://redis:6379
      - SERVICE_AGENT=http://agent-service:8001
      - SERVICE_ORCHESTRATION=http://orchestration-service:8002
      - SERVICE_MEMORY=http://memory-service:8003
      - SERVICE_GOVERNANCE=http://governance-service:8004
      - SERVICE_CONFLICT=http://conflict-resolution-service:8005
      - SERVICE_VALUE=http://value-discovery-service:8006
      - SERVICE_QUANTUM=http://quantum-collective-service:8007
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - augur-network
    logging: *default-logging

  # Agent Service
  agent-service:
    build:
      context: ./backend/services/agent-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_agents
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - augur-network
    logging: *default-logging

  # Orchestration Service
  orchestration-service:
    build:
      context: ./backend/services/orchestration-service
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_orchestration
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - augur-network
    logging: *default-logging

  # Memory Service (с pgvector)
  memory-service:
    build:
      context: ./backend/services/memory-service
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_memory
      - REDIS_URL=redis://redis:6379
      - NEO4J_URI=bolt://neo4j:7687
    depends_on:
      - postgres
      - redis
      - neo4j
    networks:
      - augur-network
    logging: *default-logging

  # Governance Service
  governance-service:
    build:
      context: ./backend/services/governance-service
      dockerfile: Dockerfile
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_governance
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - augur-network
    logging: *default-logging

  # Conflict Resolution Service
  conflict-resolution-service:
    build:
      context: ./backend/services/conflict-resolution-service
      dockerfile: Dockerfile
    ports:
      - "8005:8005"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_conflict
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - augur-network
    logging: *default-logging

  # Value Discovery Service
  value-discovery-service:
    build:
      context: ./backend/services/value-discovery-service
      dockerfile: Dockerfile
    ports:
      - "8006:8006"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_value
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - augur-network
    logging: *default-logging

  # Quantum Collective Service
  quantum-collective-service:
    build:
      context: ./backend/services/quantum-collective-service
      dockerfile: Dockerfile
    ports:
      - "8007:8007"
    environment:
      - DATABASE_URL=postgresql://augur:augur@postgres:5432/augur_quantum
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - augur-network
    logging: *default-logging

  # PostgreSQL with TimescaleDB and pgvector
  postgres:
    image: timescale/timescaledb:latest-pg14
    environment:
      - POSTGRES_USER=augur
      - POSTGRES_PASSWORD=augur
      - POSTGRES_DB=augur
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./infra/postgres/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U augur"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - augur-network
    logging: *default-logging

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - augur-network
    logging: *default-logging

  # Neo4j
  neo4j:
    image: neo4j:latest
    environment:
      - NEO4J_AUTH=neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j-data:/data
    networks:
      - augur-network
    logging: *default-logging

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - api-gateway
    networks:
      - augur-network
    logging: *default-logging

volumes:
  postgres-data:
  redis-data:
  neo4j-data:

networks:
  augur-network:
    driver: bridge
""")
    print_success("docker-compose.yml создан")

    # 3. Создаём базовый код для всех микросервисов
    print_step("Создаём базовый код для микросервисов...")

    # Общий requirements.txt для всех сервисов
    common_reqs = """fastapi==0.104.1
uvicorn[standard]==0.24.0
asyncpg==0.29.0
redis==5.0.1
pydantic==2.4.2
python-dotenv==1.0.0
httpx==0.25.1
numpy==1.24.3
scikit-learn==1.3.0
"""

    # Общий Dockerfile
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

    # Шаблон main.py для сервиса
    main_template = """from fastapi import FastAPI
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="{service_name}", version="0.1.0")

@app.on_event("startup")
async def startup():
    logger.info("{service_name} started")

@app.get("/health")
async def health():
    return {{
        "status": "healthy",
        "service": "{service_name}",
        "timestamp": datetime.now().isoformat()
    }}

@app.get("/")
async def root():
    return {{
        "service": "{service_name}",
        "version": "0.1.0",
        "status": "operational"
    }}
"""

    for service in microservices:
        service_path = f"backend/services/{service}"

        # Создаём requirements.txt
        with open(f"{service_path}/requirements.txt", "w") as f:
            f.write(common_reqs)

        # Создаём Dockerfile
        with open(f"{service_path}/Dockerfile", "w") as f:
            f.write(dockerfile_content)

        # Создаём src/main.py
        service_display = service.replace("-", " ").title()
        with open(f"{service_path}/src/main.py", "w") as f:
            f.write(main_template.format(service_name=service_display))

        # Создаём __init__.py
        with open(f"{service_path}/src/__init__.py", "w") as f:
            f.write("# AUGUR microservice\n")

        print(f"  - {service}")

    # 4. Создаём инициализацию баз данных
    print_step("Создаём инициализацию баз данных...")
    os.makedirs("infra/postgres/init", exist_ok=True)

    with open("infra/postgres/init/01-init.sql", "w") as f:
        f.write("""-- Создаём базы данных для каждого сервиса
CREATE DATABASE augur_agents;
CREATE DATABASE augur_orchestration;
CREATE DATABASE augur_memory;
CREATE DATABASE augur_governance;
CREATE DATABASE augur_conflict;
CREATE DATABASE augur_value;
CREATE DATABASE augur_quantum;

-- Подключаемся к augur_memory и включаем pgvector
\\c augur_memory;
CREATE EXTENSION IF NOT EXISTS vector;

-- Таблица для векторов памяти
CREATE TABLE IF NOT EXISTS memory_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID,
    vector vector(1536),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаём индекс для поиска по сходству
CREATE INDEX IF NOT EXISTS idx_memory_vectors_vector ON memory_vectors 
USING ivfflat (vector vector_cosine_ops);

-- Подключаемся к augur_agents и создаём таблицу агентов
\\c augur_agents;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'inactive',
    capabilities JSONB,
    config JSONB,
    fingerprint_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

-- Таблица для поведенческих паттернов
CREATE TABLE IF NOT EXISTS behavioral_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id),
    pattern_hash VARCHAR(64),
    pattern_data JSONB,
    entropy_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создаём базу для метрик (TimescaleDB)
\\c augur;
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS metrics (
    time TIMESTAMPTZ NOT NULL,
    service VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    tags JSONB
);

SELECT create_hypertable('metrics', 'time', if_not_exists => TRUE);
""")
    print_success("Инициализация БД создана")

    # 5. Улучшаем frontend структуру
    print_step("Улучшаем структуру фронтенда...")
    frontend_dirs = [
        "frontend/src/components/dashboard",
        "frontend/src/components/agents",
        "frontend/src/components/workflows",
        "frontend/src/components/governance",
        "frontend/src/components/analytics",
        "frontend/src/hooks",
        "frontend/src/services",
        "frontend/src/store",
        "frontend/src/types",
        "frontend/public"
    ]

    for d in frontend_dirs:
        os.makedirs(d, exist_ok=True)

    # Создаём package.json для React + TypeScript
    with open("frontend/package.json", "w") as f:
        f.write("""{
  "name": "augur-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^5.0.0",
    "axios": "^1.6.0",
    "recharts": "^2.10.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
""")

    # Создаём tsconfig.json
    with open("frontend/tsconfig.json", "w") as f:
        f.write("""{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
""")

    # Создаём базовый App.tsx
    with open("frontend/src/App.tsx", "w") as f:
        f.write("""import React from 'react';
import Dashboard from './components/dashboard/Dashboard';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;
""")

    # Создаём Dashboard компонент
    with open("frontend/src/components/dashboard/Dashboard.tsx", "w") as f:
        f.write("""import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Dashboard: React.FC = () => {
  const [services, setServices] = useState<any>({});

  useEffect(() => {
    axios.get('http://localhost:8000/health')
      .then(response => setServices(response.data.services))
      .catch(error => console.error('Error fetching services:', error));
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>AUGUR Enterprise Platform</h1>
      <h2>System Status</h2>
      <pre>{JSON.stringify(services, null, 2)}</pre>
    </div>
  );
};

export default Dashboard;
""")

    # Создаём Dockerfile для фронтенда
    with open("frontend/Dockerfile", "w") as f:
        f.write("""FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

CMD ["npm", "start"]
""")
    print_success("Фронтенд обновлён")

    # 6. Создаём Makefile
    print_step("Создаём Makefile...")
    with open("Makefile", "w") as f:
        f.write("""# AUGUR Enterprise Platform Makefile

.PHONY: help build up down logs clean init test

help:
\t@echo "Available commands:"
\t@echo "  make build    - Build all Docker images"
\t@echo "  make up       - Start all services"
\t@echo "  make down     - Stop all services"
\t@echo "  make logs     - View logs"
\t@echo "  make clean    - Remove containers and volumes"
\t@echo "  make init     - Initialize the platform"
\t@echo "  make test     - Run tests"

build:
\tdocker-compose build

up:
\tdocker-compose up -d
\t@echo ""
\t@echo "🚀 AUGUR Enterprise Platform is starting..."
\t@echo "📊 API Gateway: http://localhost:8000"
\t@echo "📈 API Docs: http://localhost:8000/docs"
\t@echo "🖥️  Frontend: http://localhost:3000"
\t@echo "🗄️  Neo4j Browser: http://localhost:7474"

down:
\tdocker-compose down

logs:
\tdocker-compose logs -f

clean:
\tdocker-compose down -v
\tdocker system prune -f

init:
\t@echo "Initializing databases..."
\tdocker-compose up -d postgres redis
\tsleep 5
\tpython scripts/init_db.py

test:
\tpytest tests/
""")
    print_success("Makefile создан")

    # 7. Создаём тестовый скрипт
    print_step("Создаём тестовый скрипт...")
    os.makedirs("scripts", exist_ok=True)

    with open("scripts/test_platform.py", "w") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Test script for AUGUR Enterprise Platform
Запустите после docker-compose up
\"\"\"

import httpx
import asyncio
import sys
from datetime import datetime

SERVICES = [
    ("API Gateway", "http://localhost:8000/health"),
    ("Agent Service", "http://localhost:8001/health"),
    ("Orchestration", "http://localhost:8002/health"),
    ("Memory Service", "http://localhost:8003/health"),
    ("Governance", "http://localhost:8004/health"),
    ("Conflict Resolution", "http://localhost:8005/health"),
    ("Value Discovery", "http://localhost:8006/health"),
    ("Quantum Collective", "http://localhost:8007/health"),
]

async def test_service(name, url):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name:20} - Healthy ({data.get('service', 'unknown')})")
                return True
            else:
                print(f"❌ {name:20} - Returned {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ {name:20} - Failed: {str(e)}")
        return False

async def test_agent_api():
    print("\\n🔧 Testing Agent Service API...")
    base = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Create agent
        agent_data = {
            "name": "Test Agent",
            "type": "assistant",
            "description": "Test agent for platform verification",
            "capabilities": ["text-generation", "code-analysis"],
            "config": {"model": "gpt-4", "temperature": 0.7}
        }

        try:
            response = await client.post(f"{base}/agents", json=agent_data)
            if response.status_code == 200:
                agent = response.json()
                print(f"✅ Created agent: {agent['id']}")

                # Get agent
                response = await client.get(f"{base}/agents/{agent['id']}")
                if response.status_code == 200:
                    print(f"✅ Retrieved agent: {response.json()['name']}")

                # List agents
                response = await client.get(f"{base}/agents")
                if response.status_code == 200:
                    agents = response.json()
                    print(f"✅ Listed agents: {len(agents)} total")

                # Send heartbeat
                response = await client.post(f"{base}/agents/{agent['id']}/heartbeat")
                if response.status_code == 200:
                    print(f"✅ Heartbeat sent")

                return True
            else:
                print(f"❌ Failed to create agent: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API test failed: {str(e)}")
            return False

async def main():
    print("\\n" + "="*60)
    print("🧪 TESTING AUGUR ENTERPRISE PLATFORM")
    print("="*60 + "\\n")

    # Test all services
    all_healthy = True
    for name, url in SERVICES:
        if not await test_service(name, url):
            all_healthy = False

    if all_healthy:
        print("\\n✅ All services are healthy!")
        # Test Agent API
        await test_agent_api()
    else:
        print("\\n❌ Some services are not responding")

    print("\\n" + "="*60)
    print(f"🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
""")
    print_success("Тестовый скрипт создан")

    # 8. Создаём скрипт инициализации БД
    with open("scripts/init_db.py", "w") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Initialize AUGUR databases
\"\"\"

import asyncio
import asyncpg
import os

async def init_database():
    # Connect to postgres to create extensions
    conn = await asyncpg.connect(
        user='augur',
        password='augur',
        database='augur',
        host='localhost',
        port=5432
    )

    try:
        # Enable TimescaleDB
        await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')
        print("✅ TimescaleDB enabled")

        # Enable pgvector in memory database
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
        print("✅ pgvector enabled")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
""")

    # 9. Обновляем README
    print_step("Обновляем README.md...")
    with open("README.md", "r") as f:
        old_readme = f.read()

    new_readme = old_readme + """

## 🚀 Enterprise Platform Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/karamik/AUGUR.git
cd AUGUR
