# Đối chiếu lý thuyết ↔ mã (theory/code audit)

**Mục tiêu:** mọi mệnh đề đã chứng minh trong bài (Bổ đề, Định lý, Giả định, Hệ quả, Nhận xét) phải đúng với **đúng đoạn mã mà các study đã chạy**. Chỗ nào lệch thì:
- sửa mã (luôn sửa trong `gatekeeper_ext`, vì `gatekeeper_lite` đã freeze), kèm test hoặc kiểm số dựa trên chứng minh;
- hoặc sửa câu chữ trong bài cho khớp với mã.

Viết ngày 31/10/2026.

## Bảng đối chiếu

| # | Mệnh đề trong bài | Mã | Kết luận | Đã làm |
|---|---|---|---|---|
| TC1 | Bổ đề 2.1: mức cược λ < 1/(θ − y_min), các nhân tử dương | `eprocess.py`: Betting (λ ≤ 0,5/(1+θ)), HarmCert (λ = 0,9/(1−η)), HarmAlarm (μ ≤ 0,95/η), DiscordantSign (λ ≤ 0,95/q0) | **Khớp.** Mọi nhân tử ≥ 0,05 > 0; λ chỉ dùng dữ liệu quá khứ | C1, C9 (sẵn có) |
| TC2 | Định lý 2.2: sổ cái α_{c,k} cố định trước theo danh tính của **mọi** ô, kể cả tổ hợp và thư viện lớn dần | `AlphaLedger` chỉ có danh sách ô cố định lúc khởi tạo; không có quy tắc cho tổ hợp hay kỹ năng thêm sau | **Thiếu** (D–H không có tổ hợp nên không ảnh hưởng kết quả) | `gatekeeper_ext/ledger.py`: α_c chỉ phụ thuộc kích thước ô và sức chứa N; tổng ≤ α (C11, test). Cách phân bổ của mô phỏng cũng ≤ α (C11) |
| TC3 | Bài chỉ phát biểu ngưỡng 1/α_{c,k}; thực nghiệm D–H lại dùng **e-Holm trên min(e_ben, e_cert) đọc tại thời điểm dừng** | `drawharness.py` + `studyd_decisions.py`; `run_study_h.py` | **Mã đúng, nhưng bài thiếu mệnh đề.** Giá trị tại τ là e-value nhờ optional stopping; min là e-value dưới null hợp; e-Holm kiểm soát FWER (giá trị max chạy thì *không* phải e-value, mã đã không dùng) | Thêm Nhận xét `rem:eholm`; kiểm số C10 chạy đúng luật dừng/luật quyết định với θ = 0,2, η = 5%, 16 ô, ở cả hai biên của null |
| TC4 | Mục 7.3 viết "benefit e-process với e-Holm" | Quyết định thật dùng min(benefit, harm certificate) | **Câu chữ sai** | Sửa câu trong mục 7.3 |
| TC5 | Hệ quả 2.6 cần: footprint rời nhau ⇒ không tương tác | `footprint_overlap` (đã freeze) **bỏ qua** `func:<module>`, nên hai kỹ năng cùng sửa mã cấp module của cùng một tệp bị coi là rời nhau; census R2 lần đầu cũng bỏ mã cấp module | **Lỗi không chặt (unsound)** | `execution.site_footprint`: footprint gắn kèm tên module, có cả mã cấp module; census giữ `<module>` theo từng tệp (amendment R2-A2, chạy lại) |
| TC6 | Giả định 4: footprint lấy trên mã gốc là đủ | Census R2: một phép viết lại tạo site cho phép viết lại khác ở hàm khác | **Giả định sai trên dữ liệu thật** | Cạnh enabling (R2-A1), `execution.components(..., edges)` |
| TC7 | Định lý 2.2 dành cho e-process cược trung bình trên mẫu i.i.d. | `gatekeeper()` có các tùy chọn: `task_priority` (không hoán đổi được), lọc reach (biên độ nhân với p_reach), `discordant_sign` (biên độ phụ thuộc P(Z ≠ 0)), e-BH (FDR) | **Bảo đảm yếu hơn bài nói.** Không study nào được trích trong bài dùng các tùy chọn này | `gatekeeper_ext/conformance.py` gắn nhãn FULL / SIGN_ONLY / FDR / NONE cho từng config; test khẳng định D, E, G, H đều FULL |
| TC8 | Định lý 2.2: "mỗi epoch dùng task mới" | `gatekeeper()` dùng lại cùng bộ task, chỉ xáo thứ tự theo seed·1000 + epoch | **Vẫn hợp lệ.** Retirement kích hoạt bằng fingerprint, không bằng kết quả, nên dãy Z của epoch k vẫn i.i.d. theo P^(k); "task mới" là điều kiện đủ | Ghi lại ở đây; không cần sửa |
| TC9 | Study P: e_patch là e-value dưới null "A hoặc B" | `patch_rule.py` | **Khớp:** trung bình các e-value (A), min các e_cert (B), min của hai cái | — |
| TC10 | Bổ đề 2.3 / Mệnh đề 2.4 / Định lý 2.5 / Mệnh đề 2.7 | Không có trong mã quyết định | Kiểm bằng số (C3, C4, C5) | — |
| TC11 | Thẻ hành vi (`behavior:*`) dùng chung làm hai kỹ năng thành "giao nhau" | `footprint_overlap` | **Chặt nhưng bảo thủ** (chỉ tốn thêm ô tổ hợp); census dùng footprint theo (tệp, hàm) | Ghi lại |

## Kết quả kiểm
Kết quả nằm trong `research_closure/results/theory/THEORY_CHECKS.json`:
- **C10** (luật quyết định của D–H): FWER ở cả hai biên của null ≤ α, và E[e_τ] ≤ 1 (trong khoảng 3 sai số chuẩn).
- **C11** (sổ cái): tổng ≤ α.

Test liên quan: `tests/test_conformance.py`, `tests/test_execution_rule.py`, `tests/test_library_census.py`.
