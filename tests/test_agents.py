from multi_agent_research_lab.agents import (
    AnalystAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow


def test_supervisor_routes_to_missing_step() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = SupervisorAgent().run(state)
    assert result.route_history == ["researcher"]


def test_worker_agents_populate_state() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    state = ResearcherAgent().run(state)
    state = AnalystAgent().run(state)
    state = WriterAgent().run(state)
    assert state.sources
    assert state.research_notes
    assert state.analysis_notes
    assert state.final_answer


def test_workflow_runs_end_to_end() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = MultiAgentWorkflow().run(state)
    assert result.route_history[-1] == "done"
    assert result.final_answer
