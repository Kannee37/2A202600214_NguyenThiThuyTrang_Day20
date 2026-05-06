"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import LabError
from multi_agent_research_lab.observability.tracing import trace_span


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client.

    The lab implementation defaults to a deterministic mock so the workflow can
    run without API keys. Set `LLM_PROVIDER=llama_server` to call a running
    llama.cpp server through its OpenAI-compatible HTTP endpoint.
    """

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a completion-like response with lightweight token accounting."""

        settings = get_settings()
        with trace_span(
            "llm.complete",
            {"provider": settings.llm_provider, "model": _model_name_for_trace()},
        ) as span:
            if settings.llm_provider == "llama_server":
                response = self._complete_with_llama_server(system_prompt, user_prompt)
            elif settings.llm_provider == "llama_cpp":
                response = self._complete_with_llama_cpp(system_prompt, user_prompt)
            elif settings.llm_provider == "mock":
                response = self._complete_with_mock(system_prompt, user_prompt)
            else:
                raise LabError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
            span["output_tokens"] = response.output_tokens
            span["input_tokens"] = response.input_tokens
            return response

    def _complete_with_mock(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a deterministic response for tests and offline demos."""

        system_words = system_prompt.split()
        user_words = user_prompt.split()
        summary = " ".join(user_words[:80])
        content = f"{system_prompt.strip()}\n\n{summary}".strip()
        output_tokens = max(1, len(content.split()))
        input_tokens = len(system_words) + len(user_words)
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=round((input_tokens + output_tokens) * 0.0000005, 6),
        )

    def _complete_with_llama_cpp(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Run a local GGUF model through llama-cpp-python."""

        settings = get_settings()
        if not settings.llama_cpp_model_path:
            raise LabError("LLAMA_CPP_MODEL_PATH must be set when LLM_PROVIDER=llama_cpp")

        model_path = Path(settings.llama_cpp_model_path)
        if not model_path.exists():
            raise LabError(f"Local GGUF model not found: {model_path}")

        llm = _load_llama_cpp_model(str(model_path))
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
            f"{system_prompt.strip()}<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n"
            f"{user_prompt.strip()}<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n"
        )
        result = llm(
            prompt,
            max_tokens=settings.llama_cpp_max_tokens,
            temperature=0.2,
            top_p=0.9,
            stop=["<|eot_id|>"],
        )
        content = str(result["choices"][0]["text"]).strip()
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        return LLMResponse(
            content=content,
            input_tokens=input_tokens if isinstance(input_tokens, int) else None,
            output_tokens=output_tokens if isinstance(output_tokens, int) else None,
            cost_usd=0.0,
        )

    def _complete_with_llama_server(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Run a completion through a running llama.cpp HTTP server."""

        settings = get_settings()
        endpoint = settings.llama_server_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": settings.llama_server_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": settings.llama_cpp_max_tokens,
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=settings.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except (TimeoutError, URLError) as exc:
            raise LabError(
                f"Could not reach llama-server at {settings.llama_server_url}. "
                "Start llama-server first, reduce LLAMA_CPP_MAX_TOKENS, increase "
                "TIMEOUT_SECONDS, or set LLM_PROVIDER=mock."
            ) from exc

        data: dict[str, Any] = json.loads(raw)
        message = data["choices"][0]["message"]
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        return LLMResponse(
            content=str(message.get("content", "")).strip(),
            input_tokens=input_tokens if isinstance(input_tokens, int) else None,
            output_tokens=output_tokens if isinstance(output_tokens, int) else None,
            cost_usd=0.0,
        )


@lru_cache(maxsize=1)
def _load_llama_cpp_model(model_path: str) -> object:
    settings = get_settings()
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise LabError(
            "llama-cpp-python is required for LLM_PROVIDER=llama_cpp. "
            "Install it in the active environment first."
        ) from exc

    kwargs: dict[str, object] = {
        "model_path": model_path,
        "n_ctx": settings.llama_cpp_n_ctx,
        "verbose": False,
    }
    if settings.llama_cpp_n_threads is not None:
        kwargs["n_threads"] = settings.llama_cpp_n_threads
    return Llama(**kwargs)


def _model_name_for_trace() -> str:
    settings = get_settings()
    if settings.llm_provider == "llama_server":
        return settings.llama_server_model
    if settings.llm_provider == "llama_cpp":
        return settings.llama_cpp_model_path or "local-gguf"
    return "mock"
