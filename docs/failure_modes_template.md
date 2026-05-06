# Failure modes & fixes (template)

Mục tiêu: viết ngắn gọn (khoảng 10-20 dòng) nhưng dựa trên trace/log thật.

## 1) Failure mode

- **Symptom**: mô tả lỗi/biểu hiện (ví dụ: trả lời sai trọng tâm, không có citation, loop quá lâu, timeout, hallucination...).
- **Where**: agent/bước nào? (dựa vào `route_history` / trace).
- **Impact**: ảnh hưởng gì tới quality/latency/cost?

## 2) Root cause

- **Prompting**: system/user prompt chưa ràng buộc? thiếu format? thiếu tiêu chí dừng?
- **State/handoff**: thiếu field hoặc worker không dùng đúng context?
- **Routing**: supervisor route sai thời điểm? stop condition sai?
- **Tools/search**: nguồn search không liên quan? parsing lỗi? thiếu fallback?
- **Guardrails**: thiếu timeout/retry/validation?

## 3) Fix implemented

- **Change**: bạn sửa gì (code/prompt/config).
- **Why it works**: cơ chế fix.
- **Trade-offs**: tốn cost hơn? tăng latency? giảm coverage?

## 4) Evidence

- **Before/after**: 1-2 dòng so sánh.
- **Trace proof**: screenshot/link trace, hoặc log event/route history.
