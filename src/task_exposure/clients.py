"""API clients for OpenAI, Anthropic, and Google Gemini."""

from __future__ import annotations

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Callable, TypeVar

import openai
import anthropic
from google import genai

T = TypeVar("T")


class NonRetryableAPIError(Exception):
    """Base class for API errors that should not be retried."""

    pass


class QuotaExhaustedError(NonRetryableAPIError):
    """Daily or monthly quota exceeded. Will recover later, but not with backoff."""

    pass


class BillingError(NonRetryableAPIError):
    """Insufficient funds or billing disabled. Requires manual intervention."""

    pass


class TruncatedResponseError(NonRetryableAPIError):
    """Response was truncated because it hit the max_tokens ceiling.

    Attributes:
        partial_text: The truncated response text
        max_tokens: The max_tokens value that caused truncation
    """

    def __init__(self, message: str, *, partial_text: str, max_tokens: int):
        super().__init__(message)
        self.partial_text = partial_text
        self.max_tokens = max_tokens


async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of attempts
        base_delay: Base delay in seconds (doubles each retry)

    Returns:
        Result of successful function call

    Raises:
        Exception: The last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except NonRetryableAPIError:
            raise
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)

    raise last_exception


class BaseClient(ABC):
    """Abstract base class for LLM API clients."""

    @abstractmethod
    async def classify(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Send a classification prompt and get a response.

        Args:
            prompt: The formatted prompt to send (user message)
            system_prompt: Optional system prompt for taxonomy/rules (enables caching)

        Returns:
            The raw response string from the LLM
        """
        pass


class OpenAIClient(BaseClient):
    """OpenAI API client."""

    def __init__(
        self,
        model: str,
        api_key: str,
        max_concurrent: int = 50,
        timeout: float = 30.0,
        max_tokens: int = 16384,
        temperature: float | None = None,
    ):
        self.model = model
        self.model_name = model  # Alias for compatibility
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def close(self):
        """Close the client session."""
        await self.client.close()

    async def classify(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Send classification prompt to OpenAI."""

        async def _call():
            async with self._semaphore:
                try:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})
                    kwargs = dict(
                        model=self.model,
                        messages=messages,
                    )
                    # Newer models (o-series, gpt-5*) use max_completion_tokens;
                    # older models (gpt-4*) use max_tokens
                    if self.model.startswith("o") or self.model.startswith("gpt-5"):
                        kwargs["max_completion_tokens"] = self.max_tokens
                    else:
                        kwargs["max_tokens"] = self.max_tokens
                    is_reasoning = self.model.startswith("o") or "mini" in self.model
                    if self.temperature is not None and not is_reasoning:
                        kwargs["temperature"] = self.temperature
                    elif self.temperature is not None and is_reasoning:
                        pass  # Reasoning models only support temperature=1; skip silently
                    elif not is_reasoning:
                        kwargs["temperature"] = 0.0
                    response = await asyncio.wait_for(
                        self.client.chat.completions.create(**kwargs),
                        timeout=self.timeout,
                    )
                    text = response.choices[0].message.content
                    if response.choices[0].finish_reason == "length":
                        raise TruncatedResponseError(
                            f"OpenAI response truncated at {self.max_tokens} max_tokens",
                            partial_text=text,
                            max_tokens=self.max_tokens,
                        )
                    return text
                except openai.RateLimitError as e:
                    body = getattr(e, "body", {}) or {}
                    error_code = body.get("error", {}).get("code", "")
                    if error_code == "insufficient_quota":
                        raise BillingError(str(e)) from e
                    raise

        return await retry_with_backoff(_call)


