"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import os
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context used by the workflow."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    with ExitStack() as stack:
        external_spans: list[Any] = []
        try:
            external_spans = _start_external_spans(stack, name, span["attributes"])
            yield span
        except Exception:
            span["status"] = "error"
            raise
        finally:
            span["duration_seconds"] = perf_counter() - started
            for external_span in external_spans:
                _update_external_span(external_span, span)


def flush_traces() -> None:
    """Flush external tracing clients for short-lived CLI commands."""

    settings = get_settings()
    providers = _selected_providers(settings.trace_provider)
    if "langfuse" in providers and settings.langfuse_public_key and settings.langfuse_secret_key:
        try:
            _configure_langfuse_environment()
            from langfuse import get_client

            get_client().flush()
        except Exception:
            return


def _selected_providers(trace_provider: str) -> set[str]:
    if trace_provider == "both":
        return {"langsmith", "langfuse"}
    return {item.strip() for item in trace_provider.split(",") if item.strip()}


def _start_external_spans(
    stack: ExitStack,
    name: str,
    attributes: dict[str, Any],
) -> list[Any]:
    settings = get_settings()
    providers = _selected_providers(settings.trace_provider)
    spans: list[Any] = []

    if "langsmith" in providers and settings.langsmith_api_key:
        try:
            _configure_langsmith_environment()
            from langsmith.run_helpers import trace

            run = stack.enter_context(
                trace(
                    name,
                    run_type="chain",
                    inputs=attributes,
                    project_name=settings.langsmith_project,
                    metadata={"source": "multi-agent-research-lab"},
                )
            )
            spans.append(run)
        except Exception:
            pass

    if "langfuse" in providers and settings.langfuse_public_key and settings.langfuse_secret_key:
        try:
            _configure_langfuse_environment()
            from langfuse import get_client

            client = get_client()
            if hasattr(client, "start_as_current_observation"):
                observation = stack.enter_context(
                    client.start_as_current_observation(
                        as_type="span",
                        name=name,
                        input=attributes,
                    )
                )
            else:
                observation = stack.enter_context(
                    client.start_as_current_span(name=name, input=attributes)
                )
            client.update_current_trace(
                name=name,
                input=attributes,
                metadata={"source": "multi-agent-research-lab"},
            )
            spans.append(observation)
        except Exception:
            pass

    return spans


def _update_external_span(external_span: Any, span: dict[str, Any]) -> None:
    try:
        if hasattr(external_span, "update"):
            external_span.update(output=span)
        elif hasattr(external_span, "end"):
            external_span.end(outputs=span)
    except Exception:
        pass
    try:
        settings = get_settings()
        providers = _selected_providers(settings.trace_provider)
        has_langfuse_keys = settings.langfuse_public_key and settings.langfuse_secret_key
        if "langfuse" in providers and has_langfuse_keys:
            _configure_langfuse_environment()
            from langfuse import get_client

            get_client().update_current_trace(output=span)
    except Exception:
        pass


def _configure_langfuse_environment() -> None:
    settings = get_settings()
    base_url = settings.langfuse_base_url or settings.langfuse_host
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key or "")
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key or "")
    os.environ.setdefault("LANGFUSE_BASE_URL", base_url)


def _configure_langsmith_environment() -> None:
    settings = get_settings()
    os.environ.setdefault("LANGSMITH_API_KEY", settings.langsmith_api_key or "")
    os.environ.setdefault("LANGSMITH_PROJECT", settings.langsmith_project)
    os.environ.setdefault("LANGSMITH_TRACING", "true")
