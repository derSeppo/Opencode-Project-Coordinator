"""Anthropic provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import AnthropicSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Anthropic API provider"""
    
    provider_type = ProviderType.ANTHROPIC
    settings_class = AnthropicSettings
    
    # Anthropic pricing (as of 2024)
    PRICING = {
        "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},  # per 1M tokens
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-2-1": {"input": 8.0, "output": 24.0},
        "claude-2": {"input": 8.0, "output": 24.0},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "claude-3-5-sonnet": 8192,
        "claude-3-haiku": 8192,
        "claude-3-sonnet": 8192,
        "claude-3-opus": 100000,
        "claude-2-1": 100000,
        "claude-2": 100000,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://api.anthropic.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        headers["X-API-Key"] = self.api_key or ""
        headers["Anthropic-Version"] = "2023-06-01"
        if "X-API-Key" in headers:
            del headers["Authorization"]
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
        """Generate text using Anthropic Messages API"""
        model = model or self.models[0]
        
        # Build messages for Anthropic format
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        
        # Convert messages to Anthropic format
        anthropic_messages = self._convert_to_anthropic_messages(messages)
        
        data = {
            "model": model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", "/messages", data)
            
            content = self._extract_content(response)
            
            # Calculate usage
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens
            
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
                finish_reason=response.get("stop_reason"),
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
        """Chat completion using Anthropic"""
        return await self.generate(
            prompt="",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
            **kwargs
        )
    
    def _convert_to_anthropic_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert standard messages to Anthropic format"""
        anthropic_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Anthropic uses "user" and "assistant" roles
            if role == "system":
                # System prompts are typically handled differently in Anthropic
                # For now, treat as user
                anthropic_messages.append({"role": "user", "content": content})
            else:
                anthropic_messages.append({"role": role, "content": content})
        
        return anthropic_messages
    
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Anthropic response"""
        if "content" in response:
            # Handle both single string and list of blocks
            content = response["content"]
            if isinstance(content, list):
                # Extract text from content blocks
                return "".join(block.get("text", "") for block in content if block.get("type") == "text")
            return str(content)
        
        # Try to get from first message
        messages = response.get("messages", [])
        if messages:
            return self._extract_content(messages[-1])
        
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
        """Calculate cost for Anthropic tokens"""
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
