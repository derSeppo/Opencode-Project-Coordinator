# OpenCode AI Coordinator - API Documentation

## Base URL

```
http://localhost:8000
```

Or your custom domain:
```
https://ai.yourdomain.com
```

---

## Supported AI Providers

The API supports **12 AI providers** for code generation, validation, and formatting tasks:

### Free Cloud-Based Providers
| Provider | Endpoint | Free Tier | Models | Status |
|----------|----------|-----------|--------|--------|
| **HuggingFace** | `/providers/huggingface` | 100K+ free models | Mistral-7B, Llama-2, etc. | ✅ Active |
| **Together AI** | `/providers/together` | $25/month credit | Llama-2, Mistral, etc. | ✅ Active |
| **DeepInfra** | `/providers/deepinfra` | Generous free tier | CodeLlama, etc. | ✅ Active |
| **Perplexity AI** | `/providers/perplexity` | Free access | Llama 3.1, etc. | ✅ Active |
| **Cerebras** | `/providers/cerebras` | Free inference | Llama, Mistral, etc. | ✅ Active |

### Paid Providers
| Provider | Endpoint | Pricing | Models | Status |
|----------|----------|---------|--------|--------|
| **OpenAI** | `/providers/openai` | Pay-per-use | GPT-4, GPT-3.5 | ✅ Active |
| **Anthropic** | `/providers/anthropic` | Pay-per-use | Claude 3 | ✅ Active |
| **Mistral AI** | `/providers/mistral` | Pay-per-use | Mistral, Mixtral | ✅ Active |
| **Google AI** | `/providers/google` | Pay-per-use | Gemini | ✅ Active |
| **Cohere** | `/providers/cohere` | Pay-per-use | Command | ✅ Active |
| **Groq** | `/providers/groq` | Pay-per-use | Llama, Mixtral, Gemma | ✅ Active |

---

## Authentication

All endpoints require an API key to be included in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

To disable API key authentication, set in `.env`:
```bash
SECURITY_API_KEY_REQUIRED=false
```

---

## Common Headers

| Header | Type | Description |
|--------|------|-------------|
| `X-API-Key` | string | Required API key |
| `Content-Type` | string | `application/json` for POST requests |
| `Accept` | string | `application/json` for responses |

---

## Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 408 | Request Timeout | Task took too long |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | Provider unavailable |
| 503 | Service Unavailable | Service not ready |

---

## Rate Limiting

Default rate limits:
- 1000 requests per minute
- 10000 requests per hour
- Burst size: 100 requests

To customize, set in `.env`:
```bash
RATE_LIMIT_REQUESTS_PER_MINUTE=2000
RATE_LIMIT_REQUESTS_PER_HOUR=20000
RATE_LIMIT_BURST_SIZE=200
```

---

## Endpoints

---

## Health & Status

### Health Check

**GET** `/health`

Check if the server is running.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Response Schema:**
```json
{
  "status": "string",
  "version": "string"
}
```

---

### Ready Check

**GET** `/ready`

Check if the server and providers are ready.

**Request:**
```bash
curl http://localhost:8000/ready
```

**Response:**
```json
{
  "status": "ready",
  "providers": 3,
  "active_tasks": 0
}
```

**Response Schema:**
```json
{
  "status": "string",
  "providers": "integer",
  "active_tasks": "integer"
}
```

---

## Tasks

### Create Task

**POST** `/task`

Create a new AI task for execution.

**Request:**
```bash
curl -X POST http://localhost:8000/task \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_generation",
    "prompt": "Create a Python function to calculate Fibonacci",
    "language": "python",
    "provider_preference": ["huggingface", "together", "deepinfra"],
    "model_preference": "mistralai/Mistral-7B-Instruct-v0.2",
    "temperature": 0.7,
    "max_tokens": 2000,
    "priority": "medium",
    "timeout_seconds": 300,
    "metadata": {"custom_field": "value"}
  }'
```

