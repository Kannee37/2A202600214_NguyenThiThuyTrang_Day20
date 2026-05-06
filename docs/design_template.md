# Design Template

## Problem

Build a research assistant that accepts a query, gathers source-backed notes,
analyzes the evidence, and writes a final answer with citations.

## Why multi-agent?

A single-agent baseline is useful for comparison, but it mixes searching,
analysis, and writing in one step. The multi-agent workflow separates those
responsibilities so the trace shows who did what, what evidence was used, and
where failures happened.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Route to the next worker or stop | Shared state | Route history and trace event | Wrong route or max-iteration stop |
| Researcher | Collect source documents and concise notes | Query and max source count | Sources and research notes | Empty or weak sources |
| Analyst | Extract claims, evidence strength, and risks | Research notes and sources | Analysis notes | Missing research context |
| Writer | Produce final answer with source references | Research and analysis notes | Final answer | Weak citation coverage |

## Shared state

- `request`: original query, audience, and source limit.
- `iteration`: guardrail against infinite routing loops.
- `route_history`: debuggable sequence of supervisor decisions.
- `sources`: documents gathered by the researcher.
- `research_notes`, `analysis_notes`, `final_answer`: handoff artifacts.
- `agent_results`: structured output from each agent.
- `trace`: timing and decision events for review.
- `errors`: recoverable failures and validation warnings.

## Routing policy

Supervisor routes to Researcher when research notes are missing, Analyst when
analysis notes are missing, Writer when the final answer is missing, and `done`
when all required outputs exist or the iteration limit is reached.

## Guardrails

- Max iterations: configured by `MAX_ITERATIONS`, default 6.
- Timeout: configured by `TIMEOUT_SECONDS`, available for provider adapters.
- Retry: provider-specific retries belong in service clients.
- Fallback: local LLM/search mocks keep the lab runnable without API keys.
- Validation: Pydantic schemas validate user query, metrics, and source shape.

## Benchmark plan

- Query: "Research GraphRAG state-of-the-art and write a 500-word summary".
- Metrics: latency, estimated cost, quality score, citation coverage, and error count.
- Expected outcome: the multi-agent run should have clearer traceability and
  citation coverage than the baseline, with some extra orchestration latency.
