# AUGUR API Specification

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
      },
      "fingerprint": {
        "id": "fp_7f8e3d2a",
        "confidence": 98.7,
        "last_verified": "2024-03-20T10:00:00Z"
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
  "configuration": {
    "model": "claude-3-opus-20240229",
    "temperature": 0.7,
    "max_tokens": 4096,
    "system_prompt": "You are a helpful customer support agent..."
  },
  "created_at": "2024-01-15T09:00:00Z",
  "created_by": "user_admin",
  "last_seen": "2024-03-20T10:23:45Z",
  "last_modified": "2024-03-01T14:30:00Z",
  "tags": ["production", "customer-facing", "high-priority"],
  "metadata": {
    "cost_center": "support",
    "owner": "team-support",
    "sla": "24h"
  },
  "metrics": {
    "total_actions": 15432,
    "actions_last_24h": 847,
    "avg_latency_ms": 847,
    "p95_latency_ms": 1243,
    "error_rate": 0.02,
    "tokens_used": 2456789,
    "estimated_cost": 123.45,
    "estimated_savings": 12345.67
  },
  "fingerprint": {
    "id": "fp_7f8e3d2a",
    "vector": "7f8e3d2a1c5b9e4f6a2d8c3b7e1f9a4d",
    "confidence": 98.7,
    "dimensions_analyzed": 7,
    "last_verified": "2024-03-20T10:00:00Z",
    "drift_detected": false
  },
  "conflicts": {
    "last_24h": 2,
    "prevented": 5,
    "high_risk_pairs": ["agent_inventory", "agent_pricing"]
  },
  "roi": {
    "daily": 1234.56,
    "weekly": 8641.92,
    "monthly": 37008.23,
    "quarterly": 111024.69,
    "annual_projected": 444098.76
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
  "configuration": {
    "model": "claude-3-opus-20240229",
    "temperature": 0.7,
    "max_tokens": 4096,
    "system_prompt": "You are a helpful customer support agent..."
  },
  "tags": ["staging", "test"],
  "metadata": {
    "cost_center": "support",
    "owner": "team-support"
  }
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
  "created_at": "2024-03-20T10:30:00Z",
  "next_steps": [
    "Configure agent to send events to webhook URL",
    "Wait for baseline data collection (24-48 hours)",
    "Fingerprint will be generated automatically"
  ]
}
```

#### Update Agent

```http
PATCH /api/v1/agents/{agent_id}
Content-Type: application/json

{
  "name": "customer-support-claude-v2",
  "configuration": {
    "temperature": 0.5
  },
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
  "updated_fields": ["name", "configuration.temperature", "tags", "status"]
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
    "tokens_used": 156,
    "model": "claude-3-opus",
    "temperature": 0.7
  },
  "context": {
    "session_id": "sess_abcdef",
    "user_id": "user_123",
    "department": "support"
  }
}
```

**Response:** (202 Accepted)
```json
{
  "event_id": "evt_abcdef123456",
  "status": "processing",
  "estimated_processing_time": "50ms"
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
      "data": { "query": "How do I reset my password?", "response": "..." }
    },
    {
      "agent_id": "agent_123456",
      "event_type": "query",
      "timestamp": "2024-03-20T10:24:12Z",
      "data": { "query": "What are your hours?", "response": "..." }
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
  "errors": [],
  "status_url": "/api/v1/events/batch/batch_abcdef/status"
}
```

#### Get Events

```http
GET /api/v1/events?agent_id=agent_123456&start=2024-03-01T00:00:00Z&end=2024-03-07T23:59:59Z&limit=100
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | Filter by agent |
| `event_type` | string | Filter by event type |
| `start` | datetime | Start time (ISO 8601) |
| `end` | datetime | End time (ISO 8601) |
| `limit` | integer | Max items per page |
| `offset` | integer | Pagination offset |

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
        "response": "To reset your password, please visit...",
        "latency_ms": 847,
        "tokens_used": 156
      },
      "analysis": {
        "policy_violations": [],
        "anomaly_score": 0.02,
        "confidence": 0.95
      }
    }
  ],
  "pagination": {
    "total": 15432,
    "limit": 100,
    "offset": 0
  },
  "summary": {
    "total_events": 15432,
    "avg_latency": 847,
    "error_rate": 0.02
  }
}
```

### Audit

#### Get Audit Logs

```http
GET /api/v1/audit/logs?agent_id=agent_123456&severity=high&limit=50
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
      "agent_name": "customer-support-claude",
      "description": "Agent attempted to access restricted customer data",
      "details": {
        "policy": "data_privacy_policy_v2",
        "rule": "no_pii_in_logs",
        "violation": "credit_card_number_detected",
        "action_taken": "blocked_and_logged"
      },
      "recommendation": "Review agent configuration and retrain on PII detection",
      "acknowledged": false
    }
  ],
  "summary": {
    "total": 23,
    "critical": 2,
    "high": 5,
    "medium": 8,
    "low": 8
  }
}
```

#### Create Audit Rule

```http
POST /api/v1/audit/rules
Content-Type: application/json

