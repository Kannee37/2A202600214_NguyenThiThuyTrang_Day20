"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        source_count = len(state.sources)
        if not state.research_notes:
            state.errors.append("Analyst ran before research notes were available.")
            state.analysis_notes = "No research notes were available for analysis."
        else:
            claims = [
                "Use multi-agent workflows when the task naturally separates into search, "
                "analysis, and synthesis.",
                "Keep the shared state explicit so every handoff is debuggable.",
                "Add guardrails such as max iterations, validation, and fallback behavior.",
                "Benchmark against a single-agent baseline because extra agents add latency "
                "and coordination cost.",
            ]
            evidence = (
                f"Evidence strength: {source_count} source(s) available; "
                "claims should cite sources in the final answer."
            )
            state.analysis_notes = "\n".join(
                [f"- Claim {index}: {claim}" for index, claim in enumerate(claims, start=1)]
                + [f"- {evidence}"]
            )

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=state.analysis_notes,
                metadata={"source_count": source_count, "error_count": len(state.errors)},
            )
        )
        state.add_trace_event(
            "analyst.summarize",
            {"source_count": source_count, "has_research_notes": bool(state.research_notes)},
        )
        return state
