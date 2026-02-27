#!/usr/bin/env python3
"""
ШАГ 8: Добавляем Prometheus + Grafana мониторинг
Запустите этот скрипт в папке AUGUR-REAL
"""

import os
import sys

def run(cmd):
    print(f"▶ {cmd}")
    os.system(cmd)

print("""
╔══════════════════════════════════════════════════════════════╗
║  ШАГ 8: Добавляем Prometheus + Grafana мониторинг          ║
║  для всех микросервисов                                     ║
╚══════════════════════════════════════════════════════════════╝
""")

# 1. Создаём структуру для мониторинга
os.makedirs("monitoring/prometheus", exist_ok=True)
os.makedirs("monitoring/grafana/provisioning/datasources", exist_ok=True)
os.makedirs("monitoring/grafana/provisioning/dashboards", exist_ok=True)
os.makedirs("monitoring/grafana/dashboards", exist_ok=True)
os.makedirs("monitoring/alertmanager", exist_ok=True)

# 2. Создаём Prometheus конфигурацию
with open("monitoring/prometheus/prometheus.yml", "w") as f:
    f.write("""# Prometheus Configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'augur-platform'

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# Rule files
rule_files:
  - 'alerts.yml'

# Scrape configuration
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    metrics_path: /metrics
    static_configs:
      - targets: ['api-gateway:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'api-gateway'

  - job_name: 'agent-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['agent-service:8001']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'agent-service'

  - job_name: 'orchestration-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['orchestration-service:8002']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'orchestration'

  - job_name: 'memory-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['memory-service:8003']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'memory-service'

  - job_name: 'governance-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['governance-service:8004']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'governance'

  - job_name: 'conflict-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['conflict-service:8005']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'conflict'

  - job_name: 'value-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['value-service:8006']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'value-service'

  - job_name: 'quantum-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['quantum-service:8007']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'quantum-service'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
""")

# 3. Создаём алерты
with open("monitoring/prometheus/alerts.yml", "w") as f:
    f.write("""groups:
  - name: augur_alerts
    interval: 30s
    rules:
      # Service down alerts
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute."

      # High error rate alerts
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: "Error rate is {{ $value }} for the last 5 minutes"

      # High latency alerts
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.job }}"
          description: "95th percentile latency is {{ $value }}s"

      # Database connection alerts
      - alert: DatabaseConnectionsLow
        expr: pg_stat_database_numbackends < 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low database connections"
          description: "Database has fewer than 5 active connections"

      # Redis memory alerts
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis is using {{ $value | humanizePercentage }} of max memory"

      # Agent count alerts
      - alert: LowAgentCount
        expr: agent_registered_count < 5
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Low agent count"
          description: "Only {{ $value }} agents registered"

      # Conflict rate alerts
      - alert: HighConflictRate
        expr: rate(conflicts_detected_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High conflict rate"
          description: "{{ $value }} conflicts per second detected"

      # Swarm intelligence alerts
      - alert: LowSwarmIntelligence
        expr: swarm_intelligence_score < 0.5
        for: 15m
        labels:
          severity: info
        annotations:
          summary: "Low swarm intelligence"
          description: "Swarm intelligence score is {{ $value }}"

      # API rate limit alerts
      - alert: ApproachingRateLimit
        expr: rate(http_requests_total[1m]) > 800
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Approaching rate limit"
          description: "{{ $value }} requests per minute, limit is 1000"

      # Disk space alerts
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Less than 10% disk space available"

      # CPU alerts
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.job }}"
          description: "CPU usage is {{ $value }}"
""")

# 4. Создаём Alertmanager конфигурацию
with open("monitoring/alertmanager/config.yml", "w") as f:
    f.write("""# Alertmanager Configuration
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'

route:
  group_by: ['alertname', 'job']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default-receiver'
  routes:
    - match:
        severity: critical
      receiver: 'critical-receiver'
      continue: true
    - match:
        severity: warning
      receiver: 'warning-receiver'
    - match:
        service: 'database'
      receiver: 'database-receiver'

receivers:
  - name: 'default-receiver'
    slack_configs:
      - channel: '#alerts'
        title: 'AUGUR Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}\n{{ end }}'

  - name: 'critical-receiver'
    slack_configs:
      - channel: '#critical'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
    email_configs:
      - to: 'admin@augur.com'
        from: 'alerts@augur.com'
        smarthost: 'smtp.gmail.com:587'

  - name: 'warning-receiver'
    slack_configs:
      - channel: '#warnings'
        title: '⚠️ Warning: {{ .GroupLabels.alertname }}'

  - name: 'database-receiver'
    slack_configs:
      - channel: '#database'
        title: '🗄️ Database Alert'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'job']
""")

