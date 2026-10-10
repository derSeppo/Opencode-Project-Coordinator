"""Task models for the OpenCode AI Coordinator"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Type of task"""
    CODE_GENERATION = "code_generation"
    CODE_VALIDATION = "code_validation"
    CODE_FORMATTING = "code_formatting"
    CODE_REFACTORING = "code_refactoring"
    CODE_DOCUMENTATION = "code_documentation"
    CODE_OPTIMIZATION = "code_optimization"
    UNIT_TEST_GENERATION = "unit_test_generation"
    DEBUGGING = "debugging"
    EXPLANATION = "explanation"
    CUSTOM = "custom"


class ProviderType(str, Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    GOOGLE = "google"
    COHERE = "cohere"
    GROQ = "groq"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"
    TOGETHER = "together"
    DEEPINFRA = "deepinfra"
    PERPLEXITY = "perplexity"
    CEREBRAS = "cerebras"


class TaskPriority(str, Enum):
    """Priority levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskRequest(BaseModel):
    """Request model for creating a new task"""
    task_type: TaskType = Field(..., description="Type of task to perform")
    prompt: str = Field(..., description="The main prompt/instruction for the AI")
    code: Optional[str] = Field(None, description="Existing code to work with (for validation, formatting, etc.)")
    language: str = Field(default="python", description="Programming language")
    provider_preference: Optional[List[ProviderType]] = Field(
        None, 
        description="Preferred providers in order of priority"
    )
    model_preference: Optional[str] = Field(
        None,
        description="Preferred model (e.g., 'gpt-4', 'claude-3-sonnet')"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Creativity temperature")
    max_tokens: int = Field(default=4096, ge=1, le=32768, description="Maximum tokens to generate")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    timeout_seconds: int = Field(default=300, ge=10, le=3600, description="Timeout in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        """Validate that language is a valid programming language"""
        valid_languages = [
            'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 'go',
            'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'sql', 'bash',
            'html', 'css', 'json', 'yaml', 'markdown', 'text'
        ]
        if v.lower() not in valid_languages:
            raise ValueError(f"Unsupported language: {v}. Supported: {valid_languages}")
        return v.lower()


class TaskResponse(BaseModel):
    """Response model for task results"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current status of the task")
    result: Optional[str] = Field(None, description="Generated/processed result")
    provider_used: Optional[ProviderType] = Field(None, description="Provider that handled the task")
    model_used: Optional[str] = Field(None, description="Model that was used")
    tokens_used: int = Field(default=0, description="Number of tokens used")
    cost: float = Field(default=0.0, description="Cost in USD")
    execution_time_ms: float = Field(default=0.0, description="Execution time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional response metadata")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")


class TaskCreateResponse(BaseModel):
    """Response when a task is created"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Initial task status")
    message: str = Field(default="Task created successfully", description="Status message")
    created_at: datetime = Field(..., description="When the task was created")


class TaskListResponse(BaseModel):
    """Response for listing tasks"""
    tasks: List[TaskResponse] = Field(default_factory=list, description="List of tasks")
    total: int = Field(default=0, description="Total number of tasks")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=10, description="Number of tasks per page")


class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    prompt: str = Field(..., description="Description of what code to generate")
    language: str = Field(default="python", description="Programming language")
    framework: Optional[str] = Field(None, description="Optional framework (e.g., 'fastapi', 'django', 'react')")
    include_comments: bool = Field(default=True, description="Whether to include comments in generated code")
    include_tests: bool = Field(default=False, description="Whether to include unit tests")
    
    # Inherit from TaskRequest for common fields
    provider_preference: Optional[List[ProviderType]] = Field(
        None, 
        description="Preferred providers in order of priority"
    )
    model_preference: Optional[str] = Field(None, description="Preferred model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=32768)


class CodeValidationRequest(BaseModel):
    """Request model for code validation"""
    code: str = Field(..., description="Code to validate")
    language: str = Field(default="python", description="Programming language")
    check_syntax: bool = Field(default=True, description="Check for syntax errors")
    check_semantics: bool = Field(default=True, description="Check for semantic issues")
    check_style: bool = Field(default=True, description="Check code style")
    lint_config: Optional[Dict[str, Any]] = Field(None, description="Custom linting configuration")


class CodeFormattingRequest(BaseModel):
    """Request model for code formatting"""
    code: str = Field(..., description="Code to format")
    language: str = Field(default="python", description="Programming language")
    style: Optional[str] = Field(None, description="Formatting style (e.g., 'pep8', 'black', 'prettier')")
    indent_size: int = Field(default=4, ge=1, le=8, description="Indentation size")
    line_length: int = Field(default=88, ge=40, le=120, description="Maximum line length")


class TemplateRequest(BaseModel):
    """Request model for using templates"""
    template_name: str = Field(..., description="Name of the template to use")
    variables: Dict[str, str] = Field(default_factory=dict, description="Template variables")
    language: str = Field(default="python", description="Programming language")


class ProviderConfig(BaseModel):
    """Configuration for an AI provider"""
    provider_type: ProviderType = Field(..., description="Type of provider")
    api_key: str = Field(..., description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL (for self-hosted)")
    models: List[str] = Field(default_factory=list, description="Available models")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=120, description="Timeout in seconds")
    enabled: bool = Field(default=True, description="Whether this provider is enabled")
    priority: int = Field(default=1, description="Priority (lower = higher priority)")
    
    class Config:
        from_attributes = True


class CodeTemplate(BaseModel):
    """Model for code templates"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    language: str = Field(..., description="Programming language")
    template: str = Field(..., description="The template content")
    variables: List[str] = Field(default_factory=list, description="List of required variables")
    tags: List[str] = Field(default_factory=list, description="Template tags")


class StatsResponse(BaseModel):
    """Response model for statistics"""
    total_tasks: int = Field(default=0, description="Total tasks processed")
    completed_tasks: int = Field(default=0, description="Successfully completed tasks")
    failed_tasks: int = Field(default=0, description="Failed tasks")
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost: float = Field(default=0.0, description="Total cost in USD")
    avg_execution_time_ms: float = Field(default=0.0, description="Average execution time")
    provider_usage: Dict[str, int] = Field(default_factory=dict, description="Usage per provider")
    model_usage: Dict[str, int] = Field(default_factory=dict, description="Usage per model")
    task_type_distribution: Dict[str, int] = Field(default_factory=dict, description="Task types distribution")
