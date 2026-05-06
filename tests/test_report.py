from multi_agent_research_lab.core.schemas import BenchmarkMetrics, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.report import render_markdown_report


def test_report_renders_markdown() -> None:
    report = render_markdown_report([BenchmarkMetrics(run_name="baseline", latency_seconds=1.23)])
    assert "Benchmark Report" in report
    assert "baseline" in report


def test_report_can_include_answers() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    state.final_answer = "Final baseline answer."
    report = render_markdown_report(
        [BenchmarkMetrics(run_name="baseline", latency_seconds=1.23)],
        {"baseline": state},
    )
    assert "## Answers" in report
    assert "Final baseline answer." in report
