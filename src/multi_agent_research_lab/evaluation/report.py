"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


def render_markdown_report(
    metrics: list[BenchmarkMetrics],
    states: dict[str, ResearchState] | None = None,
) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "This report compares runs by latency, estimated cost, quality, and operational notes.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | "
            f"{cost} | {quality} | {item.notes} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Use the baseline to check whether a single model call is already sufficient.",
            "- Use the multi-agent run when source gathering, analysis, and "
            "writing need separate accountability.",
            "- Review trace events for route decisions, agent outputs, failures, "
            "and stop conditions.",
        ]
    )
    if states:
        lines.extend(["", "## Answers"])
        for item in metrics:
            state = states.get(item.run_name)
            if state is None:
                continue
            answer = state.final_answer or "No final answer was produced."
            lines.extend(["", f"### {item.run_name}", "", answer])
    return "\n".join(lines) + "\n"
