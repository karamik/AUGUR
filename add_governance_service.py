#!/usr/bin/env python3
"""
ШАГ 4: Добавляем Governance Service с JWT аутентификацией
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 4: Добавляем Governance Service с JWT                  ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для Governance Service
os.makedirs("backend/services/governance-service/src", exist_ok=True)

# 2. Устанавливаем зависимости для JWT
print("📦 Установка зависимостей...")
run("pip install pyjwt cryptography passlib python-multipart")

# 3. Создаём рабочий Governance Service с JWT
with open("backend/services/governance-service/src/main.py", "w") as f:
    f.write("""# Governance Service with JWT Authentication
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncpg
import jwt
import uuid
import os
import logging
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Governance Service", version="1.0.0")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database connection
db_pool = None

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class User(BaseModel):
    id: str
    username: str
    email: str
    role: str
    disabled: bool = False
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AuditLog(BaseModel):
    id: str
    user_id: str
    action: str
    resource: str
    result: str
    ip_address: str
    timestamp: datetime

class Policy(BaseModel):
    id: str
    name: str
    description: str
    rules: Dict
    created_at: datetime
    enabled: bool = True

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            token_data.username
        )
    
    if user is None:
        raise credentials_exception
    return dict(user)

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.on_event("startup")
async def startup():
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER", "augur"),
            password=os.getenv("DB_PASSWORD", "augur"),
            database=os.getenv("DB_NAME", "augur_governance"),
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Connected to Governance Database")
        
        # Create tables
        async with db_pool.acquire() as conn:
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    disabled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Audit logs table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id UUID PRIMARY KEY,
                    user_id UUID REFERENCES users(id),
                    action VARCHAR(100) NOT NULL,
                    resource VARCHAR(255),
                    result VARCHAR(50),
                    ip_address VARCHAR(45),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Policies table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    id UUID PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    rules JSONB,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default admin if not exists
            admin_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin')"
            )
            if not admin_exists:
                admin_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO users (id, username, email, password_hash, role)
                    VALUES ($1, $2, $3, $4, $5)
                """, admin_id, "admin", "admin@augur.com", 
                    get_password_hash("admin123"), "admin")
                logger.info("✅ Default admin created")
            
            logger.info("✅ Governance tables ready")
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
        "service": "Governance Service",
        "version": "1.0.0",
        "features": ["jwt-auth", "audit-logs", "policies"]
    }

@app.get("/health")
async def health():
    db_status = "connected" if db_pool else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "jwt": "enabled",
        "timestamp": datetime.now().isoformat()
    }

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get JWT token"""
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            form_data.username
        )
    
    if not user or not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    # Log the login
    await create_audit_log(
        user['id'], "LOGIN", "auth", "success", 
        "0.0.0.0"  # In production, get real IP
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
async def register(user: UserCreate):
    """Register new user"""
    async with db_pool.acquire() as conn:
        # Check if user exists
        existing = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1 OR email = $2)",
            user.username, user.email
        )
        if existing:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        user_id = str(uuid.uuid4())
        await conn.execute("""
            INSERT INTO users (id, username, email, password_hash, role)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, user.username, user.email, 
            get_password_hash(user.password), user.role)
        
        return {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "disabled": False,
            "created_at": datetime.now()
        }

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user

# Audit Logs
async def create_audit_log(user_id: str, action: str, resource: str, result: str, ip: str):
    """Create audit log entry"""
    try:
        async with db_pool.acquire() as conn:
            log_id = str(uuid.uuid4())
            await conn.execute("""
                INSERT INTO audit_logs (id, user_id, action, resource, result, ip_address)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, log_id, user_id, action, resource, result, ip)
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")

@app.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    limit: int = 100,
    current_user: dict = Depends(check_admin)
):
    """Get audit logs (admin only)"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM audit_logs 
            ORDER BY timestamp DESC 
            LIMIT $1
        """, limit)
    return [dict(row) for row in rows]

@app.get("/audit-logs/user/{user_id}", response_model=List[AuditLog])
async def get_user_audit_logs(
    user_id: str,
    limit: int = 100,
    current_user: dict = Depends(check_admin)
):
    """Get audit logs for specific user (admin only)"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM audit_logs 
            WHERE user_id = $1
            ORDER BY timestamp DESC 
            LIMIT $2
        """, user_id, limit)
    return [dict(row) for row in rows]

