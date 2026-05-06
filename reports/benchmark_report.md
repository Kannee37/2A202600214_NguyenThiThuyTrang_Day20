# Benchmark Report

This report compares runs by latency, estimated cost, quality, and operational notes.

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| baseline | 29.77 | 0.0000 | 4.0 | words=98; sources=0; citation_coverage=0%; errors=0 |
| multi-agent | 0.01 | 0.0001 | 10.0 | words=210; sources=4; citation_coverage=100%; errors=0 |

## Interpretation

- Use the baseline to check whether a single model call is already sufficient.
- Use the multi-agent run when source gathering, analysis, and writing need separate accountability.
- Review trace events for route decisions, agent outputs, failures, and stop conditions.

## Answers

### baseline

GraphRAG is a state-of-the-art model for graph-based tasks. It is a variant of the RAG (Recurrent Architectural Graph) model, which is a type of transformer-based model that is designed to handle graph-based data. GraphRAG is particularly well-suited for tasks that involve reasoning over graphs, such as link prediction, node classification, and graph generation.
One of the key advantages of GraphRAG is its ability to handle large graphs efficiently. The model is designed to be memory-efficient, which means that it can handle graphs with millions of nodes and edges without running out of memory. This is achieved through the

### multi-agent

Query: Research GraphRAG state-of-the-art and write a 500-word summary

Summary:
A reliable research assistant should start with a simple single-agent baseline, then use a multi-agent workflow when the problem benefits from separated roles. In this implementation, the Supervisor chooses the next step, the Researcher collects source-backed notes, the Analyst extracts claims and risks, and the Writer produces the final response with citations.

Key takeaways:
1. Role clarity reduces overlap and makes debugging easier.
2. Shared state preserves handoff context across agents.
3. Guardrails such as max iterations and explicit stop conditions prevent loops.
4. Benchmarking is required because multi-agent quality gains can come with higher latency and coordination cost.

Analysis notes:
- Claim 1: Use multi-agent workflows when the task naturally separates into search, analysis, and synthesis.
- Claim 2: Keep the shared state explicit so every handoff is debuggable.
- Claim 3: Add guardrails such as max iterations, validation, and fallback behavior.
- Claim 4: Benchmark against a single-agent baseline because extra agents add latency and coordination cost.
- Evidence strength: 4 source(s) available; claims should cite sources in the final answer.

Sources:
- [1] Anthropic: Building Effective Agents (https://www.anthropic.com/engineering/building-effective-agents)
- [2] OpenAI Agents SDK: Orchestration and Handoffs (https://developers.openai.com/api/docs/guides/agents/orchestration)
- [3] LangGraph Concepts (https://langchain-ai.github.io/langgraph/concepts/)
- [4] Lab Design Note
