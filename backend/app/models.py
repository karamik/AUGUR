from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)
    status = Column(String, default="active")
    environment = Column(String, default="production")
    version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    
    fingerprints = relationship("Fingerprint", back_populates="agent")
    events = relationship("Event", back_populates="agent")

class Fingerprint(Base):
    __tablename__ = "fingerprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    fingerprint_vector = Column(JSON)
    confidence = Column(Float)
    dimensions = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)
    is_baseline = Column(Boolean, default=False)
    
    agent = relationship("Agent", back_populates="fingerprints")

class Event(Base):
    __tablename__ = "events"
    
    __table_args__ = {"schema": "timeseries"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    event_type = Column(String)
    timestamp = Column(DateTime, primary_key=True)
    latency_ms = Column(Integer)
    tokens_used = Column(Integer)
    data = Column(JSON)
    
    agent = relationship("Agent", back_populates="events")

class ConflictPrediction(Base):
    __tablename__ = "conflict_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_a_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    agent_b_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    probability = Column(Float)
    conflict_type = Column(String)
    predicted_time = Column(DateTime)
    severity = Column(String)
    resolved = Column(Boolean, default=False)
    resolution_strategy = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ValueDiscovery(Base):
    __tablename__ = "value_discoveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_type = Column(String)
    description = Column(Text)
    confidence = Column(Float)
    estimated_value_annual = Column(Float)
    agents_involved = Column(JSON)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    recommendations = Column(JSON, default=[])
    implemented = Column(Boolean, default=False)
