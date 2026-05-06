# Lab 20: Multi-Agent Research System

Dự án này xây dựng một research assistant gồm **Supervisor + Researcher + Analyst + Writer** và so sánh với **single-agent baseline**. Hệ thống có CLI để chạy baseline, multi-agent workflow, benchmark report và trace lên Langfuse.

## Kiến trúc

```text
User Query
   |
   v
Supervisor / Router
   |------> Researcher Agent  -> research_notes
   |------> Analyst Agent     -> analysis_notes
   |------> Writer Agent      -> final_answer
   |
   v
Trace + Benchmark Report
```

## Cấu trúc dự án

```text
src/multi_agent_research_lab/
  agents/          # Supervisor, Researcher, Analyst, Writer, Critic
  core/            # Config, schemas, shared state, errors
  graph/           # MultiAgentWorkflow orchestration
  services/        # LLM client, search client, storage
  evaluation/      # Benchmark và markdown report
  observability/   # Trace span + Langfuse/LangSmith adapter
  cli.py           # CLI entrypoint

configs/           # Config mẫu
docs/              # Lab guide, rubric, design note
reports/           # benchmark_report.md
tests/             # Unit tests
```

## Yêu cầu môi trường

- Python 3.11+
- PowerShell trên Windows
- Nếu dùng local LLM: `llama-server.exe` từ `llama.cpp`
- Nếu dùng trace online: Langfuse API keys

## Cài đặt

Đi vào thư mục project:

```powershell
cd D:\mine\VinAI\day020_060526\2A202600214_NguyenThiThuyTrang_Day20
```

Nếu dùng virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

### Cài đặt thư viện

```powershell
python -m pip install -e ".[llm,dev]"
```

Nếu cần dùng Langfuse/LangSmith để xem trace online, cài thêm nhóm observability:

```powershell
python -m pip install -e ".[llm,dev,observability]"
```

Set `PYTHONPATH` để Python import code trong thư mục `src/`:

```powershell
$env:PYTHONPATH='src'
```

Kiểm tra test:

```powershell
$env:TRACE_PROVIDER='local'
python -m pytest tests -q
```

Kết quả mong đợi:

```text
[100%]
```

## Cấu hình `.env`

File `.env` điều khiển LLM, tracing và runtime.

### Chạy nhanh không dùng LLM thật

```env
LLM_PROVIDER=mock
TRACE_PROVIDER=local
```

### Dùng local LLM qua llama-server

```env
LLM_PROVIDER=llama_server
LLAMA_SERVER_URL=http://127.0.0.1:8080
LLAMA_SERVER_MODEL=local-gguf
LLAMA_CPP_MAX_TOKENS=128
TIMEOUT_SECONDS=240
```

Start `llama-server` ở một PowerShell riêng:

```powershell
D:\mine\VinAI\llama\llama.cpp\build\bin\Debug\llama-server.exe `
  -m D:\mine\VinAI\llama\llama.cpp\models\qwen2.5-1.5b-instruct-q4_k_m.gguf `
  --host 127.0.0.1 `
  --port 8080 `
  -c 2048
```

Kiểm tra server:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health
```

### Dùng Langfuse trace

```env
TRACE_PROVIDER=langfuse
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

Nếu project Langfuse ở region default/EU, dùng:

```env
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Kiểm tra Langfuse auth:

```powershell
@'
from dotenv import load_dotenv
load_dotenv(".env")

from langfuse import get_client

lf = get_client()
print("Langfuse auth:", lf.auth_check())
'@ | python -
```

## Cách chạy

### 1. Chạy single-agent baseline

```powershell
$env:PYTHONPATH='src'
$env:TRACE_PROVIDER='langfuse'
python -m multi_agent_research_lab.cli baseline --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Baseline gọi LLM trực tiếp và không tách riêng bước search, analysis, writing.

### 2. Chạy multi-agent workflow

```powershell
$env:PYTHONPATH='src'
$env:TRACE_PROVIDER='langfuse'
python -m multi_agent_research_lab.cli multi-agent --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Workflow sẽ chạy:

```text
Supervisor -> Researcher -> Supervisor -> Analyst -> Supervisor -> Writer -> Supervisor -> done
```

Output JSON có các field quan trọng:

- `route_history`
- `sources`
- `research_notes`
- `analysis_notes`
- `final_answer`
- `trace`
- `errors`

### 3. Chạy benchmark

```powershell
$env:PYTHONPATH='src'
$env:TRACE_PROVIDER='langfuse'
$env:LLM_PROVIDER='llama_server'
$env:LLAMA_CPP_MAX_TOKENS='128'
$env:TIMEOUT_SECONDS='240'

python -m multi_agent_research_lab.cli benchmark --query "Research GraphRAG state-of-the-art and write a 500-word summary"
```

Lệnh benchmark tự động chạy:

```text
1. baseline
2. multi-agent
3. tính metric
4. ghi reports/benchmark_report.md
5. đẩy trace lên Langfuse nếu TRACE_PROVIDER=langfuse
```

Report gồm bảng metric và đáp án cuối của từng run:

```text
reports/benchmark_report.md
```

## Xem trace trong Langfuse

Sau khi chạy lệnh với `TRACE_PROVIDER=langfuse`, vào Langfuse và tìm trace:

- `cli.baseline`
- `cli.multi_agent`
- `cli.benchmark`

Waterfall mong đợi cho multi-agent:

```text
cli.multi_agent
  workflow.supervisor
  workflow.researcher
  workflow.supervisor
  workflow.analyst
  workflow.writer
  workflow.supervisor
```

Screenshot waterfall này có thể dùng cho deliverable "Screenshot trace hoặc link trace".

## Guardrails hiện có

- `MAX_ITERATIONS`: chặn workflow lặp vô hạn.
- `TIMEOUT_SECONDS`: timeout khi gọi `llama-server`.
- Pydantic schemas: validate query, source, agent result và metrics.
- `errors`: ghi lỗi vào shared state.
- Benchmark không crash toàn bộ nếu một runner fail.
- Trace span cho từng bước workflow.

## Troubleshooting

Nếu Python không import được package:

```powershell
$env:PYTHONPATH='src'
```

Nếu `llama-server` timeout:

```powershell
$env:LLAMA_CPP_MAX_TOKENS='64'
$env:TIMEOUT_SECONDS='300'
```

Nếu chỉ muốn test nhanh, không đẩy trace:

```powershell
$env:TRACE_PROVIDER='local'
python -m pytest tests -q
```

Nếu Langfuse 401:

- Kiểm tra `LANGFUSE_PUBLIC_KEY` và `LANGFUSE_SECRET_KEY` có cùng một project không.
- Kiểm tra region: `https://us.cloud.langfuse.com` hoặc `https://cloud.langfuse.com`.

## References

- Anthropic: Building effective agents - https://www.anthropic.com/engineering/building-effective-agents
- OpenAI Agents SDK orchestration/handoffs - https://developers.openai.com/api/docs/guides/agents/orchestration
- LangGraph concepts - https://langchain-ai.github.io/langgraph/concepts/
- Langfuse tracing - https://langfuse.com/docs
