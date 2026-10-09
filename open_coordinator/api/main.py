"""FastAPI application for OpenCode AI Coordinator"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from open_coordinator.config.settings import get_settings, Settings
from open_coordinator.models.task import (
    CodeFormattingRequest,
    CodeGenerationRequest,
    CodeValidationRequest,
    ProviderType,
    StatsResponse,
    TaskCreateResponse,
    TaskListResponse,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskType,
    TemplateRequest,
)
from open_coordinator.providers.factory import (
    get_provider_factory,
    initialize_providers,
    close_providers,
)
from open_coordinator.tasks.manager import (
    get_task_manager,
    initialize_task_manager,
    close_task_manager,
)

logger = logging.getLogger(__name__)


# Initialize settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize providers and task manager
    await initialize_providers()
    await initialize_task_manager()
    
    logger.info("OpenCode AI Coordinator started")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Server: {settings.server.host}:{settings.server.port}")
    
    yield
    
    # Cleanup
    await close_task_manager()
    await close_providers()
    
    logger.info("OpenCode AI Coordinator stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.cors_origins,
    allow_credentials=settings.security.cors_allow_credentials,
    allow_methods=settings.security.cors_allow_methods,
    allow_headers=settings.security.cors_allow_headers,
)


# Dependency for API key authentication
async def verify_api_key(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    request: Request = None
) -> bool:
    """Verify API key if required"""
    if not settings.security.api_key_required:
        return True
    
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide it in the X-API-Key header."
        )
    
    if api_key not in settings.security.api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


async def get_api_key(
    api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Optional[str]:
    """Get the API key from request"""
    return api_key


# Endpoint: Health check
@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


# Endpoint: Ready check
@app.get("/ready", tags=["health"])
async def ready_check() -> Dict[str, str]:
    """Ready check endpoint"""
    try:
        manager = get_task_manager()
        factory = get_provider_factory()
        
        enabled_providers = len(factory.get_enabled_providers())
        active_tasks = len(manager._tasks)
        
        return {
            "status": "ready",
            "providers": enabled_providers,
            "active_tasks": active_tasks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


# ============================================================================
# Task Endpoints
# ============================================================================

@app.post(
    "/task",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"]
)
async def create_task(
    request: TaskRequest,
    _: bool = Depends(verify_api_key)
) -> TaskCreateResponse:
    """Create a new AI task"""
    manager = get_task_manager()
    return await manager.create_task(request)


@app.get(
    "/task/{task_id}",
    response_model=TaskResponse,
    tags=["tasks"]
)
async def get_task(
    task_id: str,
    _: bool = Depends(verify_api_key)
) -> TaskResponse:
    """Get task by ID"""
    manager = get_task_manager()
    task = await manager.get_task(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task


@app.get(
    "/tasks",
    response_model=TaskListResponse,
    tags=["tasks"]
)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    _: bool = Depends(verify_api_key)
) -> TaskListResponse:
    """List all tasks with optional filtering"""
    manager = get_task_manager()
    return await manager.list_tasks(status=status, limit=limit, offset=offset)


@app.post(
    "/task/{task_id}/cancel",
    status_code=status.HTTP_200_OK,
    tags=["tasks"]
)
async def cancel_task(
    task_id: str,
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Cancel a task"""
    manager = get_task_manager()
    success = await manager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} cannot be cancelled (may already be completed)"
        )
    
    return {"status": "cancelled", "task_id": task_id}


@app.delete(
    "/task/{task_id}",
    status_code=status.HTTP_200_OK,
    tags=["tasks"]
)
async def delete_task(
    task_id: str,
    _: bool = Depends(verify_api_key)
) -> Dict[str, str]:
    """Delete a task from memory"""
    manager = get_task_manager()
    
    async with manager._lock:
        if task_id in manager._tasks:
            del manager._tasks[task_id]
            return {"status": "deleted", "task_id": task_id}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


# ============================================================================
# Code Generation Endpoints
# ============================================================================

@app.post(
    "/code/generate",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["code", "generation"]
)
async def generate_code(
    request: CodeGenerationRequest,
    _: bool = Depends(verify_api_key)
) -> TaskCreateResponse:
    """Generate code from a prompt"""
    # Convert to TaskRequest
    task_request = TaskRequest(
        task_type=TaskType.CODE_GENERATION,
        prompt=request.prompt,
        language=request.language,
        provider_preference=request.provider_preference,
        model_preference=request.model_preference,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        metadata={
            "framework": request.framework,
            "include_comments": request.include_comments,
            "include_tests": request.include_tests
        }
    )
    
    manager = get_task_manager()
    return await manager.create_task(task_request)


@app.post(
    "/code/generate-from-template",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["code", "templates"]
)
async def generate_from_template(
    request: TemplateRequest,
    _: bool = Depends(verify_api_key)
) -> TaskCreateResponse:
    """Generate code from a template"""
    # Load template
    template = self._load_template(request.template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template {request.template_name} not found"
        )
    
    # Replace variables
    code = template.template
    for key, value in request.variables.items():
        code = code.replace(f"{{{{{key}}}}}", value)
    
    # Create task
    task_request = TaskRequest(
        task_type=TaskType.CODE_GENERATION,
        prompt=f"Complete and enhance the following {request.language} code template:\n\n{code}",
        language=request.language,
        metadata={"template": request.template_name, "variables": request.variables}
    )
    
    manager = get_task_manager()
    return await manager.create_task(task_request)


# ============================================================================
# Code Validation Endpoints
# ============================================================================

