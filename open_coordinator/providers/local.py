"""Local provider implementation (Ollama, etc.)"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import LocalSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class LocalProvider(BaseProvider):
    """Local LLM provider (Ollama, etc.)"""
    
    provider_type = ProviderType.LOCAL
    settings_class = LocalSettings
    
    # Local models have no cost
    PRICING = {}
    
    # Model max tokens (can be very high for local models)
    MAX_TOKENS = {
        "llama2": 4096,
        "mistral": 32768,
        "phi3": 128000,
    }
    
    def _get_default_base_url(self) -> str:
        return "http://localhost:11434/v1"
    
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
        """Generate text using local LLM (OpenAI-compatible API)"""
        model = model or self.models[0]
        
        # Build messages
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
            "stream": False,  # Ensure non-streaming for simplicity
            **kwargs
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
                cost=0.0,  # Local models are free
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
        """Chat completion using local LLM"""
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
            "local": True
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        return [self.get_model_info(model) for model in self.models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Local models have no cost"""
        return 0.0
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
