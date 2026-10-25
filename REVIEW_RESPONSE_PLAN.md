# Trạng thái trả lời review (cập nhật 24/10/2026, gói closure trên main fcdd1b8b)

Phân tích mới là **thứ cấp / post hoc**, trừ khi ghi khác. Không đổi kết quả chính D/E/G/H. Study F có amendment F-A3 trước paid B9, vẫn HOLD. Báo cáo kiểm tra và giới hạn: `research_closure/RESULT.md`. Local PASS không có nghĩa workflow mới đã chạy trên GitHub.

| # | Vấn đề | Trạng thái | Bằng chứng |
|---|---|---|---|
| M1 | Triển khai toàn patch khi một scope ADMIT, scope khác chỉ QUARANTINE | **Đã sửa (thiết kế), đã kiểm tra trên dữ liệu cũ** | `gatekeeper_ext/patch_rule.py`: `e_patch = min(mean_s min(e_ben_s, e_cert_s), min_s e_cert_s)`, e-Holm trên patch. Áp cho D/E/G: cùng quyết định (chỉ D1, D3). Study F: Amendment **F-A2**, họ 72 patch |
| M2 | Thiếu baseline cùng η, α; so B8 không công bằng | **Đã sửa phép so sánh, ưu thế GK chưa được xác lập** | `research_closure/results/statistics/STATISTICS_RESULT.md`: IUT không chia alpha/2; fixed-200 Holm đạt 19/50 và 15/50 ở h=2%,3%, so với GK 17/50 và 11/50; 1200 so với 1300,5 draw/họ. Nhận định cũ "GK mạnh hơn ở cùng chi phí" không còn đủ cơ sở |
| M3 | Skill thứ hai mới có 1 target có hại | **Có thêm bằng chứng hồi cứu, chưa khép generalization** | Study I: SQLAlchemy thêm 9 regression upstream cấp 1; NetworkX có upstream witness được sửa và 54 census test vẫn pass. CI 40084717332 xanh. Đây không phải cohort prospective mới |
| M4 | H là dữ liệu tổng hợp; đơn vị FWER | **Đã sửa đơn vị**: 0/50 họ có admit sai | `SECONDARY_STUDY_H.md` |
| M5 | Chi phí thật, model | **Đã đo chi phí local trên hai case; model vẫn mở** | `research_closure/results/cost/`: dừng thật và full draws cùng census, ba lần lặp; không suy ra LLM economics. F-A3 scorer/aggregator có kiểm tra inventory/trace/usage; B9 HOLD |
| M6 | Thiếu dữ liệu/nhãn sai trong B9 scoring | **Sửa code và kiểm tra offline** | `tests/test_study_f_integrity.py`, F-A3: 72 patches đủ raw/candidate, raw e-value recomputation, seed/hash/usage checks, budget-cap replay; không tạo model evidence |
| M7 | Validation độc lập sau tìm kiếm target | **BLOCKED: thiếu cohort mới** | `study_j/PROTOCOL.md`, preflight và 98 repo đã có dấu vết khảo sát trong manifests. DRAFT, không gọi là preregistered result |
| — | e-Holm dùng e-value ở n_max chứ không ở thời điểm dừng | **Đã kiểm tra**: không tập admit nào đổi ở D/E/G và 50/50 lần lặp H | ghi trong bài |
| — | Độ bền khi vi phạm i.i.d. | **Đã đo** (mô phỏng): lặp 2 lần → 7,5% admit sai ở biên; i.i.d. là điều kiện bắt buộc | `study_h/results/DEPENDENCE_SIM.md` |
| — | Tính không trạng thái của harness | **Đã kiểm chứng trên 12 target thật**: 2.400 lần rút, 0 sai khác | `harness_checks/STATELESSNESS_SUMMARY.md` |
| — | Chính sách lai smoke → Gatekeeper | **Đã đo (post hoc)**: 0 lỗi, rẻ hơn 21%, power thấp hơn một chút | `SECONDARY_STUDY_H.md` |
| — | Biên confidence sequence trên lưới | **Đã sửa** (mở rộng một bước lưới mỗi phía) | `tools/secondary_analyses.py` |
| — | Related work (Registered Reports, APR/LLM, validation) | **Đã bổ sung, chỉ trích dẫn đã xác minh** | bài báo |

## Review lần 5 (23/10/2026)

| Điểm | Trả lời |
|---|---|
| Mã hoá Y của e-process lợi ích mơ hồ | Y = −Z ∈ [−1, 1] (không mã hoá Bernoulli); prior 0,5 và phương sai 0,25 là hằng số điều chỉnh cho các mức cược đầu, tính hợp lệ không phụ thuộc vào chúng; mức cược bị cắt ở một nửa mức tối đa nên mỗi thừa số ≥ 0,5. Ghi trong bài và phụ lục mới (có ví dụ từng lần rút) |
| Hướng dẫn chọn mức cược, ngân sách lần rút | Phụ lục mới: tốc độ tăng trưởng kỳ vọng, số lần rút để vượt K/α theo c và h; e-process lợi ích vượt ngưỡng sau 18–80 lần rút (tỉ lệ có lợi ≥ 0,4), nên chứng chỉ mới là ràng buộc |
| Lý do chọn mức cược báo động (Kelly tại h = 0,5) | Dừng nhanh khi tác hại thường xuyên; mức cược tại h = η có tăng trưởng bằng 0 ở đó |
| Worker có thể mang trạng thái | Kiểm tra trên 12 target: 0 sai khác / 2.400 lần rút |
| Đăng ký trước B6-S, quy tắc mức patch, futility | Cam kết cho các study sau, ghi trong Kết luận |
| Fingerprint chặt hơn | Fingerprint yêu cầu đúng phiên bản phụ thuộc của nguồn sẽ từ chối mọi lần chuyển giao trong các study này: an toàn nhưng vô dụng |
| PraxisMemBench, các so sánh khác | Chưa xác minh được nguồn; không đưa vào bài |


### Follow-up 25/10/2026

Study K adds a retrospective python-control beneficial transfer for skill 2, with an unchanged parent-revision upstream smoke test and an independent analytical draw oracle. This improves target breadth but does not close prospective validity, full-patch coverage, new harmful-target breadth, or model dependence. Raw logs and environment failures are retained; no paid B9 call. See `study_k/RESULT_VI.md`.
