from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
import numpy as np

from app.database import get_db
from app import models
from algorithms.conflict import ConflictPredictor

router = APIRouter()
predictor = ConflictPredictor()

@router.get("/predictions")
async def get_predictions(
    time_horizon: int = 24,
    db: Session = Depends(get_db)
):
    """Получить предсказания конфликтов"""
    agents = db.query(models.Agent).limit(10).all()
    
    if len(agents) < 2:
        return {"predictions": [], "message": "Not enough agents"}
    
    agent_dicts = [
        {"id": str(a.id), "name": a.name, "metadata": a.metadata}
        for a in agents
    ]
    
    # Заглушка для событий
    recent_events = {}
    for agent in agents:
        recent_events[str(agent.id)] = [
            {"timestamp": datetime.utcnow().isoformat(), "latency_ms": np.random.randint(100, 1000)}
            for _ in range(10)
        ]
    
    predictions = predictor.predict_conflicts(agent_dicts, recent_events)
    
    # Сохраняем в БД
    for pred in predictions[:5]:  # сохраняем только первые 5
        db_pred = models.ConflictPrediction(
            id=uuid.uuid4(),
            agent_a_id=uuid.UUID(pred["agent_a_id"]),
            agent_b_id=uuid.UUID(pred["agent_b_id"]),
            probability=pred["probability"],
            conflict_type=pred["conflict_type"],
            predicted_time=datetime.fromisoformat(pred["predicted_time"]),
            severity=pred["severity"]
        )
        db.add(db_pred)
    db.commit()
    
    return {
        "predictions": predictions,
        "total": len(predictions),
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/negotiate")
async def negotiate_conflict(
    conflict_data: dict,
    db: Session = Depends(get_db)
):
    """Запустить переговоры для разрешения конфликта"""
    resolution = predictor.suggest_resolution(conflict_data)
    
    return {
        "negotiation_id": str(uuid.uuid4()),
        "conflict_id": conflict_data.get("conflict_id", "unknown"),
        "status": "completed",
        "resolution": resolution
    }