@app.post(
    "/code/validate",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["code", "validation"]
)
async def validate_code(
    request: CodeValidationRequest,
    _: bool = Depends(verify_api_key)
) -> TaskCreateResponse:
    """Validate code for errors and issues"""
    task_request = TaskRequest(
        task_type=TaskType.CODE_VALIDATION,
        code=request.code,
        language=request.language,
        metadata={
            "check_syntax": request.check_syntax,
            "check_semantics": request.check_semantics,
            "check_style": request.check_style,
            "lint_config": request.lint_config
        }
    )
    
    manager = get_task_manager()
    return await manager.create_task(task_request)


# ============================================================================
# Code Formatting Endpoints
# ============================================================================

@app.post(
    "/code/format",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["code", "formatting"]
)
async def format_code(
    request: CodeFormattingRequest,
    _: bool = Depends(verify_api_key)
) -> TaskCreateResponse:
    """Format code according to style guidelines"""
    task_request = TaskRequest(
        task_type=TaskType.CODE_FORMATTING,
        code=request.code,
        language=request.language,
        metadata={
            "style": request.style,
            "indent_size": request.indent_size,
            "line_length": request.line_length
        }
    )
    
    manager = get_task_manager()
    return await manager.create_task(task_request)


# ============================================================================
# Provider Endpoints
# ============================================================================

@app.get(
    "/providers",
    tags=["providers"]
)
async def list_providers(
    _: bool = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """List all available providers"""
    factory = get_provider_factory()
    return factory.get_provider_info()


@app.get(
    "/providers/{provider_name}",
    tags=["providers"]
)
async def get_provider(
    provider_name: str,
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get information about a specific provider"""
    try:
        provider_type = ProviderType(provider_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_name} not found"
        )
    
    factory = get_provider_factory()
    provider = factory.get_provider(provider_type)
    
    return {
        "name": provider.name,
        "type": provider.provider_type.value,
        "enabled": provider.enabled,
        "priority": provider.priority,
        "base_url": provider.base_url,
        "models": provider.models,
        "rate_limit": provider.rate_limit,
        "timeout": provider.timeout
    }


@app.get(
    "/providers/{provider_name}/models",
    tags=["providers"]
)
async def list_provider_models(
    provider_name: str,
    _: bool = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """List models for a specific provider"""
    try:
        provider_type = ProviderType(provider_name)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider {provider_name} not found"
        )
    
    factory = get_provider_factory()
    provider = factory.get_provider(provider_type)
    
    return provider.list_models()


@app.get(
    "/models",
    tags=["providers"]
)
async def list_all_models(
    _: bool = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """List all available models from all providers"""
    factory = get_provider_factory()
    return factory.list_all_models()


# ============================================================================
# Statistics Endpoints
# ============================================================================

@app.get(
    "/stats",
    response_model=StatsResponse,
    tags=["stats"]
)
async def get_stats(
    _: bool = Depends(verify_api_key)
) -> StatsResponse:
    """Get statistics about task execution"""
    manager = get_task_manager()
    stats = manager.get_stats()
    
    return StatsResponse(
        total_tasks=stats["total_tasks"],
        completed_tasks=stats["completed_tasks"],
        failed_tasks=stats["failed_tasks"],
        total_tokens=stats["total_tokens"],
        total_cost=stats["total_cost"],
        avg_execution_time_ms=stats["avg_execution_time_ms"],
        provider_usage={},
        model_usage={},
        task_type_distribution={}
    )


# ============================================================================
# Template Endpoints
# ============================================================================

@app.get(
    "/code/templates",
    tags=["templates"]
)
async def list_templates(
    _: bool = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """List all available code templates"""
    templates = []
    
    # Try to load templates from directory
    template_dir = settings.templates.template_dir
    if template_dir.exists():
        for template_file in template_dir.glob("*.py") + template_dir.glob("*.js") + template_dir.glob("*.ts"):
            templates.append({
                "name": template_file.stem,
                "path": str(template_file)
            })
    
    return templates


# ============================================================================
# Direct Execution Endpoints (for simple use cases)
# ============================================================================

@app.post(
    "/execute",
    tags=["direct"]
)
async def execute_direct(
    request: TaskRequest,
    wait: bool = Query(True, description="Whether to wait for completion"),
    timeout: int = Query(300, description="Timeout in seconds"),
    _: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Execute a task directly and return the result (for simple use cases)"""
    import asyncio
    
    manager = get_task_manager()
    
    # Create task
    create_response = await manager.create_task(request)
    task_id = create_response.task_id
    
    if not wait:
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Task created, use /task/{task_id} to get results"
        }
    
    # Wait for completion
    start_time = asyncio.get_event_loop().time()
    
    while True:
        # Check task status
        task = await manager.get_task(task_id)
        
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            if task.status == TaskStatus.FAILED:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Task failed: {task.error}"
                )
            return {
                "task_id": task_id,
                "status": task.status.value,
                "result": task.result,
                "provider": task.provider_used.value if task.provider_used else None,
                "model": task.model_used,
                "tokens_used": task.tokens_used,
                "cost": task.cost,
                "execution_time_ms": task.execution_time_ms
            }
        
        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout:
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail=f"Task did not complete within {timeout} seconds"
            )
        
        # Wait a bit before checking again
        await asyncio.sleep(0.5)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None
        }
    )


# Helper function to load templates
async def _load_template(name: str) -> Optional[Dict[str, Any]]:
    """Load a template by name"""
    # This would be implemented to load from database or file system
    # For now, return None
    return None
