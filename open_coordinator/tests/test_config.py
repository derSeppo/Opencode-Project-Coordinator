"""Tests for configuration settings"""

import pytest
import os
from pathlib import Path

from open_coordinator.config.settings import (
    Settings,
    get_settings,
    reset_settings,
    ProviderSettings,
    OpenAISettings,
    AnthropicSettings,
    MistralSettings,
    GoogleSettings,
    CohereSettings,
    GroqSettings,
    LocalSettings,
    ProviderConfigs,
    DatabaseSettings,
    RedisSettings,
    RateLimitSettings,
    SecuritySettings,
    LoggingSettings,
    TemplateSettings,
    CodeSettings,
    ServerSettings,
)
from open_coordinator.models.task import ProviderType


@pytest.fixture(autouse=True)
def cleanup_settings():
    """Cleanup settings after each test"""
    yield
    reset_settings()


@pytest.fixture
def temp_env():
    """Create a temporary environment for testing"""
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['APP_NAME'] = 'Test App'
    os.environ['ENVIRONMENT'] = 'test'
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_settings_creation():
    """Test settings creation"""
    settings = Settings()
    
    assert settings.app_name == "OpenCode AI Coordinator"
    assert settings.app_version == "1.0.0"
    assert settings.environment == "development"


def test_settings_from_env(temp_env):
    """Test settings from environment variables"""
    settings = Settings()
    
    assert settings.app_name == "Test App"
    assert settings.environment == "test"


def test_get_settings():
    """Test get_settings function"""
    settings = get_settings()
    
    assert isinstance(settings, Settings)
    assert settings.app_name is not None


def test_reset_settings():
    """Test reset_settings function"""
    settings1 = get_settings()
    
    reset_settings()
    
    settings2 = get_settings()
    
    # Should get a fresh instance
    assert settings1 is not settings2


def test_server_settings():
    """Test server settings"""
    server_settings = ServerSettings()
    
    assert server_settings.host == "0.0.0.0"
    assert server_settings.port == 8000
    assert server_settings.debug == False
    assert server_settings.workers == 4
    assert server_settings.reload == False


def test_database_settings():
    """Test database settings"""
    db_settings = DatabaseSettings()
    
    assert db_settings.database_url == "sqlite:///./open_coordinator.db"
    assert db_settings.echo == False
    assert db_settings.pool_size == 5
    assert db_settings.max_overflow == 10


def test_redis_settings():
    """Test Redis settings"""
    redis_settings = RedisSettings()
    
    assert redis_settings.redis_url == "redis://localhost:6379/0"
    assert redis_settings.cache_ttl == 3600
    assert redis_settings.queue_name == "open_coordinator_tasks"


def test_rate_limit_settings():
    """Test rate limit settings"""
    rate_limit_settings = RateLimitSettings()
    
    assert rate_limit_settings.enabled == True
    assert rate_limit_settings.requests_per_minute == 1000
    assert rate_limit_settings.requests_per_hour == 10000
    assert rate_limit_settings.burst_size == 100


def test_security_settings():
    """Test security settings"""
    security_settings = SecuritySettings()
    
    assert security_settings.api_key_required == True
    assert security_settings.api_keys == []
    assert security_settings.cors_origins == ["*"]
    assert security_settings.cors_allow_credentials == True
    assert security_settings.cors_allow_methods == ["*"]
    assert security_settings.cors_allow_headers == ["*"]


def test_logging_settings():
    """Test logging settings"""
    logging_settings = LoggingSettings()
    
    assert logging_settings.level == "INFO"
    assert logging_settings.log_file is None
    assert logging_settings.enable_console == True


def test_template_settings():
    """Test template settings"""
    template_settings = TemplateSettings()
    
    assert template_settings.template_dir == Path("templates")
    assert template_settings.auto_reload == True


def test_code_settings():
    """Test code settings"""
    code_settings = CodeSettings()
    
    assert code_settings.default_language == "python"
    assert code_settings.default_timeout == 300
    assert code_settings.max_tokens == 32768
    assert code_settings.default_temperature == 0.7


def test_openai_settings():
    """Test OpenAI settings"""
    openai_settings = OpenAISettings()
    
    assert openai_settings.provider_type == ProviderType.OPENAI
    assert openai_settings.base_url == "https://api.openai.com/v1"
    assert openai_settings.enabled == True
    assert len(openai_settings.models) > 0
    assert "gpt-4o" in openai_settings.models


def test_anthropic_settings():
    """Test Anthropic settings"""
    anthropic_settings = AnthropicSettings()
    
    assert anthropic_settings.provider_type == ProviderType.ANTHROPIC
    assert anthropic_settings.base_url == "https://api.anthropic.com/v1"
    assert anthropic_settings.enabled == True
    assert len(anthropic_settings.models) > 0


def test_mistral_settings():
    """Test Mistral settings"""
    mistral_settings = MistralSettings()
    
    assert mistral_settings.provider_type == ProviderType.MISTRAL
    assert mistral_settings.base_url == "https://api.mistral.ai/v1"
    assert mistral_settings.enabled == True
    assert len(mistral_settings.models) > 0


