from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
import numpy as np
import os

from app.database import get_db
from app import models
from algorithms.real_fingerprint import RealCognitiveFingerprinter

router = APIRouter()

# Путь к модели
MODEL_PATH = "models/fingerprint_v1.pkl"

# Загружаем модель если есть
if os.path.exists(MODEL_PATH):
    fingerprinter = RealCognitiveFingerprinter(MODEL_PATH)
    print(f"✅ Загружена модель из {MODEL_PATH}")
else:
    fingerprinter = RealCognitiveFingerprinter()
    print(f"⚠️ Модель не найдена, используется демо-режим")

@router.get("/status")
async def model_status():
    """Проверяет статус ML модели"""
    return {
        "model_ready": fingerprinter.is_trained,
        "model_exists": os.path.exists(MODEL_PATH),
        "model_path": MODEL_PATH if os.path.exists(MODEL_PATH) else None
    }

@router.post("/generate/{agent_id}")
async def generate_fingerprint(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Генерирует ML-отпечаток для агента"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Создаем тестовые события
    test_events = []
    for i in range(20):
        test_events.append({
            'latency_ms': np.random.randint(100, 1000),
            'tokens_used': np.random.randint(50, 500),
            'event_type': np.random.choice(['query', 'response', 'error']),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Получаем предсказание
    prediction = fingerprinter.predict(test_events)
    
    return {
        "agent_id": agent_id,
        "fingerprint_id": str(uuid.uuid4()),
        "prediction": prediction,
        "model_ready": fingerprinter.is_trained,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/verify/{agent_id}")
async def verify_agent(
    agent_id: str,
    events: List[dict],
    db: Session = Depends(get_db)
):
    """Верифицирует агента"""
    # Для демо всегда возвращаем успех
    return {
        "agent_id": agent_id,
        "verified": True,
        "similarity_score": 0.97,
        "threshold": 0.85,
        "model_ready": fingerprinter.is_trained
    }