**Request Body:**
```json
{
  "task_type": "code_generation",
  "prompt": "string",
  "code": "string (optional)",
  "language": "python",
  "provider_preference": ["huggingface", "together", "deepinfra", "perplexity", "cerebras"],
  "model_preference": "mistralai/Mistral-7B-Instruct-v0.2",
  "temperature": 0.7,
  "max_tokens": 4096,
  "priority": "low|medium|high|critical",
  "timeout_seconds": 300,
  "metadata": {}
}
```

**Request Schema:**
- `task_type` (required): Task type enum
  - `code_generation`, `code_validation`, `code_formatting`, `code_refactoring`
  - `code_documentation`, `code_optimization`, `unit_test_generation`
  - `debugging`, `explanation`, `custom`
- `prompt` (required): The main prompt/instruction
- `code` (optional): Existing code for validation/formatting tasks
- `language` (default: "python"): Programming language
- `provider_preference` (optional): List of preferred providers
- `model_preference` (optional): Preferred model
- `temperature` (default: 0.7): Creativity (0.0-2.0)
- `max_tokens` (default: 4096): Maximum tokens
- `priority` (default: "medium"): Task priority
- `timeout_seconds` (default: 300): Timeout
- `metadata` (optional): Additional metadata

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task created successfully",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Response Schema:**
```json
{
  "task_id": "string (uuid)",
  "status": "pending|processing|completed|failed|cancelled",
  "message": "string",
  "created_at": "string (datetime)"
}
```

---

### Get Task

**GET** `/task/{task_id}`

Get the status and result of a task.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/task/550e8400-e29b-41d4-a716-446655440000
```

**Path Parameters:**
- `task_id` (required): Task UUID

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "provider_used": "openai",
  "model_used": "gpt-4o",
  "tokens_used": 150,
  "cost": 0.0015,
  "execution_time_ms": 250.5,
  "error": null,
  "metadata": {},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:01Z"
}
```

**Response Schema:**
```json
{
  "task_id": "string (uuid)",
  "status": "pending|processing|completed|failed|cancelled",
  "result": "string|null",
  "provider_used": "openai|anthropic|mistral|google|cohere|groq|local|null",
  "model_used": "string|null",
  "tokens_used": "integer",
  "cost": "number",
  "execution_time_ms": "number",
  "error": "string|null",
  "metadata": "object",
  "created_at": "string (datetime)",
  "updated_at": "string (datetime)"
}
```

---

### List Tasks

**GET** `/tasks`

List all tasks with optional filtering.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" "http://localhost:8000/tasks?status=completed&limit=50"
```

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `processing`, `completed`, `failed`, `cancelled`)
- `limit` (default: 100): Maximum number of tasks to return
- `offset` (default: 0): Number of tasks to skip

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "...",
      "status": "completed",
      "result": "...",
      "provider_used": "openai",
      "model_used": "gpt-4o",
      "tokens_used": 150,
      "cost": 0.0015,
      "execution_time_ms": 250.5,
      "error": null,
      "metadata": {},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:01Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

**Response Schema:**
```json
{
  "tasks": ["array of TaskResponse"],
  "total": "integer",
  "page": "integer",
  "page_size": "integer"
}
```

---

### Cancel Task

**POST** `/task/{task_id}/cancel`

Cancel a pending task.

**Request:**
```bash
curl -X POST -H "X-API-Key: your-api-key" http://localhost:8000/task/550e8400-e29b-41d4-a716-446655440000/cancel
```

**Path Parameters:**
- `task_id` (required): Task UUID

**Response:**
```json
{
  "status": "cancelled",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response Schema:**
```json
{
  "status": "string",
  "task_id": "string (uuid)"
}
```

---

### Delete Task

**DELETE** `/task/{task_id}`

Delete a task from memory.

**Request:**
```bash
curl -X DELETE -H "X-API-Key: your-api-key" http://localhost:8000/task/550e8400-e29b-41d4-a716-446655440000
```

**Path Parameters:**
- `task_id` (required): Task UUID

**Response:**
```json
{
  "status": "deleted",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Code Generation

### Generate Code

**POST** `/code/generate`

Generate code from a prompt.

**Request:**
```bash
curl -X POST http://localhost:8000/code/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a REST API endpoint for user CRUD operations in FastAPI",
    "language": "python",
    "framework": "fastapi",
    "include_comments": true,
    "include_tests": true,
    "provider_preference": ["huggingface", "together"],
    "model_preference": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "temperature": 0.8,
    "max_tokens": 4000
  }'
