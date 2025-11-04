# 🚀 Deploy em Produção

Guia completo para deploy da Pizzaria API em ambiente de produção com alta disponibilidade e segurança.

## 🏗️ Arquitetura de Produção

```mermaid
graph TB
    A[Internet] --> B[Load Balancer<br/>Nginx/Traefik]
    B --> C[Frontend Container 1]
    B --> D[Frontend Container 2]
    C --> E[API Gateway]
    D --> E
    E --> F[Backend Container 1]
    E --> G[Backend Container 2]
    F --> H[PostgreSQL Master]
    G --> H
    F --> I[PostgreSQL Replica]
    G --> I
    H --> J[Backup Storage]
    K[Redis Cache] --> F
    K --> G
    L[Monitoring<br/>Prometheus/Grafana] --> F
    L --> G
    L --> H
```

## 🐳 Docker Production Setup

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  # Traefik Load Balancer
  traefik:
    image: traefik:v2.10
    container_name: pizzaria_traefik
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${ACME_EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_letsencrypt:/letsencrypt
    networks:
      - pizzaria_prod
    restart: unless-stopped

  # PostgreSQL Master
  postgres_master:
    image: postgres:15-alpine
    container_name: pizzaria_postgres_master
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_REPLICATION_MODE: master
      POSTGRES_REPLICATION_USER: ${DB_REPL_USER}
      POSTGRES_REPLICATION_PASSWORD: ${DB_REPL_PASSWORD}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./docker/postgres/pg_hba.conf:/etc/postgresql/pg_hba.conf
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - pizzaria_prod
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 30s
      timeout: 10s
      retries: 5

  # PostgreSQL Replica
  postgres_replica:
    image: postgres:15-alpine
    container_name: pizzaria_postgres_replica
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_REPLICATION_USER: ${DB_REPL_USER}
      POSTGRES_REPLICATION_PASSWORD: ${DB_REPL_PASSWORD}
      POSTGRES_MASTER_HOST: postgres_master
      POSTGRES_MASTER_PORT: 5432
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
    networks:
      - pizzaria_prod
    depends_on:
      postgres_master:
        condition: service_healthy
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: pizzaria_redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - pizzaria_prod
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API (scaled)
  backend:
    image: ${REGISTRY_URL}/pizzaria/backend:${VERSION}
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres_master:5432/${DB_NAME}
      - DATABASE_REPLICA_URL=postgresql://${DB_USER}:${DB_PASSWORD}@postgres_replica:5432/${DB_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ENVIRONMENT=production
      - SENTRY_DSN=${SENTRY_DSN}
    networks:
      - pizzaria_prod
    depends_on:
      - postgres_master
      - redis
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.${DOMAIN}`)"
      - "traefik.http.routers.backend.entrypoints=websecure"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"
      - "traefik.http.middlewares.backend-auth.basicauth.users=${TRAEFIK_USERS}"

  # Frontend (scaled)
  frontend:
    image: ${REGISTRY_URL}/pizzaria/frontend:${VERSION}
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
    networks:
      - pizzaria_prod
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`${DOMAIN}`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=80"

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: pizzaria_prometheus
    volumes:
      - ./docker/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=15d'
      - '--web.enable-lifecycle'
    networks:
      - pizzaria_prod
    restart: unless-stopped

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: pizzaria_grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - pizzaria_prod
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.grafana.rule=Host(`grafana.${DOMAIN}`)"
      - "traefik.http.routers.grafana.entrypoints=websecure"
      - "traefik.http.routers.grafana.tls.certresolver=letsencrypt"
      - "traefik.http.services.grafana.loadbalancer.server.port=3000"
    restart: unless-stopped

  # Log Aggregation
  loki:
    image: grafana/loki:latest
    container_name: pizzaria_loki
    volumes:
      - ./docker/monitoring/loki.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    networks:
      - pizzaria_prod
    restart: unless-stopped

volumes:
  postgres_master_data:
  postgres_replica_data:
  redis_data:
  traefik_letsencrypt:
  prometheus_data:
  grafana_data:
  loki_data:

networks:
  pizzaria_prod:
    driver: overlay
    external: true
```

## ☁️ Cloud Deployment

### AWS ECS Deployment

```yaml
# ecs-task-definition.json
{
  "family": "pizzaria-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "pizzaria-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/pizzaria-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:pizzaria/database-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:pizzaria/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/pizzaria-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Terraform Infrastructure

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "pizzaria-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = var.environment
    Project     = "pizzaria"
  }
}

# Application Load Balancer
resource "aws_lb" "pizzaria_alb" {
  name               = "pizzaria-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets

  enable_deletion_protection = var.environment == "production"

  tags = {
    Environment = var.environment
    Project     = "pizzaria"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "pizzaria_db" {
  identifier = "pizzaria-db-${var.environment}"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.pizzaria_db.name
  
  backup_retention_period = var.environment == "production" ? 7 : 1
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "production"
  
  tags = {
    Environment = var.environment
    Project     = "pizzaria"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "pizzaria_cluster" {
  name = "pizzaria-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    Project     = "pizzaria"
  }
}

# ECS Service
resource "aws_ecs_service" "pizzaria_backend" {
  name            = "pizzaria-backend"
  cluster         = aws_ecs_cluster.pizzaria_cluster.id
  task_definition = aws_ecs_task_definition.pizzaria_backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.backend.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "pizzaria-backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.backend]

  tags = {
    Environment = var.environment
    Project     = "pizzaria"
  }
}
```

### Kubernetes Deployment

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pizzaria
  labels:
    name: pizzaria
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pizzaria-config
  namespace: pizzaria
data:
  ENVIRONMENT: "production"
  DEBUG: "False"
  REDIS_URL: "redis://pizzaria-redis:6379"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: pizzaria-secrets
  namespace: pizzaria
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@postgres:5432/pizzaria"
  SECRET_KEY: "your-jwt-secret-key"
  REDIS_PASSWORD: "your-redis-password"

---
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pizzaria-backend
  namespace: pizzaria
  labels:
    app: pizzaria-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pizzaria-backend
  template:
    metadata:
      labels:
        app: pizzaria-backend
    spec:
      containers:
      - name: backend
        image: pizzaria/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: pizzaria-config
              key: ENVIRONMENT
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pizzaria-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: pizzaria-secrets
              key: SECRET_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: pizzaria-backend-service
  namespace: pizzaria
spec:
  selector:
    app: pizzaria-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pizzaria-ingress
  namespace: pizzaria
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://pizzaria.example.com"
spec:
  tls:
  - hosts:
    - api.pizzaria.example.com
    secretName: pizzaria-tls
  rules:
  - host: api.pizzaria.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pizzaria-backend-service
            port:
              number: 80
```

## 🔒 Security Configuration

### SSL/TLS Setup

```yaml
# docker/nginx/ssl.conf
server {
    listen 80;
    server_name pizzaria.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pizzaria.example.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/pizzaria.crt;
    ssl_certificate_key /etc/ssl/private/pizzaria.key;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # API proxy with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Environment Variables Security

```bash
# .env.production (use external secret management in real prod)
# Database
DATABASE_URL=postgresql://pizzaria_user:$(cat /run/secrets/db_password)@db.internal:5432/pizzaria_prod

# JWT
SECRET_KEY=$(cat /run/secrets/jwt_secret)

# External Services
SENTRY_DSN=$(cat /run/secrets/sentry_dsn)
REDIS_PASSWORD=$(cat /run/secrets/redis_password)

# Email
SMTP_PASSWORD=$(cat /run/secrets/smtp_password)
SMTP_USER=noreply@pizzaria.example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587

# File Upload
AWS_ACCESS_KEY_ID=$(cat /run/secrets/aws_access_key)
AWS_SECRET_ACCESS_KEY=$(cat /run/secrets/aws_secret_key)
AWS_S3_BUCKET=pizzaria-uploads-prod
AWS_REGION=us-east-1
```

## 📊 Monitoring & Observability

### Prometheus Configuration

```yaml
# docker/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'pizzaria-backend'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend:8000']
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Pizzaria API Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ endpoint }}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ]
      }
    ]
  }
}
```

## 🚨 Alerting Rules

```yaml
# docker/monitoring/rules/alerts.yml
groups:
- name: pizzaria.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: DatabaseDown
    expr: up{job="postgres"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database is down"

  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%"

  - alert: DiskSpaceLow
    expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Low disk space"
      description: "Disk space is {{ $value }}% full"
```

## 🔄 CI/CD Pipeline

### GitHub Actions Production Deploy

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          cd backend
          curl -sSL https://install.python-poetry.org | python3 - || pip install poetry
          poetry install
          
      - name: Run tests
        run: |
          cd backend
          poetry run pytest tests/ -v --cov=src --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security scan
        uses: securecodewarrior/github-action-add-sarif@v1
        with:
          sarif-file: security-scan.sarif

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/Dockerfile.backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        
      - name: Deploy to Kubernetes
        env:
          KUBE_CONFIG: ${{ secrets.KUBE_CONFIG }}
          IMAGE_TAG: ${{ needs.build.outputs.image-tag }}
        run: |
          echo "$KUBE_CONFIG" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
          
          # Update image tag
          kubectl set image deployment/pizzaria-backend \
            backend=$IMAGE_TAG \
            -n pizzaria
            
          # Wait for rollout
          kubectl rollout status deployment/pizzaria-backend -n pizzaria
          
      - name: Run database migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          kubectl exec deployment/pizzaria-backend \
            -n pizzaria \
            -- alembic upgrade head

  notify:
    needs: [deploy]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 📈 Performance Optimization

### Database Optimization

```sql
-- Production database optimizations
-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Logging for monitoring
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;

-- Reload configuration
SELECT pg_reload_conf();
```

### Application Caching

```python
# backend/src/config/cache.py
import redis.asyncio as redis
from functools import wraps
import json
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    def cache(self, expire: int = 300):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key_data = f"{func.__name__}:{args}:{kwargs}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.redis.setex(
                    cache_key, 
                    expire, 
                    json.dumps(result, default=str)
                )
                return result
            return wrapper
        return decorator

# Usage
cache_manager = CacheManager(settings.REDIS_URL)

@cache_manager.cache(expire=600)
async def get_menu_items():
    return await database.fetch_all("SELECT * FROM items WHERE active = true")
```

## 🔧 Maintenance Scripts

### Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="pizzaria_prod"
S3_BUCKET="pizzaria-backups"

# Database backup
docker exec pizzaria_postgres pg_dump -U pizzaria_user $DB_NAME | \
  gzip > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz" \
  "s3://$S3_BUCKET/database/"

# Cleanup old local backups (keep 7 days)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

# Upload logs
docker logs pizzaria_backend 2>&1 | \
  gzip > "$BACKUP_DIR/logs_$TIMESTAMP.log.gz"
  
aws s3 cp "$BACKUP_DIR/logs_$TIMESTAMP.log.gz" \
  "s3://$S3_BUCKET/logs/"

echo "Backup completed successfully: $TIMESTAMP"
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

# Check all services
services=("pizzaria_frontend" "pizzaria_backend" "pizzaria_postgres" "pizzaria_redis")

for service in "${services[@]}"; do
    if ! docker ps | grep -q $service; then
        echo "ERROR: $service is not running"
        exit 1
    fi
done

# Check API health
if ! curl -f http://localhost:8000/health; then
    echo "ERROR: API health check failed"
    exit 1
fi

# Check database connection
if ! docker exec pizzaria_postgres pg_isready -U pizzaria_user; then
    echo "ERROR: Database connection failed"
    exit 1
fi

echo "All services are healthy"
```

Este guia de deploy em produção oferece uma base sólida para colocar a Pizzaria API em produção com alta disponibilidade, monitoramento e segurança adequados.