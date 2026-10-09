# OpenCode AI Coordinator - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Server Options](#server-options)
6. [Security](#security)
7. [Monitoring](#monitoring)
8. [Scaling](#scaling)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **OpenCode AI Coordinator** is a production-ready web application that coordinates multiple AI providers to handle code-related tasks. This guide covers all aspects of deploying and managing the coordinator on your server.

---

## Prerequisites

### Hardware Requirements

| Deployment Type | CPU Cores | RAM | Disk Space | Notes |
|----------------|-----------|-----|------------|-------|
| Development | 2 | 4GB | 10GB | Local testing |
| Small Production | 4 | 8GB | 20GB | ~1000 requests/day |
| Medium Production | 8 | 16GB | 50GB | ~10,000 requests/day |
| Large Production | 16+ | 32GB+ | 100GB+ | High availability |

### Software Requirements

**Required:**
- Python 3.11 or higher
- pip 23.0 or higher
- Git 2.0 or higher

**Optional:**
- Docker 20.10 or higher (for containerized deployment)
- Docker Compose 2.0 or higher
- Redis 7.0 or higher (for caching and task queue)
- PostgreSQL 14 or higher (for persistent storage)
- Nginx (for reverse proxy)
- Certbot (for SSL certificates)

### Network Requirements

- Outbound internet access (for AI provider APIs)
- Inbound access to port 8000 (or custom port)
- Optional: Port 80/443 for web traffic (if using Nginx)
- Optional: Port 6379 for Redis
- Optional: Port 5432 for PostgreSQL

---

## Installation Methods

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/derSeppo/Opencode-Project-Coordinator.git
cd Opencode-Project-Coordinator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment file
cp .env.example .env
nano .env  # Edit with your settings
```

### Method 2: Direct Download

```bash
# Download the repository as ZIP
wget https://github.com/derSeppo/Opencode-Project-Coordinator/archive/refs/heads/main.zip
unzip main.zip
cd Opencode-Project-Coordinator-main

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env
```

### Method 3: Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/derSeppo/Opencode-Project-Coordinator.git
cd Opencode-Project-Coordinator

# Copy and configure environment file
cp .env.example .env
nano .env

# Build and run with Docker Compose
docker-compose up -d
```

### Method 4: Manual Installation

```bash
# Install Python dependencies
pip install fastapi uvicorn aiohttp pydantic pydantic-settings backoff

# Clone or download the repository
# ...

# Configure
cp .env.example .env
nano .env
```

---

## Configuration

### Environment Variables

The coordinator is configured through environment variables in the `.env` file. Here are all available options:

#### Application Settings

```bash
APP_NAME="OpenCode AI Coordinator"
APP_VERSION="1.0.0"
APP_DESCRIPTION="A production-ready webapp that coordinates AI providers"
ENVIRONMENT="production"  # development, staging, production
```

#### Server Settings

```bash
SERVER_HOST="0.0.0.0"      # Bind to all interfaces
SERVER_PORT=8000           # Port to listen on
SERVER_DEBUG=false        # Disable debug in production
SERVER_WORKERS=4          # Number of worker processes
SERVER_RELOAD=false       # Disable auto-reload in production
```

#### Security Settings

```bash
# API Key Authentication
SECURITY_API_KEY_REQUIRED=true
SECURITY_API_KEYS="key1,key2,key3"

# CORS Settings
SECURITY_CORS_ORIGINS="https://yourdomain.com,https://another.com"
SECURITY_CORS_ALLOW_CREDENTIALS=true
SECURITY_CORS_ALLOW_METHODS="GET,POST,PUT,DELETE,OPTIONS"
SECURITY_CORS_ALLOW_HEADERS="*"
```

#### Database Settings

**SQLite (Default):**
```bash
DATABASE_URL="sqlite:///./open_coordinator.db"
```

**PostgreSQL:**
```bash
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/open_coordinator"
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

#### Redis Settings

```bash
REDIS_URL="redis://localhost:6379/0"
REDIS_CACHE_TTL=3600
REDIS_QUEUE_NAME="open_coordinator_tasks"
```

#### Rate Limit Settings

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_REQUESTS_PER_HOUR=10000
RATE_LIMIT_BURST_SIZE=100
```

#### Logging Settings

```bash
LOGGING_LEVEL="INFO"
LOGGING_LOG_FILE="/var/log/open_coordinator.log"
LOGGING_ENABLE_CONSOLE=true
```

#### Template Settings

```bash
TEMPLATES_TEMPLATE_DIR="/opt/open_coordinator/templates"
TEMPLATES_AUTO_RELOAD=true
```

#### Code Settings

```bash
CODE_DEFAULT_LANGUAGE="python"
CODE_DEFAULT_TIMEOUT=300
CODE_MAX_TOKENS=32768
CODE_DEFAULT_TEMPERATURE=0.7
```

### AI Provider Configuration

#### OpenAI

```bash
OPENAI_API_KEY="sk-..."
OPENAI_BASE_URL="https://api.openai.com/v1"
OPENAI_RATE_LIMIT=100
OPENAI_TIMEOUT=120
OPENAI_ENABLED=true
OPENAI_PRIORITY=1
```

#### Anthropic

```bash
ANTHROPIC_API_KEY="sk-ant-..."
ANTHROPIC_BASE_URL="https://api.anthropic.com/v1"
ANTHROPIC_RATE_LIMIT=100
ANTHROPIC_TIMEOUT=120
ANTHROPIC_ENABLED=true
ANTHROPIC_PRIORITY=2
```

#### Mistral AI

```bash
MISTRAL_API_KEY="..."
MISTRAL_BASE_URL="https://api.mistral.ai/v1"
MISTRAL_RATE_LIMIT=100
MISTRAL_TIMEOUT=120
MISTRAL_ENABLED=true
MISTRAL_PRIORITY=3
```

#### Google (Gemini)

```bash
GOOGLE_API_KEY="..."
GOOGLE_BASE_URL="https://generativelanguage.googleapis.com/v1beta"
GOOGLE_RATE_LIMIT=100
GOOGLE_TIMEOUT=120
GOOGLE_ENABLED=false
GOOGLE_PRIORITY=4
```

#### Cohere

```bash
COHERE_API_KEY="..."
COHERE_BASE_URL="https://api.cohere.ai/v1"
COHERE_RATE_LIMIT=100
COHERE_TIMEOUT=120
COHERE_ENABLED=false
COHERE_PRIORITY=5
```

#### Groq

```bash
GROQ_API_KEY="..."
GROQ_BASE_URL="https://api.groq.com/v1"
GROQ_RATE_LIMIT=100
GROQ_TIMEOUT=120
GROQ_ENABLED=false
GROQ_PRIORITY=6
```

#### Local (Ollama, etc.)

```bash
LOCAL_API_KEY=""
LOCAL_BASE_URL="http://localhost:11434/v1"
LOCAL_RATE_LIMIT=100
LOCAL_TIMEOUT=120
LOCAL_ENABLED=false
LOCAL_PRIORITY=7
```

---

## Server Options

### Option 1: Local Development

```bash
# Start with auto-reload and debug
python main.py --debug --reload

# Or with uvicorn
uvicorn open_coordinator.api.main:app --reload --port 8000
```

### Option 2: Production with Uvicorn

```bash
# Start production server
uvicorn open_coordinator.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Option 3: Systemd Service

Create a systemd service file at `/etc/systemd/system/open-coordinator.service`:

```ini
[Unit]
Description=OpenCode AI Coordinator
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/opt/open_coordinator
EnvironmentFile=/opt/open_coordinator/.env
ExecStart=/opt/open_coordinator/.venv/bin/python /opt/open_coordinator/main.py
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable open-coordinator

# Start service
sudo systemctl start open-coordinator

# Check status
sudo systemctl status open-coordinator

# View logs
sudo journalctl -u open-coordinator -f
```

### Option 4: Docker

```bash
# Build the image
docker build -t open-coordinator .

# Run the container
docker run -d \
  --name open-coordinator \
  -p 8000:8000 \
  -v /opt/open_coordinator/.env:/app/.env \
  -v /opt/open_coordinator/logs:/app/logs \
  open-coordinator
```

### Option 5: Docker Compose (Recommended)

```bash
# Start all services (coordinator, redis, nginx)
docker-compose up -d

# View logs
docker-compose logs -f coordinator

# Stop services
docker-compose down

# Update
docker-compose pull && docker-compose up -d --build
```

### Option 6: Nginx Reverse Proxy

Create an Nginx configuration file at `/etc/nginx/sites-available/open-coordinator`:

```nginx
server {
    listen 80;
    server_name ai.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static/ {
        alias /opt/open_coordinator/static/;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/open-coordinator /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

## Security

### API Key Authentication

The coordinator supports API key authentication. Configure in `.env`:

```bash
SECURITY_API_KEY_REQUIRED=true
SECURITY_API_KEYS="key1,key2,key3"
```

Then include the API key in requests:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

### HTTPS with Let's Encrypt

Install Certbot and obtain a certificate:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d ai.yourdomain.com

# Auto-renew certificates
sudo certbot renew --dry-run
```

Update your Nginx configuration to use HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name ai.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/ai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name ai.yourdomain.com;
    return 301 https://$host$request_uri;
}
```

### Firewall Configuration

Configure UFW (Ubuntu firewall):

```bash
# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow custom port (if not using Nginx)
sudo ufw allow 8000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Rate Limiting

Configure rate limiting in `.env`:

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_REQUESTS_PER_HOUR=10000
RATE_LIMIT_BURST_SIZE=100
```

### Security Headers

Add security headers to your Nginx configuration:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline';" always;
```

---

## Monitoring

### Built-in Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Ready check (includes provider status)
curl http://localhost:8000/ready

# Statistics
curl -H "X-API-Key: your-key" http://localhost:8000/stats
```

### Prometheus Metrics

Add Prometheus support to your FastAPI app:

```python
from prometheus_client import make_asgi_app
from prometheus_client.openmetrics.exposition import CONTENT_TYPE_OPENMETRICS

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

Configure Prometheus (`prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'open-coordinator'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard

Create a Grafana dashboard with panels for:
- Request rate
- Error rate
- Response times
- Token usage
- Cost tracking
- Provider usage

### Logging

Configure logging in `.env`:

```bash
LOGGING_LEVEL="INFO"
LOGGING_LOG_FILE="/var/log/open_coordinator.log"
LOGGING_ENABLE_CONSOLE=true
```

View logs:

```bash
# Tail the log file
tail -f /var/log/open_coordinator.log

# Docker logs
docker logs open_coordinator

# Systemd logs
journalctl -u open-coordinator -f
```

---

## Scaling

### Horizontal Scaling

Run multiple instances behind a load balancer:

```bash
# Instance 1
uvicorn open_coordinator.api.main:app --host 0.0.0.0 --port 8001 --workers 4

# Instance 2
uvicorn open_coordinator.api.main:app --host 0.0.0.0 --port 8002 --workers 4

# Instance 3
uvicorn open_coordinator.api.main:app --host 0.0.0.0 --port 8003 --workers 4
```

Configure Nginx as load balancer:

```nginx
upstream open_coordinator {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
    
    # Load balancing method
    least_conn;
}

server {
    listen 80;
    server_name ai.yourdomain.com;
    
    location / {
        proxy_pass http://open_coordinator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Vertical Scaling

Increase resources for a single instance:

```bash
# Use more workers
uvicorn open_coordinator.api.main:app --workers 8

# Increase timeout
uvicorn open_coordinator.api.main:app --timeout-keep-alive 60
```

### Provider Load Balancing

The coordinator automatically load balances between enabled providers based on priority. Configure in `.env`:

```bash
# Higher priority = used first
OPENAI_PRIORITY=1
ANTHROPIC_PRIORITY=2
MISTRAL_PRIORITY=3

# Enable/disable providers
OPENAI_ENABLED=true
ANTHROPIC_ENABLED=true
MISTRAL_ENABLED=true
```

---

## Maintenance

### Updates

```bash
# Git pull
cd /opt/open_coordinator
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart open-coordinator

# Or with Docker
docker-compose pull && docker-compose up -d --build
```

### Backups

```bash
# Database backup (SQLite)
cp /opt/open_coordinator/open_coordinator.db /opt/backups/open_coordinator_$(date +%Y%m%d).db

# Configuration backup
cp /opt/open_coordinator/.env /opt/backups/open_coordinator_$(date +%Y%m%d).env

# Full backup
tar -czvf /opt/backups/open_coordinator_$(date +%Y%m%d).tar.gz /opt/open_coordinator
```

### Cron Jobs

Set up automatic backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * tar -czvf /opt/backups/open_coordinator_$(date +\%Y\%m\%d).tar.gz /opt/open_coordinator

# Add weekly cleanup of old backups
0 3 * * 0 find /opt/backups/open_coordinator_*.tar.gz -mtime +30 -delete
```

### Database Maintenance

For PostgreSQL:

```bash
# Vacuum and analyze
sudo -u postgres psql -d open_coordinator -c "VACUUM ANALYZE;"

# Check connections
sudo -u postgres psql -d open_coordinator -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'open_coordinator';"
```

For SQLite:

```bash
# Vacuum database
sqlite3 /opt/open_coordinator/open_coordinator.db "VACUUM;"

# Check integrity
sqlite3 /opt/open_coordinator/open_coordinator.db "PRAGMA integrity_check;"
```

### Cleanup

```bash
# Remove old logs
find /var/log/open_coordinator*.log -mtime +30 -delete

# Remove old database backups
find /opt/backups/open_coordinator*.db -mtime +30 -delete

# Docker system cleanup
docker system prune -f
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Find and kill the process
sudo lsof -i :8000
sudo kill -9 <PID>

# Or change the port
SERVER_PORT=8001
```

**2. Module not found**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or check Python path
python -c "import sys; print(sys.path)"
```

**3. Permission denied**
```bash
# Check file permissions
ls -la /opt/open_coordinator/

# Fix permissions
sudo chown -R appuser:appuser /opt/open_coordinator/
sudo chmod -R 755 /opt/open_coordinator/
```

**4. Connection refused (Redis)**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis

# Check Redis logs
sudo journalctl -u redis -f
```

**5. Out of memory**
```bash
# Check memory usage
free -h

# Increase swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**6. API rate limits**
```bash
# Check provider rate limits
curl -H "X-API-Key: your-key" http://localhost:8000/providers

# Increase rate limits in .env
OPENAI_RATE_LIMIT=200
```

### Debugging

**Enable debug mode:**
```bash
SERVER_DEBUG=true
```

**View detailed logs:**
```bash
# Tail logs with more context
tail -n 100 -f /var/log/open_coordinator.log

# Docker logs with timestamps
docker logs --timestamps open_coordinator

# Systemd logs with details
journalctl -u open-coordinator -f --no-pager
```

**Test API endpoints:**
```bash
# Health check
curl -v http://localhost:8000/health

# Ready check
curl -v http://localhost:8000/ready

# List providers
curl -v -H "X-API-Key: your-key" http://localhost:8000/providers
```

### Performance Issues

**1. Slow responses**
- Check provider response times
- Increase timeout in `.env`
- Use faster providers (Groq, Local)

**2. High CPU usage**
- Reduce number of workers
- Use async I/O
- Scale horizontally

**3. High memory usage**
- Reduce `SERVER_WORKERS`
- Use smaller models
- Enable Redis for caching

---

## Migration

### From Version 0.x to 1.0

```bash
# Backup old configuration
cp .env .env.backup

# Update dependencies
pip install --upgrade -r requirements.txt

# Review new .env.example
# Copy new settings to .env

# Restart service
sudo systemctl restart open-coordinator
```

### Database Migration

If using SQLite:
```bash
# Backup old database
cp open_coordinator.db open_coordinator.db.backup

# New version will create new database
# Migrate data manually if needed
```

If using PostgreSQL:
```bash
# Run migrations
# (Add migration commands here when available)
```

---

## Best Practices

### Security

1. **Always use HTTPS** in production
2. **Enable API key authentication**
3. **Restrict CORS origins** to your domains
4. **Use firewall** to limit access
5. **Keep software updated**
6. **Monitor for suspicious activity**

### Performance

1. **Use connection pooling** for databases
2. **Enable caching** with Redis
3. **Load balance** between providers
4. **Monitor resource usage**
5. **Scale horizontally** when needed
6. **Use async I/O** for better throughput

### Reliability

1. **Enable multiple providers** for fallback
2. **Set appropriate timeouts**
3. **Implement retry logic**
4. **Monitor error rates**
5. **Have backups** of configuration and data
6. **Test updates** in staging before production

---

## Support

- **Documentation**: See QUICK_START.md, API_DOCUMENTATION.md, EXAMPLES.md
- **Issues**: Report on GitHub
- **Community**: Join the discussion
- **Contributing**: See CONTRIBUTING.md

---

**Happy Deploying!** 🚀