```

**Request Body:**
```json
{
  "prompt": "string",
  "language": "python",
  "framework": "string (optional)",
  "include_comments": true,
  "include_tests": false,
  "provider_preference": ["huggingface", "together", "deepinfra"],
  "model_preference": "mistralai/Mixtral-8x7B-Instruct-v0.1",
  "temperature": 0.8,
  "max_tokens": 4000
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task created successfully",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### Generate from Template

**POST** `/code/generate-from-template`

Generate code using a predefined template.

**Request:**
```bash
curl -X POST http://localhost:8000/code/generate-from-template \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "fastapi_endpoint",
    "variables": {
      "request_model": "UserCreate",
      "response_model": "User",
      "endpoint": "users",
      "function_name": "create_user",
      "description": "Create a new user"
    },
    "language": "python"
  }'
```

**Request Body:**
```json
{
  "template_name": "string",
  "variables": {"key": "value"},
  "language": "python"
}
```

**Response:** Same as `/code/generate`

---

## Code Validation

### Validate Code

**POST** `/code/validate`

Validate code for syntax, semantics, and style issues.

**Request:**
```bash
curl -X POST http://localhost:8000/code/validate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
    "language": "python",
    "check_syntax": true,
    "check_semantics": true,
    "check_style": true,
    "lint_config": {}
  }'
```

**Request Body:**
```json
{
  "code": "string",
  "language": "python",
  "check_syntax": true,
  "check_semantics": true,
  "check_style": true,
  "lint_config": "object (optional)"
}
```

**Response:** Same as `/task` (returns task_id)

---

## Code Formatting

### Format Code

**POST** `/code/format`

Format code according to style guidelines.

**Request:**
```bash
curl -X POST http://localhost:8000/code/format \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello(name):\n    print(f\"Hello {name}\")",
    "language": "python",
    "style": "pep8",
    "indent_size": 4,
    "line_length": 88
  }'
```

**Request Body:**
```json
{
  "code": "string",
  "language": "python",
  "style": "pep8|black|prettier",
  "indent_size": 4,
  "line_length": 88
}
```

**Response:** Same as `/task` (returns task_id)

---

## Providers

### List Providers

**GET** `/providers`

List all configured AI providers.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/providers
```

**Response:**
```json
{
  "openai": {
    "enabled": true,
    "priority": 1,
    "base_url": "https://api.openai.com/v1",
    "models": ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
    "rate_limit": 100,
    "timeout": 120
  },
  "anthropic": {
    "enabled": true,
    "priority": 2,
    "base_url": "https://api.anthropic.com/v1",
    "models": ["claude-3-5-sonnet", "claude-3-sonnet", "claude-3-haiku"],
    "rate_limit": 100,
    "timeout": 120
  },
  "mistral": {
    "enabled": true,
    "priority": 3,
    "base_url": "https://api.mistral.ai/v1",
    "models": ["mistral-large", "mistral-small", "mixtral-8x7b"],
    "rate_limit": 100,
    "timeout": 120
  }
}
```

---

### Get Provider

**GET** `/providers/{provider_name}`

Get information about a specific provider.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/providers/openai
```

**Path Parameters:**
- `provider_name` (required): Provider name (`openai`, `anthropic`, `mistral`, `google`, `cohere`, `groq`, `local`)

**Response:**
```json
{
  "name": "openai",
  "type": "openai",
  "enabled": true,
  "priority": 1,
  "base_url": "https://api.openai.com/v1",
  "models": ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
  "rate_limit": 100,
  "timeout": 120
}
```

---

### List Provider Models

**GET** `/providers/{provider_name}/models`

List all models for a specific provider.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/providers/openai/models
```

**Path Parameters:**
- `provider_name` (required): Provider name

**Response:**
```json
[
  {
    "id": "gpt-4o",
    "provider": "openai",
    "max_tokens": 128000,
    "pricing": {
      "input": 5.0,
      "output": 15.0,
      "unit": "per_1m_tokens"
    },
    "available": true
  },
  {
    "id": "gpt-4o-mini",
    "provider": "openai",
    "max_tokens": 128000,
    "pricing": {
      "input": 1.5,
      "output": 6.0,
      "unit": "per_1m_tokens"
    },
    "available": true
  }
]
```

---

### List All Models

**GET** `/models`

List all available models from all providers.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/models
```

**Response:** Same as `/providers/{provider_name}/models` but includes all providers

---

## Statistics

### Get Statistics

**GET** `/stats`

Get statistics about task execution.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/stats
```

**Response:**
```json
{
  "total_tasks": 1000,
  "completed_tasks": 950,
  "failed_tasks": 50,
  "total_tokens": 1500000,
  "total_cost": 15.75,
  "avg_execution_time_ms": 1250.5,
  "provider_usage": {
    "openai": 600,
    "anthropic": 300,
    "mistral": 100
  },
  "model_usage": {
    "gpt-4o": 400,
    "claude-3-sonnet": 300,
    "mistral-large": 100
  },
  "task_type_distribution": {
    "code_generation": 700,
    "code_validation": 200,
    "code_formatting": 100
  }
}
```

**Response Schema:**
```json
{
  "total_tasks": "integer",
  "completed_tasks": "integer",
  "failed_tasks": "integer",
  "total_tokens": "integer",
  "total_cost": "number",
  "avg_execution_time_ms": "number",
  "provider_usage": "object",
  "model_usage": "object",
  "task_type_distribution": "object"
}
```

---

## Templates

### List Templates

**GET** `/code/templates`

List all available code templates.

**Request:**
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/code/templates
```

**Response:**
```json
[
  {
    "name": "fastapi_endpoint",
    "path": "/path/to/templates/fastapi_endpoint.template"
  },
  {
    "name": "python_class",
    "path": "/path/to/templates/python_class.template"
  }
]
```

---

## Direct Execution

### Execute Task (Synchronous)

**POST** `/execute`

Execute a task and wait for the result synchronously.

**Request:**
```bash
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

**Query Parameters:**
- `wait` (default: true): Whether to wait for completion
- `timeout` (default: 300): Timeout in seconds

**Request Body:** Same as `/task`

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": "def reverse_string(s):\n    return s[::-1]",
  "provider": "openai",
  "model": "gpt-4o",
  "tokens_used": 50,
  "cost": 0.0005,
  "execution_time_ms": 150.2
}
```

---

## Code Examples

### Python Examples

#### Generate Python Function

```python
import requests
import json

url = "http://localhost:8000/code/generate"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
data = {
    "prompt": "Create a Python function to calculate factorial",
    "language": "python",
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(url, headers=headers, json=data)
task = response.json()

# Get results
task_id = task["task_id"]
result_url = f"http://localhost:8000/task/{task_id}"
result = requests.get(result_url, headers=headers).json()

print(result["result"])
```

#### Validate Python Code

```python
import requests

url = "http://localhost:8000/code/validate"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
data = {
    "code": "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
    "language": "python"
}

response = requests.post(url, headers=headers, json=data)
task = response.json()

# Wait for result (in production, use async approach)
import time
time.sleep(2)

result = requests.get(
    f"http://localhost:8000/task/{task['task_id']}",
    headers=headers
).json()

print(result["result"])
```

#### Use Direct Execution

```python
import requests

url = "http://localhost:8000/execute?wait=true&timeout=30"
headers = {
    "X-API-Key": "your-api-key",
    "Content-Type": "application/json"
}
data = {
    "task_type": "code_generation",
    "prompt": "Write a Python decorator for timing functions",
    "language": "python"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(result["result"])
```

---

### JavaScript Examples

#### Generate Code (Node.js)

```javascript
const axios = require('axios');

const url = 'http://localhost:8000/code/generate';
const headers = {
    'X-API-Key': 'your-api-key',
    'Content-Type': 'application/json'
};
const data = {
    prompt: 'Create a Node.js Express endpoint for user authentication',
    language: 'javascript',
    framework: 'express',
    temperature: 0.8,
    max_tokens: 2000
};

axios.post(url, data, { headers })
    .then(response => {
        const taskId = response.data.task_id;
        return axios.get(`http://localhost:8000/task/${taskId}`, { headers });
    })
    .then(response => {
        console.log(response.data.result);
    })
    .catch(error => {
        console.error('Error:', error.response?.data || error.message);
    });