{
  "name": "Block PII in responses",
  "description": "Prevent agents from exposing PII in responses",
  "severity": "critical",
  "conditions": {
    "type": "regex_match",
    "field": "data.response",
    "pattern": "\\b\\d{3}-\\d{2}-\\d{4}\\b|\\b\\d{16}\\b"
  },
  "action": "block_and_alert",
  "enabled": true,
  "notify": ["security@company.com", "slack:security-alerts"]
}
```

**Response:**
```json
{
  "id": "rule_123456",
  "name": "Block PII in responses",
  "created_at": "2024-03-20T10:40:00Z",
  "created_by": "user_admin",
  "test_results": {
    "matches_found": 12,
    "false_positives": 1,
    "accuracy": 0.92
  }
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
        "p95": 1243,
        "distribution": "normal",
        "signature": "a1b2c3d4"
      }
    },
    {
      "name": "vocabulary_fingerprint",
      "value": {
        "unique_words": 1243,
        "formality_score": 0.87,
        "top_terms": ["password", "account", "reset", "help", "thanks"],
        "signature": "e5f6g7h8"
      }
    }
  ],
  "generated_at": "2024-03-15T00:00:00Z",
  "last_verified": "2024-03-20T10:00:00Z",
  "drift_detected": false,
  "drift_score": 2.3,
  "stability": "stable"
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
      "response": "To reset your password, please visit...",
      "latency_ms": 847,
      "tokens_used": 156
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
  "confidence": 99.2,
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
        "max_usd": 18000,
        "description": "API rate limit contention causing delays"
      },
      "resolution_available": true,
      "resolution": {
        "approach": "caching_intervention",
        "action": "Route pricing agent to cache",
        "estimated_outcome": "Conflict avoided, $14,500 saved"
      }
    }
  ],
  "summary": {
    "total_predicted": 12,
    "critical": 2,
    "high": 4,
    "medium": 6,
    "total_at_risk_value": 124000
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
      "pattern_type": "cross_functional_synergy",
      "discovered_at": "2024-03-15T08:23:18Z",
      "confidence": 0.97,
      "description": "Marketing agent and Sales agent discovered sharing customer intent data",
      "agents_involved": ["content-optimizer", "deal-desk"],
      "value": {
        "annual": 4200000,
        "quarterly": 1050000,
        "monthly": 350000,
        "attribution": {
          "direct_revenue": 2800000,
          "cost_savings": 1400000
        }
      },
      "mechanism": "Marketing intent signals allow sales to prioritize leads with 3.2x higher conversion probability",
      "recommendations": [
        {
          "action": "Formalize data sharing protocol",
          "estimated_additional_value": 8100000,
          "implementation_cost": 120000,
          "roi_percent": 6750,
          "priority": "critical"
        }
      ]
    }
  ],
  "summary": {
    "total_discoveries": 17,
    "total_annual_value": 18400000,
    "pending_recommendations": 23,
    "total_potential_value": 41200000
  }
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
  "timeframe": {
    "start": "2024-03-01T00:00:00Z",
    "end": "2024-03-20T23:59:59Z"
  },
  "summary": {
    "total_cost": 123.45,
    "total_savings": 12345.67,
    "net_roi": 12222.22,
    "roi_percentage": 9900,
    "payback_period_days": 3
  },
  "metrics": {
    "queries_handled": 8472,
    "avg_cost_per_query": 0.0146,
    "human_equivalent_hours": 847,
    "human_hourly_rate": 45,
    "savings_calculation": "847 hours * $45 = $38,115 - $123.45 cost = $37,991.55"
  },
  "breakdown": [
    {
      "category": "direct_cost_savings",
      "amount": 37991.55,
      "description": "Support hours saved"
    },
    {
      "category": "revenue_impact",
      "amount": 2345.67,
      "description": "Increased conversion from faster responses"
    },
    {
      "category": "prevented_costs",
      "amount": 567.89,
      "description": "Escalations avoided"
    }
  ],
  "trend": {
    "daily": [1234, 1245, 1256, 1267, 1278],
    "labels": ["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"]
  }
}
```

## Webhooks

AUGUR can send real-time notifications to your endpoints.

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
    "description": "PII detected in response",
    "details": {
      "policy": "data_privacy_policy_v2",
      "matched_pattern": "credit_card"
    }
  },
  "signature": "sha256=5d5b09f6b7c9d9a6b3b8d9c8a7b6c5d4e3f2g1h0i9j8k7l6m5n4o3p2q1r0s"
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

# Get agent details
agent = client.agents.get("agent_123456")
print(f"ROI: ${agent.roi.monthly:,.2f}")

# Ingest event
client.events.ingest(
    agent_id="agent_123456",
    event_type="query",
    data={
        "query": "How do I reset my password?",
        "response": "Visit account settings...",
        "latency_ms": 847
    }
)

# Get conflict predictions
predictions = client.conflict.predictions(time_horizon="24h")
for pred in predictions:
    if pred.probability > 0.8:
        print(f"⚠️ High conflict risk: {pred.agents}")
```