def test_google_settings():
    """Test Google settings"""
    google_settings = GoogleSettings()
    
    assert google_settings.provider_type == ProviderType.GOOGLE
    assert google_settings.base_url == "https://generativelanguage.googleapis.com/v1beta"
    assert google_settings.enabled == False  # Disabled by default
    assert len(google_settings.models) > 0


def test_cohere_settings():
    """Test Cohere settings"""
    cohere_settings = CohereSettings()
    
    assert cohere_settings.provider_type == ProviderType.COHERE
    assert cohere_settings.base_url == "https://api.cohere.ai/v1"
    assert cohere_settings.enabled == False  # Disabled by default
    assert len(cohere_settings.models) > 0


def test_groq_settings():
    """Test Groq settings"""
    groq_settings = GroqSettings()
    
    assert groq_settings.provider_type == ProviderType.GROQ
    assert groq_settings.base_url == "https://api.groq.com/v1"
    assert groq_settings.enabled == False  # Disabled by default
    assert len(groq_settings.models) > 0


def test_local_settings():
    """Test Local settings"""
    local_settings = LocalSettings()
    
    assert local_settings.provider_type == ProviderType.LOCAL
    assert local_settings.base_url == "http://localhost:11434/v1"
    assert local_settings.enabled == False  # Disabled by default
    assert len(local_settings.models) > 0


def test_provider_configs():
    """Test provider configs"""
    provider_configs = ProviderConfigs()
    
    assert isinstance(provider_configs.openai, OpenAISettings)
    assert isinstance(provider_configs.anthropic, AnthropicSettings)
    assert isinstance(provider_configs.mistral, MistralSettings)
    assert isinstance(provider_configs.google, GoogleSettings)
    assert isinstance(provider_configs.cohere, CohereSettings)
    assert isinstance(provider_configs.groq, GroqSettings)
    assert isinstance(provider_configs.local, LocalSettings)


def test_nested_settings():
    """Test nested settings structure"""
    settings = Settings()
    
    assert isinstance(settings.server, ServerSettings)
    assert isinstance(settings.database, DatabaseSettings)
    assert isinstance(settings.redis, RedisSettings)
    assert isinstance(settings.providers, ProviderConfigs)
    assert isinstance(settings.security, SecuritySettings)
    assert isinstance(settings.rate_limit, RateLimitSettings)
    assert isinstance(settings.logging, LoggingSettings)
    assert isinstance(settings.templates, TemplateSettings)
    assert isinstance(settings.code, CodeSettings)


def test_settings_equality():
    """Test settings equality"""
    settings1 = Settings()
    settings2 = Settings()
    
    # Default settings should be equal
    assert settings1.app_name == settings2.app_name
    assert settings1.app_version == settings2.app_version
    assert settings1.environment == settings2.environment


def test_custom_settings():
    """Test custom settings"""
    from pydantic import BaseSettings
    
    class CustomSettings(BaseSettings):
        custom_value: str = "default"
        
        class Config:
            env_file = ".env"
    
    # This tests that we can create custom settings
    custom = CustomSettings()
    assert custom.custom_value == "default"


def test_settings_validation():
    """Test settings validation"""
    # Test with invalid port
    with pytest.raises(Exception):
        ServerSettings(port=-1)
    
    # Test with invalid rate limit
    with pytest.raises(Exception):
        RateLimitSettings(requests_per_minute=-1)


def test_settings_with_env_file():
    """Test settings with environment file"""
    # Create a temporary .env file
    env_file = Path("test.env")
    env_file.write_text("APP_NAME=TestFromFile\n")
    
    try:
        # Create settings with custom env file
        class TestSettings(BaseSettings):
            app_name: str = "default"
            
            class Config:
                env_file = "test.env"
        
        settings = TestSettings()
        assert settings.app_name == "TestFromFile"
    finally:
        # Cleanup
        if env_file.exists():
            env_file.unlink()


@pytest.mark.asyncio
async def test_get_provider_settings():
    """Test get_provider_settings function"""
    from open_coordinator.config.settings import get_provider_settings
    
    # Test with OpenAI
    openai_settings = get_provider_settings(ProviderType.OPENAI)
    assert isinstance(openai_settings, ProviderSettings)
    assert openai_settings.provider_type == ProviderType.OPENAI
    
    # Test with Anthropic
    anthropic_settings = get_provider_settings(ProviderType.ANTHROPIC)
    assert isinstance(anthropic_settings, ProviderSettings)
    assert anthropic_settings.provider_type == ProviderType.ANTHROPIC


@pytest.mark.asyncio
async def test_provider_settings_cache():
    """Test that provider settings are cached"""
    from open_coordinator.config.settings import get_provider_settings
    
    settings1 = get_provider_settings(ProviderType.OPENAI)
    settings2 = get_provider_settings(ProviderType.OPENAI)
    
    # Should return the same cached instance
    assert settings1 is settings2