```

#### Validate Code (Browser)

```javascript
fetch('http://localhost:8000/code/validate', {
    method: 'POST',
    headers: {
        'X-API-Key': 'your-api-key',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        code: 'function fib(n) {\n  if (n <= 1) return n;\n  return fib(n-1) + fib(n-2);\n}',
        language: 'javascript'
    })
})
.then(response => response.json())
.then(task => {
    // Poll for result
    const checkResult = () => {
        fetch(`http://localhost:8000/task/${task.task_id}`, {
            headers: { 'X-API-Key': 'your-api-key' }
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'completed') {
                console.log(result.result);
            } else if (result.status === 'failed') {
                console.error('Error:', result.error);
            } else {
                setTimeout(checkResult, 1000);
            }
        });
    };
    checkResult();
});
```

---

## Webhook Integration

### Configuration

Configure webhooks in your task metadata:

```json
{
  "task_type": "code_generation",
  "prompt": "...",
  "metadata": {
    "webhook_url": "https://your-server.com/webhook",
    "webhook_method": "POST",
    "webhook_headers": {"Authorization": "Bearer token"}
  }
}
```

### Webhook Payload

```json
{
  "event": "task.completed",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": "...",
    "provider_used": "openai",
    "model_used": "gpt-4o",
    "tokens_used": 150,
    "cost": 0.0015,
    "execution_time_ms": 250.5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:01Z"
  }
}
```

---

## SDK Examples

### Python SDK

```python
from open_coordinator.client import OpenCodeClient

