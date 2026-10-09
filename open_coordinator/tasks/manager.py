"""Task manager for handling AI tasks"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

from open_coordinator.config.settings import get_settings, Settings
from open_coordinator.models.task import (
    TaskCreateResponse,
    TaskListResponse,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskType,
    ProviderType,
)
from open_coordinator.providers.base import BaseProvider, ProviderError, ProviderResponse
from open_coordinator.providers.factory import get_provider_factory, ProviderFactory

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Internal task representation"""
    task_id: str
    request: TaskRequest
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    provider_used: Optional[ProviderType] = None
    model_used: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    retries: int = 0
    max_retries: int = 3
    
    def to_response(self) -> TaskResponse:
        """Convert to API response model"""
        return TaskResponse(
            task_id=self.task_id,
            status=self.status,
            result=self.result,
            provider_used=self.provider_used,
            model_used=self.model_used,
            tokens_used=self.tokens_used,
            cost=self.cost,
            execution_time_ms=self.execution_time_ms,
            error=self.error,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class TaskManager:
    """Manages AI tasks with load balancing and retry logic"""
    
    def __init__(
        self,
        provider_factory: Optional[ProviderFactory] = None,
        settings: Optional[Settings] = None
    ):
        self.provider_factory = provider_factory or get_provider_factory()
        self.settings = settings or get_settings()
        self._tasks: Dict[str, Task] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._active_tasks: int = 0
        self._max_concurrent_tasks: int = self.settings.server.workers * 2
        self._running: bool = False
        self._lock = asyncio.Lock()
        self._task_processors: List[asyncio.Task] = []
    
    async def initialize(self) -> None:
        """Initialize the task manager"""
        logger.info("Initializing TaskManager...")
        await self.provider_factory.initialize()
        self._running = True
        
        # Start task processors
        for i in range(self._max_concurrent_tasks):
            processor = asyncio.create_task(
                self._task_processor(i),
                name=f"TaskProcessor-{i}"
            )
            self._task_processors.append(processor)
        
        logger.info(f"TaskManager initialized with {self._max_concurrent_tasks} workers")
    
    async def close(self) -> None:
        """Close the task manager"""
        logger.info("Closing TaskManager...")
        self._running = False
        
        # Cancel all task processors
        for processor in self._task_processors:
            processor.cancel()
        
        # Wait for processors to finish
        await asyncio.gather(*self._task_processors, return_exceptions=True)
        
        # Close providers
        await self.provider_factory.close_all()
        
        logger.info("TaskManager closed")
    
    async def create_task(self, request: TaskRequest) -> TaskCreateResponse:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            request=request,
            max_retries=self.settings.code.default_timeout // 10  # 10s between retries
        )
        
        async with self._lock:
            self._tasks[task_id] = task
        
        # Add to queue
        await self._task_queue.put(task_id)
        
        logger.info(f"Created task {task_id} of type {request.task_type.value}")
        
        return TaskCreateResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Task created successfully",
            created_at=task.created_at
        )
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get task by ID"""
        async with self._lock:
            task = self._tasks.get(task_id)
        
        if task:
            return task.to_response()
        return None
    
    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> TaskListResponse:
        """List tasks with optional filtering"""
        async with self._lock:
            tasks = list(self._tasks.values())
        
        # Filter by status
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Paginate
        total = len(tasks)
        page_tasks = tasks[offset:offset + limit]
        
        return TaskListResponse(
            tasks=[t.to_response() for t in page_tasks],
            total=total,
            page=offset // limit + 1,
            page_size=limit
        )
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        async with self._lock:
            task = self._tasks.get(task_id)
        
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.utcnow()
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    async def _task_processor(self, worker_id: int) -> None:
        """Background task processor"""
        logger.debug(f"TaskProcessor {worker_id} started")
        
        while self._running:
            try:
                # Get next task from queue
                task_id = await self._task_queue.get()
                
                async with self._lock:
                    task = self._tasks.get(task_id)
                
                if task is None:
                    continue
                
                # Skip if already completed or cancelled
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    continue
                
                # Mark as processing
                task.status = TaskStatus.PROCESSING
                task.updated_at = datetime.utcnow()
                self._active_tasks += 1
                
                logger.debug(f"Processing task {task_id} on worker {worker_id}")
                
                try:
                    await self._execute_task(task)
                except Exception as e:
                    logger.error(f"Error executing task {task_id}: {e}")
                    async with self._lock:
                        task.status = TaskStatus.FAILED
                        task.error = str(e)
                        task.updated_at = datetime.utcnow()
                finally:
                    self._active_tasks -= 1
                    self._task_queue.task_done()
                
            except asyncio.CancelledError:
                logger.debug(f"TaskProcessor {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in TaskProcessor {worker_id}: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on error
        
        logger.debug(f"TaskProcessor {worker_id} stopped")
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task"""
        start_time = time.time()
        
        try:
            # Get the best provider for this task
            provider = self._get_provider_for_task(task)
            if provider is None:
                raise ProviderError("No available providers", ProviderType.OPENAI)
            
            task.provider_used = provider.provider_type
            
            # Execute based on task type
            if task.request.task_type == TaskType.CODE_GENERATION:
                result = await self._execute_code_generation(task, provider)
            elif task.request.task_type == TaskType.CODE_VALIDATION:
                result = await self._execute_code_validation(task, provider)
            elif task.request.task_type == TaskType.CODE_FORMATTING:
                result = await self._execute_code_formatting(task, provider)
            elif task.request.task_type == TaskType.CODE_REFACTORING:
                result = await self._execute_code_refactoring(task, provider)
            elif task.request.task_type == TaskType.CODE_DOCUMENTATION:
                result = await self._execute_code_documentation(task, provider)
            elif task.request.task_type == TaskType.CODE_OPTIMIZATION:
                result = await self._execute_code_optimization(task, provider)
            elif task.request.task_type == TaskType.UNIT_TEST_GENERATION:
                result = await self._execute_unit_test_generation(task, provider)
            elif task.request.task_type == TaskType.DEBUGGING:
                result = await self._execute_debugging(task, provider)
            elif task.request.task_type == TaskType.EXPLANATION:
                result = await self._execute_explanation(task, provider)
            else:
                # Generic task execution
                result = await self._execute_generic_task(task, provider)
            
            # Update task with results
            task.result = result.content
            task.model_used = result.model
            task.tokens_used = result.tokens_used
            task.cost = result.cost
            task.status = TaskStatus.COMPLETED
            task.error = None
            
        except ProviderError as e:
            logger.error(f"Provider error for task {task.task_id}: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
            
            # Retry if possible
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Retrying task {task.task_id} (attempt {task.retries})")
                await asyncio.sleep(2 ** task.retries)  # Exponential backoff
                await self._task_queue.put(task.task_id)
        except Exception as e:
            logger.error(f"Unexpected error for task {task.task_id}: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
        finally:
            task.execution_time_ms = (time.time() - start_time) * 1000
            task.updated_at = datetime.utcnow()
            logger.info(f"Completed task {task.task_id} in {task.execution_time_ms:.1f}ms")
    
    def _get_provider_for_task(self, task: Task) -> Optional[BaseProvider]:
        """Get the best provider for a task"""
        # Use provider preference if specified
        if task.request.provider_preference:
            provider = self.provider_factory.get_provider_by_preference(
                preferred_providers=task.request.provider_preference
            )
            if provider:
                return provider
        
        # Otherwise, get any enabled provider
        enabled_providers = self.provider_factory.get_enabled_providers()
        if enabled_providers:
            # Sort by priority
            enabled_providers.sort(key=lambda p: p.priority)
            return enabled_providers[0]
        
        return None
    
    async def _execute_code_generation(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code generation task"""
        model = task.request.model_preference or provider.models[0]
        
        # Build system prompt for code generation
        system_prompt = self._get_code_generation_system_prompt(task.request)
        
        return await provider.generate(
            prompt=task.request.prompt,
            model=model,
            temperature=task.request.temperature,
            max_tokens=task.request.max_tokens,
            system_prompt=system_prompt,
            language=task.request.language
        )
    
    async def _execute_code_validation(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code validation task"""
        if not task.request.code:
            raise ValueError("No code provided for validation")
        
        return await provider.validate_code(
            code=task.request.code,
            language=task.request.language
        )
    
    async def _execute_code_formatting(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code formatting task"""
        if not task.request.code:
            raise ValueError("No code provided for formatting")
        
        return await provider.format_code(
            code=task.request.code,
            language=task.request.language
        )
    
    async def _execute_code_refactoring(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code refactoring task"""
        if not task.request.code:
            raise ValueError("No code provided for refactoring")
        
        refactor_prompt = f"""Refactor the following {task.request.language} code to improve:
1. Readability
2. Performance
3. Maintainability
4. Follow best practices

Original code:
```{task.request.language}
{task.request.code}
```

Provide the refactored code with explanations of the improvements."""
        
        return await provider.generate(
            prompt=refactor_prompt,
            temperature=0.3,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_code_documentation(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code documentation task"""
        if not task.request.code:
            raise ValueError("No code provided for documentation")
        
        doc_prompt = f"""Generate comprehensive documentation for the following {task.request.language} code:

1. Overall description of what the code does
2. Function/class documentation
3. Parameter descriptions
4. Return value descriptions
5. Usage examples
6. Edge cases and error handling

Code:
```{task.request.language}
{task.request.code}
```

Provide the documentation in Markdown format."""
        
        return await provider.generate(
            prompt=doc_prompt,
            temperature=0.2,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_code_optimization(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute code optimization task"""
        if not task.request.code:
            raise ValueError("No code provided for optimization")
        
        optimize_prompt = f"""Optimize the following {task.request.language} code for:
1. Performance (speed and memory usage)
2. Readability
3. Maintainability

Original code:
```{task.request.language}
{task.request.code}
```

Provide the optimized code with explanations of the optimizations."""
        
        return await provider.generate(
            prompt=optimize_prompt,
            temperature=0.2,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_unit_test_generation(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute unit test generation task"""
        if not task.request.code:
            raise ValueError("No code provided for test generation")
        
        test_prompt = f"""Generate comprehensive unit tests for the following {task.request.language} code:

1. Test normal functionality
2. Test edge cases
3. Test error handling
4. Test invalid inputs

Code:
```{task.request.language}
{task.request.code}
```

Provide tests in the same language as the code, using appropriate testing frameworks."""
        
        return await provider.generate(
            prompt=test_prompt,
            temperature=0.5,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_debugging(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute debugging task"""
        if not task.request.code:
            raise ValueError("No code provided for debugging")
        
        debug_prompt = f"""Debug the following {task.request.language} code:

1. Identify potential bugs
2. Explain what's wrong
3. Provide fixes
4. Suggest improvements

Code:
```{task.request.language}
{task.request.code}
```

Error/Problem description: {task.request.prompt}

Provide a detailed analysis and fixes."""
        
        return await provider.generate(
            prompt=debug_prompt,
            temperature=0.3,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_explanation(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute explanation task"""
        if not task.request.code:
            explanation_prompt = f"Explain the following concept: {task.request.prompt}"
        else:
            explanation_prompt = f"""Explain the following {task.request.language} code:

1. What it does
2. How it works
3. Key concepts used
4. Potential improvements

Code:
```{task.request.language}
{task.request.code}
```

Provide a clear, educational explanation."""
        
        return await provider.generate(
            prompt=explanation_prompt,
            temperature=0.3,
            max_tokens=task.request.max_tokens
        )
    
    async def _execute_generic_task(
        self,
        task: Task,
        provider: BaseProvider
    ) -> ProviderResponse:
        """Execute a generic/custom task"""
        return await provider.generate(
            prompt=task.request.prompt,
            temperature=task.request.temperature,
            max_tokens=task.request.max_tokens
        )
    
    def _get_code_generation_system_prompt(self, request: TaskRequest) -> str:
        """Get system prompt for code generation"""
        return f"""You are an expert {request.language} developer. 
Generate clean, well-documented, and production-ready code.
Follow best practices and include appropriate error handling.
Respond with code only, no explanations unless explicitly requested."""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tasks"""
        async with self._lock:
            tasks = list(self._tasks.values())
        
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in tasks if t.status == TaskStatus.FAILED])
        pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
        processing = len([t for t in tasks if t.status == TaskStatus.PROCESSING])
        
        total_tokens = sum(t.tokens_used for t in tasks)
        total_cost = sum(t.cost for t in tasks)
        avg_execution_time = sum(t.execution_time_ms for t in tasks) / total if total > 0 else 0
        
        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "pending_tasks": pending,
            "processing_tasks": processing,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "avg_execution_time_ms": avg_execution_time,
            "active_workers": self._active_tasks,
            "max_workers": self._max_concurrent_tasks
        }


# Global task manager instance
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Get the global task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


async def initialize_task_manager() -> TaskManager:
    """Initialize the global task manager"""
    manager = get_task_manager()
    await manager.initialize()
    return manager


async def close_task_manager() -> None:
    """Close the global task manager"""
    global _task_manager
    if _task_manager is not None:
        await _task_manager.close()
        _task_manager = None
