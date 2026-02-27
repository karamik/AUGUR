-- Создаём базы данных для каждого сервиса
CREATE DATABASE augur_agents;
CREATE DATABASE augur_orchestration;
CREATE DATABASE augur_memory;
CREATE DATABASE augur_governance;
CREATE DATABASE augur_conflict;
CREATE DATABASE augur_value;
CREATE DATABASE augur_quantum;

-- Подключаемся к augur_agents и создаём таблицы
\c augur_agents;

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'inactive',
    capabilities JSONB,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id),
    fingerprint_hash VARCHAR(64),
    behavior_data JSONB,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Подключаемся к augur_memory и создаём векторные таблицы
\c augur_memory;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS memory_vectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID,
    vector vector(1536),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_memory_vectors_vector ON memory_vectors USING ivfflat (vector vector_cosine_ops);

-- Подключаемся к augur_orchestration
\c augur_orchestration;

CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    definition JSONB,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    status VARCHAR(20),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB
);
