from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.database import get_db, get_ts_db
from app import models
from algorithms.fingerprint import CognitiveFingerprinter

router = APIRouter()
fingerprinter = CognitiveFingerprinter()

@router.post("/generate/{agent_id}")
async def generate_fingerprint(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Генерирует когнитивный отпечаток для агента"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Для демо генерируем случайные события
    sample_events = []
    for i in range(20):
        sample_events.append({
            'latency_ms': np.random.randint(100, 1000),
            'tokens_used': np.random.randint(50, 500),
            'event_type': 'query',
            'timestamp': datetime.utcnow()
        })
    
    fingerprint_vector, confidence = fingerprinter.generate_fingerprint(sample_events)
    
    fp = models.Fingerprint(
        id=uuid.uuid4(),
        agent_id=agent_uuid,
        fingerprint_vector=fingerprint_vector,
        confidence=confidence,
        dimensions={"sample_size": 20},
        is_baseline=True
    )
    
    db.add(fp)
    db.commit()
    
    return {
        "agent_id": agent_id,
        "fingerprint_id": str(fp.id),
        "confidence": confidence,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/{agent_id}/current")
async def get_current_fingerprint(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Получает текущий отпечаток агента"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    fp = db.query(models.Fingerprint).filter(
        models.Fingerprint.agent_id == agent_uuid,
        models.Fingerprint.is_baseline == True
    ).order_by(models.Fingerprint.generated_at.desc()).first()
    
    if not fp:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    
    return {
        "agent_id": agent_id,
        "fingerprint_id": str(fp.id),
        "fingerprint_vector": fp.fingerprint_vector[:5],
        "confidence": fp.confidence,
        "generated_at": fp.generated_at.isoformat()
    }

@router.post("/verify/{agent_id}")
async def verify_agent(
    agent_id: str,
    events: List[dict],
    db: Session = Depends(get_db)
):
    """Верифицирует агента по его отпечатку"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    baseline = db.query(models.Fingerprint).filter(
        models.Fingerprint.agent_id == agent_uuid,
        models.Fingerprint.is_baseline == True
    ).first()
    
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline fingerprint not found")
    
    current_vector, confidence = fingerprinter.generate_fingerprint(events)
    similarity = fingerprinter.compare_fingerprints(
        baseline.fingerprint_vector,
        current_vector
    )
    
    return {
        "agent_id": agent_id,
        "verified": similarity >= 85.0,
        "similarity_score": similarity,
        "threshold": 85.0,
        "confidence": confidence
    }
