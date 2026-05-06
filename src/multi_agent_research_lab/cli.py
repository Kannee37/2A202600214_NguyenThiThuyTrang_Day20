"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.tracing import flush_traces, trace_span
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.storage import LocalArtifactStore

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline."""

    _init()
    with trace_span("cli.baseline", {"query": query}) as span:
        request = ResearchQuery(query=query)
        state = ResearchState(request=request)
        response = LLMClient().complete(
            "Single-agent baseline response.",
            (
                "Answer the research query directly and mention that this baseline does "
                f"not separate search, analysis, and writing roles. Query: {query}"
            ),
        )
        state.final_answer = response.content
        state.add_trace_event(
            "baseline.complete",
            {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            },
        )
        span["final_answer_length"] = len(state.final_answer)
        console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
    flush_traces()


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    with trace_span("cli.multi_agent", {"query": query}) as span:
        state = ResearchState(request=ResearchQuery(query=query))
        workflow = MultiAgentWorkflow()
        try:
            result = workflow.run(state)
        except StudentTodoError as exc:
            console.print(Panel.fit(str(exc), title="Implementation Error", style="yellow"))
            raise typer.Exit(code=2) from exc
        span["route_history"] = result.route_history
        span["error_count"] = len(result.errors)
        console.print(result.model_dump_json(indent=2))
    flush_traces()


@app.command("benchmark")
def benchmark(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run baseline and multi-agent benchmarks, then write a markdown report."""

    _init()
    with trace_span("cli.benchmark", {"query": query}) as span:

        def baseline_runner(inner_query: str) -> ResearchState:
            state = ResearchState(request=ResearchQuery(query=inner_query))
            response = LLMClient().complete("Single-agent baseline response.", inner_query)
            state.final_answer = response.content
            return state

        def multi_agent_runner(inner_query: str) -> ResearchState:
            return MultiAgentWorkflow().run(ResearchState(request=ResearchQuery(query=inner_query)))

        baseline_state, baseline_metrics = run_benchmark("baseline", query, baseline_runner)
        multi_state, multi_metrics = run_benchmark("multi-agent", query, multi_agent_runner)
        report = render_markdown_report(
            [baseline_metrics, multi_metrics],
            {"baseline": baseline_state, "multi-agent": multi_state},
        )
        path = LocalArtifactStore().write_text("benchmark_report.md", report)
        span["baseline"] = baseline_metrics.model_dump()
        span["multi_agent"] = multi_metrics.model_dump()
        console.print(Panel.fit(report, title=f"Wrote {path}"))
    flush_traces()


if __name__ == "__main__":
    app()
