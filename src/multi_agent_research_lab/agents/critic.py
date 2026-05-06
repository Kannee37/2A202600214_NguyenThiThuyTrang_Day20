"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        final_answer = state.final_answer or ""
        citation_count = sum(1 for source in state.sources if source.title in final_answer)
        if not state.final_answer:
            finding = "No final answer was available for review."
            state.errors.append(finding)
        elif citation_count == 0:
            finding = "Final answer needs stronger citation coverage."
            state.errors.append(finding)
        else:
            finding = f"Final answer includes {citation_count} source reference(s)."

        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=finding,
                metadata={"citation_count": citation_count},
            )
        )
        state.add_trace_event(
            "critic.review",
            {"finding": finding, "citation_count": citation_count},
        )
        return state
