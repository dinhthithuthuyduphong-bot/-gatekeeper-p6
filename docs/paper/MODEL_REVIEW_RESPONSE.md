# Xử lý từng điểm của model review (kiểm chứng minh + 3 phản biện giả lập)

Nguồn: `research_closure/results/model_reviews/PROOF_REVIEW.md` và `MOCK_REVIEWS.md` (gemini-4-argon, workflow `Gatekeeper model stand-ins`, run 41229462629; chi phí 0,02 + 0,13 USD). Đây là review do model viết, **không thay được người**. Mỗi điểm đều được kiểm lại bằng tay với bài và mã trước khi sửa.

**Mức độ tổng thể của 3 phản biện giả lập:**
- lý thuyết: *accept*;
- thực nghiệm: *strong accept*;
- ứng dụng: *weak accept*.

Không nên tin các mức này; giá trị của chúng nằm ở danh sách yếu điểm.

## Kiểm chứng minh

| # | Điểm | Kiểm lại | Đã sửa |
|---|---|---|---|
| P1 | Công thức sổ cái theo N quên chia cho số scope L | **Đúng** | Theory: α_s cho từng scope, Σα_s ≤ α; công thức trong scope dùng α_s. `LibraryLedger` vốn là một instance cho mỗi scope (truyền α_s) |
| P2 | Nhận xét e-Holm phải nói τ_c dừng ngay khi chạm K/α | **Đúng** về câu chữ; mã (`drawharness`) đã dừng như vậy | τ_c = lần đầu min ≥ K/α hoặc alarm, nếu không thì hết ngân sách |
| P3 | Mệnh đề 1(b): Z = ±1 phải hiện thực được với định nghĩa loss | **Đúng** | Nói rõ u, d hiện thực được với ℓ ∈ {0,1} |
| P4 | Định lý 2 dùng Giả định 3 mà không nêu | **Đúng** | Thêm "Under Assumption 3" |
| P5 | Luật thực thi chỉ đòi thành phần ≥ 2 kỹ năng, chứng minh cần mọi thành phần | **Đúng** về câu chữ; mã (`check_execution`) đã đòi mọi thành phần | Sửa luật trong mục Problem |

## Phản biện giả lập

| # | Điểm (người nêu) | Kiểm lại | Đã làm |
|---|---|---|---|
| M1 | `\input{related_stats}` nằm sau Data Availability (theory, empirical, practice) | **Sai**: PDF đúng thứ tự. Do tool review của mình ghép văn bản sai thứ tự | Sửa tool (`inline_inputs`), có test |
| M2 | Không nêu chiến lược cược của e-process lợi ích (theory) | **Đúng** | Implementation: công thức λ_i, khớp `BettingEProcess._bet` |
| M3 | Hệ số 1/C(N,m) làm ô tổ hợp lớn rất đắt (theory, empirical) | **Đúng** | Theory: nói rõ cái giá, và vì sao chấp nhận được (thành phần hiếm và nhỏ theo R2) |
| M4 | Quá nhiều mã study nội bộ, cần bảng tổng quan (empirical, practice) | **Đúng** | Bảng `tab:studies`; tên mô tả cho B2, B6-R, B8 |
| M5 | Không rõ P/Q dùng khung như thế nào (empirical) | **Đúng** | Đoạn nối: patch là thư viện một ô, draw là một input sinh ra |
| M6 | "Task", "draw" thực tế là gì (practice) | **Đúng** | Problem: draw = input từ generator của oracle, ℓ ∈ {0,1}, Z ∈ {−1,0,1} |
| M7 | Loss 0,5/regression gây nhầm (practice) | **Đúng** | Problem: chỉ Z từ draw đi vào e-process; suite loss chỉ để báo cáo |
| M8 | 6/55 mâu thuẫn với 43,1% / 11,1%? (practice) | Không mâu thuẫn: khác đơn vị (instance và patch), nhưng câu chữ dễ nhầm | Evaluation: định nghĩa đơn vị của HQ1; nói rõ hai tỉ lệ trả lời hai câu hỏi khác nhau |
| M9 | Vì sao 19/55 không tái tạo (empirical) | **Đúng là thiếu** | Lần chạy gốc không lưu generator do model viết; sinh lại thì khác ở 17/19 đơn vị (có trong bộ kiểm số) |
| M10 | Tương tác ba kỹ năng bị kiểm theo cặp bỏ sót; chi phí bậc hai (empirical) | **Đúng** | Threats |
| M11 | Kỹ năng do agent tự học (empirical, practice; major) | **Đúng, là giới hạn thật** | Threats: cách đưa kỹ năng do agent học vào ⟨π, D, I, P, K⟩ và giới hạn của binder. Intro đã nói không khẳng định gì về thư viện học được. Muốn đóng hẳn thì cần một study mới (việc 7.9) |
| M12 | Tác hại trên target thật gần như tất định, cơ chế thống kê không cần (practice) | Bài đã nói điều này (RQ1, mục 7.3); Study H là trường hợp tác hại hiếm | Giữ nguyên; bảng `tab:studies` nhấn mạnh H |
| M13 | Thời gian chạy so với B8 (practice) | Có số lần chạy trial (3.220 so với 3.600) | Giữ nguyên |