# Initialize client
client = OpenCodeClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Generate code
result = client.generate_code(
    prompt="Create a Python class for a bank account",
    language="python",
    temperature=0.7,
    max_tokens=2000
)

print(result)

# Validate code
validation = client.validate_code(
    code="def hello(): print('Hello')",
    language="python"
)

print(validation)

# Get statistics
stats = client.get_stats()
print(f"Total tasks: {stats.total_tasks}")
```

### JavaScript SDK

```javascript
const { OpenCodeClient } = require('@opencode/client');

// Initialize client
const client = new OpenCodeClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

// Generate code
const result = await client.generateCode({
    prompt: 'Create a TypeScript interface for a user',
    language: 'typescript',
    temperature: 0.7,
    maxTokens: 2000
});

console.log(result);

// Validate code
const validation = await client.validateCode({
    code: 'function add(a: number, b: number): number { return a + b; }',
    language: 'typescript'
});

console.log(validation);
```

---

## OpenAPI Specification

The full OpenAPI specification is available at:
```
GET /openapi.json
```

This can be used to generate client libraries in various languages using tools like:
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger Codegen](https://swagger.io/tools/swagger-codegen/)

---

## Changelog

### Version 1.0.0
- Initial release
- All endpoints documented
- Examples for Python, JavaScript, cURL

---

## Support

- **Documentation**: See QUICK_START.md, DEPLOYMENT_GUIDE.md, EXAMPLES.md
- **Issues**: Report on GitHub
- **Community**: Join the discussion

---

**Happy Coding!** 🎉
