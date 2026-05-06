# Benchmark Report: Single-agent vs Multi-agent

> Trạng thái chạy: **không chạy được bằng LLM thật** trong môi trường hiện tại do lỗi `401 Unauthorized / invalid_api_key` từ OpenAI API.
>
> File này được tạo để đáp ứng deliverable trong `README.md` (mục 3 & 4), và mô tả rõ **failure mode** + **cách fix**.  
> Khi bạn có API key hợp lệ, chạy lại lệnh benchmark để ghi số liệu thật.

## Setup

- Repo: `multi-agent-research-lab`
- Baseline: `malab baseline`
- Multi-agent: `malab multi-agent` (Supervisor → Researcher → Analyst → Writer)
- Benchmark CLI: `malab benchmark`

### Queries dùng để benchmark

Trích từ `configs/lab_default.yaml`:

- Research GraphRAG state-of-the-art and write a 500-word summary
- Compare single-agent and multi-agent workflows for customer support
- Summarize production guardrails for LLM agents

## Results (placeholder)

> Vì chưa chạy được LLM thật, bảng dưới đây để trống các cột cần token/cost/quality.  
> Latency/cost/quality thực tế phụ thuộc model, network, prompt và tool/search provider.

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| Single-Agent Baseline | N/A | N/A | N/A | Blocked by `invalid_api_key` (401) |
| Multi-Agent System | N/A | N/A | N/A | Blocked by `invalid_api_key` (401) |

## How to reproduce (when API key is valid)

1) Cập nhật `.env`:

```bash
OPENAI_API_KEY=... # key hợp lệ
OPENAI_MODEL=gpt-4o-mini
```

2) Chạy benchmark 1 query và xuất report:

```bash
python -m multi_agent_research_lab.cli benchmark \
  --query "What are multi-agent systems?" \
  --out reports/benchmark_report.md
```

3) Chạy theo nhiều query từ file YAML:

```bash
python -m multi_agent_research_lab.cli benchmark \
  --queries-file configs/lab_default.yaml \
  --out reports/benchmark_report.md
```

## Failure mode & fix (deliverable #4)

### Failure mode

- **Symptom**: lệnh `malab benchmark` fail ngay ở bước baseline, log trả về `HTTP/1.1 401 Unauthorized` và lỗi `openai.AuthenticationError` với `code: invalid_api_key`.
- **Where**: xảy ra trong `LLMClient.complete()` khi gọi OpenAI Chat Completions API.
- **Impact**: baseline và multi-agent đều không thể chạy → không sinh được benchmark metrics / report số liệu thật.

### Root cause

- **Cấu hình `.env`** chứa `OPENAI_API_KEY` không hợp lệ (hoặc thiếu quyền / sai project key), dẫn đến API trả `401`.

### Fix

- **Fix chính**: dùng API key hợp lệ trong `.env` (hoặc export env var), sau đó chạy lại benchmark.
- **Guardrail đề xuất** (nếu muốn làm “production-grade” hơn):
  - Validate key sớm và trả lỗi thân thiện (hiện `LLMClient` đã fail-fast nếu thiếu key; còn trường hợp “key sai” thì sẽ fail khi gọi API).
  - Thêm fallback runner dạng **mock** khi chạy trong môi trường lab không có key (ví dụ: flag `--mock-llm` hoặc auto-detect 401 để chuyển sang stub).

### Evidence

- Log thực tế đã quan sát: `HTTP Request ... 401 Unauthorized` và `AuthenticationError: invalid_api_key`.

