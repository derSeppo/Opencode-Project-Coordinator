"""DeepInfra (Inference Labs) provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import DeepInfraSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class DeepInfraProvider(BaseProvider):
    """DeepInfra (Inference Labs) provider"""
    
    provider_type = ProviderType.DEEPINFRA
    settings_class = DeepInfraSettings
    
    # DeepInfra pricing (as of 2024) - has generous free tier
    PRICING = {
        "mistralai/Mistral-7B-Instruct-v0.1": {"input": 0.0, "output": 0.0},  # Free
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"input": 0.0, "output": 0.0},  # Free
        "meta-llama/Llama-2-7b-chat-hf": {"input": 0.0, "output": 0.0},  # Free
        "meta-llama/Llama-2-13b-chat-hf": {"input": 0.0, "output": 0.0},  # Free
        "meta-llama/Llama-2-70b-chat-hf": {"input": 0.0, "output": 0.0},  # Free
        "google/flan-t5-xxl": {"input": 0.0, "output": 0.0},  # Free
        "google/flan-t5-large": {"input": 0.0, "output": 0.0},  # Free
        "codellama/CodeLlama-7b-Instruct-hf": {"input": 0.0, "output": 0.0},  # Free
        "codellama/CodeLlama-13b-Instruct-hf": {"input": 0.0, "output": 0.0},  # Free
        "codellama/CodeLlama-34b-Instruct-hf": {"input": 0.0, "output": 0.0},  # Free
    }
    
    # Model max tokens
    MAX_TOKENS = {
        "mistralai/Mistral-7B-Instruct-v0.1": 32768,
        "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
        "meta-llama/Llama-2-7b-chat-hf": 4096,
        "meta-llama/Llama-2-13b-chat-hf": 4096,
        "meta-llama/Llama-2-70b-chat-hf": 4096,
        "google/flan-t5-xxl": 4096,
        "google/flan-t5-large": 2048,
        "codellama/CodeLlama-7b-Instruct-hf": 16384,
        "codellama/CodeLlama-13b-Instruct-hf": 16384,
        "codellama/CodeLlama-34b-Instruct-hf": 16384,
    }
    
    # All models are free on DeepInfra
    FREE_MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.1",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "meta-llama/Llama-2-70b-chat-hf",
        "google/flan-t5-xxl",
        "google/flan-t5-large",
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ]
    
    def _get_default_base_url(self) -> str:
        return "https://api.deepinfra.com/v1"
    
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
        """Generate text using DeepInfra"""
        model = model or self.models[0] if self.models else "mistralai/Mistral-7B-Instruct-v0.1"
        
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
            response = await self._make_request("POST", "/openai/chat/completions", data)
            
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
                cost=0.0,  # Free on DeepInfra!
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
        """Chat completion using DeepInfra"""
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
            "mistralai/Mistral-7B-Instruct-v0.1",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "meta-llama/Llama-2-7b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "meta-llama/Llama-2-70b-chat-hf",
            "google/flan-t5-xxl",
            "google/flan-t5-large",
            "codellama/CodeLlama-7b-Instruct-hf",
            "codellama/CodeLlama-13b-Instruct-hf",
            "codellama/CodeLlama-34b-Instruct-hf",
        ]
        
        if self.models:
            return [self.get_model_info(model) for model in self.models]
        
        return [self.get_model_info(model) for model in default_models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """DeepInfra is free"""
        return 0.0
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
