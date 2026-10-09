"""Google AI provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import GoogleSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    """Google AI (Gemini) API provider"""
    
    provider_type = ProviderType.GOOGLE
    settings_class = GoogleSettings
    
    # Google pricing (as of 2024)
    PRICING = {
        "gemini-1.5-pro": {"input": 3.5, "output": 10.5},  # per 1M tokens
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
        "gemini-1.0-pro": {"input": 5.0, "output": 15.0},
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "gemini-1.5-pro": 1048576,  # 1M tokens
        "gemini-1.5-flash": 1048576,
        "gemini-1.0-pro": 32768,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta"
    
    def _get_headers(self) -> Dict[str, str]:
        headers = super()._get_headers()
        headers["Content-Type"] = "application/json"
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
        """Generate text using Google Gemini API"""
        model = model or self.models[0]
        
        # Build messages for Google format
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
        
        # Convert to Google format (they use "role" and "parts")
        google_messages = self._convert_to_google_messages(messages)
        
        data = {
            "model": f"models/{model}",
            "messages": google_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                **{k: v for k, v in kwargs.items() if k not in ['model', 'messages', 'temperature', 'max_tokens']}
            }
        }
        
        # Google uses different endpoint format
        model_path = model.replace("-", "")
        endpoint = f"/models/{model_path}:generateContent"
        
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", endpoint, data)
            
            content = self._extract_content(response)
            
            # Calculate usage
            usage = response.get("usageMetadata", {})
            prompt_tokens = usage.get("promptTokenCount", 0)
            completion_tokens = usage.get("candidatesTokenCount", 0)
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
                finish_reason=response.get("finishReason"),
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
        """Chat completion using Google"""
        return await self.generate(
            prompt="",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
            **kwargs
        )
    
    def _convert_to_google_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert standard messages to Google format"""
        google_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Google uses "role" and "parts" (array of content parts)
            google_messages.append({
                "role": role,
                "parts": [{"text": content}]
            })
        
        return google_messages
    
    def _extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from Google response"""
        candidates = response.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            return "".join(part.get("text", "") for part in parts)
        
        # Try alternative format
        if "content" in response:
            return response["content"]
        
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
        """Calculate cost for Google tokens"""
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
