# Failure Modes và Cách Khắc Phục

## 1. Local LLM bị timeout

**Failure mode:** Baseline có thể bị timeout khi gọi `llama-server`, đặc biệt khi chạy model GGUF local trên CPU. Lỗi thường xuất hiện khi chương trình chờ phản hồi từ endpoint `http://127.0.0.1:8080/v1/chat/completions` quá lâu.

**Ảnh hưởng:** Benchmark chạy chậm hoặc baseline thất bại trước khi đến lượt multi-agent.

**Cách khắc phục:** Giảm số token sinh ra và tăng timeout khi cần.

```env
LLAMA_CPP_MAX_TOKENS=128
TIMEOUT_SECONDS=240
```

Trong code, benchmark runner cũng đã được xử lý để nếu một runner lỗi thì ghi lỗi vào report thay vì làm crash toàn bộ benchmark.

## 2. Chưa chạy llama-server

**Failure mode:** Nếu `.env` đặt `LLM_PROVIDER=llama_server` nhưng `llama-server` chưa chạy, ứng dụng sẽ không kết nối được tới `http://127.0.0.1:8080`.

**Ảnh hưởng:** Baseline thất bại vì baseline cần gọi local LLM endpoint.

**Cách khắc phục:** Mở một PowerShell riêng và start `llama-server` trước khi chạy baseline hoặc benchmark.

```powershell
D:\mine\VinAI\llama\llama.cpp\build\bin\Debug\llama-server.exe `
  -m D:\mine\VinAI\llama\llama.cpp\models\qwen2.5-1.5b-instruct-q4_k_m.gguf `
  --host 127.0.0.1 `
  --port 8080 `
  -c 2048
```

## 3. Lỗi xác thực hoặc network khi gửi trace

**Failure mode:** Langfuse có thể trả về `401 Unauthorized` nếu public key, secret key hoặc region URL không đúng. LangSmith có thể timeout nếu máy không kết nối được tới `https://api.smith.langchain.com`.

**Ảnh hưởng:** Workflow vẫn chạy được, nhưng trace không được gửi lên provider bên ngoài. Trace local vẫn còn trong `ResearchState.trace`.

**Cách khắc phục:** Dùng Langfuse làm trace provider chính và kiểm tra đúng region của project.

```env
TRACE_PROVIDER=langfuse
LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
```

Nếu project Langfuse nằm ở region default/EU, dùng:

```env
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Ngoài ra, cần chắc chắn `LANGFUSE_PUBLIC_KEY` và `LANGFUSE_SECRET_KEY` thuộc cùng một project.

## 4. Workflow bị lặp vô hạn hoặc route sai

**Failure mode:** Multi-agent workflow có thể bị lặp vô hạn nếu Supervisor không có stop condition rõ ràng.

**Ảnh hưởng:** Hệ thống tốn compute, trace khó đọc và không tạo được `final_answer`.

**Cách khắc phục:** Supervisor dùng rule routing rõ ràng và giới hạn `MAX_ITERATIONS`.

```text
thiếu research_notes -> researcher
thiếu analysis_notes -> analyst
thiếu final_answer -> writer
đủ output cần thiết -> done
```

```env
MAX_ITERATIONS=6
```

Nhờ vậy workflow có giới hạn, dừng được và từng quyết định route đều hiển thị trong trace.
