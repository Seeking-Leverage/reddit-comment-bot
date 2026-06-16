import logging
from dataclasses import dataclass
from typing import Optional

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from bot.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    base_url: Optional[str]


class LLMClient:
    """
    OpenAI-compatible chat client.

    Works with OpenAI, OpenRouter, Azure OpenAI, Groq, LiteLLM, etc.
    Set LLM_BASE_URL + LLM_API_KEY + LLM_MODEL in .env per provider docs.
    """

    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise ValueError(
                "LLM_API_KEY is not set. Add it to .env (OPENAI_API_KEY also accepted)."
            )

        client_kwargs = {
            "api_key": settings.llm_api_key,
            "timeout": settings.llm_timeout_seconds,
            "max_retries": 0,
        }
        base_url = settings.llm_base_url_or_none
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = OpenAI(**client_kwargs)
        self._model = settings.llm_model
        self._base_url = base_url

    def complete(self, *, system: str, user: str) -> LLMResponse:
        text = self._call_with_retry(system=system, user=user)
        return LLMResponse(text=text, model=self._model, base_url=self._base_url)

    @retry(
        retry=retry_if_exception_type(
            (APIConnectionError, RateLimitError, APIStatusError)
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        reraise=True,
    )
    def _call_with_retry(self, *, system: str, user: str) -> str:
        logger.debug("LLM request model=%s base_url=%s", self._model, self._base_url)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
        return (response.choices[0].message.content or "").strip()