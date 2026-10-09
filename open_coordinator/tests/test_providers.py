"""Tests for AI providers"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp

from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
    ProviderType,
)
from open_coordinator.providers.openai import OpenAIProvider
from open_coordinator.providers.anthropic import AnthropicProvider
from open_coordinator.providers.mistral import MistralProvider
from open_coordinator.providers.google import GoogleProvider
from open_coordinator.providers.cohere import CohereProvider
from open_coordinator.providers.groq import GroqProvider
from open_coordinator.providers.local import LocalProvider
from open_coordinator.providers.factory import ProviderFactory, get_provider_factory
from open_coordinator.config.settings import get_settings, OpenAISettings


@pytest.mark.asyncio
async def test_openai_provider_initialization():
    """Test OpenAI provider initialization"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    assert provider.provider_type == ProviderType.OPENAI
    assert provider.enabled == True
    assert provider.api_key == "test-key"
    assert provider.base_url == "https://api.openai.com/v1"


@pytest.mark.asyncio
async def test_openai_provider_health():
    """Test OpenAI provider health check"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization"""
    from open_coordinator.config.settings import AnthropicSettings
    
    settings = AnthropicSettings(
        api_key="test-key",
        base_url="https://api.anthropic.com/v1",
        enabled=True
    )
    
    provider = AnthropicProvider(settings)
    assert provider.provider_type == ProviderType.ANTHROPIC
    assert provider.enabled == True
    assert provider.api_key == "test-key"


@pytest.mark.asyncio
async def test_mistral_provider_initialization():
    """Test Mistral provider initialization"""
    from open_coordinator.config.settings import MistralSettings
    
    settings = MistralSettings(
        api_key="test-key",
        base_url="https://api.mistral.ai/v1",
        enabled=True
    )
    
    provider = MistralProvider(settings)
    assert provider.provider_type == ProviderType.MISTRAL
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_google_provider_initialization():
    """Test Google provider initialization"""
    from open_coordinator.config.settings import GoogleSettings
    
    settings = GoogleSettings(
        api_key="test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        enabled=True
    )
    
    provider = GoogleProvider(settings)
    assert provider.provider_type == ProviderType.GOOGLE
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_cohere_provider_initialization():
    """Test Cohere provider initialization"""
    from open_coordinator.config.settings import CohereSettings
    
    settings = CohereSettings(
        api_key="test-key",
        base_url="https://api.cohere.ai/v1",
        enabled=True
    )
    
    provider = CohereProvider(settings)
    assert provider.provider_type == ProviderType.COHERE
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_groq_provider_initialization():
    """Test Groq provider initialization"""
    from open_coordinator.config.settings import GroqSettings
    
    settings = GroqSettings(
        api_key="test-key",
        base_url="https://api.groq.com/v1",
        enabled=True
    )
    
    provider = GroqProvider(settings)
    assert provider.provider_type == ProviderType.GROQ
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_local_provider_initialization():
    """Test Local provider initialization"""
    from open_coordinator.config.settings import LocalSettings
    
    settings = LocalSettings(
        api_key="",
        base_url="http://localhost:11434/v1",
        enabled=True
    )
    
    provider = LocalProvider(settings)
    assert provider.provider_type == ProviderType.LOCAL
    assert provider.enabled == True


@pytest.mark.asyncio
async def test_provider_factory():
    """Test provider factory"""
    factory = ProviderFactory()
    await factory.initialize()
    
    # Test getting providers
    openai_provider = factory.get_provider(ProviderType.OPENAI)
    assert openai_provider.provider_type == ProviderType.OPENAI
    
    anthropic_provider = factory.get_provider(ProviderType.ANTHROPIC)
    assert anthropic_provider.provider_type == ProviderType.ANTHROPIC
    
    await factory.close_all()


@pytest.mark.asyncio
async def test_provider_models():
    """Test provider model listing"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    models = provider.list_models()
    
    assert len(models) > 0
    assert all('id' in model for model in models)
    assert all('provider' in model for model in models)


@pytest.mark.asyncio
async def test_provider_model_info():
    """Test provider model info"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    model_info = provider.get_model_info("gpt-4o")
    
    assert model_info['id'] == "gpt-4o"
    assert model_info['provider'] == "openai"
    assert 'max_tokens' in model_info
    assert 'pricing' in model_info


@pytest.mark.asyncio
async def test_provider_cost_calculation():
    """Test provider cost calculation"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    cost = provider.calculate_cost(1000, "gpt-4o")
    
    assert cost > 0
    assert isinstance(cost, float)


@pytest.mark.asyncio
async def test_provider_max_tokens():
    """Test provider max tokens"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    max_tokens = provider.get_max_tokens("gpt-4o")
    
    assert max_tokens > 0
    assert isinstance(max_tokens, int)


@pytest.mark.asyncio
async def test_disabled_provider():
    """Test disabled provider"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=False
    )
    
    provider = OpenAIProvider(settings)
    assert provider.enabled == False


@pytest.mark.asyncio
async def test_provider_priority():
    """Test provider priority"""
    from open_coordinator.config.settings import OpenAISettings, AnthropicSettings
    
    openai_settings = OpenAISettings(
        api_key="test-key",
        enabled=True,
        priority=1
    )
    anthropic_settings = AnthropicSettings(
        api_key="test-key",
        enabled=True,
        priority=2
    )
    
    openai_provider = OpenAIProvider(openai_settings)
    anthropic_provider = AnthropicProvider(anthropic_settings)
    
    assert openai_provider.priority == 1
    assert anthropic_provider.priority == 2
    assert openai_provider.priority < anthropic_provider.priority


@pytest.mark.asyncio
async def test_provider_headers():
    """Test provider headers"""
    settings = OpenAISettings(
        api_key="test-key",
        base_url="https://api.openai.com/v1",
        enabled=True
    )
    
    provider = OpenAIProvider(settings)
    headers = provider._get_headers()
    
    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"
    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test-key"


@pytest.mark.asyncio
async def test_anthropic_headers():
    """Test Anthropic headers"""
    from open_coordinator.config.settings import AnthropicSettings
    
    settings = AnthropicSettings(
        api_key="test-key",
        base_url="https://api.anthropic.com/v1",
        enabled=True
    )
    
    provider = AnthropicProvider(settings)
    headers = provider._get_headers()
    
    assert "Content-Type" in headers
    assert "X-API-Key" in headers
    assert headers["X-API-Key"] == "test-key"
    assert "Anthropic-Version" in headers


@pytest.mark.asyncio
async def test_provider_error():
    """Test provider error handling"""
    error = ProviderError("Test error", ProviderType.OPENAI, 400)
    
    assert str(error) == "[openai] Test error"
    assert error.provider == ProviderType.OPENAI
    assert error.status_code == 400
