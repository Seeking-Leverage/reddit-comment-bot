from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Provider-neutral LLM config (preferred)
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = ""
    llm_max_tokens: int = 180
    llm_temperature: float = 0.8
    llm_timeout_seconds: float = 30.0

    # Legacy env names — still accepted, overridden by LLM_* when both are set
    openai_api_key: str = ""
    openai_model: str = ""
    openai_max_tokens: int = 0
    openai_temperature: float = 0.0
    openai_timeout_seconds: float = 0.0

    bot_config_dir: Path = Path("config/clients")
    bot_data_dir: Path = Path("data")

    max_post_chars: int = 1200
    max_parent_comment_chars: int = 500

    @model_validator(mode="after")
    def merge_legacy_openai_env(self) -> "Settings":
        """Support OPENAI_* env vars from older clones without breaking."""
        if not self.llm_api_key and self.openai_api_key:
            object.__setattr__(self, "llm_api_key", self.openai_api_key)
        if self.openai_model:
            object.__setattr__(self, "llm_model", self.openai_model)
        if self.openai_max_tokens:
            object.__setattr__(self, "llm_max_tokens", self.openai_max_tokens)
        if self.openai_temperature:
            object.__setattr__(self, "llm_temperature", self.openai_temperature)
        if self.openai_timeout_seconds:
            object.__setattr__(self, "llm_timeout_seconds", self.openai_timeout_seconds)
        return self

    @property
    def database_path(self) -> Path:
        self.bot_data_dir.mkdir(parents=True, exist_ok=True)
        return self.bot_data_dir / "bot.db"

    @property
    def llm_base_url_or_none(self) -> Optional[str]:
        return self.llm_base_url.strip() or None


settings = Settings()