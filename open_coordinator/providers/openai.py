"""OpenAI provider implementation"""

import json
import logging
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import OpenAISettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI API provider"""
    
    provider_type = ProviderType.OPENAI
    settings_class = OpenAISettings
    
    # OpenAI pricing (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 5.0, "output": 15.0},  # per 1M tokens
        "gpt-4o-mini": {"input": 1.5, "output": 6.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
        "gpt-3.5-turbo-16k": {"input": 1.0, "output": 2.0},
        "gpt-3.5-turbo-instruct": {"input": 1.5, "output": 2.0},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16384,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-instruct": 4096,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://api.openai.com/v1"
    
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
        """Generate text using OpenAI completion API"""
        import time
        
        model = model or self.models[0]  # Default to first available model
        
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
        """Chat completion using OpenAI"""
        # Chat is the same as generate for OpenAI
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
        """Calculate cost for OpenAI tokens"""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        # Assume roughly half input, half output for estimation
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