class AnthropicClient(BaseClient):
    """Anthropic Claude API client."""

    def __init__(
        self,
        model: str,
        api_key: str,
        max_concurrent: int = 50,
        timeout: float = 30.0,
        max_tokens: int = 16384,
        temperature: float | None = None,
    ):
        self.model = model
        self.model_name = model  # Alias for compatibility
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def close(self):
        """Close the client session."""
        await self.client.close()

    async def classify(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Send classification prompt to Anthropic."""

        async def _call():
            async with self._semaphore:
                try:
                    kwargs = dict(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    if system_prompt:
                        kwargs["system"] = system_prompt
                    if self.temperature is not None:
                        kwargs["temperature"] = self.temperature
                    response = await asyncio.wait_for(
                        self.client.messages.create(**kwargs),
                        timeout=self.timeout,
                    )
                    text = response.content[0].text
                    if response.stop_reason == "max_tokens":
                        raise TruncatedResponseError(
                            f"Anthropic response truncated at {self.max_tokens} max_tokens",
                            partial_text=text,
                            max_tokens=self.max_tokens,
                        )
                    return text
                except anthropic.PermissionDeniedError as e:
                    raise BillingError(str(e)) from e

        return await retry_with_backoff(_call)


class GeminiClient(BaseClient):
    """Google Gemini API client using the google-genai SDK."""

    def __init__(
        self,
        model: str,
        api_key: str,
        max_concurrent: int = 50,
        timeout: float = 30.0,
        max_tokens: int = 16384,
        temperature: float | None = None,
    ):
        self.model_name = model
        self.client = genai.Client(api_key=api_key)
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.max_tokens = max_tokens
        # NOTE: Gemini T=0 causes greedy-decoding verbosity that exhausts
        # max_output_tokens via thinking tokens. create_client() silently
        # drops temperature for Gemini models to prevent this.
        self.temperature = temperature

    async def classify(self, prompt: str, *, system_prompt: str | None = None) -> str:
        """Send classification prompt to Gemini using native async."""
        from google.genai.errors import ClientError
        from google.genai import types

        async def _call():
            async with self._semaphore:
                try:
                    kwargs = dict(
                        model=self.model_name,
                        contents=prompt,
                    )
                    config_kwargs = dict(max_output_tokens=self.max_tokens)
                    if system_prompt:
                        config_kwargs["system_instruction"] = system_prompt
                    if self.temperature is not None:
                        config_kwargs["temperature"] = self.temperature
                    kwargs["config"] = types.GenerateContentConfig(**config_kwargs)
                    response = await asyncio.wait_for(
                        self.client.aio.models.generate_content(**kwargs),
                        timeout=self.timeout,
                    )
                    text = response.text
                    if response.candidates and response.candidates[0].finish_reason == "MAX_TOKENS":
                        raise TruncatedResponseError(
                            f"Gemini response truncated at {self.max_tokens} max_tokens",
                            partial_text=text,
                            max_tokens=self.max_tokens,
                        )
                    return text
                except ClientError as e:
                    msg = str(e).lower()
                    if e.code == 429:
                        if "per day" in msg:
                            raise QuotaExhaustedError(str(e)) from e
                        elif "per minute" in msg or "perminute" in msg:
                            # Per-minute rate limit — let retry_with_backoff handle it
                            raise
                        elif "billing" in msg:
                            raise BillingError(str(e)) from e
                    raise

        return await retry_with_backoff(_call)

    async def close(self):
        """Close the client session (no-op for Gemini)."""
        pass


def create_client(model: str, api_key: str, **kwargs) -> BaseClient:
    """Factory function to create appropriate client for a model.

    Args:
        model: Model name (e.g., 'gpt-4o', 'claude-opus-4-5-20251101', 'gemini-3-pro-preview')
        api_key: API key for the provider
        **kwargs: Additional arguments passed to client constructor

    Returns:
        Appropriate client instance

    Raises:
        ValueError: If model name doesn't match any known provider
    """
    if model.startswith("gpt") or model.startswith("o"):
        return OpenAIClient(model=model, api_key=api_key, **kwargs)
    elif model.startswith("claude"):
        return AnthropicClient(model=model, api_key=api_key, **kwargs)
    elif model.startswith("gemini"):
        # Gemini T=0 causes greedy-decoding verbosity that exhausts
        # max_output_tokens via thinking tokens. Silently drop temperature
        # for Gemini to prevent this.
        if kwargs.get("temperature") is not None:
            import warnings

            warnings.warn(
                f"Gemini temperature={kwargs['temperature']} silently dropped by "
                f"create_client() to prevent thinking-token exhaustion.",
                stacklevel=2,
            )
            kwargs.pop("temperature")
        return GeminiClient(model=model, api_key=api_key, **kwargs)
    else:
        raise ValueError(f"Unknown model: {model}")