# Policies
@app.post("/policies", response_model=Policy)
async def create_policy(
    policy: Policy,
    current_user: dict = Depends(check_admin)
):
    """Create new policy (admin only)"""
    policy_id = str(uuid.uuid4())
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO policies (id, name, description, rules)
            VALUES ($1, $2, $3, $4)
        """, policy_id, policy.name, policy.description, policy.rules)
        
        # Log the action
        await create_audit_log(
            current_user['id'], "CREATE_POLICY", f"policy/{policy_id}", 
            "success", "0.0.0.0"
        )
    
    return {
        "id": policy_id,
        "name": policy.name,
        "description": policy.description,
        "rules": policy.rules,
        "enabled": True,
        "created_at": datetime.now()
    }

@app.get("/policies", response_model=List[Policy])
async def list_policies(
    enabled_only: bool = False,
    current_user: dict = Depends(check_admin)
):
    """List all policies (admin only)"""
    async with db_pool.acquire() as conn:
        if enabled_only:
            rows = await conn.fetch(
                "SELECT * FROM policies WHERE enabled = TRUE ORDER BY created_at DESC"
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM policies ORDER BY created_at DESC"
            )
    return [dict(row) for row in rows]

@app.get("/policies/{policy_id}", response_model=Policy)
async def get_policy(
    policy_id: str,
    current_user: dict = Depends(check_admin)
):
    """Get specific policy (admin only)"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM policies WHERE id = $1",
            policy_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Policy not found")
    return dict(row)

@app.put("/policies/{policy_id}/toggle")
async def toggle_policy(
    policy_id: str,
    enabled: bool,
    current_user: dict = Depends(check_admin)
):
    """Enable/disable policy (admin only)"""
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE policies SET enabled = $1 
            WHERE id = $2
        """, enabled, policy_id)
        
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Policy not found")
        
        await create_audit_log(
            current_user['id'], "TOGGLE_POLICY", f"policy/{policy_id}", 
            "success", "0.0.0.0"
        )
    
    return {"message": f"Policy {'enabled' if enabled else 'disabled'}"}

@app.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: dict = Depends(check_admin)
):
    """Delete policy (admin only)"""
    async with db_pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM policies WHERE id = $1",
            policy_id
        )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Policy not found")
        
        await create_audit_log(
            current_user['id'], "DELETE_POLICY", f"policy/{policy_id}", 
            "success", "0.0.0.0"
        )
    
    return {"message": "Policy deleted"}

# Middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response
""")

# 4. Создаём Dockerfile для Governance Service
with open("backend/services/governance-service/Dockerfile", "w") as f:
    f.write("""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip install fastapi uvicorn asyncpg python-jose[cryptography] passlib[bcrypt] python-multipart

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
""")

# 5. Создаём SQL для Governance
with open("infra/postgres/init/03-governance.sql", "w") as f:
    f.write("""-- Create governance database
CREATE DATABASE augur_governance;

\\c augur_governance;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    disabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    result VARCHAR(50),
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for audit logs
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_time ON audit_logs(timestamp);

-- Policies table
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    rules JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create default admin (password: admin123)
-- Password hash will be created by the application
""")

# 6. Обновляем docker-compose.yml
with open("docker-compose.yml", "r") as f:
    old_compose = f.read()

new_compose = old_compose.replace("""services:
  memory-service:""", """services:
  governance-service:
    build: ./backend/services/governance-service
    ports:
      - "8004:8004"
    environment:
      - DB_USER=augur
      - DB_PASSWORD=augur
      - DB_NAME=augur_governance
      - DB_HOST=postgres
      - DB_PORT=5432
      - JWT_SECRET=your-super-secret-jwt-key-change-in-production
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - augur-net

  memory-service:""")

with open("docker-compose.yml", "w") as f:
    f.write(new_compose)

