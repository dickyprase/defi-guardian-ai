"""
MiMo API Client Wrapper
Handles authentication, rate limiting, and token tracking for MiMo V2.5 models.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class TokenMetrics:
    """Track token consumption across all requests."""
    total_input: int = 0
    total_output: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_tokens(self) -> int:
        return self.total_input + self.total_output

    @property
    def avg_tokens_per_request(self) -> float:
        if self.total_requests == 0:
            return 0
        return self.total_tokens / self.total_requests

    def to_dict(self) -> dict:
        return {
            "total_input": self.total_input,
            "total_output": self.total_output,
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "avg_tokens_per_request": round(self.avg_tokens_per_request, 1),
            "uptime_hours": round((datetime.utcnow() - self.start_time).total_seconds() / 3600, 2),
        }


class MiMoClient:
    """
    Async client for MiMo V2.5 API.
    Compatible with OpenAI SDK format.
    """

    def __init__(self):
        self.api_key = os.getenv("MIMO_API_KEY")
        self.base_url = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
        self.model_pro = os.getenv("MIMO_MODEL_PRO", "mimo-v2.5-pro")
        self.model_lite = os.getenv("MIMO_MODEL_LITE", "mimo-v2.5-lite")

        if not self.api_key:
            raise ValueError("MIMO_API_KEY environment variable is required")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        self.metrics = TokenMetrics()
        logger.info(f"MiMo client initialized: {self.base_url}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def chat(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> dict:
        """
        Send chat completion request to MiMo API.
        
        Returns:
            {"content": str, "usage": {"input": int, "output": int}}
        """
        model = model or self.model_pro

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
            usage = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            }

            # Update metrics
            self.metrics.total_input += usage["input"]
            self.metrics.total_output += usage["output"]
            self.metrics.total_requests += 1

            return {"content": content, "usage": usage}

        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"MiMo API error: {e}")
            raise

    async def reason(self, system: str, prompt: str, model: Optional[str] = None) -> str:
        """Simple reasoning interface."""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        result = await self.chat(messages, model=model)
        return result["content"]

    def get_metrics(self) -> dict:
        """Return current token consumption metrics."""
        return self.metrics.to_dict()
