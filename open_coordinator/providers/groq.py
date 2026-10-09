"""Groq provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import GroqSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseProvider):
    """Groq API provider"""
    
    provider_type = ProviderType.GROQ
    settings_class = GroqSettings
    
    # Groq pricing (as of 2024)
    PRICING = {
        "llama3-8b-8192": {"input": 0.1, "output": 0.1},  # per 1M tokens
        "llama3-70b-8192": {"input": 0.59, "output": 0.79},
        "mixtral-8x7b-32768": {"input": 0.27, "output": 0.27},
        "gemma-7b-it": {"input": 0.1, "output": 0.1},
        "gemma2-9b-it": {"input": 0.1, "output": 0.1},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "llama3-8b-8192": 8192,
        "llama3-70b-8192": 8192,
        "mixtral-8x7b-32768": 32768,
        "gemma-7b-it": 8192,
        "gemma2-9b-it": 8192,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://api.groq.com/v1"
    
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
        """Generate text using Groq API (OpenAI-compatible)"""
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
            
            # Calculate cost
            cost = self.calculate_cost(total_tokens, model)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=content,
                provider=self.provider_type,
                model=model,
                tokens_used=total_tokens,
                cost=cost,
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
        """Chat completion using Groq"""
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
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        max_tokens = self.MAX_TOKENS.get(model, 32768)
        
        return {
            "id": model,
            "provider": self.provider_type.value,
            "max_tokens": max_tokens,
            "pricing": {
                "input": pricing["input"],
                "output": pricing["output"],
                "unit": "per_1m_tokens"
            },
            "available": model in self.models
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        return [self.get_model_info(model) for model in self.models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost for Groq tokens"""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        # Groq typically has same pricing for input and output
        # Assume all tokens are output tokens for simplicity
        cost = (tokens / 1_000_000) * pricing["output"]
        
        return cost
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
