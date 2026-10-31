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
| TC12 | Vùng footprint là một hàm cụ thể | Census R2 định danh vùng bằng (tệp, **tên** hàm), nên hai method cùng tên ở hai class khác nhau bị gộp thành một vùng (ví dụ nhiều method `map` trong trino) | **Chặt nhưng bảo thủ:** báo thừa chồng lấn, không bao giờ báo thiếu | Study S định danh đơn vị bằng tên đầy đủ (qualname). Ghi lại; số của R2 là cận trên của chồng lấn |
| TC11 | Thẻ hành vi (`behavior:*`) dùng chung làm hai kỹ năng thành "giao nhau" | `footprint_overlap` | **Chặt nhưng bảo thủ** (chỉ tốn thêm ô tổ hợp); census dùng footprint theo (tệp, hàm) | Ghi lại |

## Vòng 2 (31/10/2026): mọi mệnh đề có chứng minh, mã và baseline theo lý thuyết

| # | Mệnh đề / thành phần | Mã | Kết luận | Đã làm |
|---|---|---|---|---|
| TC13 | Nhận xét 1 (harm certificate) chỉ có tính nhẩm | `HarmCertEProcess`, `gates.gatekeeper_path` (λ = c/(1−η), c = 0,9) | Thiếu chứng minh | Thành **Mệnh đề `prop:harm`** có chứng minh: quy về Bổ đề 1 với Y = 1−H, θ = 1−η; ngưỡng tăng h* (luật số lớn); số draw sạch. Kiểm bằng C9 |
| TC14 | Tổng sổ cái theo kích thước ô ≤ α_s | `gatekeeper_ext/ledger.py` | Thiếu chứng minh trong bài | **Bổ đề `lem:ledger`** + chứng minh (chuỗi Basel). Kiểm bằng C11 |
| TC15 | e-Holm trên min(e_ben, e_cert) tại τ | `drawharness` + `studyd_decisions.e_holm` | Mới là phác thảo | **Mệnh đề `rem:eholm`** (a) optional stopping, (b) closed testing + Markov, (c) e-Holm trội hơn ngưỡng K/α; nói rõ mã chỉ cần kiểm tập con có trung bình nhỏ nhất ở mỗi kích thước. Kiểm bằng C10 |
| TC16 | Giả định 4 và Hệ quả 2.6 sau khi thêm cạnh enabling | `execution.components(..., edges)` | Giả định cũ viết cho footprint rời nhau, còn luật thực thi dùng đồ thị có cạnh enabling | Phát biểu lại cho **tập không kề nhau** (footprint hoặc enabling); chứng minh theo thành phần liên thông. Nói rõ: với loss {0,1}, giả định đòi không task nào bị cả A và B đổi kết quả |
| TC17 | Đo cộng tính trong Study S | `composition_study.interaction` dùng `min(1, la+lb)`, lỏng hơn Giả định 4 | **Lệch nhỏ.** Không ảnh hưởng số báo cáo: ở S-A5 không đơn vị nào có cả A và B cùng đổi trên một input | Sửa thành `lab == la + lb` và thêm `both_parts_change`; có test |
| TC18 | Định lý 1 đòi "task mới mỗi epoch" | `gatekeeper()` dùng lại input, xáo theo epoch | Lý thuyết viết chặt hơn cần | Điều kiện mới: dãy task i.i.d. P^(k) *cho trước quyết định mở epoch*; dùng lại input hợp lệ khi quyết định đó không phụ thuộc kết quả (retirement theo fingerprint) |
| TC19 | Baseline B2 = admit khi bind | `studyd_decisions.decide`: `ADMIT if binds` | **Khớp** | — |
| TC20 | Baseline B6-R = replay đúng trên nguồn **và** fingerprint MATCH | `studyd_decisions`: `replay_ok and fingerprint == "MATCH"`; `gatekeeper.comparators` | **Khớp** | — |
| TC21 | Baseline B8 = không draw nào và không test nào của suite hồi quy | `studyd_decisions`: `REJECT if b8.hurt or census_bad` | **Khớp** | — |
| TC22 | Gate tuần tự của Study P = harm certificate, ngưỡng K/α (sổ cái α/K) | `gates.gatekeeper_path`: λ = 0,9/0,95, ngưỡng log(K/α), alarm μ và 20 = 1/0,05 | **Khớp** với Mệnh đề harm và Định lý 1 | — |
| TC23 | Người chấm model của Q-A1 có phân biệt R/B không | `rater_calibration.py` (20 mục biết trước đáp án) | **Có**: argon và flash đều 20/20 | Người chấm model hợp lệ cho S8 |

| TC24 | Ô tổ hợp có một thứ tự chuẩn duy nhất (do model kiểm vòng 3 chỉ ra: nếu không thì cách đếm C(N,m) sai) | `execution.canonical_order` (thứ tự đăng ký) | **Thiếu trước đó**, vì luật chưa nói áp dụng theo thứ tự nào | Thêm vào Problem, Bổ đề sổ cái và mã; có test. Study S đã đo cả hai thứ tự AB và BA |

## Kết quả kiểm
Kết quả nằm trong `research_closure/results/theory/THEORY_CHECKS.json`:
- **C10** (luật quyết định của D–H): FWER ở cả hai biên của null ≤ α, và E[e_τ] ≤ 1 (trong khoảng 3 sai số chuẩn).
- **C11** (sổ cái): tổng ≤ α.

Test liên quan: `tests/test_conformance.py`, `tests/test_execution_rule.py`, `tests/test_library_census.py`.
