"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import logging
from dataclasses import dataclass

from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client with OpenAI support."""

    # Token costs for GPT-4o-mini (as of 2024)
    COSTS_PER_MILLION = {
        "input": 0.15,
        "output": 0.60,
    }

    def __init__(self) -> None:
        self.settings = get_settings()
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "OpenAI SDK is not installed. Install optional deps with: pip install -e '.[llm]'"
            ) from e

        if not self.settings.openai_api_key:
            raise ValueError(
                "Missing OPENAI_API_KEY. Set it in your environment or `.env` to use LLMClient."
            )
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.model = self.settings.openai_model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion with retry logic and cost estimation."""
        
        logger.debug(
            f"Requesting completion from {self.model}",
            extra={"system_len": len(system_prompt), "user_len": len(user_prompt)},
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=2048,
            temperature=0.7,
        )
        
        # Extract token counts
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        
        # Estimate cost
        if input_tokens is not None and output_tokens is not None:
            cost_usd = (
                (input_tokens / 1_000_000) * self.COSTS_PER_MILLION["input"]
                + (output_tokens / 1_000_000) * self.COSTS_PER_MILLION["output"]
            )
        else:
            cost_usd = None
        
        content = (response.choices[0].message.content or "").strip()
        
        logger.info(
            f"Completion received",
            extra={
                "model": self.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
            },
        )
        
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )
