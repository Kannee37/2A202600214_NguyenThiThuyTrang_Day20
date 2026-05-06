"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str,
    query: str,
    runner: Runner,
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and derive lightweight benchmark metrics."""

    started = perf_counter()
    try:
        state = runner(query)
    except Exception as exc:
        state = ResearchState(request=ResearchQuery(query=query))
        state.errors.append(f"{run_name} failed: {type(exc).__name__}: {exc}")
        state.final_answer = ""
    latency = perf_counter() - started
    final_answer = state.final_answer or ""
    word_count = len(final_answer.split())
    citation_hits = sum(1 for source in state.sources if source.title in final_answer)
    citation_coverage = citation_hits / max(1, len(state.sources))
    quality_score = min(
        10.0,
        4.0
        + (2.0 if state.research_notes else 0.0)
        + (2.0 if state.analysis_notes else 0.0)
        + (2.0 * citation_coverage),
    )
    estimated_cost = round(word_count * 0.0000005, 6)
    notes = (
        f"words={word_count}; sources={len(state.sources)}; "
        f"citation_coverage={citation_coverage:.0%}; errors={len(state.errors)}"
    )
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=estimated_cost,
        quality_score=quality_score,
        notes=notes,
    )
    return state, metrics
