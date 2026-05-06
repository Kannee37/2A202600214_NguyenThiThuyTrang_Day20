"""Application configuration.

Keep config small and explicit. Do not read environment variables directly in agents.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")

    llm_provider: str = Field(default="mock", validation_alias="LLM_PROVIDER")
    llama_cpp_model_path: str | None = Field(default=None, validation_alias="LLAMA_CPP_MODEL_PATH")
    llama_cpp_n_ctx: int = Field(default=4096, ge=512, validation_alias="LLAMA_CPP_N_CTX")
    llama_cpp_n_threads: int | None = Field(default=None, validation_alias="LLAMA_CPP_N_THREADS")
    llama_cpp_max_tokens: int = Field(default=512, ge=1, validation_alias="LLAMA_CPP_MAX_TOKENS")
    llama_server_url: str = Field(
        default="http://127.0.0.1:8080",
        validation_alias="LLAMA_SERVER_URL",
    )
    llama_server_model: str = Field(default="local-gguf", validation_alias="LLAMA_SERVER_MODEL")

    langsmith_api_key: str | None = Field(default=None, validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(
        default="multi-agent-research-lab",
        validation_alias="LANGSMITH_PROJECT",
    )

    trace_provider: str = Field(default="local", validation_alias="TRACE_PROVIDER")
    langfuse_public_key: str | None = Field(default=None, validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias="LANGFUSE_HOST",
    )
    langfuse_base_url: str | None = Field(default=None, validation_alias="LANGFUSE_BASE_URL")

    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")

    max_iterations: int = Field(default=6, ge=1, le=20, validation_alias="MAX_ITERATIONS")
    timeout_seconds: int = Field(default=60, ge=5, le=600, validation_alias="TIMEOUT_SECONDS")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
