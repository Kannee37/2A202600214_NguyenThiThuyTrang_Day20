"""LangGraph workflow skeleton."""

from dataclasses import dataclass

from multi_agent_research_lab.agents import (
    AnalystAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


@dataclass(frozen=True)
class WorkflowGraph:
    """Small graph description used by the local runner."""

    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    terminal: str = "done"


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(
        self,
        supervisor: SupervisorAgent | None = None,
        researcher: ResearcherAgent | None = None,
        analyst: AnalystAgent | None = None,
        writer: WriterAgent | None = None,
    ) -> None:
        self.supervisor = supervisor or SupervisorAgent()
        self.workers: dict[str, BaseAgent] = {
            "researcher": researcher or ResearcherAgent(),
            "analyst": analyst or AnalystAgent(),
            "writer": writer or WriterAgent(),
        }

    def build(self) -> object:
        """Create the graph description for the local workflow runner."""

        return WorkflowGraph(
            nodes=("supervisor", "researcher", "analyst", "writer", "done"),
            edges=(
                ("supervisor", "researcher"),
                ("supervisor", "analyst"),
                ("supervisor", "writer"),
                ("supervisor", "done"),
                ("researcher", "supervisor"),
                ("analyst", "supervisor"),
                ("writer", "supervisor"),
            ),
        )

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        settings = get_settings()
        self.build()

        while state.iteration < settings.max_iterations:
            with trace_span("workflow.supervisor", {"iteration": state.iteration}) as span:
                state = self.supervisor.run(state)
            state.add_trace_event("span.workflow.supervisor", span)

            route = state.route_history[-1]
            if route == "done":
                break

            worker = self.workers.get(route)
            if worker is None:
                message = f"Unknown workflow route: {route}"
                state.errors.append(message)
                raise AgentExecutionError(message)

            try:
                with trace_span(f"workflow.{route}", {"iteration": state.iteration}) as span:
                    state = worker.run(state)
                state.add_trace_event(f"span.workflow.{route}", span)
            except Exception as exc:
                message = f"{route} failed: {exc}"
                state.errors.append(message)
                raise AgentExecutionError(message) from exc

        if state.route_history[-1:] != ["done"]:
            state.add_trace_event(
                "workflow.stop",
                {"reason": "max_iterations reached", "iteration": state.iteration},
            )
        return state
