from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

from app.database import engine, Base
from app.routers import agents, fingerprint, conflict

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AUGUR API",
    description="Agentic Unified Governance & Review Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(fingerprint.router, prefix="/api/v1/fingerprint", tags=["Fingerprint"])
app.include_router(conflict.router, prefix="/api/v1/conflict", tags=["Conflict"])

@app.get("/")
async def root():
    return {
        "service": "AUGUR API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    return {
        "api_version": "v1",
        "features": [
            "cognitive_fingerprinting",
            "conflict_prediction"
        ],
        "uptime": "operational"
    }
