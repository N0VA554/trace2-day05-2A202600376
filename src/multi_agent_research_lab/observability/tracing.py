"""Tracing hooks with LangSmith and fallback to local spans."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context with LangSmith support if available."""

    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    # Try to use LangSmith if configured
    try:
        settings = get_settings()
        if settings.langsmith_api_key:
            from langsmith import trace as langsmith_trace
            with langsmith_trace(
                name=name,
                run_type="tool",
                inputs=attributes or {},
            ) as run:
                try:
                    yield span
                finally:
                    span["duration_seconds"] = perf_counter() - started
                    run.end(outputs={"duration": span["duration_seconds"]})
        else:
            # Fallback to local span
            try:
                yield span
            finally:
                span["duration_seconds"] = perf_counter() - started
    except ImportError:
        logger.debug("LangSmith not available, using local tracing")
        try:
            yield span
        finally:
            span["duration_seconds"] = perf_counter() - started
    except Exception as e:
        logger.warning(f"Tracing error: {e}")
        try:
            yield span
        finally:
            span["duration_seconds"] = perf_counter() - started
