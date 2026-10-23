# Trạng thái trả lời review (cập nhật 23/10/2026, sau review kỹ thuật tại commit 26a1978)

Mọi phân tích mới là **thứ cấp / post hoc** trên trace đã đóng băng, trừ khi ghi khác. Không kết quả chính nào của D/E/F/G/H bị thay đổi.

| # | Vấn đề | Trạng thái | Bằng chứng |
|---|---|---|---|
| M1 | Triển khai toàn patch khi một scope ADMIT, scope khác chỉ QUARANTINE | **Đã sửa (thiết kế), đã kiểm tra trên dữ liệu cũ** | `gatekeeper_ext/patch_rule.py`: `e_patch = min(mean_s min(e_ben_s, e_cert_s), min_s e_cert_s)`, e-Holm trên patch. Áp cho D/E/G: cùng quyết định (chỉ D1, D3). Study F: Amendment **F-A2**, họ 72 patch |
| M2 | Thiếu baseline cùng η, α; so B8 không công bằng | **Đã làm (post hoc, Study H)** | `study_h/results/SECONDARY_STUDY_H.md`: cỡ mẫu cố định 200/300 lần rút mỗi ô; Gatekeeper mạnh hơn ở cùng chi phí, kém hơn cỡ mẫu 300 nhưng rẻ hơn 28% |
| M3 | Skill thứ hai mới có 1 target có hại | **Giới hạn, ghi rõ** | Phía có lợi BLOCKED sau khi kiểm định 29/29 ứng viên |
| M4 | H là dữ liệu tổng hợp; đơn vị FWER | **Đã sửa đơn vị**: 0/50 họ có admit sai | `SECONDARY_STUDY_H.md` |
| M5 | Chi phí thật, model | **Mở** (B9/Study F HOLD) | — |
| — | e-Holm dùng e-value ở n_max chứ không ở thời điểm dừng | **Đã kiểm tra**: không tập admit nào đổi ở D/E/G và 50/50 lần lặp H | ghi trong bài |
| — | Độ bền khi vi phạm i.i.d. | **Đã đo** (mô phỏng): lặp 2 lần → 7,5% admit sai ở biên; i.i.d. là điều kiện bắt buộc | `study_h/results/DEPENDENCE_SIM.md` |
| — | Tính không trạng thái của harness | **Công cụ sẵn sàng**, tự kiểm tra ngoại tuyến 0/60 sai khác | `tools/statelessness_check.py`, workflow `statelessness-check.yml` |
| — | Chính sách lai smoke → Gatekeeper | **Đã đo (post hoc)**: 0 lỗi, rẻ hơn 21%, power thấp hơn một chút | `SECONDARY_STUDY_H.md` |
| — | Biên confidence sequence trên lưới | **Đã sửa** (mở rộng một bước lưới mỗi phía) | `tools/secondary_analyses.py` |
| — | Related work (Registered Reports, APR/LLM, validation) | **Đã bổ sung, chỉ trích dẫn đã xác minh** | bài báo |
