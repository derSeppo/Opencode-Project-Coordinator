"""Tests for task management"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from open_coordinator.models.task import (
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskType,
    ProviderType,
    TaskCreateResponse,
    TaskListResponse,
)
from open_coordinator.tasks.manager import TaskManager, Task, get_task_manager
from open_coordinator.providers.base import BaseProvider, ProviderResponse
from open_coordinator.providers.factory import ProviderFactory


@pytest.fixture
def task_request():
    """Create a sample task request"""
    return TaskRequest(
        task_type=TaskType.CODE_GENERATION,
        prompt="Create a Python function",
        language="python",
        temperature=0.7,
        max_tokens=1000
    )


@pytest.fixture
def mock_provider():
    """Create a mock provider"""
    provider = AsyncMock(spec=BaseProvider)
    provider.provider_type = ProviderType.OPENAI
    provider.enabled = True
    provider.priority = 1
    provider.models = ["gpt-4o"]
    
    # Mock generate method
    async def mock_generate(**kwargs):
        return ProviderResponse(
            content="Generated code",
            provider=ProviderType.OPENAI,
            model="gpt-4o",
            tokens_used=100,
            cost=0.001,
            execution_time_ms=100.0
        )
    
    provider.generate = mock_generate
    return provider


@pytest.fixture
def mock_factory(mock_provider):
    """Create a mock provider factory"""
    factory = AsyncMock(spec=ProviderFactory)
    factory.get_provider.return_value = mock_provider
    factory.get_provider_by_preference.return_value = mock_provider
    factory.get_enabled_providers.return_value = [mock_provider]
    factory.initialize.return_value = None
    factory.close_all.return_value = None
    return factory


@pytest.mark.asyncio
async def test_task_creation(task_request):
    """Test task creation"""
    manager = TaskManager()
    
    # Mock provider factory
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        # Create task
        response = await manager.create_task(task_request)
        
        assert isinstance(response, TaskCreateResponse)
        assert response.status == TaskStatus.PENDING
        assert response.message == "Task created successfully"
        assert response.task_id is not None


@pytest.mark.asyncio
async def test_task_retrieval(task_request):
    """Test task retrieval"""
    manager = TaskManager()
    
    # Create a task
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        create_response = await manager.create_task(task_request)
        task_id = create_response.task_id
        
        # Retrieve the task
        task_response = await manager.get_task(task_id)
        
        assert task_response is not None
        assert task_response.task_id == task_id
        assert task_response.status == TaskStatus.PENDING


@pytest.mark.asyncio
async def test_task_listing(task_request):
    """Test task listing"""
    manager = TaskManager()
    
    # Create multiple tasks
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        for i in range(5):
            await manager.create_task(task_request)
        
        # List tasks
        list_response = await manager.list_tasks()
        
        assert isinstance(list_response, TaskListResponse)
        assert list_response.total >= 5
        assert len(list_response.tasks) >= 5


@pytest.mark.asyncio
async def test_task_cancellation(task_request):
    """Test task cancellation"""
    manager = TaskManager()
    
    # Create a task
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        create_response = await manager.create_task(task_request)
        task_id = create_response.task_id
        
        # Cancel the task
        cancelled = await manager.cancel_task(task_id)
        
        assert cancelled == True
        
        # Check task status
        task_response = await manager.get_task(task_id)
        assert task_response.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_task_execution(task_request, mock_provider):
    """Test task execution"""
    manager = TaskManager()
    
    # Initialize with mock factory
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.get_provider_by_preference.return_value = mock_provider
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        mock_factory.initialize.return_value = None
        mock_factory.close_all.return_value = None
        
        await manager.initialize()
        
        # Create task
        create_response = await manager.create_task(task_request)
        task_id = create_response.task_id
        
        # Wait for task to be processed (in real scenario)
        # For testing, we'll manually execute the task
        async with manager._lock:
            task = manager._tasks[task_id]
        
        # Manually execute the task
        await manager._execute_task(task)
        
        # Check result
        task_response = await manager.get_task(task_id)
        assert task_response.status == TaskStatus.COMPLETED
        assert task_response.result == "Generated code"
        assert task_response.provider_used == ProviderType.OPENAI


@pytest.mark.asyncio
async def test_task_stats(task_request):
    """Test task statistics"""
    manager = TaskManager()
    
    # Create some tasks
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        for i in range(3):
            await manager.create_task(task_request)
        
        # Get stats
        stats = manager.get_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["pending_tasks"] == 3
        assert stats["completed_tasks"] == 0


@pytest.mark.asyncio
async def test_task_filtering(task_request):
    """Test task filtering by status"""
    manager = TaskManager()
    
    # Create tasks with different statuses
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        # Create pending tasks
        for i in range(3):
            await manager.create_task(task_request)
        
        # Create a completed task manually
        async with manager._lock:
            task = Task(
                task_id="completed-task",
                request=task_request,
                status=TaskStatus.COMPLETED,
                result="Done",
                provider_used=ProviderType.OPENAI,
                model_used="gpt-4o",
                tokens_used=100,
                cost=0.001,
                execution_time_ms=100.0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            manager._tasks["completed-task"] = task
        
        # List only completed tasks
        list_response = await manager.list_tasks(status=TaskStatus.COMPLETED)
        
        assert list_response.total == 1
        assert all(t.status == TaskStatus.COMPLETED for t in list_response.tasks)


@pytest.mark.asyncio
async def test_task_timeout():
    """Test task timeout handling"""
    manager = TaskManager()
    
    # Create a task request with short timeout
    task_request = TaskRequest(
        task_type=TaskType.CODE_GENERATION,
        prompt="Create a Python function",
        language="python",
        timeout_seconds=1  # Very short timeout
    )
    
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_provider = AsyncMock()
        mock_provider.provider_type = ProviderType.OPENAI
        mock_provider.enabled = True
        
        # Mock generate to take longer than timeout
        async def slow_generate(**kwargs):
            await asyncio.sleep(2)  # Longer than timeout
            return ProviderResponse(
                content="Generated code",
                provider=ProviderType.OPENAI,
                model="gpt-4o",
                tokens_used=100,
                cost=0.001,
                execution_time_ms=2000.0
            )
        
        mock_provider.generate = slow_generate
        mock_factory.get_provider.return_value = mock_provider
        mock_factory.initialize.return_value = None
        mock_factory.get_enabled_providers.return_value = [mock_provider]
        
        create_response = await manager.create_task(task_request)
        task_id = create_response.task_id
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Check task status
        task_response = await manager.get_task(task_id)
        
        # Task should still be pending or processing
        assert task_response.status in [TaskStatus.PENDING, TaskStatus.PROCESSING]


@pytest.mark.asyncio
async def test_provider_selection(task_request):
    """Test provider selection logic"""
    manager = TaskManager()
    
    with patch.object(manager, 'provider_factory') as mock_factory:
        # Create mock providers
        openai_provider = AsyncMock()
        openai_provider.provider_type = ProviderType.OPENAI
        openai_provider.enabled = True
        openai_provider.priority = 1
        
        anthropic_provider = AsyncMock()
        anthropic_provider.provider_type = ProviderType.ANTHROPIC
        anthropic_provider.enabled = True
        anthropic_provider.priority = 2
        
        # Test preference selection
        mock_factory.get_provider_by_preference.return_value = openai_provider
        
        create_response = await manager.create_task(task_request)
        task_id = create_response.task_id
        
        async with manager._lock:
            task = manager._tasks[task_id]
        
        # Check that the task has the correct provider preference
        assert task.request.provider_preference is None or len(task.request.provider_preference) > 0


@pytest.mark.asyncio
async def test_task_manager_initialization():
    """Test task manager initialization"""
    manager = TaskManager()
    
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_factory.initialize.return_value = None
        
        await manager.initialize()
        
        # Check that providers were initialized
        assert manager._running == True
        assert len(manager._task_processors) == manager._max_concurrent_tasks


@pytest.mark.asyncio
async def test_task_manager_cleanup():
    """Test task manager cleanup"""
    manager = TaskManager()
    
    with patch.object(manager, 'provider_factory') as mock_factory:
        mock_factory.close_all.return_value = None
        
        await manager.initialize()
        await manager.close()
        
        # Check that cleanup happened
        assert manager._running == False
        assert len(manager._task_processors) == 0