# 5. Создаём Grafana datasource
with open("monitoring/grafana/provisioning/datasources/prometheus.yml", "w") as f:
    f.write("""apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "15s"
      queryTimeout: "30s"
      httpMethod: "POST"

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      maxLines: 1000
""")

# 6. Создаём Grafana dashboard provisioning
with open("monitoring/grafana/provisioning/dashboards/dashboards.yml", "w") as f:
    f.write("""apiVersion: 1

providers:
  - name: 'AUGUR Dashboards'
    orgId: 1
    folder: 'AUGUR'
    folderUid: ''
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 10
    options:
      path: /etc/grafana/dashboards
""")

# 7. Создаём главный дашборд для AUGUR
with open("monitoring/grafana/dashboards/augur_main.json", "w") as f:
    f.write("""{
  "dashboard": {
    "title": "AUGUR Platform Overview",
    "description": "Main dashboard for AUGUR Enterprise Platform",
    "timezone": "browser",
    "panels": [
      {
        "title": "Services Status",
        "type": "stat",
        "datasource": "Prometheus",
        "gridPos": {"h": 4, "w": 4, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "count(up == 1)",
            "legendFormat": "Healthy"
          },
          {
            "expr": "count(up == 0)",
            "legendFormat": "Unhealthy"
          }
        ]
      },
      {
        "title": "Total Agents",
        "type": "stat",
        "datasource": "Prometheus",
        "gridPos": {"h": 4, "w": 4, "x": 4, "y": 0},
        "targets": [
          {
            "expr": "agent_registered_count",
            "legendFormat": "Agents"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])",
            "legendFormat": "{{job}}"
          }
        ]
      },
      {
        "title": "Response Time (95th Percentile)",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))",
            "legendFormat": "{{job}}"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "connections"
          }
        ]
      },
      {
        "title": "Redis Memory Usage",
        "type": "gauge",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 6, "x": 0, "y": 20},
        "targets": [
          {
            "expr": "redis_memory_used_bytes / redis_memory_max_bytes",
            "legendFormat": "memory usage"
          }
        ]
      },
      {
        "title": "Active Conflicts",
        "type": "stat",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 6, "x": 6, "y": 20},
        "targets": [
          {
            "expr": "conflicts_active_count",
            "legendFormat": "conflicts"
          }
        ]
      },
      {
        "title": "Swarm Intelligence Score",
        "type": "gauge",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 6, "x": 12, "y": 20},
        "targets": [
          {
            "expr": "swarm_intelligence_score",
            "legendFormat": "score"
          }
        ]
      },
      {
        "title": "Value Discovery",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 6, "x": 18, "y": 20},
        "targets": [
          {
            "expr": "value_streams_discovered_total",
            "legendFormat": "discovered"
          },
          {
            "expr": "value_streams_implemented_total",
            "legendFormat": "implemented"
          }
        ]
      }
    ],
    "refresh": "10s",
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
""")

