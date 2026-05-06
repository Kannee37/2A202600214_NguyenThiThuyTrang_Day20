"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        citations = []
        for index, source in enumerate(state.sources, start=1):
            label = f"[{index}] {source.title}"
            if source.url:
                label = f"{label} ({source.url})"
            citations.append(label)

        citation_text = "\n".join(f"- {item}" for item in citations) or "- No sources available."
        state.final_answer = (
            f"Query: {state.request.query}\n\n"
            "Summary:\n"
            "A reliable research assistant should start with a simple single-agent baseline, "
            "then use a multi-agent workflow when the problem benefits from separated roles. "
            "In this implementation, the Supervisor chooses the next step, the Researcher "
            "collects source-backed notes, the Analyst extracts claims and risks, and the "
            "Writer produces the final response with citations.\n\n"
            "Key takeaways:\n"
            "1. Role clarity reduces overlap and makes debugging easier.\n"
            "2. Shared state preserves handoff context across agents.\n"
            "3. Guardrails such as max iterations and explicit stop conditions prevent loops.\n"
            "4. Benchmarking is required because multi-agent quality gains can come with "
            "higher latency and coordination cost.\n\n"
            f"Analysis notes:\n{state.analysis_notes or 'No analysis notes were produced.'}\n\n"
            f"Sources:\n{citation_text}"
        )
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=state.final_answer,
                metadata={"citation_count": len(citations)},
            )
        )
        state.add_trace_event(
            "writer.compose",
            {"citation_count": len(citations), "answer_length": len(state.final_answer)},
        )
        return state
