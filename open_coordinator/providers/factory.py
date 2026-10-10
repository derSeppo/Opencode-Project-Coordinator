"""Provider factory for creating and managing AI providers"""

import logging
from typing import Any, Dict, List, Optional, Type

from open_coordinator.config.settings import get_settings, Settings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import BaseProvider
from open_coordinator.providers.openai import OpenAIProvider
from open_coordinator.providers.anthropic import AnthropicProvider
from open_coordinator.providers.mistral import MistralProvider
from open_coordinator.providers.google import GoogleProvider
from open_coordinator.providers.cohere import CohereProvider
from open_coordinator.providers.groq import GroqProvider
from open_coordinator.providers.local import LocalProvider
from open_coordinator.providers.huggingface import HuggingFaceProvider
from open_coordinator.providers.together import TogetherProvider
from open_coordinator.providers.deepinfra import DeepInfraProvider
from open_coordinator.providers.perplexity import PerplexityProvider
from open_coordinator.providers.cerebras import CerebrasProvider

logger = logging.getLogger(__name__)


# Mapping of provider types to their classes
PROVIDER_CLASSES: Dict[ProviderType, Type[BaseProvider]] = {
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.ANTHROPIC: AnthropicProvider,
    ProviderType.MISTRAL: MistralProvider,
    ProviderType.GOOGLE: GoogleProvider,
    ProviderType.COHERE: CohereProvider,
    ProviderType.GROQ: GroqProvider,
    ProviderType.LOCAL: LocalProvider,
    ProviderType.HUGGINGFACE: HuggingFaceProvider,
    ProviderType.TOGETHER: TogetherProvider,
    ProviderType.DEEPINFRA: DeepInfraProvider,
    ProviderType.PERPLEXITY: PerplexityProvider,
    ProviderType.CEREBRAS: CerebrasProvider,
}


class ProviderFactory:
    """Factory for creating and managing AI providers"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self._providers: Dict[ProviderType, BaseProvider] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all enabled providers"""
        if self._initialized:
            return
        
        logger.info("Initializing AI providers...")
        
        # Initialize all provider types
        for provider_type in PROVIDER_CLASSES:
            try:
                provider = self._create_provider(provider_type)
                if provider.enabled:
                    await provider.initialize()
                    self._providers[provider_type] = provider
                    logger.info(f"Initialized {provider_type.value} provider")
                else:
                    logger.info(f"{provider_type.value} provider is disabled")
            except Exception as e:
                logger.error(f"Failed to initialize {provider_type.value} provider: {e}")
        
        self._initialized = True
        logger.info(f"Initialized {len(self._providers)} providers")
    
    def _create_provider(self, provider_type: ProviderType) -> BaseProvider:
        """Create a provider instance"""
        provider_class = PROVIDER_CLASSES.get(provider_type)
        if provider_class is None:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        # Get settings for this provider
        provider_settings = self.settings.providers
        provider_attr = provider_type.value.lower()
        
        if hasattr(provider_settings, provider_attr):
            settings = getattr(provider_settings, provider_attr)
        else:
            settings = None
        
        return provider_class(settings)
    
    def get_provider(self, provider_type: ProviderType) -> BaseProvider:
        """Get a specific provider instance"""
        if provider_type not in self._providers:
            self._providers[provider_type] = self._create_provider(provider_type)
        return self._providers[provider_type]
    
    def get_enabled_providers(self) -> List[BaseProvider]:
        """Get all enabled providers"""
        return [
            provider for provider in self._providers.values()
            if provider.enabled
        ]
    
    def get_provider_by_preference(
        self,
        preferred_providers: Optional[List[ProviderType]] = None,
        exclude: Optional[List[ProviderType]] = None
    ) -> Optional[BaseProvider]:
        """
        Get the best available provider based on preference.
        
        Args:
            preferred_providers: List of preferred providers in order
            exclude: List of providers to exclude
        
        Returns:
            The best available provider or None
        """
        exclude = exclude or []
        
        # If preferred providers specified, try them first
        if preferred_providers:
            for provider_type in preferred_providers:
                if provider_type not in exclude:
                    provider = self.get_provider(provider_type)
                    if provider.enabled:
                        return provider
        
        # Otherwise, return the highest priority enabled provider
        enabled_providers = self.get_enabled_providers()
        if enabled_providers:
            # Sort by priority (lower = higher priority)
            enabled_providers.sort(key=lambda p: p.priority)
            return enabled_providers[0]
        
        return None
    
    async def close_all(self) -> None:
        """Close all provider connections"""
        for provider in self._providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.error(f"Error closing {provider.name} provider: {e}")
        self._providers.clear()
    
    def list_all_models(self) -> List[Dict[str, Any]]:
        """List all available models from all providers"""
        all_models = []
        for provider in self._providers.values():
            try:
                models = provider.list_models()
                all_models.extend(models)
            except Exception as e:
                logger.error(f"Error listing models for {provider.name}: {e}")
        return all_models
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about all providers"""
        info = {}
        for provider_type, provider in self._providers.items():
            info[provider_type.value] = {
                "enabled": provider.enabled,
                "priority": provider.priority,
                "base_url": provider.base_url,
                "models": provider.models,
                "rate_limit": provider.rate_limit,
                "timeout": provider.timeout
            }
        return info


# Global provider factory instance
_provider_factory: Optional[ProviderFactory] = None


def get_provider_factory() -> ProviderFactory:
    """Get the global provider factory instance"""
    global _provider_factory
    if _provider_factory is None:
        _provider_factory = ProviderFactory()
    return _provider_factory


async def initialize_providers() -> ProviderFactory:
    """Initialize the global provider factory"""
    factory = get_provider_factory()
    await factory.initialize()
    return factory


async def close_providers() -> None:
    """Close all providers"""
    global _provider_factory
    if _provider_factory is not None:
        await _provider_factory.close_all()
        _provider_factory = None
