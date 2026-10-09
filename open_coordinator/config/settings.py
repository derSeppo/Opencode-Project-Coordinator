"""Configuration settings for the OpenCode AI Coordinator"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn
from pydantic.typing import AnyHttpUrl

from open_coordinator.models.task import ProviderType


class ProviderSettings(BaseSettings):
    """Settings for a single AI provider"""
    api_key: Optional[str] = Field(None, description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=120, description="Timeout in seconds")
    enabled: bool = Field(default=True, description="Whether this provider is enabled")
    priority: int = Field(default=1, description="Priority (lower = higher priority)")
    models: List[str] = Field(default_factory=list, description="Available models")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class OpenAISettings(ProviderSettings):
    """OpenAI specific settings"""
    provider_type: ProviderType = ProviderType.OPENAI
    base_url: str = "https://api.openai.com/v1"
    models: List[str] = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k", "gpt-3.5-turbo-instruct"
    ]


class AnthropicSettings(ProviderSettings):
    """Anthropic specific settings"""
    provider_type: ProviderType = ProviderType.ANTHROPIC
    base_url: str = "https://api.anthropic.com/v1"
    models: List[str] = [
        "claude-3-5-sonnet", "claude-3-haiku", "claude-3-sonnet", 
        "claude-3-opus", "claude-2-1", "claude-2"
    ]


class MistralSettings(ProviderSettings):
    """Mistral AI specific settings"""
    provider_type: ProviderType = ProviderType.MISTRAL
    base_url: str = "https://api.mistral.ai/v1"
    models: List[str] = [
        "mistral-large", "mistral-small", "mistral-tiny",
        "mixtral-8x7b", "mixtral-8x22b"
    ]


class GoogleSettings(ProviderSettings):
    """Google AI specific settings"""
    provider_type: ProviderType = ProviderType.GOOGLE
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    models: List[str] = [
        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"
    ]


class CohereSettings(ProviderSettings):
    """Cohere specific settings"""
    provider_type: ProviderType = ProviderType.COHERE
    base_url: str = "https://api.cohere.ai/v1"
    models: List[str] = [
        "command-r", "command-r-plus", "command"
    ]


class GroqSettings(ProviderSettings):
    """Groq specific settings"""
    provider_type: ProviderType.GROQ
    base_url: str = "https://api.groq.com/v1"
    models: List[str] = [
        "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768",
        "gemma-7b-it", "gemma2-9b-it"
    ]


class LocalSettings(ProviderSettings):
    """Local/LLM specific settings"""
    provider_type: ProviderType = ProviderType.LOCAL
    base_url: str = "http://localhost:11434/v1"
    models: List[str] = ["llama2", "mistral", "phi3"]


class HuggingFaceSettings(ProviderSettings):
    """HuggingFace specific settings"""
    provider_type: ProviderType.HUGGINGFACE
    base_url: str = "https://api-inference.huggingface.co"
    models: List[str] = []


class TogetherSettings(ProviderSettings):
    """Together AI specific settings"""
    provider_type: ProviderType.TOGETHER
    base_url: str = "https://api.together.xyz/v1"
    models: List[str] = []


class ProviderConfigs(BaseSettings):
    """All provider configurations"""
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    mistral: MistralSettings = Field(default_factory=MistralSettings)
    google: GoogleSettings = Field(default_factory=GoogleSettings)
    cohere: CohereSettings = Field(default_factory=CohereSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    local: LocalSettings = Field(default_factory=LocalSettings)
    huggingface: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    together: TogetherSettings = Field(default_factory=TogetherSettings)


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    database_url: str = Field(
        default="sqlite:///./open_coordinator.db",
        description="Database URL"
    )
    async_database_url: Optional[str] = Field(
        None,
        description="Async database URL (if different)"
    )
    echo: bool = Field(default=False, description="Whether to echo SQL queries")
    pool_size: int = Field(default=5, description="Database connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow for connection pool")


class RedisSettings(BaseSettings):
    """Redis configuration for caching and task queue"""
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    queue_name: str = Field(default="open_coordinator_tasks", description="Queue name for tasks")


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration"""
    enabled: bool = Field(default=True, description="Whether rate limiting is enabled")
    requests_per_minute: int = Field(default=1000, description="Requests per minute limit")
    requests_per_hour: int = Field(default=10000, description="Requests per hour limit")
    burst_size: int = Field(default=100, description="Burst size for rate limiting")


class SecuritySettings(BaseSettings):
    """Security configuration"""
    api_key_required: bool = Field(default=True, description="Whether API key is required")
    api_keys: List[str] = Field(default_factory=list, description="List of valid API keys")
    cors_origins: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(
        default=["*"],
        description="CORS allowed methods"
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        description="CORS allowed headers"
    )
    rate_limit_enabled: bool = Field(default=True)


class LoggingSettings(BaseSettings):
    """Logging configuration"""
    level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    enable_console: bool = Field(default=True, description="Enable console logging")


class TemplateSettings(BaseSettings):
    """Template configuration"""
    template_dir: Path = Field(
        default=Path("templates"),
        description="Directory for code templates"
    )
    auto_reload: bool = Field(default=True, description="Auto reload templates")


class CodeSettings(BaseSettings):
    """Code generation settings"""
    default_language: str = Field(default="python", description="Default programming language")
    default_timeout: int = Field(default=300, description="Default timeout in seconds")
    max_tokens: int = Field(default=32768, description="Maximum tokens per request")
    default_temperature: float = Field(default=0.7, description="Default temperature")


class ServerSettings(BaseSettings):
    """Server configuration"""
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    workers: int = Field(default=4, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto reload on code changes")


class Settings(BaseSettings):
    """Main application settings"""
    app_name: str = Field(default="OpenCode AI Coordinator", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_description: str = Field(
        default="A production-ready webapp that coordinates AI providers for code tasks",
        description="Application description"
    )
    
    # Sub-settings
    server: ServerSettings = Field(default_factory=ServerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    providers: ProviderConfigs = Field(default_factory=ProviderConfigs)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    templates: TemplateSettings = Field(default_factory=TemplateSettings)
    code: CodeSettings = Field(default_factory=CodeSettings)
    
    # Environment
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def reset_settings():
    """Reset the cached settings"""
    get_settings.cache_clear()


# Convenience function to get provider settings
def get_provider_settings(provider_type: ProviderType) -> ProviderSettings:
    """Get settings for a specific provider"""
    settings = get_settings()
    provider_map = {
        ProviderType.OPENAI: settings.providers.openai,
        ProviderType.ANTHROPIC: settings.providers.anthropic,
        ProviderType.MISTRAL: settings.providers.mistral,
        ProviderType.GOOGLE: settings.providers.google,
        ProviderType.COHERE: settings.providers.cohere,
        ProviderType.GROQ: settings.providers.groq,
        ProviderType.LOCAL: settings.providers.local,
        ProviderType.HUGGINGFACE: settings.providers.huggingface,
        ProviderType.TOGETHER: settings.providers.together,
    }
    return provider_map.get(provider_type, ProviderSettings())
