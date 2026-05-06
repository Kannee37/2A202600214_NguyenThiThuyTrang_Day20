"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""

        settings = get_settings()
        if state.iteration >= settings.max_iterations:
            route = "done"
            reason = "max_iterations reached"
        elif not state.research_notes:
            route = AgentName.RESEARCHER.value
            reason = "research notes are missing"
        elif not state.analysis_notes:
            route = AgentName.ANALYST.value
            reason = "analysis notes are missing"
        elif not state.final_answer:
            route = AgentName.WRITER.value
            reason = "final answer is missing"
        else:
            route = "done"
            reason = "all required outputs are present"

        state.record_route(route)
        state.agent_results.append(
            AgentResult(
                agent=AgentName.SUPERVISOR,
                content=f"Route to {route}: {reason}.",
                metadata={"route": route, "reason": reason, "iteration": state.iteration},
            )
        )
        state.add_trace_event(
            "supervisor.route",
            {"route": route, "reason": reason, "iteration": state.iteration},
        )
        return state
