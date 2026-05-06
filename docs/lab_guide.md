# Lab Guide: Multi-Agent Research System

## Scenario

Build a research assistant that accepts a long question, gathers information,
analyzes the evidence, and writes a final answer. The lab compares two modes:

1. **Single-agent baseline**: one agent does the whole task.
2. **Multi-agent workflow**: Supervisor coordinates Researcher, Analyst, and Writer.

## Important Rules

- Do not add agents without a clear reason.
- Each agent must have a separate responsibility.
- Shared state must be explicit enough for debugging.
- Every major step should produce a trace or log event.
- Benchmark the system instead of judging only by a pretty output.

## Milestone 1: Baseline

Files:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

Implemented: baseline uses `LLMClient`, returns a deterministic local response,
and records token/cost metadata in the trace.

## Milestone 2: Supervisor

Files:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

Implemented: the supervisor routes to Researcher, Analyst, Writer, then `done`.
It also enforces `MAX_ITERATIONS` and records the route reason in state.

## Milestone 3: Worker agents

Files:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

Implemented: each worker updates shared state, appends an `AgentResult`, and
records trace events.

## Milestone 4: Trace and benchmark

Files:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark metrics:

| Metric | Suggested Measurement |
|---|---|
| Latency | Wall-clock time |
| Cost | Estimated token/output cost |
| Quality | Heuristic 0-10 score |
| Citation coverage | Source references used / total sources |
| Failure rate | Error count per run |

## Exit Ticket

1. Use multi-agent workflows when the task benefits from separated roles,
   auditable handoffs, and source-backed synthesis.
2. Avoid multi-agent workflows when the task is simple, latency-sensitive, or
   does not need separate search, analysis, and writing steps.
