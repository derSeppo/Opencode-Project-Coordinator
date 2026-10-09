"""Cohere provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import CohereSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class CohereProvider(BaseProvider):
    """Cohere API provider"""
    
    provider_type = ProviderType.COHERE
    settings_class = CohereSettings
    
    # Cohere pricing (as of 2024)
    PRICING = {
        "command-r": {"input": 0.5, "output": 1.5},  # per 1M tokens
        "command-r-plus": {"input": 3.0, "output": 15.0},
        "command": {"input": 0.5, "output": 1.5},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "command-r": 128000,
        "command-r-plus": 128000,
        "command": 4096,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://api.cohere.ai/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["Cohere-Version"] = "2024-02-05"
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
        """Generate text using Cohere API"""
        model = model or self.models[0]
        
        # Build messages for Cohere format
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "SYSTEM", "message": system_prompt})
            messages.append({"role": "USER", "message": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", "/chat", data)
            
            content = self._extract_content(response)
            
            # Calculate usage
            usage = response.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens
            
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
                finish_reason=response.get("finish_reason"),
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
        """Chat completion using Cohere"""
        return await self.generate(
            prompt="",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
            **kwargs
        )
    
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Cohere response"""
        if "text" in response:
            return response["text"]
        
        messages = response.get("messages", [])
        if messages:
            return messages[-1].get("message", "")
        
        return ""
    
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
        """Calculate cost for Cohere tokens"""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        # Assume roughly half input, half output
        input_tokens = tokens // 2
        output_tokens = tokens - input_tokens
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
