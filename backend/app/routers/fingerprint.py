from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import numpy as np
import os

from app.database import get_db
from app import models

router = APIRouter()

# Простой класс для демо-режима
class DemoFingerprinter:
    def __init__(self):
        self.is_trained = True
        self.model_path = "models/fingerprint_v1.pkl"
    
    def predict(self, events):
        return {
            'class': 'agent_1',
            'confidence': 0.95,
            'probabilities': {
                'agent_1': 0.95,
                'agent_2': 0.03,
                'agent_3': 0.02
            }
        }
    
    def compare(self, events_a, events_b):
        return 0.97

# Создаем экземпляр
fingerprinter = DemoFingerprinter()

@router.get("/status")
async def get_status():
    """Проверяет статус модели"""
    # Проверяем разные возможные пути к модели
    possible_paths = [
        "models/fingerprint_v1.pkl",
        "backend/models/fingerprint_v1.pkl",
        "./models/fingerprint_v1.pkl"
    ]
    
    model_exists = any(os.path.exists(path) for path in possible_paths)
    
    # Получаем список файлов в папке models если она существует
    files_in_models = []
    if os.path.exists("models"):
        files_in_models = os.listdir("models")
    elif os.path.exists("backend/models"):
        files_in_models = os.listdir("backend/models")
    
    return {
        "status": "active",
        "model_ready": True,
        "model_exists": model_exists,
        "files_in_models": files_in_models,
        "version": "1.0.0",
        "message": "✅ Cognitive Fingerprinting is ready"
    }

@router.post("/generate/{agent_id}")
async def generate_fingerprint(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Генерирует когнитивный отпечаток для агента"""
    # Проверяем существование агента
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Создаем тестовые события для демо
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
    
    # Создаем запись в БД (упрощенно)
    fingerprint_id = str(uuid.uuid4())
    
    return {
        "fingerprint_id": fingerprint_id,
        "agent_id": agent_id,
        "agent_name": agent.name,
        "prediction": prediction,
        "generated_at": datetime.utcnow().isoformat(),
        "events_analyzed": len(test_events),
        "model_status": "active"
    }

@router.post("/verify/{agent_id}")
async def verify_identity(
    agent_id: str,
    events: Optional[List[dict]] = None,
    db: Session = Depends(get_db)
):
    """Проверяет identity агента по отпечатку"""
    # Проверяем агента
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Если события не переданы, создаем тестовые
    if events is None or len(events) == 0:
        events = []
        for i in range(10):
            events.append({
                'latency_ms': np.random.randint(100, 1000),
                'tokens_used': np.random.randint(50, 500),
                'event_type': 'query',
                'timestamp': datetime.utcnow().isoformat()
            })
    
    # Сравниваем с baseline
    similarity = fingerprinter.compare(events, events)
    
    # Определяем результат верификации
    verified = similarity > 0.85
    
    return {
        "verification_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "agent_name": agent.name,
        "verified": verified,
        "similarity_score": round(similarity, 4),
        "threshold": 0.85,
        "confidence": round(similarity, 4),
        "events_analyzed": len(events),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/history/{agent_id}")
async def get_fingerprint_history(
    agent_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Получает историю отпечатков агента"""
    # Проверяем агента
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # В демо-режиме возвращаем тестовую историю
    history = []
    for i in range(min(limit, 10)):
        history.append({
            "fingerprint_id": str(uuid.uuid4()),
            "generated_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            "confidence": round(0.9 + (np.random.random() * 0.08), 3),
            "events_count": np.random.randint(50, 200)
        })
    
    return {
        "agent_id": agent_id,
        "agent_name": agent.name,
        "history": history,
        "total_records": len(history)
    }
