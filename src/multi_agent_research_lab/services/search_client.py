"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client with a deterministic local fallback."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Return documents relevant to a query.

        The default implementation is a local mock, which keeps the lab runnable
        offline. It preserves the same return schema a real Tavily/Bing/SerpAPI
        adapter would use.
        """

        clean_query = " ".join(query.split())
        library = [
            SourceDocument(
                title="Anthropic: Building Effective Agents",
                url="https://www.anthropic.com/engineering/building-effective-agents",
                snippet=(
                    "Effective agent systems benefit from simple composable workflows, "
                    "clear tool boundaries, and evaluation before adding complexity."
                ),
                metadata={"source_type": "reference", "rank": 1},
            ),
            SourceDocument(
                title="OpenAI Agents SDK: Orchestration and Handoffs",
                url="https://developers.openai.com/api/docs/guides/agents/orchestration",
                snippet=(
                    "Agent orchestration should define when tasks are handed off, what "
                    "context moves between agents, and how guardrails constrain behavior."
                ),
                metadata={"source_type": "reference", "rank": 2},
            ),
            SourceDocument(
                title="LangGraph Concepts",
                url="https://langchain-ai.github.io/langgraph/concepts/",
                snippet=(
                    "Graph-based agent workflows model state, nodes, conditional edges, "
                    "and stop conditions for controllable multi-step execution."
                ),
                metadata={"source_type": "reference", "rank": 3},
            ),
            SourceDocument(
                title="Lab Design Note",
                url=None,
                snippet=(
                    f"For the query '{clean_query}', compare a single-agent baseline "
                    "with a supervisor-led workflow using latency, cost, quality, "
                    "citation coverage, and failure rate."
                ),
                metadata={"source_type": "local_mock", "rank": 4},
            ),
        ]
        return library[:max_results]
