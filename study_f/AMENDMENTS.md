# Study F — amendments

## F-A1 (trước mọi lượt B9 trả phí) — sửa cổng triển khai, họ kiểm định và phạm vi hash

**Phát hiện (review ngày 22/10/2026):**
1. `tools/score_heldout.py` coi một patch là được triển khai khi chỉ cần **một** scope đạt ADMIT và census sạch, kể cả khi scope khác dừng với REJECT_HARM.
2. Bước e-Holm trên cả họ được nhắc trong docstring nhưng **chưa được cài đặt**.
3. `k_cells = 48` chưa tính các lần lặp; mỗi lần lặp là một quyết định admit riêng.
4. Công cụ chấm điểm không nằm trong danh sách hash đóng băng của Study F.

**Thay đổi:**
- Cổng (`score_heldout.py`): patch chỉ là **ứng viên** khi không scope nào REJECT_HARM, census VALID và không có regression, và ít nhất một scope đạt ngưỡng tạm thời K/α. E-value của ô thuộc patch không phải ứng viên là 0.
- Họ kiểm định: **K = 144** (4 model × 3 lần lặp × 6 target × 2 scope); `tools/aggregate_study_f.py` áp dụng e-Holm trên toàn bộ 144 ô; patch được triển khai khi ít nhất một ô của nó được e-Holm chọn. Kết quả theo từng model: số SUCCESS/HARMFUL/NO_EFFECT/NO_PATCH/BUDGET_CAP/CENSUS_INVALID của B9 thô và B9 + Gatekeeper, và hiệu ứng trong cùng model (Δ).
- Hash: `config_study_f.json` khai báo `extra_tracked` gồm `tools/score_heldout.py` và `tools/aggregate_study_f.py`.
- Seed held-out được ghim theo hash đóng băng gốc (`seed_freeze_sha256`); vì vòng drand của seed đã công khai, đóng băng lại không được phép làm đổi seed.

**Không đổi:** model, model ID, giá, ngân sách, target, oracle, mô tả lỗi, quyền sửa, θ, η, α, n_max.

**Chỉnh sửa chính xác** (áp bằng `tools/amend_study.py`): xem `F_A1_EDITS.txt`.

## F-A2 (trước mọi lượt B9 trả phí) — quyết định ở mức patch

**Phát hiện (review ngày 23/10/2026):** sau F-A1, một patch vẫn là ứng viên khi một scope đạt ADMIT và scope khác chỉ ở QUARANTINE. QUARANTINE nghĩa là chưa thấy tác hại, **không** phải đã chứng nhận ít tác hại; vì patch được triển khai nguyên vẹn, bảo đảm ở một scope không bao trùm hành vi ở scope khác.

**Thay đổi:**
- Giả thuyết được phát biểu cho **patch**: H0 = (không scope nào có lợi ích vượt θ với ít tác hại) hoặc (có scope có tỉ lệ tác hại ≥ η). E-value: `e_patch = min(mean_s min(e_ben_s, e_cert_s), min_s e_cert_s)`, tính trên đủ n_max lần rút ở mọi scope; bằng 0 nếu có báo động tác hại hoặc census có regression (`gatekeeper_ext/patch_rule.py`).
- Họ kiểm định: **K = 72 patch** (4 model × 3 lần lặp × 6 target); e-Holm trên các patch (`tools/aggregate_study_f.py`).
- `extra_tracked` thêm `gatekeeper_ext/patch_rule.py`.

**Kiểm tra trên dữ liệu đã có (post hoc):** áp quy tắc mức patch cho Study D/E/G cho cùng quyết định triển khai (chỉ D1 và D3).

**Không đổi:** model, giá, ngân sách, target, oracle, θ, η, α, n_max, seed held-out.
