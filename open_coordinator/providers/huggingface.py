"""HuggingFace Inference API provider implementation"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from open_coordinator.config.settings import HuggingFaceSettings
from open_coordinator.models.task import ProviderType
from open_coordinator.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderResponse,
)

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseProvider):
    """HuggingFace Inference API provider"""
    
    provider_type = ProviderType.HUGGINGFACE
    settings_class = HuggingFaceSettings
    
    # HuggingFace has free models - no cost
    PRICING = {}
    
    # Model max tokens (approximate)
    MAX_TOKENS = {
        "mistralai/Mistral-7B-Instruct-v0.2": 32768,
        "mistralai/Mixtral-8x7B-Instruct-v0.1": 32768,
        "meta-llama/Llama-2-7b-chat-hf": 4096,
        "meta-llama/Llama-2-13b-chat-hf": 4096,
        "google/flan-t5-xxl": 4096,
        "google/flan-t5-large": 2048,
        "t5-base": 512,
        "t5-small": 512,
        "distilbert-base-uncased": 512,
        "bert-base-uncased": 512,
    }
    
    def _get_default_base_url(self) -> str:
        return "https://api-inference.huggingface.co"
    
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
        """Generate text using HuggingFace Inference API"""
        model = model or self.models[0] if self.models else "mistralai/Mistral-7B-Instruct-v0.2"
        
        # Build payload for text generation
        # HuggingFace accepts different payload formats depending on the model
        payload = self._build_payload(prompt, model, temperature, max_tokens, system_prompt, messages, **kwargs)
        
        start_time = time.time()
        
        try:
            response = await self._make_request("POST", f"/models/{model}", payload)
            
            content = self._extract_content(response, model)
            
            # Estimate tokens (HuggingFace doesn't always return token counts)
            tokens_used = self._estimate_tokens(payload, content)
            
            execution_time = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=content,
                provider=self.provider_type,
                model=model,
                tokens_used=tokens_used,
                cost=0.0,  # Free!
                execution_time_ms=execution_time,
                finish_reason="stop",
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
        """Chat completion using HuggingFace"""
        # Convert messages to HuggingFace format
        if messages:
            # For chat models, we need to format the messages
            prompt = self._format_chat_messages(messages)
        else:
            prompt = ""
        
        return await self.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _build_payload(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Build payload for HuggingFace API"""
        # Check if this is a chat model
        chat_models = [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "meta-llama/Llama-2-7b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "google/flan-t5-xxl",
        ]
        
        if any(m in model for m in chat_models):
            # Chat model format
            payload = {
                "inputs": self._format_chat_prompt(prompt, system_prompt, messages),
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ['model', 'messages', 'temperature', 'max_tokens']}
                }
            }
        else:
            # Text generation model format
            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ['model', 'messages', 'temperature', 'max_tokens']}
                }
            }
        
        return payload
    
    def _format_chat_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Format chat messages for HuggingFace"""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"[INST] {content} [/INST]")
            elif role == "user":
                formatted.append(f"[INST] {content} [/INST]")
            elif role == "assistant":
                formatted.append(f"{content}")
            else:
                formatted.append(f"{content}")
        
        return " ".join(formatted)
    
    def _format_chat_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Format chat prompt for HuggingFace"""
        if messages:
            return self._format_chat_messages(messages)
        
        if system_prompt:
            return f"[INST] {system_prompt} [/INST]\n{prompt}"
        
        return f"[INST] {prompt} [/INST]"
    
    def _extract_content(self, response: Any, model: str) -> str:
        """Extract content from HuggingFace response"""
        if isinstance(response, list) and len(response) > 0:
            if isinstance(response[0], dict):
                return response[0].get("generated_text", "")
            return str(response[0])
        elif isinstance(response, dict):
            if "generated_text" in response:
                return response["generated_text"]
            elif "choices" in response:
                return response["choices"][0].get("text", "")
            elif "outputs" in response:
                return response["outputs"][0].get("text", "")
        
        return str(response)
    
    def _estimate_tokens(self, input_data: Dict[str, Any], output: str) -> int:
        """Estimate token count"""
        # Simple estimation: count words and characters
        input_text = str(input_data.get("inputs", ""))
        output_text = str(output)
        
        # Rough estimate: 1 token ≈ 4 characters
        input_tokens = len(input_text) // 4
        output_tokens = len(output_text) // 4
        
        return input_tokens + output_tokens
    
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
        # Return default free models
        default_models = [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "meta-llama/Llama-2-7b-chat-hf",
            "meta-llama/Llama-2-13b-chat-hf",
            "google/flan-t5-xxl",
            "google/flan-t5-large",
        ]
        
        if self.models:
            # Use configured models if available
            return [self.get_model_info(model) for model in self.models]
        
        return [self.get_model_info(model) for model in default_models]
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """HuggingFace Inference API is free"""
        return 0.0
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        return self.MAX_TOKENS.get(model, 32768)
