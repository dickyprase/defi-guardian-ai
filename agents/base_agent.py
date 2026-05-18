"""
Base Agent class with MiMo API integration.
All specialized agents inherit from this class.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all DeFi Guardian agents."""

    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model or os.getenv("MIMO_MODEL_PRO", "mimo-v2.5-pro")
        self.client = AsyncOpenAI(
            api_key=os.getenv("MIMO_API_KEY"),
            base_url=os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1"),
        )
        self.token_usage = {"input": 0, "output": 0}
        self.created_at = datetime.utcnow()
        logger.info(f"Agent [{self.name}] initialized with model {self.model}")

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass

    @abstractmethod
    async def analyze(self, data: dict) -> dict:
        """Perform analysis on the given data. Must be implemented by subclasses."""
        pass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def reason(self, prompt: str, context: str = "", temperature: float = 0.1) -> str:
        """
        Send a reasoning request to MiMo API.
        Uses long-chain reasoning for complex analysis.
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
        ]

        if context:
            messages.append({"role": "user", "content": f"Context:\n{context}"})
            messages.append({"role": "assistant", "content": "Understood. I will analyze this data carefully."})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=4096,
            )

            result = response.choices[0].message.content
            self.token_usage["input"] += response.usage.prompt_tokens
            self.token_usage["output"] += response.usage.completion_tokens

            logger.info(
                f"Agent [{self.name}] reasoning complete. "
                f"Tokens: {response.usage.prompt_tokens}+{response.usage.completion_tokens}"
            )
            return result

        except Exception as e:
            logger.error(f"Agent [{self.name}] reasoning failed: {e}")
            raise

    async def structured_reason(self, prompt: str, schema: dict, context: str = "") -> dict:
        """
        Reasoning with structured JSON output.
        """
        structured_prompt = (
            f"{prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )

        result = await self.reason(structured_prompt, context)

        # Extract JSON from response
        try:
            if "```json" in result:
                json_str = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                json_str = result.split("```")[1].split("```")[0]
            else:
                json_str = result

            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Agent [{self.name}] JSON parse failed, retrying with correction")
            correction = await self.reason(
                f"Fix this invalid JSON and return ONLY valid JSON:\n{result}",
                temperature=0.0
            )
            return json.loads(correction.strip())

    def get_stats(self) -> dict:
        """Return agent statistics."""
        return {
            "name": self.name,
            "model": self.model,
            "token_usage": self.token_usage,
            "total_tokens": self.token_usage["input"] + self.token_usage["output"],
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds(),
        }
