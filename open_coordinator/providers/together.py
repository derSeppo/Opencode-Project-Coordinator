"""Together AI provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import TogetherSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class TogetherProvider(BaseProvider):
    """Together AI provider"""
    
    provider_type = ProviderType.TOGETHER
    settings_class = TogetherSettings
    
    # Together AI pricing (as of 2024)
    PRICING = {
        "meta-llama/Llama-2-7b-chat": {"input": 0.0001, "output": 0.0001},  # per token
        "meta-llama/Llama-2-13b-chat": {"input": 0.0002, "output": 0.0002},
        "meta-llama/Llama-2-70b-chat": {"input": 0.0008, "output": 0.0008},
        "mistralai/Mistral-7B-Instruct-v0.1": {"input": 0.0001, "output": 0.0001},
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.0002, "output": 0.0002},
        "ai21-labs/j2-ultra": {"input": 0.0005, "output": 0.0005},
        "ai21-labs/j2-mid": {"input": 0.0002, "output": 0.0002},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "meta-llama/Llama-2-7b-chat": 4096,
        "meta-llama/Llama-2-13b-chat": 4096,
        "meta-llama/Llama-2-70b-chat": 4096,
        "mistralai/Mistral-7B-Instruct-v0.1": 32768,
        "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
        "ai21-labs/j2-ultra": 8191,
        "ai21-labs/j2-mid": 8191,
    }
    
    # Free models (with $25/month free credit)
    FREE_MODELS = [
        "meta-llama/Llama-2-7b-chat",
        "meta-llama/Llama-2-13b-chat",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
    ]
    
    def _get_default_base_url(self) -> str:
        return "https://api.together.xyz/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
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
        """Generate text using Together AI"""
        model = model or self.models[0] if self.models else "meta-llama/Llama-2-7b-chat"
        
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
            "repetition_penalty": kwargs.get("repetition_penalty", 1.0),
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
        """Chat completion using Together AI"""
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
        is_free = model in self.FREE_MODELS
        
        return {
            "id": model,
            "provider": self.provider_type.value,
            "max_tokens": max_tokens,
            "pricing": {
                "input": pricing["input"],
                "output": pricing["output"],
                "unit": "per_token"
            },
            "available": model in self.models,
            "free": is_free
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        # Return default free models
        default_models = [
            "meta-llama/Llama-2-7b-chat",
            "meta-llama/Llama-2-13b-chat",
            "meta-llama/Llama-2-70b-chat",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "ai21-labs/j2-ultra",
            "ai21-labs/j2-mid",
        ]
        
        if self.models:
            return [self.get_model_info(model) for model in self.models]
        
        return [self.get_model_info(model) for model in default_models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost for Together AI tokens"""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        # Assume roughly half input, half output
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens
        
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        
        return input_cost + output_cost
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
