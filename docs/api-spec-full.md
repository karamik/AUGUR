# AUGUR API Specification (Full Version)

## Overview

The AUGUR API provides programmatic access to all platform features including agent audit, orchestration, ROI analytics, and proprietary intelligence modules. The API follows RESTful principles and returns JSON responses.

**Base URL:** `https://api.augur.ai/v1`  
**Documentation:** `https://api.augur.ai/docs` (OpenAPI 3.0)  
**Status:** `https://status.augur.ai`

## Authentication

All API requests require authentication via API key or JWT token.

### API Key Authentication

```http
GET /api/v1/agents
Authorization: Bearer {your_api_key}
```

### JWT Authentication

```http
GET /api/v1/agents
Authorization: Bearer {jwt_token}
```

### Get API Key

```http
POST /api/v1/auth/api-keys
Content-Type: application/json

{
  "name": "Production Key",
  "permissions": ["read:agents", "write:events"],
  "expires_in_days": 90
}
```

**Response:**
```json
{
  "api_key": "aug_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "id": "key_123456789",
  "name": "Production Key",
  "permissions": ["read:agents", "write:events"],
  "created_at": "2024-03-20T10:00:00Z",
  "expires_at": "2024-06-18T10:00:00Z"
}
```

## Rate Limiting

| Plan | Rate Limit | Burst |
|------|------------|-------|
| Starter | 100 req/min | 200 |
| Professional | 1000 req/min | 2000 |
| Enterprise | 5000 req/min | 10000 |

Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1620000000
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "details": {
      "limit": 1000,
      "current": 1001,
      "reset_at": "2024-03-20T10:05:00Z"
    },
    "request_id": "req_abcdef123456"
  }
}
```

## Endpoints

### Agents

#### List All Agents

```http
GET /api/v1/agents
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (active, inactive, degraded) |
| `type` | string | Filter by agent type (aata, lilli, zora, openai, custom) |
| `limit` | integer | Max items per page (default: 50, max: 100) |
| `offset` | integer | Pagination offset |
| `sort` | string | Sort field (name, created_at, status) |
| `order` | string | Sort order (asc, desc) |

**Response:**
```json
{
  "data": [
    {
      "id": "agent_123456",
      "name": "customer-support-claude",
      "type": "claude-3-opus",
      "status": "active",
      "environment": "production",
      "version": "1.2.3",
      "created_at": "2024-01-15T09:00:00Z",
      "last_seen": "2024-03-20T10:23:45Z",
      "metrics": {
        "total_actions": 15432,
        "avg_latency_ms": 847,
        "error_rate": 0.02,
        "tokens_used": 2456789
      }
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 50,
    "offset": 0,
    "next": "/api/v1/agents?limit=50&offset=50",
    "prev": null
  }
}
```

#### Get Agent Details

```http
GET /api/v1/agents/{agent_id}
```

**Response:**
```json
{
  "id": "agent_123456",
  "name": "customer-support-claude",
  "type": "claude-3-opus",
  "status": "active",
  "environment": "production",
  "version": "1.2.3",
  "description": "Handles customer support inquiries",
  "capabilities": ["ticketing", "faq", "escalation"],
  "created_at": "2024-01-15T09:00:00Z",
  "last_seen": "2024-03-20T10:23:45Z",
  "metrics": {
    "total_actions": 15432,
    "avg_latency_ms": 847,
    "error_rate": 0.02,
    "tokens_used": 2456789,
    "estimated_savings": 12345.67
  }
}
```

#### Register New Agent

```http
POST /api/v1/agents
Content-Type: application/json

{
  "name": "customer-support-claude",
  "type": "claude-3-opus",
  "environment": "staging",
  "description": "Handles customer support inquiries",
  "capabilities": ["ticketing", "faq", "escalation"],
  "tags": ["staging", "test"]
}
```

**Response:** (201 Created)
```json
{
  "id": "agent_123457",
  "name": "customer-support-claude",
  "status": "pending",
  "webhook_url": "https://api.augur.ai/v1/agents/agent_123457/webhook",
  "api_key": "tmp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "created_at": "2024-03-20T10:30:00Z"
}
```

#### Update Agent

```http
PATCH /api/v1/agents/{agent_id}
Content-Type: application/json

{
  "name": "customer-support-claude-v2",
  "tags": ["production", "customer-facing"],
  "status": "active"
}
```

**Response:**
```json
{
  "id": "agent_123456",
  "name": "customer-support-claude-v2",
  "updated_at": "2024-03-20T10:35:00Z",
  "updated_fields": ["name", "tags", "status"]
}
```

#### Delete Agent

```http
DELETE /api/v1/agents/{agent_id}
```

**Response:** (204 No Content)

### Events

#### Ingest Agent Event

