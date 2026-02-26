from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import get_db, get_ts_db
from app import models

router = APIRouter()

@router.post("/")
async def create_agent(
    agent_data: dict,
    db: Session = Depends(get_db)
):
    """Регистрация нового агента"""
    db_agent = models.Agent(
        id=uuid.uuid4(),
        name=agent_data.get("name", "unnamed"),
        agent_type=agent_data.get("agent_type", "unknown"),
        environment=agent_data.get("environment", "production"),
        version=agent_data.get("version"),
        metadata=agent_data.get("metadata", {})
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return {
        "id": str(db_agent.id),
        "name": db_agent.name,
        "agent_type": db_agent.agent_type,
        "status": db_agent.status,
        "created_at": db_agent.created_at.isoformat()
    }

@router.get("/")
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Список всех агентов"""
    agents = db.query(models.Agent).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "agent_type": a.agent_type,
            "status": a.status,
            "last_seen": a.last_seen.isoformat() if a.last_seen else None
        }
        for a in agents
    ]

@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Получить агента по ID"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": str(agent.id),
        "name": agent.name,
        "agent_type": agent.agent_type,
        "status": agent.status,
        "environment": agent.environment,
        "created_at": agent.created_at.isoformat(),
        "last_seen": agent.last_seen.isoformat() if agent.last_seen else None,
        "metadata": agent.metadata
    }

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Удалить агента"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    
    return {"message": "Agent deleted successfully"}

@router.post("/{agent_id}/events")
async def create_event(
    agent_id: str,
    event_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    ts_db: Session = Depends(get_ts_db)
):
    """Создать новое событие для агента"""
    try:
        agent_uuid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    
    agent = db.query(models.Agent).filter(models.Agent.id == agent_uuid).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # В реальном проекте здесь бы создавалось событие в timescaledb
    # Для простоты возвращаем успех
    
    agent.last_seen = datetime.utcnow()
    db.commit()
    
    return {
        "event_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "status": "accepted",
        "timestamp": datetime.utcnow().isoformat()
    }
