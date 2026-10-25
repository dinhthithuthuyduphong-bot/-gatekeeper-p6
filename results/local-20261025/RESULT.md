# Python-control: kết quả hồi cứu được kiểm tra từ log thô

**VERIFIED_EXPLORATORY**; 0 lời gọi model; B9 HOLD.

| Nhánh | Pass | Fail chức năng | Lặp tiến trình mới |
|---|---:|---:|---:|
| Baseline | 15 | 1 | 3 |
| Skill đóng băng | 16 | 0 | 3 |
| Gold upstream | 16 | 0 | 3 |

Giữ nguyên toàn bộ 16 test của module upstream. Một test Nyquist F→P, 15 test đang pass được giữ; không có regression mới.

| Scope | Quyết định chẩn đoán | Draws đến dừng | Help / tie / hurt trong 300 draws |
|---|---|---:|---|
| K1_python_control/array_frequencies | ADMIT_DIAGNOSTIC | 65 | 300 / 0 / 0 |
| K1_python_control/default_frequencies | QUARANTINE | 300 | 0 / 300 / 0 |

Kiểm tra lại 100 draws/scope bằng thứ tự khác và worker mới mỗi 25 draws: không thấy sai khác.

Giới hạn: hồi cứu, một repo/phiên bản, selected-module census; test upstream là smoke test. Oracle số học riêng do nhóm nghiên cứu viết. Hai trong ba vị trí sửa được các draw scopes đi qua; gangof4_plot chưa được bao phủ. Không tuyên bố an toàn cho toàn repo, prospective success hay tiết kiệm chi phí từ lượt replay đầy đủ này.

Raw: RESULT.json, PRE_EXECUTION.json, 9 XML + log, skill.patch, draws.jsonl và statelessness.jsonl.