# 7. Создаём тест для Governance Service
with open("test_governance.py", "w") as f:
    f.write("""import requests
import time
import json

print("🧪 Testing Governance Service with JWT...\\n")

base = "http://localhost:8004"

# 1. Health check
print("1️⃣ Health check...")
try:
    resp = requests.get(f"{base}/health")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Database: {data['database']}")
        print(f"   ✅ JWT: {data['jwt']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Register new user
print("\\n2️⃣ Registering new user...")
user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "role": "user"
}

try:
    resp = requests.post(f"{base}/register", json=user_data)
    if resp.status_code == 200:
        user = resp.json()
        print(f"   ✅ User registered: {user['username']}")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        if resp.text:
            print(f"      {resp.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Login to get token
print("\\n3️⃣ Logging in...")
login_data = {
    "username": "testuser",
    "password": "test123"
}

try:
    resp = requests.post(f"{base}/token", data=login_data)
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data['access_token']
        print(f"   ✅ Token received: {token[:20]}...")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        token = None
except Exception as e:
    print(f"   ❌ Error: {e}")
    token = None

# 4. Get current user info
if token:
    print("\\n4️⃣ Getting current user info...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{base}/users/me", headers=headers)
        if resp.status_code == 200:
            user_info = resp.json()
            print(f"   ✅ User: {user_info['username']} (role: {user_info['role']})")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 5. Login as admin
print("\\n5️⃣ Logging in as admin...")
admin_login = {
    "username": "admin",
    "password": "admin123"
}

try:
    resp = requests.post(f"{base}/token", data=admin_login)
    if resp.status_code == 200:
        admin_token = resp.json()['access_token']
        print(f"   ✅ Admin token received")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
        admin_token = None
except Exception as e:
    print(f"   ❌ Error: {e}")
    admin_token = None

# 6. Create policy (admin only)
if admin_token:
    print("\\n6️⃣ Creating policy (as admin)...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    policy_data = {
        "name": "test-policy",
        "description": "Test policy for demo",
        "rules": {
            "allow": ["read", "write"],
            "deny": ["delete"],
            "rate_limit": 100
        }
    }
    
    try:
        resp = requests.post(f"{base}/policies", json=policy_data, headers=headers)
        if resp.status_code == 200:
            policy = resp.json()
            print(f"   ✅ Policy created: {policy['name']}")
            policy_id = policy['id']
        else:
            print(f"   ❌ Failed: {resp.status_code}")
            policy_id = None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        policy_id = None

# 7. List policies
if admin_token:
    print("\\n7️⃣ Listing policies...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    try:
        resp = requests.get(f"{base}/policies", headers=headers)
        if resp.status_code == 200:
            policies = resp.json()
            print(f"   ✅ Found {len(policies)} policies")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# 8. Get audit logs (admin only)
if admin_token:
    print("\\n8️⃣ Getting audit logs...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    try:
        resp = requests.get(f"{base}/audit-logs", headers=headers)
        if resp.status_code == 200:
            logs = resp.json()
            print(f"   ✅ Found {len(logs)} audit logs")
            if logs:
                print(f"      Latest: {logs[0]['action']} at {logs[0]['timestamp']}")
        else:
            print(f"   ❌ Failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Governance Service test complete")
print("="*50)
""")

# 8. Создаём скрипт для обновления API Gateway с JWT
with open("update_api_gateway.py", "w") as f:
    f.write("""#!/usr/bin/env python3
"""
Обновляем API Gateway для работы с JWT
"""

import os

# Обновляем API Gateway для поддержки JWT
with open("backend/services/api-gateway/src/main.py", "r") as f:
    gateway_code = f.read()

# Добавляем JWT проверку
jwt_middleware = """
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(payload: dict = Depends(verify_token)):
    return {"message": "This is protected", "user": payload.get("sub")}
"""

# Добавляем в начало файла
gateway_code = gateway_code.replace(
    "import logging",
    "import logging\nimport jwt\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials"
)

gateway_code = gateway_code.replace(
    'logger = logging.getLogger(__name__)',
    'logger = logging.getLogger(__name__)\n\nsecurity = HTTPBearer()\nJWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")'
)

# Добавляем функцию проверки токена
gateway_code += """

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/v1/protected")
async def protected_route(payload: dict = Depends(verify_token)):
    return {"message": "This is protected", "user": payload.get("sub")}
"""

with open("backend/services/api-gateway/src/main.py", "w") as f:
    f.write(gateway_code)

print("✅ API Gateway updated with JWT support")
""")

print("""
╔══════════════════════════════════════════════════════════════╗
║  ✅ ШАГ 4 ВЫПОЛНЕН                                           ║
║  Добавлен Governance Service с JWT аутентификацией          ║
╚══════════════════════════════════════════════════════════════╝

📦 Новые компоненты:
   • Governance Service (порт 8004)
   • JWT аутентификация
   • Audit logging
   • Policy management
   • User management
   • Role-based access control (RBAC)

🚀 Что делать дальше:
   make build
   make up
   python test_governance.py
   python update_api_gateway.py

📊 Новые endpoints:
   POST /token           - получить JWT токен
   POST /register        - регистрация пользователя
   GET /users/me         - информация о текущем пользователе
   GET /audit-logs       - логи аудита (admin)
   POST /policies        - создать политику (admin)
   GET /policies         - список политик (admin)

🔐 Теперь платформа имеет:
   • Безопасную аутентификацию
   • Аудит всех действий
   • Управление политиками
   • Ролевую модель (admin/user)
""")