### JavaScript/TypeScript

```typescript
import { AUGURClient } from '@augur/sdk';

const client = new AUGURClient({
  apiKey: 'your_api_key'
});

// List agents
const agents = await client.agents.list({ status: 'active' });
agents.forEach(agent => {
  console.log(`${agent.name}: ${agent.status}`);
});

// Get agent details
const agent = await client.agents.get('agent_123456');
console.log(`ROI: $${agent.roi.monthly.toLocaleString()}`);

// Ingest event
await client.events.ingest({
  agentId: 'agent_123456',
  eventType: 'query',
  data: {
    query: 'How do I reset my password?',
    response: 'Visit account settings...',
    latencyMs: 847
  }
});

// Webhook handling
app.post('/webhooks/augur', (req, res) => {
  const signature = req.headers['x-augur-signature'];
  if (client.webhooks.verify(signature, req.body)) {
    const event = req.body;
    console.log(`Received event: ${event.event_type}`);
    res.status(200).send('OK');
  } else {
    res.status(401).send('Invalid signature');
  }
});
```

### cURL

```bash
# List agents
curl -H "Authorization: Bearer your_api_key" \
     "https://api.augur.ai/v1/agents?status=active"

# Get agent details
curl -H "Authorization: Bearer your_api_key" \
     "https://api.augur.ai/v1/agents/agent_123456"

# Ingest event
curl -X POST \
     -H "Authorization: Bearer agent_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "agent_123456",
       "event_type": "query",
       "data": {
         "query": "How do I reset my password?",
         "latency_ms": 847
       }
     }' \
     "https://api.augur.ai/v1/events"

# Get conflict predictions
curl -H "Authorization: Bearer your_api_key" \
     "https://api.augur.ai/v1/conflict/predictions?time_horizon=24h"
```

## API Versioning

AUGUR follows semantic versioning for API changes.

| Version | Status | Release Date | End of Life |
|---------|--------|--------------|-------------|
| v1 | Current | 2024-03-20 | TBD |
| v1beta | Deprecated | 2024-01-15 | 2024-06-30 |

### Version Migration

When migrating between versions:
1. Check the [changelog](CHANGELOG.md) for breaking changes
2. Update your API base URL from `https://api.augur.ai/v1beta` to `https://api.augur.ai/v1`
3. Test thoroughly in staging environment
4. Update your SDK to latest version

## Support

- **API Status:** [status.augur.ai](https://status.augur.ai)
- **Documentation:** [docs.augur.ai](https://docs.augur.ai)
- **Support Email:** api-support@augur.ai
- **Discord:** [discord.gg/augur](https://discord.gg/augur)
- **GitHub:** [github.com/augur/api-examples](https://github.com/augur/api-examples)

---

**Last Updated:** March 2024  
**Version:** 1.0  
**OpenAPI Spec:** [augur-openapi.yaml](spec/augur-openapi.yaml)
```