```http
POST /api/v1/events
Content-Type: application/json
Authorization: Bearer {agent_api_key}

{
  "agent_id": "agent_123456",
  "event_type": "query",
  "timestamp": "2024-03-20T10:23:45Z",
  "data": {
    "query": "How do I reset my password?",
    "response": "To reset your password, please visit...",
    "latency_ms": 847,
    "tokens_used": 156
  },
  "context": {
    "session_id": "sess_abcdef",
    "user_id": "user_123"
  }
}
```

**Response:** (202 Accepted)
```json
{
  "event_id": "evt_abcdef123456",
  "status": "processing"
}
```

#### Batch Event Ingestion

```http
POST /api/v1/events/batch
Content-Type: application/json
Authorization: Bearer {agent_api_key}

{
  "events": [
    {
      "agent_id": "agent_123456",
      "event_type": "query",
      "timestamp": "2024-03-20T10:23:45Z",
      "data": { "query": "How do I reset my password?" }
    },
    {
      "agent_id": "agent_123456",
      "event_type": "query",
      "timestamp": "2024-03-20T10:24:12Z",
      "data": { "query": "What are your hours?" }
    }
  ]
}
```

**Response:**
```json
{
  "batch_id": "batch_abcdef",
  "accepted": 50,
  "failed": 0,
  "errors": []
}
```

#### Get Events

```http
GET /api/v1/events?agent_id=agent_123456&start=2024-03-01&end=2024-03-07&limit=100
```

**Response:**
```json
{
  "data": [
    {
      "id": "evt_abcdef123456",
      "agent_id": "agent_123456",
      "event_type": "query",
      "timestamp": "2024-03-20T10:23:45Z",
      "data": {
        "query": "How do I reset my password?",
        "latency_ms": 847
      }
    }
  ],
  "pagination": {
    "total": 15432,
    "limit": 100,
    "offset": 0
  }
}
```

### Audit

#### Get Audit Logs

```http
GET /api/v1/audit/logs?agent_id=agent_123456&severity=high
```

**Response:**
```json
{
  "data": [
    {
      "id": "aud_123456",
      "timestamp": "2024-03-20T09:15:23Z",
      "severity": "high",
      "category": "policy_violation",
      "agent_id": "agent_123456",
      "description": "Agent attempted to access restricted customer data",
      "details": {
        "policy": "data_privacy_policy_v2",
        "violation": "credit_card_number_detected"
      }
    }
  ],
  "summary": {
    "total": 23,
    "critical": 2,
    "high": 5
  }
}
```

#### Create Audit Rule

```http
POST /api/v1/audit/rules
Content-Type: application/json

{
  "name": "Block PII in responses",
  "severity": "critical",
  "conditions": {
    "type": "regex_match",
    "field": "data.response",
    "pattern": "\\b\\d{16}\\b"
  },
  "action": "block_and_alert",
  "enabled": true
}
```

**Response:**
```json
{
  "id": "rule_123456",
  "name": "Block PII in responses",
  "created_at": "2024-03-20T10:40:00Z"
}
```

### Cognitive Fingerprinting™

#### Get Agent Fingerprint

```http
GET /api/v1/fingerprint/{agent_id}
```

**Response:**
```json
{
  "agent_id": "agent_123456",
  "fingerprint_id": "fp_7f8e3d2a",
  "fingerprint_vector": "7f8e3d2a1c5b9e4f6a2d8c3b7e1f9a4d",
  "confidence": 98.7,
  "dimensions": [
    {
      "name": "latency_patterns",
      "value": {
        "avg": 847,
        "p95": 1243
      }
    },
    {
      "name": "vocabulary_fingerprint",
      "value": {
        "unique_words": 1243,
        "formality_score": 0.87
      }
    }
  ],
  "generated_at": "2024-03-15T00:00:00Z",
  "last_verified": "2024-03-20T10:00:00Z",
  "drift_detected": false
}
```

#### Verify Agent Identity

```http
POST /api/v1/fingerprint/verify
Content-Type: application/json

{
  "agent_id": "agent_123456",
  "recent_actions": [
    {
      "timestamp": "2024-03-20T10:45:00Z",
      "query": "How do I reset my password?",
      "latency_ms": 847
    }
  ]
}
```

**Response:**
```json
{
  "verification_id": "vfy_3a5b7c9d",
  "agent_id": "agent_123456",
  "result": "verified",
  "similarity_score": 97.8,
  "threshold": 85.0,
  "verified_at": "2024-03-20T10:46:00Z"
}
```

### Predictive Conflict Resolution™

#### Get Conflict Predictions

```http
GET /api/v1/conflict/predictions?time_horizon=24h&min_probability=0.7
```

**Response:**
```json
{
  "predictions": [
    {
      "id": "conf_pred_1234",
      "agents": ["pricing-agent", "inventory-agent"],
      "type": "resource_contention",
      "probability": 0.94,
      "predicted_time": "2024-03-21T10:30:00Z",
      "resource": "supplier-api",
      "estimated_impact": {
        "min_usd": 12000,
        "max_usd": 18000
      },
      "resolution_available": true
    }
  ],
  "summary": {
    "total_predicted": 12,
    "critical": 2,
    "total_at_risk_value": 124000
  }
}
```

