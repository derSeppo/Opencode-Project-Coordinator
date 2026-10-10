# OpenCode AI Coordinator - Quick Start Guide

## Overview

The **OpenCode AI Coordinator** is a production-ready webapp that connects to multiple AI providers to handle code generation, validation, formatting, and other AI-powered tasks. It supports **12 AI providers** including both paid and **free cloud-based** options.

This guide will get you up and running in **5 minutes**.

---

## Prerequisites

### Hardware Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 10GB disk space
- **Recommended**: 4 CPU cores, 8GB RAM, 20GB disk space

### Software Requirements
- Python 3.11 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### API Keys (Optional)
You'll need API keys for the AI providers you want to use:

#### Paid Providers (API keys required):
- [OpenAI](https://platform.openai.com/account/api-keys) - GPT-4, GPT-3.5
- [Anthropic](https://console.anthropic.com/account/keys) - Claude 3 models
- [Mistral AI](https://console.mistral.ai/api-keys) - Mistral, Mixtral
- [Google AI (Gemini)](https://makersuite.google.com/app/apikey) - Gemini models
- [Cohere](https://dashboard.cohere.com/api-keys) - Command models
- [Groq](https://console.groq.com/keys) - Fast Llama, Mixtral, Gemma

#### Free Cloud-Based Providers (No API key or free tier):
- [HuggingFace](https://huggingface.co/settings/tokens) - 100,000+ free models
- [Together AI](https://api.together.xyz/) - $25/month free credit
- [DeepInfra](https://deepinfra.com/) - Generous free tier
- [Perplexity AI](https://www.perplexity.ai/) - Free access
- [Cerebras](https://inference.cerebras.net/) - Free inference

---

## Installation

### Option 1: Using pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/derSeppo/Opencode-Project-Coordinator.git
cd Opencode-Project-Coordinator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

### Option 2: Using Docker (Easiest)

```bash
# Clone the repository
git clone https://github.com/derSeppo/Opencode-Project-Coordinator.git
cd Opencode-Project-Coordinator

# Copy and edit environment file
cp .env.example .env
nano .env

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f coordinator
```

### Option 3: Manual Installation

```bash
# Install Python dependencies manually
pip install fastapi uvicorn aiohttp pydantic pydantic-settings backoff

# Clone the repository
git clone https://github.com/derSeppo/Opencode-Project-Coordinator.git
cd Opencode-Project-Coordinator

# Create .env file
cp .env.example .env
# Edit .env with your settings
```

---

## Configuration

### Environment Variables

Edit the `.env` file with your settings:

```bash
# ============================================================================
# FREE CLOUD PROVIDERS (No API key required for basic usage)
# ============================================================================

# HuggingFace (100,000+ free models)
HUGGINGFACE_API_KEY="your-hf-token"  # Optional, get from https://huggingface.co/settings/tokens
HUGGINGFACE_ENABLED=true
HUGGINGFACE_PRIORITY=1

# Together AI ($25/month free credit)
TOGETHER_API_KEY="your-together-key"  # Get from https://api.together.xyz/
TOGETHER_ENABLED=true
TOGETHER_PRIORITY=2

# DeepInfra (Generous free tier)
DEEPINFRA_API_KEY="your-deepinfra-key"  # Get from https://deepinfra.com/
DEEPINFRA_ENABLED=true
DEEPINFRA_PRIORITY=3

# Perplexity AI (Free access)
PERPLEXITY_API_KEY="your-perplexity-key"  # Get from https://www.perplexity.ai/
PERPLEXITY_ENABLED=true
PERPLEXITY_PRIORITY=4

# Cerebras (Free inference)
CEREBRAS_API_KEY="your-cerebras-key"  # Get from https://inference.cerebras.net/
CEREBRAS_ENABLED=true
CEREBRAS_PRIORITY=5

# ============================================================================
# PAID PROVIDERS (API keys required)
# ============================================================================

# OpenAI
OPENAI_API_KEY="your-openai-key"
OPENAI_ENABLED=true
OPENAI_PRIORITY=6

# Anthropic
ANTHROPIC_API_KEY="your-anthropic-key"
ANTHROPIC_ENABLED=true
ANTHROPIC_PRIORITY=7

# Mistral AI
MISTRAL_API_KEY="your-mistral-key"
MISTRAL_ENABLED=true
MISTRAL_PRIORITY=8

# Optional: Security
SECURITY_API_KEY_REQUIRED=true
SECURITY_API_KEYS="your-secret-api-key"

# Optional: Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_DEBUG=true  # Only for development
```

### Provider Priority

The coordinator uses providers in priority order. Set lower numbers for higher priority:

```bash
# Use free providers first (recommended for testing)
HUGGINGFACE_PRIORITY=1
TOGETHER_PRIORITY=2
DEEPINFRA_PRIORITY=3

# Then paid providers
OPENAI_PRIORITY=4
ANTHROPIC_PRIORITY=5
MISTRAL_PRIORITY=6
```

**Tip**: Start with free providers to test the system before adding paid API keys!

---

## Starting the Server

### Development Mode

```bash
# Using the main script
python main.py --debug --reload

# Or using uvicorn directly
uvicorn open_coordinator.api.main:app --reload --port 8000
```

The server will start at: **http://localhost:8000**

### Production Mode

```bash
# Without reload (for production)
python main.py --host 0.0.0.0 --port 8000

# Using uvicorn with multiple workers
uvicorn open_coordinator.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build the image
docker build -t open-coordinator .

# Run the container
docker run -d --name open-coordinator -p 8000:8000 -v $(pwd)/.env:/app/.env open-coordinator

# Or using docker-compose
docker-compose up -d
```

---

## Testing the Server

### Health Check

```bash
# Check if server is running
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### Ready Check

```bash
# Check if providers are initialized
curl http://localhost:8000/ready

# Expected response:
# {"status": "ready", "providers": 3, "active_tasks": 0}
```

### List Providers

```bash
# List all configured providers
curl -H "X-API-Key: your-api-key" http://localhost:8000/providers

# Expected response:
# {"openai": {"enabled": true, ...}, "anthropic": {...}, ...}
```

### List Models

```bash
# List all available models
curl -H "X-API-Key: your-api-key" http://localhost:8000/models

# Or for a specific provider
curl -H "X-API-Key: your-api-key" http://localhost:8000/providers/openai/models
```

---

## API Examples

### Generate Code

```bash
# Simple code generation
curl -X POST http://localhost:8000/code/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Python function that calculates Fibonacci numbers",
    "language": "python",
    "temperature": 0.7,
    "max_tokens": 1000
  }'
```

### Validate Code

```bash
# Validate Python code
curl -X POST http://localhost:8000/code/validate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
    "language": "python",
    "check_syntax": true,
    "check_semantics": true
  }'
```

### Format Code

```bash
# Format Python code
curl -X POST http://localhost:8000/code/format \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(name):\n    print(f\"Hello {name}\")",
    "language": "python",
    "style": "pep8",
    "indent_size": 4
  }'
```

### Create a Task

```bash
# Create a generic task
curl -X POST http://localhost:8000/task \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_generation",
    "prompt": "Create a REST API endpoint in FastAPI for user management",
    "language": "python",
    "provider_preference": ["openai", "anthropic"],
    "temperature": 0.8,
    "max_tokens": 2000
  }'
```

### Check Task Status

```bash
# Get task results (replace TASK_ID with actual task ID)
curl -H "X-API-Key: your-api-key" http://localhost:8000/task/TASK_ID

# Expected response:
# {
#   "task_id": "...",
#   "status": "completed",
#   "result": "...",
#   "provider_used": "openai",
#   "model_used": "gpt-4o",
#   "tokens_used": 150,
#   "cost": 0.0015,
#   "execution_time_ms": 250
# }
```

---

## Direct Execution (Synchronous)

For simple use cases, you can execute tasks synchronously:

```bash
# Execute and wait for result
curl -X POST http://localhost:8000/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_generation",
    "prompt": "Write a Python function to reverse a string",
    "language": "python",
    "wait": true,
    "timeout": 30
  }'
```

---

## Accessing Documentation

### Interactive API Docs (Swagger)
- **URL**: http://localhost:8000/docs
- Explore all endpoints interactively
- Try out requests directly from the browser

### Alternative API Docs (ReDoc)
- **URL**: http://localhost:8000/redoc
- Clean, readable API documentation

### OpenAPI Specification
- **URL**: http://localhost:8000/openapi.json
- Raw OpenAPI JSON specification

### Web Interface
- **URL**: http://localhost:8000/web/
- Simple web-based UI for managing tasks and viewing statistics
- Works on Linux, Windows, and macOS

---

## Troubleshooting

### Common Issues

**1. "No available providers" error**
- Solution: Enable at least one provider in `.env` and add its API key

**2. "Authentication failed" error**
- Solution: Check your API keys in `.env`

**3. "Rate limit exceeded" error**
- Solution: Wait a minute or increase rate limits in `.env`

**4. "Module not found" error**
- Solution: Install missing dependencies with `pip install -r requirements.txt`

**5. Port already in use**
- Solution: Change `SERVER_PORT` in `.env` or kill the existing process

### Viewing Logs

```bash
# Development mode
python main.py --debug

# Docker
sudo docker logs open_coordinator

# Docker Compose
docker-compose logs -f coordinator
```

---

## Next Steps

1. **Explore the full API**: Check out the interactive docs at `/docs`
2. **Configure more providers**: Add API keys for other providers in `.env`
3. **Set up monitoring**: Use Prometheus and Grafana (see DEPLOYMENT_GUIDE.md)
4. **Deploy to production**: See DEPLOYMENT_GUIDE.md for production deployment
5. **Explore examples**: See EXAMPLES.md for practical use cases

---

## Command Reference

| Command | Description |
|---------|-------------|
| `python main.py` | Start the server |
| `python main.py --debug` | Start with debug logging |
| `python main.py --reload` | Start with auto-reload |
| `python main.py --port 9000` | Start on custom port |
| `uvicorn open_coordinator.api.main:app` | Start with uvicorn |
| `docker-compose up -d` | Start with Docker |
| `docker-compose down` | Stop Docker containers |

---

## Support

- **Documentation**: See DEPLOYMENT_GUIDE.md and API_DOCUMENTATION.md
- **Issues**: Report issues on GitHub
- **Contributing**: See CONTRIBUTING.md

---

**Congratulations!** You now have a fully functional OpenCode AI Coordinator running on your server! 🎉
