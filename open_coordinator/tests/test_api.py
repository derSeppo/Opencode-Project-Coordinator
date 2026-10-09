"""Tests for FastAPI endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from open_coordinator.api.main import app
from open_coordinator.models.task import (
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskType,
    ProviderType,
    TaskCreateResponse,
    CodeGenerationRequest,
    CodeValidationRequest,
    CodeFormattingRequest,
)
from open_coordinator.tasks.manager import TaskManager, get_task_manager
from open_coordinator.providers.factory import ProviderFactory, get_provider_factory


@pytest.fixture
def client():
    """Create a test client"""
    # Disable API key requirement for testing
    with patch.dict('os.environ', {'SECURITY_API_KEY_REQUIRED': 'false'}):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def authenticated_client():
    """Create a test client with API key"""
    with TestClient(app) as test_client:
        test_client.headers["X-API-Key"] = "test-key"
        yield test_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set test environment variables
    import os
    os.environ['SECURITY_API_KEY_REQUIRED'] = 'false'
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['SERVER_DEBUG'] = 'true'
    
    yield
    
    # Cleanup
    if 'SECURITY_API_KEY_REQUIRED' in os.environ:
        del os.environ['SECURITY_API_KEY_REQUIRED']
    if 'ENVIRONMENT' in os.environ:
        del os.environ['ENVIRONMENT']
    if 'SERVER_DEBUG' in os.environ:
        del os.environ['SERVER_DEBUG']


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    """Test ready check endpoint"""
    response = client.get("/ready")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_create_task_endpoint(client):
    """Test create task endpoint"""
    task_request = {
        "task_type": "code_generation",
        "prompt": "Create a Python function",
        "language": "python",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = client.post("/task", json=task_request)
    
    assert response.status_code == 201
    assert "task_id" in response.json()
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_endpoint(client):
    """Test get task endpoint"""
    # Create a task first
    task_request = {
        "task_type": "code_generation",
        "prompt": "Create a Python function",
        "language": "python"
    }
    
    create_response = client.post("/task", json=task_request)
    task_id = create_response.json()["task_id"]
    
    # Get the task
    response = client.get(f"/task/{task_id}")
    
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_get_nonexistent_task(client):
    """Test get nonexistent task"""
    response = client.get("/task/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks_endpoint(client):
    """Test list tasks endpoint"""
    # Create some tasks
    for i in range(3):
        client.post("/task", json={
            "task_type": "code_generation",
            "prompt": f"Task {i}",
            "language": "python"
        })
    
    # List tasks
    response = client.get("/tasks")
    
    assert response.status_code == 200
    assert "tasks" in response.json()
    assert len(response.json()["tasks"]) >= 3
    assert response.json()["total"] >= 3


@pytest.mark.asyncio
async def test_list_tasks_filtering(client):
    """Test list tasks with filtering"""
    # Create tasks
    client.post("/task", json={
        "task_type": "code_generation",
        "prompt": "Task 1",
        "language": "python"
    })
    
    # List with filter
    response = client.get("/tasks?status=pending")
    
    assert response.status_code == 200
    assert all(t["status"] == "pending" for t in response.json()["tasks"])


@pytest.mark.asyncio
async def test_cancel_task_endpoint(client):
    """Test cancel task endpoint"""
    # Create a task
    create_response = client.post("/task", json={
        "task_type": "code_generation",
        "prompt": "Task to cancel",
        "language": "python"
    })
    task_id = create_response.json()["task_id"]
    
    # Cancel the task
    response = client.post(f"/task/{task_id}/cancel")
    
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    
    # Check task status
    task_response = client.get(f"/task/{task_id}")
    assert task_response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_delete_task_endpoint(client):
    """Test delete task endpoint"""
    # Create a task
    create_response = client.post("/task", json={
        "task_type": "code_generation",
        "prompt": "Task to delete",
        "language": "python"
    })
    task_id = create_response.json()["task_id"]
    
    # Delete the task
    response = client.delete(f"/task/{task_id}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    
    # Check task is gone
    task_response = client.get(f"/task/{task_id}")
    assert task_response.status_code == 404


@pytest.mark.asyncio
async def test_code_generate_endpoint(client):
    """Test code generation endpoint"""
    request = {
        "prompt": "Create a Python function to add two numbers",
        "language": "python",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = client.post("/code/generate", json=request)
    
    assert response.status_code == 201
    assert "task_id" in response.json()
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_code_validate_endpoint(client):
    """Test code validation endpoint"""
    request = {
        "code": "def add(a, b):\n    return a + b",
        "language": "python",
        "check_syntax": True,
        "check_semantics": True
    }
    
    response = client.post("/code/validate", json=request)
    
    assert response.status_code == 201
    assert "task_id" in response.json()


@pytest.mark.asyncio
async def test_code_format_endpoint(client):
    """Test code formatting endpoint"""
    request = {
        "code": "def hello(name):\n    print(f\"Hello {name}\")",
        "language": "python",
        "style": "pep8",
        "indent_size": 4
    }
    
    response = client.post("/code/format", json=request)
    
    assert response.status_code == 201
    assert "task_id" in response.json()


@pytest.mark.asyncio
async def test_providers_endpoint(client):
    """Test providers endpoint"""
    response = client.get("/providers")
    
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    # Should have at least one provider
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_provider_endpoint(client):
    """Test specific provider endpoint"""
    response = client.get("/providers/openai")
    
    assert response.status_code == 200
    assert response.json()["name"] == "openai"
    assert "enabled" in response.json()
    assert "priority" in response.json()


@pytest.mark.asyncio
async def test_provider_not_found(client):
    """Test nonexistent provider"""
    response = client.get("/providers/nonexistent")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_provider_models_endpoint(client):
    """Test provider models endpoint"""
    response = client.get("/providers/openai/models")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Should have at least one model
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_all_models_endpoint(client):
    """Test all models endpoint"""
    response = client.get("/models")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_stats_endpoint(client):
    """Test stats endpoint"""
    # Create some tasks first
    for i in range(3):
        client.post("/task", json={
            "task_type": "code_generation",
            "prompt": f"Task {i}",
            "language": "python"
        })
    
    response = client.get("/stats")
    
    assert response.status_code == 200
    assert "total_tasks" in response.json()
    assert response.json()["total_tasks"] >= 3


@pytest.mark.asyncio
async def test_execute_endpoint(client):
    """Test execute endpoint"""
    request = {
        "task_type": "code_generation",
        "prompt": "Create a Python function",
        "language": "python",
        "wait": True,
        "timeout": 30
    }
    
    response = client.post("/execute", json=request)
    
    assert response.status_code == 200
    # Should return task_id and status
    assert "task_id" in response.json()


@pytest.mark.asyncio
async def test_templates_endpoint(client):
    """Test templates endpoint"""
    response = client.get("/code/templates")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_api_key_authentication():
    """Test API key authentication"""
    # Set API key required
    import os
    os.environ['SECURITY_API_KEY_REQUIRED'] = 'true'
    os.environ['SECURITY_API_KEYS'] = 'test-key,another-key'
    
    from fastapi.testclient import TestClient
    from open_coordinator.api.main import app
    
    with TestClient(app) as client:
        # Without API key
        response = client.get("/health")
        assert response.status_code == 401
        
        # With valid API key
        response = client.get("/health", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        
        # With invalid API key
        response = client.get("/health", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401
    
    # Cleanup
    del os.environ['SECURITY_API_KEY_REQUIRED']
    if 'SECURITY_API_KEYS' in os.environ:
        del os.environ['SECURITY_API_KEYS']


@pytest.mark.asyncio
async def test_invalid_request_data(client):
    """Test invalid request data"""
    # Missing required fields
    response = client.post("/task", json={"prompt": "test"})
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_invalid_language(client):
    """Test invalid language"""
    request = {
        "task_type": "code_generation",
        "prompt": "Create a function",
        "language": "invalid-language"
    }
    
    response = client.post("/task", json=request)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_invalid_task_type(client):
    """Test invalid task type"""
    request = {
        "task_type": "invalid_type",
        "prompt": "Create a function",
        "language": "python"
    }
    
    response = client.post("/task", json=request)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_pagination(client):
    """Test pagination in list tasks"""
    # Create multiple tasks
    for i in range(15):
        client.post("/task", json={
            "task_type": "code_generation",
            "prompt": f"Task {i}",
            "language": "python"
        })
    
    # Get first page
    response = client.get("/tasks?limit=10&offset=0")
    
    assert response.status_code == 200
    assert response.json()["page"] == 1
    assert response.json()["page_size"] == 10
    assert len(response.json()["tasks"]) == 10
    
    # Get second page
    response = client.get("/tasks?limit=10&offset=10")
    
    assert response.status_code == 200
    assert response.json()["page"] == 2
    assert len(response.json()["tasks"]) <= 10


@pytest.mark.asyncio
async def test_error_handling(client):
    """Test error handling"""
    # Try to get a task that doesn't exist
    response = client.get("/task/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
    assert "error" in response.json()


@pytest.mark.asyncio
async def test_cancel_nonexistent_task(client):
    """Test cancel nonexistent task"""
    response = client.post("/task/00000000-0000-0000-0000-000000000000/cancel")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_task(client):
    """Test delete nonexistent task"""
    response = client.delete("/task/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 404