# 8. Создаём дашборд для микросервисов
with open("monitoring/grafana/dashboards/microservices.json", "w") as f:
    f.write("""{
  "dashboard": {
    "title": "Microservices Details",
    "description": "Detailed metrics for each microservice",
    "timezone": "browser",
    "panels": [
      {
        "title": "API Gateway",
        "type": "row",
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 0}
      },
      {
        "title": "Request Rate - API Gateway",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 12, "x": 0, "y": 1},
        "targets": [
          {
            "expr": "rate(http_requests_total{job='api-gateway'}[5m])",
            "legendFormat": "requests"
          }
        ]
      },
      {
        "title": "Latency - API Gateway",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 12, "x": 12, "y": 1},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job='api-gateway'}[5m]))",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "Agent Service",
        "type": "row",
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 7}
      },
      {
        "title": "Active Agents",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "agent_active_count",
            "legendFormat": "active"
          }
        ]
      },
      {
        "title": "Agent Operations",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 8},
        "targets": [
          {
            "expr": "rate(agent_operations_total[5m])",
            "legendFormat": "{{operation}}"
          }
        ]
      },
      {
        "title": "Fingerprint Analysis",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 8},
        "targets": [
          {
            "expr": "rate(fingerprint_analysis_total[5m])",
            "legendFormat": "{{result}}"
          }
        ]
      },
      {
        "title": "Orchestration Service",
        "type": "row",
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 14}
      },
      {
        "title": "Queue Size",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 15},
        "targets": [
          {
            "expr": "task_queue_size",
            "legendFormat": "queue"
          }
        ]
      },
      {
        "title": "Task Processing Rate",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 15},
        "targets": [
          {
            "expr": "rate(tasks_processed_total[5m])",
            "legendFormat": "{{status}}"
          }
        ]
      },
      {
        "title": "Worker Count",
        "type": "stat",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 15},
        "targets": [
          {
            "expr": "worker_active_count",
            "legendFormat": "workers"
          }
        ]
      },
      {
        "title": "Memory Service",
        "type": "row",
        "gridPos": {"h": 1, "w": 24, "x": 0, "y": 21}
      },
      {
        "title": "Vector Store Size",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 0, "y": 22},
        "targets": [
          {
            "expr": "memory_vectors_count",
            "legendFormat": "vectors"
          }
        ]
      },
      {
        "title": "Search Operations",
        "type": "graph",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 8, "y": 22},
        "targets": [
          {
            "expr": "rate(search_operations_total[5m])",
            "legendFormat": "searches"
          }
        ]
      },
      {
        "title": "Average Similarity Score",
        "type": "gauge",
        "datasource": "Prometheus",
        "gridPos": {"h": 6, "w": 8, "x": 16, "y": 22},
        "targets": [
          {
            "expr": "avg_similarity_score",
            "legendFormat": "score"
          }
        ]
      }
    ],
    "refresh": "10s",
    "time": {
      "from": "now-1h",
      "to": "now"
    }
  }
}
""")

# 9. Добавляем метрики в микросервисы
print("📊 Добавляем метрики в микросервисы...")

# Обновляем Agent Service с метриками
with open("backend/services/agent-service/src/main.py", "r") as f:
    agent_code = f.read()

# Добавляем импорт для метрик
if "from prometheus_client" not in agent_code:
    agent_code = agent_code.replace(
        "import logging",
        "import logging\nfrom prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY\nfrom fastapi import Response"
    )

# Добавляем метрики
metrics_code = """
# Prometheus metrics
agent_created = Counter('agent_created_total', 'Total agents created')
agent_deleted = Counter('agent_deleted_total', 'Total agents deleted')
agent_heartbeats = Counter('agent_heartbeats_total', 'Total agent heartbeats')
agent_active = Gauge('agent_active_count', 'Number of active agents')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@app.middleware("http")
async def monitor_requests(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    request_duration.labels(method=request.method, endpoint=request.url.path).observe(duration)
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
"""

# Вставляем метрики после импортов
agent_code = agent_code.replace(
    "app = FastAPI(title=\"Agent Service\", version=\"1.0.0\")",
    "app = FastAPI(title=\"Agent Service\", version=\"1.0.0\")\n" + metrics_code
)

# Обновляем счётчики в операциях
agent_code = agent_code.replace(
    "logger.info(f\"✅ Agent created: {agent_id}\")",
    "agent_created.inc()\n        agent_active.inc()\n        logger.info(f\"✅ Agent created: {agent_id}\")"
)

agent_code = agent_code.replace(
    "logger.info(f\"✅ Agent deleted: {agent_id}\")",
    "agent_deleted.inc()\n        agent_active.dec()\n        logger.info(f\"✅ Agent deleted: {agent_id}\")"
)

agent_code = agent_code.replace(
    "logger.info(f\"✅ Agent heartbeat: {agent_id}\")" if "heartbeat" in agent_code else "",
    "agent_heartbeats.inc()\n        logger.info(f\"✅ Agent heartbeat: {agent_id}\")"
)

with open("backend/services/agent-service/src/main.py", "w") as f:
    f.write(agent_code)

print("   ✅ Agent Service updated with metrics")

# 10. Обновляем docker-compose.yml с мониторингом
with open("docker-compose.yml", "r") as f:
    compose = f.read()

