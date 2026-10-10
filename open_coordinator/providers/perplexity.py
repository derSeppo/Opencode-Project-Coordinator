"""Perplexity AI provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import PerplexitySettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class PerplexityProvider(BaseProvider):
    """Perplexity AI provider"""
    
    provider_type = ProviderType.PERPLEXITY
    settings_class = PerplexitySettings
    
    # Perplexity pricing (as of 2024)
    PRICING = {
        "llama-3.1-sonar-small-128k-online": {"input": 0.0, "output": 0.0},  # Free
        "llama-3.1-sonar-large-128k-online": {"input": 0.0, "output": 0.0},  # Free
        "llama-3.1-70b-instruct": {"input": 0.0, "output": 0.0},  # Free
        "llama-3-70b-instruct": {"input": 0.0, "output": 0.0},  # Free
        "llama-2-70b-chat": {"input": 0.0, "output": 0.0},  # Free
        "mixtral-8x7b-instruct": {"input": 0.0, "output": 0.0},  # Free
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "llama-3.1-sonar-small-128k-online": 128000,
        "llama-3.1-sonar-large-128k-online": 128000,
        "llama-3.1-70b-instruct": 32768,
        "llama-3-70b-instruct": 32768,
        "llama-2-70b-chat": 4096,
        "mixtral-8x7b-instruct": 32768,
    }
    
    # Free models on Perplexity
    FREE_MODELS = [
        "llama-3.1-sonar-small-128k-online",
        "llama-3.1-sonar-large-128k-online",
        "llama-3.1-70b-instruct",
        "llama-3-70b-instruct",
        "llama-2-70b-chat",
        "mixtral-8x7b-instruct",
    ]
    
    def _get_default_base_url(self) -> str:
        return "https://api.perplexity.ai"
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Accept"] = "application/json"
        return headers
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> ProviderResponse:
        """Generate text using Perplexity AI"""
        model = model or self.models[0] if self.models else "llama-3.1-sonar-small-128k-online"
        
        # Build messages for chat API
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 0.9),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
        }
        
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", "/chat/completions", data)
            
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            # Calculate usage
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=content,
                provider=self.provider_type,
                model=model,
                tokens_used=total_tokens,
                cost=0.0,  # Free on Perplexity!
                execution_time_ms=execution_time,
                finish_reason=choice.get("finish_reason"),
                raw_response=response
            )
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(f"Generation failed: {str(e)}", self.provider_type)
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        """Chat completion using Perplexity"""
        return await self.generate(
            prompt="",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
            **kwargs
        )
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        max_tokens = self.MAX_TOKENS.get(model, 32768)
        
        return {
            "id": model,
            "provider": self.provider_type.value,
            "max_tokens": max_tokens,
            "pricing": {
                "input": 0,
                "output": 0,
                "unit": "free"
            },
            "available": model in self.models,
            "free": True
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        default_models = [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-70b-instruct",
            "llama-3-70b-instruct",
            "llama-2-70b-chat",
            "mixtral-8x7b-instruct",
        ]
        
        if self.models:
            return [self.get_model_info(model) for model in self.models]
        
        return [self.get_model_info(model) for model in default_models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Perplexity is free"""
        return 0.0
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
