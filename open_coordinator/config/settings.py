"""Configuration settings for the OpenCode AI Coordinator"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict
from typing import Any

from open_coordinator.models.task import ProviderType


class ProviderSettings(BaseSettings):
    """Settings for a single AI provider"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    api_key: Optional[str] = Field(None, description="API key for the provider")
    base_url: Optional[str] = Field(None, description="Custom base URL")
    rate_limit: int = Field(default=100, description="Rate limit per minute")
    timeout: int = Field(default=120, description="Timeout in seconds")
    enabled: bool = Field(default=True, description="Whether this provider is enabled")
    priority: int = Field(default=1, description="Priority (lower = higher priority)")
    models: List[str] = Field(default_factory=list, description="Available models")


class OpenAISettings(ProviderSettings):
    """OpenAI specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.OPENAI
    base_url: str = "https://api.openai.com/v1/"
    models: List[str] = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k", "gpt-3.5-turbo-instruct"
    ]


class AnthropicSettings(ProviderSettings):
    """Anthropic specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.ANTHROPIC
    base_url: str = "https://api.anthropic.com/v1/"
    models: List[str] = [
        "claude-3-5-sonnet", "claude-3-haiku", "claude-3-sonnet", 
        "claude-3-opus", "claude-2-1", "claude-2"
    ]


class MistralSettings(ProviderSettings):
    """Mistral AI specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.MISTRAL
    base_url: str = "https://api.mistral.ai/v1/"
    models: List[str] = [
        "mistral-large", "mistral-small", "mistral-tiny",
        "mixtral-8x7b", "mixtral-8x22b"
    ]


class GoogleSettings(ProviderSettings):
    """Google AI specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.GOOGLE
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/"
    models: List[str] = [
        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"
    ]


class CohereSettings(ProviderSettings):
    """Cohere specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.COHERE
    base_url: str = "https://api.cohere.ai/v1/"
    models: List[str] = [
        "command-r", "command-r-plus", "command"
    ]


class GroqSettings(ProviderSettings):
    """Groq specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.GROQ
    base_url: str = "https://api.groq.com/v1/"
    models: List[str] = [
        "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768",
        "gemma-7b-it", "gemma2-9b-it"
    ]


class LocalSettings(ProviderSettings):
    """Local/LLM specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.LOCAL
    base_url: str = "http://localhost:11434/v1/"
    models: List[str] = ["llama2", "mistral", "phi3"]


class HuggingFaceSettings(ProviderSettings):
    """HuggingFace specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.HUGGINGFACE
    base_url: str = "https://api-inference.huggingface.co/"
    models: List[str] = [
        "mistralai/Mistral-7B-Instruct-v0.2",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "google/flan-t5-xxl",
    ]


class TogetherSettings(ProviderSettings):
    """Together AI specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.TOGETHER
    base_url: str = "https://api.together.xyz/v1/"
    models: List[str] = [
        "meta-llama/Llama-2-7b-chat",
        "meta-llama/Llama-2-13b-chat",
        "meta-llama/Llama-2-70b-chat",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
    ]


class DeepInfraSettings(ProviderSettings):
    """DeepInfra specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.DEEPINFRA
    base_url: str = "https://api.deepinfra.com/v1/"
    models: List[str] = [
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "codellama/CodeLlama-7b-Instruct-hf",
    ]


class PerplexitySettings(ProviderSettings):
    """Perplexity AI specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.PERPLEXITY
    base_url: str = "https://api.perplexity.ai/"
    models: List[str] = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-70b-instruct",
        "llama-3-70b-instruct",
        "mixtral-8x7b-instruct",
    ]


class CerebrasSettings(ProviderSettings):
    """Cerebras specific settings"""
    model_config = SettingsConfigDict(extra="ignore")
    
    provider_type: ProviderType = ProviderType.CEREBRAS
    base_url: str = "https://inference.cerebras.net/v1/"
    models: List[str] = [
        "llama-3.1-70b",
        "llama-3.1-8b",
        "llama-3-70b",
        "llama-3-8b",
        "mistral-7b",
        "mixtral-8x7b",
        "gemma-7b",
        "gemma-2-9b",
    ]


class ProviderConfigs(BaseSettings):
    """All provider configurations"""
    model_config = SettingsConfigDict(extra="ignore")
    
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    mistral: MistralSettings = Field(default_factory=MistralSettings)
    google: GoogleSettings = Field(default_factory=GoogleSettings)
    cohere: CohereSettings = Field(default_factory=CohereSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    local: LocalSettings = Field(default_factory=LocalSettings)
    huggingface: HuggingFaceSettings = Field(default_factory=HuggingFaceSettings)
    together: TogetherSettings = Field(default_factory=TogetherSettings)
    deepinfra: DeepInfraSettings = Field(default_factory=DeepInfraSettings)
    perplexity: PerplexitySettings = Field(default_factory=PerplexitySettings)
    cerebras: CerebrasSettings = Field(default_factory=CerebrasSettings)


class DatabaseSettings(BaseSettings):
    """Database configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
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
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    queue_name: str = Field(default="open_coordinator_tasks", description="Queue name for tasks")


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    enabled: bool = Field(default=True, description="Whether rate limiting is enabled")
    requests_per_minute: int = Field(default=1000, description="Requests per minute limit")
    requests_per_hour: int = Field(default=10000, description="Requests per hour limit")
    burst_size: int = Field(default=100, description="Burst size for rate limiting")


class SecuritySettings(BaseSettings):
    """Security configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
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
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    enable_console: bool = Field(default=True, description="Enable console logging")


class TemplateSettings(BaseSettings):
    """Template configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    template_dir: Path = Field(
        default=Path("templates"),
        description="Directory for code templates"
    )
    auto_reload: bool = Field(default=True, description="Auto reload templates")


class CodeSettings(BaseSettings):
    """Code generation settings"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    default_language: str = Field(default="python", description="Default programming language")
    default_timeout: int = Field(default=300, description="Default timeout in seconds")
    max_tokens: int = Field(default=32768, description="Maximum tokens per request")
    default_temperature: float = Field(default=0.7, description="Default temperature")


class ServerSettings(BaseSettings):
    """Server configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    workers: int = Field(default=4, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto reload on code changes")


class Settings(BaseSettings):
    """Main application settings"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    
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
        ProviderType.DEEPINFRA: settings.providers.deepinfra,
        ProviderType.PERPLEXITY: settings.providers.perplexity,
        ProviderType.CEREBRAS: settings.providers.cerebras,
    }
    return provider_map.get(provider_type, ProviderSettings())
