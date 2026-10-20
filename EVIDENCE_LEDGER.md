# Sổ bằng chứng (evidence ledger)

Mỗi dòng là một lần chạy trên GitHub Actions. "Phạm vi" ghi rõ điều được và **không** được kết luận. Digest có dấu `…` là bản rút gọn (12 ký tự đầu, tính từ file artifact đã tải về); cần bổ sung đầy đủ từ trang Actions.

| Mốc | Run ID | Commit | Artifact (sha256) | Phạm vi |
|---|---|---|---|---|
| P6.6 runner closure | 38847724560 | 243e3a3 | OCR `d5300dac7b37…`, pandas `9fd43227a4ba…` | Runner phát triển: 24 container, seed cố định, timeout, cleanup. Không phải trial độc lập |
| P7.0 source skill expansion | 38876972775 | 2a27674 | click `08778db1b871…`, requests `36ffab807725…`, werkzeug `cf6abdc1801c…` | Ba nguồn sửa lỗi chạy lại được; test nguồn đã lộ; không phải transfer |
| P7.1 independent oracle pilot | 38916044021 | cf3b4da | skill `eb071b9152f3…`, oracle `1c25072a70ad…` | Skill đóng băng sửa ca đã biết nhưng hỏng một đầu vào mới; 1 cụm issue |
| P7.2 repaired source / independent scope | (bổ sung) | (bổ sung) | `bbc13f77dbd2…`, `8af2995ccefe…` | v2 sửa có thông tin về target (không độc lập); v2 từ chối ở cụm đối chứng âm |
| P7.3 anchored binder | 38996416312 | e5e4422 | exposed `66bdbae17445fc737b0a5eac34c6a3c2bab13314ea1c484f0fc2de03af6463a5`, source `16c2d4a7337111685abb8ee44e24dfde4c666c7ef70459117cc48b3234188045` | Binder v3 trên target đã dùng để phát triển (#3298): bằng chứng phát triển |
| Gatekeeper-Lite demo #2 | 39139075701 | 6908381 | `b58c2391c3e194ce5eeb8d490a5872ef5a834fe2d1095affe0101bab00564b64` | Toàn chuỗi trên target dựng sẵn; không phải repository độc lập |
| Gatekeeper-Lite demo #4 (demo + real-click v1) | 39141922266 | d028bae | demo `6b608e67bc2e41d4db4140c5c9209a7003509a57c934ee765ea281967db8f8d8`, real `23a404752829f67c06e30906d920ce208c1aded98093bedec16ee9beb38158e6` | Pipeline chạy trên Click thật lần đầu. Thiết kế R1 của bản này sai (commit chưa có nhánh cần sửa); thay bằng real-click v2 |
| P7 extract embedded sources | (bổ sung) | (bổ sung) | `P7_SOURCES_READABLE` | Mã P7.0–P7.3 giải nén ra dạng đọc được; binder v3 khớp hash `BINDER_FREEZE.json` |
| Gatekeeper-Lite demo #5 (real-click v2) | 39143998624 | f4f781c | demo `d2a7f166958da5729f37bda8d3b0a72644eb5383d6ce4bdb388d046caa391db6`, real `cdbaba9fb8f249be4fb9b139cb322f593691b4f586d81180538e0592996358e3` | 6 cặp: R1 có lợi (1 task phân biệt trên 552) với cả hai binder; R2 binder neo theo hàm từ chối, v3 áp dụng; R3 không đổi. B6-R và B8 admit 5/6; Gatekeeper QUARANTINE cả 5 (24 task lấy ngẫu nhiên không chạm task phân biệt) |
| Gatekeeper-Lite demo #7 (real-click v3) | 39145008309 | 6867531 | demo `274ee502c68146ce942e25b6ce2c0e4e26c1d41992b8e3929c72ed9b1c6913a7`, real `c50991eff60a675c8b2a8111de1e415fc7b53035aaeaa379e8abd282111ed5bf` | 4 cặp có hại (sửa ca so sánh chặt, hỏng ca chuỗi lazy rỗng): B6-R admit 4/4, B8 và Gatekeeper 0/4; Gatekeeper không admit cặp có lợi duy nhất. Nhãn có hại phụ thuộc lớp chuỗi lazy do mình khai báo; bỏ lớp này thì cả 4 thành có lợi |
| real-click v4 | (bổ sung) | (bổ sung) | `GK_LITE_REAL_CLICK_OUTPUT` | Kiểm định dấu: Gatekeeper REJECT_HARM 4/4 cặp có hại sau 14–17 task; B6-R admit 4/4; B8 reject 4/4; cặp có lợi duy nhất QUARANTINE. Bỏ lớp lazy thì cả 4 thành có lợi |
| real-click v5 | (bổ sung) | (bổ sung) | `GK_LITE_REAL_CLICK_OUTPUT` | Oracle metamorphic: B6-R admit 5/5 cặp có hại, B8 reject 5/5, Gatekeeper REJECT_HARM 4 + QUARANTINE 1; v3 trên 8.1.7 chuyển thành có hại (backport nhánh `""` làm help không nhất quán với chuỗi lazy rỗng) |
| Study B candidate scan v2 (tag) | (bổ sung) | (bổ sung) | `STUDY_B_CANDIDATE_SCAN` | asyncclick 8.3.0.6+async `4e5fea9cc5a3` chưa sửa; asyncclick ≥ 8.3.3 đã sửa; rich-click v1.9.5–v1.9.9 đều chưa sửa |
| real-click v5 lần chạy lại + demo | (bổ sung) | (bổ sung) | `GK_LITE_REAL_CLICK_OUTPUT_1`, `GK_LITE_DEMO_OUTPUT_1` | Hai lần chạy độc lập cho quyết định giống hệt nhau ở mọi cặp (tái lập) |
| Study B freeze | — | (commit gắn tag `study-b-freeze`) | `study_b/FREEZE.json` (28 file) | D1 kiểm định dấu; D2 e-BH FDR 0,1, dừng sớm ở E ≥ 40, tác hại ở e ≥ 20; D3 lớp lazy khai báo trước; D4 rich-click v1.9.9 + asyncclick 8.3.0.6 |
| Study B run #4 | 39218140976 | c571174 | `STUDY_B_OUTPUT` (chỉ PIP_FREEZE) | Qua kiểm tra đóng băng, dừng ở bước tải target; chưa chạy cặp nào. Sửa bằng Amendment A1 |
| Study B run sau A1 | (bổ sung) | (bổ sung) | `STUDY_B_OUTPUT` (chỉ PIP_FREEZE) | Dừng trước khi tạo kết quả, không có log; sửa bằng Amendment A2 |
| **Study B v1 (sau A2)** | 39219880641 | (bổ sung) | `STUDY_B_OUTPUT` `fe28cc2896dc5bcae18c4ef8a6fcb87d4103f4217bac3264721bb60a0bd54722` | **Bằng chứng prospective đầu tiên.** rich-click v1.9.9 + asyncclick 8.3.0.6: B6-R admit 3/3 cặp có hại; B8 reject 3/3 (2.224 lượt); Gatekeeper REJECT_HARM 3/3 sau 9 task (1.166 lượt); v3 từ chối ở rich-click. Bỏ lớp lazy: cả 3 có lợi. Bộ test gốc rich-click không chạy (thiếu `typer`). Chi tiết: `study_b/results/` |
| Study B v1 chạy lại (tái lập) | 39221665509 | (bổ sung) | `STUDY_B_OUTPUT` `918a6001f7bd3ac77224a22659a87947f793a7f2c2958f1caf5d4b490a24609b` | Quyết định, số task và danh sách task sửa/hỏng giống hệt lần chạy chính: xác nhận tái lập, không đổi kết quả |
| real-click v5 + demo chạy lại | 39221649072 | (bổ sung) | `GK_LITE_REAL_CLICK_OUTPUT`, `GK_LITE_DEMO_OUTPUT` | Giống hệt các lần trước |
| Study B S1 (hậu kiểm) lần 1 | 39249192992 | (bổ sung) | `STUDY_B_S1_OUTPUT` | Bộ test gốc rich-click vẫn không chạy (`pyproject` yêu cầu `pytest-cov`); oracle metamorphic cho cùng kết quả Study B. Sửa: thêm `pytest-cov` |
| Quét ứng viên vòng 3 | 39249187394 | (bổ sung) | `STUDY_B_CANDIDATE_SCAN` | 9 repository hệ sinh thái Click: không có site trên giá trị default. Tổng 3 vòng: 15 repository, 2 đủ điều kiện (đã dùng ở Study B) |
| Study C freeze | — | (tag `study-c-freeze`) | `study_c/FREEZE.json` | Regime A: 6 bản phát hành Click chưa chạy × 2 binder × 2 scope = 24 ô; oracle metamorphic v2 |
| **Study C v1** | 39250346083 | (bổ sung) | `STUDY_C_OUTPUT` `0c60525862de328fe68dadca0bc9ba4ffd194921d7bed4b3993ff2137a35a27a` | **H1–H3 xác nhận** trên 6 bản Click chưa chạy: Gatekeeper admit 12/12 ô *đối tượng*, REJECT_HARM 12/12 ô *chuỗi lazy*; B6-R admit cả 24 ô (12 có hại); chi phí Gatekeeper 5.128 so với B8 9.200. Ablation: `study_c/results/ABLATION_study-c-v1.md` |
| Study B S1 (hậu kiểm) lần 2 | 39250323194 | (bổ sung) | `STUDY_B_S1_OUTPUT` `a1d92b3ce7fdd8b8d760b45e85557c561cab4e112c092a8b0ceef5b23f70bdec` | Bộ test gốc rich-click đã chạy (29 task) nhưng cả 29 đều fail ở cả hai nhánh (môi trường không khớp), nên không cho thông tin; kết luận Study B giữ nguyên |
| Study B run (thử) | (bổ sung) | (bổ sung) | `STUDY_B_OUTPUT` (chỉ PIP_FREEZE) | Dừng có chủ đích: protocol còn DRAFT. Không có kết quả Study B nào được tạo ra |
| Study B candidate scan v1 | (bổ sung) | (bổ sung) | `STUDY_B_CANDIDATE_SCAN` | rich-click `4ee6d4b27950` có site chưa guard trong `_get_parameter_default`; asyncclick HEAD đã sửa; typer, click-extra, cloup không có site |

## Thay đổi thiết kế sau đánh giá phản biện (20/10/2026)

Study B/C được hạ xuống **bằng chứng pilot** vì đếm các ca gần trùng lặp thành bằng chứng độc lập, dùng thứ tự ưu tiên và FDR. Thiết kế chính mới là Study D (`study_d/STUDY_D_PROTOCOL_DRAFT.md`): scope là bộ sinh đầu vào i.i.d., bộ test gốc là cổng census, chứng nhận ít tác hại η = 0,05, e-Holm (FWER).

## Kiểm định target Study D (lần 1)

| Target | Kết quả | Ghi chú |
|---|---|---|
| Cerberus `2b63c1b9` → `d25ae8f6` (Python 3.8.18) | **ĐẠT** | 1 test fail trước/pass sau: `TestValidation::test_boolean_is_not_a_number`; 146 test giữ pass |
| py_ecc `5cb90f33` → `fe448d99` (PR #161, Python 3.12.15) | **ĐẠT** (lần 2) | 5 test fail trước/pass sau qua API công khai; 96 test giữ pass; 5 test import helper mới bị loại. Lần 1 chưa kết luận do lỗi công cụ (pytest dừng cả phiên vì lỗi collection) |

## Mở rộng bộ dữ liệu Study D (20/10/2026)

Thêm ứng viên dương D3 spec-kit #3268, D4 open-feature #621, D5 pycubrid #479; đối chứng khả năng áp dụng A1 spec-kit #2589; đối chứng no-op C1 jsonschema v4.23.0; đối chứng ngữ nghĩa C2 voluptuous 0.15.2. D3–D5 và A1 chờ kiểm định (workflow `vet-targets.yml`).

## Kiểm định target Study D (lần 3, 20/10/2026)

| Target | Kết quả | Chi tiết |
|---|---|---|
| D3 spec-kit #3268 (merge 13/7/2026, `903d707d`) | **ĐẠT** | 1 test fail trước/pass sau (`TestExtensionPriorityCLI::test_set_priority_repairs_corrupted_bool`), 342 test giữ pass; fix upstream trùng dạng skill |
| D4 open-feature #621 (merge 30/8/2026, `7d945ec5`) | **ĐẠT** | 11 test fail trước/pass sau, 80 test giữ pass; kiểu kiểm tra qua biến `py_type`, fix còn đổi giá trị trả về |
| D5 pycubrid #479 (merge 2/10/2026, `4efe599d`) | Chạy lại | `conftest.py` cần `hypothesis`; fix upstream trùng dạng skill |
| A1 spec-kit #2589 (merge 21/5/2026, `0dee2faf`) | **ĐẠT** | 1 test fail trước/pass sau, 245 test giữ pass; fix nằm trước `int(...)`, không qua `isinstance` |
| D1 py_ecc, D2 Cerberus | Tái lập đúng | |

## Ghi chú tái lập Study B

Sau Study B, `gatekeeper_lite/` có thêm admission theo scope (`scoped.py`), nên `freeze_study.py verify study_b` trên `main` sẽ báo file thay đổi — đúng như thiết kế, để không ai chạy lại Study B bằng code mới. Muốn tái lập Study B v1, checkout tag `study-b-freeze-a2`.

## Việc còn thiếu để tái lập

- Mã P7.x đang được **nhúng trong file workflow** dưới dạng base64 nén xz (ví dụ `p7-3-anchored-binder.yml`, bước "Unpack frozen binder revision and exposed target"). Mã chạy được và đóng băng, nhưng người đọc không xem hay diff được. Cần giải nén ra dạng đọc được bằng `python tools/extract_embedded_payload.py .github/workflows/p7-3-anchored-binder.yml p7/p7_3` và commit thư mục `p7/` kèm `MANIFEST.json` (sha256 của payload và từng file).
- Gắn tag cho các commit bằng chứng, ví dụ `p7.3-evidence` → `e5e4422`, `gk-lite-demo-v1` → `6908381`.
- Prospective pairs (trên target độc lập, protocol đóng băng trước): **0**.