#### Trigger Pre-Conflict Negotiation

```http
POST /api/v1/conflict/negotiate
Content-Type: application/json

{
  "conflict_id": "conf_pred_1234",
  "auto_resolve": true
}
```

**Response:**
```json
{
  "negotiation_id": "neg_5678",
  "status": "completed",
  "resolution_path": {
    "strategy": "caching",
    "action": "Route pricing agent to cache for 15 minutes",
    "estimated_outcome": {
      "conflict_avoided": true,
      "cost_savings": 14500
    }
  }
}
```

### Value Discovery Engine™

#### Get Discovered Value

```http
GET /api/v1/value/discoveries?timeframe=last_30_days&min_value=10000
```

**Response:**
```json
{
  "discoveries": [
    {
      "id": "val_disc_7890",
      "pattern_type": "CROSS_FUNCTIONAL_SYNERGY",
      "discovered_at": "2024-03-15T08:23:18Z",
      "confidence": 0.97,
      "description": "Marketing and Sales agents sharing customer intent data",
      "agents_involved": ["content-optimizer", "deal-desk"],
      "value": {
        "annual": 4200000,
        "quarterly": 1050000
      },
      "recommendations": [
        {
          "action": "Formalize data sharing protocol",
          "estimated_additional_value": 8100000
        }
      ]
    }
  ],
  "summary": {
    "total_discoveries": 17,
    "total_annual_value": 18400000
  }
}
```

#### Run Manual Discovery

```http
POST /api/v1/value/discover
Content-Type: application/json

{
  "scope": "all_agents",
  "lookback_days": 90,
  "min_confidence": 0.8
}
```

**Response:**
```json
{
  "discovery_job_id": "job_4567",
  "status": "PROCESSING",
  "estimated_completion": "2024-03-21T10:30:00Z"
}
```

### ROI Analytics

#### Get ROI Dashboard

```http
GET /api/v1/roi/dashboard?agent_id=agent_123456&timeframe=month
```

**Response:**
```json
{
  "agent_id": "agent_123456",
  "agent_name": "customer-support-claude",
  "summary": {
    "total_cost": 123.45,
    "total_savings": 12345.67,
    "net_roi": 12222.22,
    "roi_percentage": 9900
  },
  "metrics": {
    "queries_handled": 8472,
    "avg_cost_per_query": 0.0146,
    "human_equivalent_hours": 847
  }
}
```

## Webhooks

### Register Webhook

```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-company.com/webhooks/augur",
  "events": ["audit.violation", "conflict.predicted", "value.discovered"],
  "secret": "your_webhook_secret",
  "enabled": true
}
```

**Response:**
```json
{
  "id": "wh_123456",
  "url": "https://your-company.com/webhooks/augur",
  "events": ["audit.violation", "conflict.predicted", "value.discovered"],
  "created_at": "2024-03-20T11:00:00Z",
  "status": "active"
}
```

### Webhook Payload Example

```json
{
  "event_id": "evt_webhook_123456",
  "event_type": "audit.violation",
  "timestamp": "2024-03-20T11:05:00Z",
  "data": {
    "violation_id": "aud_123456",
    "severity": "critical",
    "agent_id": "agent_123456",
    "description": "PII detected in response"
  }
}
```

## SDK Examples

### Python

```python
from augur import AUGURClient

client = AUGURClient(api_key="your_api_key")

# List agents
agents = client.agents.list(status="active")
for agent in agents:
    print(f"{agent.name}: {agent.status}")

# Ingest event
client.events.ingest(
    agent_id="agent_123456",
    event_type="query",
    data={"query": "How do I reset my password?"}
)

# Get predictions
predictions = client.conflict.predictions(time_horizon="24h")
```

### JavaScript

```javascript
import { AUGURClient } from '@augur/sdk';

const client = new AUGURClient({
  apiKey: 'your_api_key'
});

// List agents
const agents = await client.agents.list({ status: 'active' });

// Ingest event
await client.events.ingest({
  agentId: 'agent_123456',
  eventType: 'query',
  data: { query: 'How do I reset my password?' }
});
```

### cURL

```bash
# List agents
curl -H "Authorization: Bearer your_api_key" \
     "https://api.augur.ai/v1/agents"

# Ingest event
curl -X POST \
     -H "Authorization: Bearer agent_api_key" \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "agent_123456", "event_type": "query", "data": {"query": "Hello"}}' \
     "https://api.augur.ai/v1/events"
```

## API Versioning

| Version | Status | Release Date |
|---------|--------|--------------|
| v1 | Current | 2024-03-20 |
| v1beta | Deprecated | 2024-01-15 |

## Support

- **API Status:** [status.augur.ai](https://status.augur.ai)
- **Documentation:** [docs.augur.ai](https://docs.augur.ai)
- **Support Email:** api-support@augur.ai

---

**Last Updated:** March 2024
**Version:** 1.0
```
