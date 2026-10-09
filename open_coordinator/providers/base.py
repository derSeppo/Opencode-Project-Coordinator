"""Base provider interface for AI providers"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import backoff

from open_coordinator.config.settings import get_provider_settings, ProviderSettings
from open_coordinator.models.task import ProviderType, TaskStatus

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors"""
    def __init__(self, message: str, provider: ProviderType, status_code: Optional[int] = None):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"[{provider.value}] {message}")


class RateLimitError(ProviderError):
    """Rate limit exceeded"""
    pass


class AuthenticationError(ProviderError):
    """Authentication failed"""
    pass


class ModelNotFoundError(ProviderError):
    """Model not found"""
    pass


class ProviderTimeoutError(ProviderError):
    """Request timeout"""
    pass


class ProviderResponse(BaseModel):
    """Standardized response from any provider"""
    content: str
    provider: ProviderType
    model: str
    tokens_used: int
    cost: float
    execution_time_ms: float
    finish_reason: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True


class BaseProvider(ABC):
    """Abstract base class for all AI providers"""
    
    provider_type: ProviderType
    settings_class: type[ProviderSettings]
    
    def __init__(self, settings: Optional[ProviderSettings] = None):
        self.settings = settings or self._get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining: int = self.settings.rate_limit
        self._rate_limit_reset: float = time.time()
        self._last_request_time: float = 0
        
    def _get_settings(self) -> ProviderSettings:
        """Get settings for this provider"""
        return get_provider_settings(self.provider_type)
    
    @property
    def name(self) -> str:
        """Provider name"""
        return self.provider_type.value
    
    @property
    def base_url(self) -> str:
        """Base URL for API requests"""
        return self.settings.base_url or self._get_default_base_url()
    
    @property
    def api_key(self) -> Optional[str]:
        """API key for authentication"""
        return self.settings.api_key
    
    @property
    def enabled(self) -> bool:
        """Whether this provider is enabled"""
        return self.settings.enabled
    
    @property
    def priority(self) -> int:
        """Provider priority (lower = higher priority)"""
        return self.settings.priority
    
    @property
    def timeout(self) -> int:
        """Request timeout in seconds"""
        return self.settings.timeout
    
    @property
    def rate_limit(self) -> int:
        """Rate limit per minute"""
        return self.settings.rate_limit
    
    @property
    def models(self) -> List[str]:
        """Available models"""
        return self.settings.models or []
    
    def _get_default_base_url(self) -> str:
        """Get default base URL for this provider"""
        return ""
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def initialize(self):
        """Initialize the provider (create session, etc.)"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=timeout
            )
    
    async def close(self):
        """Close the provider (clean up resources)"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        jitter=backoff.full_jitter
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the provider API"""
        if not self.enabled:
            raise ProviderError("Provider is disabled", self.provider_type)
        
        await self.initialize()
        
        # Rate limiting
        await self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            async with self.session.request(
                method,
                url,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout or self.timeout)
            ) as response:
                self._update_rate_limit(response)
                
                if response.status == 429:
                    raise RateLimitError(
                        "Rate limit exceeded",
                        self.provider_type,
                        status_code=429
                    )
                elif response.status == 401:
                    raise AuthenticationError(
                        "Authentication failed",
                        self.provider_type,
                        status_code=401
                    )
                elif response.status == 404:
                    raise ModelNotFoundError(
                        "Model not found",
                        self.provider_type,
                        status_code=404
                    )
                elif response.status >= 400:
                    error_text = await response.text()
                    raise ProviderError(
                        f"API error: {response.status} - {error_text}",
                        self.provider_type,
                        status_code=response.status
                    )
                
                return await response.json()
        except asyncio.TimeoutError:
            raise ProviderTimeoutError(
                f"Request timeout after {timeout or self.timeout} seconds",
                self.provider_type
            )
        except aiohttp.ClientError as e:
            raise ProviderError(f"Client error: {str(e)}", self.provider_type)
    
    def _update_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        """Update rate limit tracking from response headers"""
        # Try to get rate limit info from headers
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        
        if remaining:
            self._rate_limit_remaining = int(remaining)
        if reset:
            self._rate_limit_reset = float(reset)
    
    async def _check_rate_limit(self) -> None:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Reset rate limit if we've passed the reset time
        if current_time > self._rate_limit_reset:
            self._rate_limit_remaining = self.rate_limit
            self._rate_limit_reset = current_time + 60  # Reset every minute
        
        # Check if we have remaining requests
        if self._rate_limit_remaining <= 0:
            wait_time = self._rate_limit_reset - current_time
            if wait_time > 0:
                logger.warning(f"Rate limit reached for {self.name}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time + 0.1)  # Add small buffer
                self._rate_limit_remaining = self.rate_limit
                self._rate_limit_reset = time.time() + 60
        
        # Ensure minimum time between requests
        min_interval = 60.0 / self.rate_limit if self.rate_limit > 0 else 0
        time_since_last = current_time - self._last_request_time
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self._last_request_time = time.time()
        self._rate_limit_remaining -= 1
    
    @abstractmethod
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
        """Generate text/code from a prompt"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> ProviderResponse:
        """Chat completion"""
        pass
    
    async def validate_code(
        self,
        code: str,
        language: str = "python",
        **kwargs
    ) -> ProviderResponse:
        """Validate code (default implementation uses generation)"""
        validation_prompt = self._get_validation_prompt(code, language)
        return await self.generate(
            prompt=validation_prompt,
            temperature=0.0,  # Low temperature for deterministic validation
            max_tokens=500,
            **kwargs
        )
    
    async def format_code(
        self,
        code: str,
        language: str = "python",
        **kwargs
    ) -> ProviderResponse:
        """Format code (default implementation uses generation)"""
        format_prompt = self._get_format_prompt(code, language)
        return await self.generate(
            prompt=format_prompt,
            temperature=0.0,
            max_tokens=len(code) * 2,  # Allow for expansion
            **kwargs
        )
    
    def _get_validation_prompt(self, code: str, language: str) -> str:
        """Get prompt for code validation"""
        return f"""Analyze the following {language} code and identify any issues:

1. Syntax errors
2. Semantic issues
3. Potential bugs
4. Style violations

Code:
```{language}
{code}
```

Respond with a JSON object containing:
- "valid": boolean
- "errors": list of error messages
- "warnings": list of warning messages
- "suggestions": list of improvement suggestions

Only respond with valid JSON, no other text."""
    
    def _get_format_prompt(self, code: str, language: str) -> str:
        """Get prompt for code formatting"""
        return f"""Format the following {language} code according to best practices:

1. Fix indentation
2. Ensure consistent style
3. Add proper spacing
4. Follow language conventions

Code:
```{language}
{code}
```

Respond with the formatted code only, no explanations or comments."""
    
    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        pass
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost for a given number of tokens"""
        # Default implementation - override in subclasses
        return 0.0
    
    def get_max_tokens(self, model: str) -> int:
        """Get maximum tokens for a model"""
        # Default implementation - override in subclasses
        return 32768