# Добавляем сервисы мониторинга
monitoring_services = """
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    networks:
      - augur-net
    depends_on:
      - alertmanager

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/config.yml'
      - '--storage.path=/alertmanager'
    networks:
      - augur-net

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/augur_main.json
    volumes:
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./monitoring/grafana/dashboards:/etc/grafana/dashboards
      - grafana-data:/var/lib/grafana
    networks:
      - augur-net
    depends_on:
      - prometheus

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - augur-net

  # cAdvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks:
      - augur-net

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://augur:augur@postgres:5432/augur?sslmode=disable
    networks:
      - augur-net
    depends_on:
      - postgres

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis:6379
    networks:
      - augur-net
    depends_on:
      - redis

  # Loki (log aggregation)
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - augur-net

  # Promtail (log collector)
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    command: -config.file=/etc/promtail/config.yml
    networks:
      - aur-net
"""

# Добавляем volumes
monitoring_volumes = """
  prometheus-data:
  grafana-data:
"""

# Вставляем сервисы перед последним сервисом
last_service_index = compose.rfind("\n  #")
compose = compose[:last_service_index] + monitoring_services + compose[last_service_index:]

# Добавляем volumes
compose = compose.replace("volumes:\n  postgres-data:", "volumes:\n  postgres-data:" + monitoring_volumes)

with open("docker-compose.yml", "w") as f:
    f.write(compose)

print("   ✅ docker-compose.yml updated with monitoring services")

# 11. Создаём тест для мониторинга
with open("test_monitoring.py", "w") as f:
    f.write("""import requests
import time

print("🧪 Testing Monitoring Stack...\\n")

# 1. Check Prometheus
print("1️⃣ Checking Prometheus...")
try:
    resp = requests.get("http://localhost:9090/-/healthy")
    if resp.status_code == 200:
        print("   ✅ Prometheus is healthy")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check Grafana
print("\\n2️⃣ Checking Grafana...")
try:
    resp = requests.get("http://localhost:3001/api/health")
    if resp.status_code == 200:
        print("   ✅ Grafana is healthy")
        print("      URL: http://localhost:3001 (admin/admin)")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check Alertmanager
print("\\n3️⃣ Checking Alertmanager...")
try:
    resp = requests.get("http://localhost:9093/-/healthy")
    if resp.status_code == 200:
        print("   ✅ Alertmanager is healthy")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Check metrics endpoints
print("\\n4️⃣ Checking metrics endpoints...")
services = [
    ("Agent Service", "http://localhost:8001/metrics"),
    ("API Gateway", "http://localhost:8000/metrics"),
]

for name, url in services:
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            print(f"   ✅ {name} metrics available")
        else:
            print(f"   ❌ {name} failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ {name} error: {e}")

# 5. Check exporters
print("\\n5️⃣ Checking exporters...")
exporters = [
    ("Node Exporter", "http://localhost:9100/metrics"),
    ("cAdvisor", "http://localhost:8080/metrics"),
    ("PostgreSQL Exporter", "http://localhost:9187/metrics"),
    ("Redis Exporter", "http://localhost:9121/metrics"),
]

for name, url in exporters:
    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            print(f"   ✅ {name} is running")
        else:
            print(f"   ❌ {name} failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ {name} error: {e}")

# 6. Check Loki
print("\\n6️⃣ Checking Loki...")
try:
    resp = requests.get("http://localhost:3100/ready")
    if resp.status_code == 200:
        print("   ✅ Loki is ready")
    else:
        print(f"   ❌ Failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\\n" + "="*50)
print("✅ Monitoring test complete")
print("="*50)
print("\\n📊 Access your monitoring stack:")
print("   • Grafana: http://localhost:3001 (admin/admin)")
print("   • Prometheus: http://localhost:9090")
print("   • Alertmanager: http://localhost:9093")
print("   • cAdvisor: http://localhost:8080")
""")

# 12. Создаём README для мониторинга
with open("monitoring/README.md", "w") as f:
    f.write("""# AUGUR Monitoring Stack

## 📊 Components

| Component | Port | Description |
|-----------|------|-------------|
| **Grafana** | 3001 | Visualization and dashboards |
| **Prometheus** | 9090 | Metrics collection and storage |
| **Alertmanager** | 9093 | Alert handling and notification |
| **Loki** | 3100 | Log aggregation |
| **Node Exporter** | 9100 | System metrics |
| **cAdvisor** | 8080 | Container metrics |
| **PostgreSQL Exporter** | 9187 | Database metrics |
| **Redis Exporter** | 9121 | Redis metrics |

## 🚀 Quick Start

```bash
# Everything should already be running
docker-compose ps

# Check all services
python test_monitoring.py
