# Nợ kỹ thuật (PAPER_TODO giai đoạn 3)

| # | Vấn đề | Ảnh hưởng | Trạng thái | Cách xử lý |
|---|---|---|---|---|
| TD1 | Freeze lệch của Study B, C, N, P | P: chỉ văn bản; B, C, N: không trích trong bài | ✅ đã giải thích | `EVIDENCE_LEDGER.md`, mục 31/10/2026 (3.1) |
| TD2 | `tools/q_analyze.py` tính Q5 khác định nghĩa của giao thức | Bài dùng số tính lại 3,88 | ✅ đã ghi trong bài | `latex/sections/threats.tex`; `STUDY_Q_RESULT.md` |
| TD3 | `gatekeeper_ext/fn_draws.py: score_fn_patch` ghi tệp của patch vào bản sao mà không tạo thư mục cha. Patch **tạo tệp trong thư mục mới** thì gặp `FileNotFoundError` (4 instance của Study Q) | 4/469 instance tính là không dùng được | ⏳ chưa sửa mã: tệp thuộc freeze của Study P và Q | Ghi trong Threats. Với study sau: thêm `(patched / rel).parent.mkdir(parents=True, exist_ok=True)` trước `write_text`, qua amendment hoặc ở bản công cụ mới, kèm test |
| TD4 | Token Vertex hết hạn sau khoảng 1 giờ, vì `gcloud auth print-access-token` trả token còn trong bộ nhớ đệm | Một lần chạy người chấm thứ hai thất bại | ✅ sửa tận gốc | `tools/fresh_gcp_token.py` luôn tạo token mới (google-auth refresh); 13 workflow gọi model dùng nó làm `GK_TOKEN_CMD`; kiểm bằng workflow `Gatekeeper Vertex token check`; test `tests/test_fresh_gcp_token.py` |
| TD5 | `tools/rq5_rate_llm.py` chỉ ghi kết quả ở cuối, nên một lỗi giữa chừng làm mất hết | Như TD4 | ✅ giảm thiểu | Chia thành nhiều job (`study-q-review-rate.yml`). Không sửa công cụ vì là công cụ đã đóng băng của RQ5 |
| TD6 | Các lần chạy thất bại trong lịch sử | 64 run | ✅ đã phân nhóm | `docs/API_AND_FAILURES.md`, workflow `Gatekeeper failure audit` |
| TD7 | Luật thực thi (G1 của PHASE1_REVIEW) chưa có trong hệ thống | Hệ thống chưa chặn việc chạy chung các kỹ năng có footprint giao nhau khi tổ hợp chưa được admit | ✅ đã cài | `gatekeeper_ext/execution.py`: `components`, `check_execution`, `executable_subset`, `composites_to_test`; 8 test, gồm test thuộc tính trên 300 thư viện ngẫu nhiên (`tests/test_execution_rule.py`). Đặt ở `gatekeeper_ext` vì mọi study đã đóng băng băm **mọi** module của `gatekeeper_lite`; freeze của D, E, G, H, Q vẫn verified |
