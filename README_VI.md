# Gatekeeper-Lite — bản demo end-to-end

Bộ code này chạy trọn chuỗi quyết định của Gatekeeper trên một bộ target dựng sẵn:

```
skill S = ⟨π, D, I, P, K⟩ + target
  → scope screen (D, I)          → OUT_OF_SCOPE nếu không hợp
  → binder (AST, abstain khi mơ hồ)
  → paired trials (không skill / có skill, cùng snapshot, cùng seed)
  → e-process (bằng chứng tích lũy)  → ADMIT nếu Eₙ ≥ 1/α, nếu không QUARANTINE
  + so sánh với B2, B6-R, B8 · kiểm tra composition · retirement khi môi trường đổi
```

> **Loại bằng chứng: CONSTRUCTED_DEMO_FIXTURES.** Target là dựng sẵn để minh hoạ cơ chế. Kết quả không phải bằng chứng nghiên cứu về chuyển giao trên repository độc lập.

Chỉ dùng thư viện chuẩn của Python (≥ 3.9; đã chạy với 3.12.3). Không cần Docker để chạy cục bộ.

## Chạy nhanh

```bash
# ở thư mục gốc của repo (hoặc thư mục chứa gatekeeper_lite/)
python -m unittest discover -s tests -v                              # 31 test
python -m gatekeeper_lite run --config demo/config.json --out out_demo
python -m gatekeeper_lite show out_demo/RESULT.json T2_help_lazy     # giải thích 1 cặp
```

Kết quả: `out_demo/REPORT.md` (báo cáo tiếng Việt) và `out_demo/RESULT.json` (đầy đủ: diff code, kết quả từng task, quỹ đạo e-process, alpha đã chi, hash cấu hình).

Trên GitHub: chạy workflow `.github/workflows/gk-lite-demo.yml` (tự tìm thư mục dự án, chạy unit test và demo, đưa REPORT.md vào trang Summary, upload artifact `GK_LITE_DEMO_OUTPUT`). Ghim SHA của action theo `actions.lock` trước khi dùng làm bằng chứng.

## Ánh xạ với paper

| Thành phần paper | File | Ghi chú |
|---|---|---|
| Skill package S = ⟨π, D, I, P, K⟩ | `skill.py`, `demo/skills/*.json` | π là một transform AST; P là ví dụ before/after của nguồn |
| Procedure π, footprint K | `transforms.py` | Viết lại đúng đoạn mã khớp, giữ nguyên phần còn lại; abstain: `NO_MATCH`, `MULTIPLE_MATCHES`, `ALREADY_GUARDED`, `BUILTIN_SHADOWED`, `MISSING_SYMBOL` |
| Scope screen: I(x) ∧ Compatible(D, x) | `screen.py` | Quan hệ môi trường MATCH / DRIFT / UNRESOLVED; thiếu thông tin thì không admit |
| Paired trials, pair integrity | `runner.py`, `harness.py` | Hai nhánh copy từ cùng snapshot, chỉ khác file được sửa; mỗi nhánh một process |
| STR, Z, loss | `runner.py`, `gatekeeper.py` | Z theo task ∈ {−1, 0, 1}; loss của bộ test = (1 − tỉ lệ pass) + 0,5 mỗi regression, chặn [0, 1] |
| e-process, ngưỡng 1/α (Theorem 4) | `eprocess.py` | E-process cá cược cho H₀: E[Z] > −θ; có test kiểm tỉ lệ vượt ngưỡng nhầm ≤ α |
| Alpha theo cell, không tái chế | `eprocess.py` (`AlphaLedger`) | Epoch k chi α·6/(π²(k+1)²), tổng các epoch ≤ α của cell |
| Composition (Theorem 7) | `gatekeeper.py`, `experiment.py` | Footprint giao nhau → bài toán admission riêng cho skill ghép |
| Retirement | `gatekeeper.py` (`retirement_check`) | Fingerprint đổi → thu hồi, kiểm lại với alpha của epoch mới |
| B1, B2, B6-R, B8 | `gatekeeper.py` (`comparators`) | B6-R là bản tái dựng: bind + replay nguồn + fingerprint; B8 chạy mọi task |

## Kết quả demo hiện tại

| Target | Skill | Nhãn thật | B2 | B6-R | B8 | Gatekeeper |
|---|---|---|---|---|---|---|
| T1 · default là object bất kỳ | empty-string-guard | có lợi | ADMIT | ADMIT | ADMIT | **ADMIT** (21 task) |
| T2 · default là chuỗi lazy | empty-string-guard | **có hại** | ADMIT | **ADMIT** | REJECT | **QUARANTINE** |
| T3 · đã có guard | empty-string-guard | — | ngoài scope | REJECT | ngoài scope | ABSTAIN |
| T4 · `str` bị alias | empty-string-guard | — | ngoài scope | REJECT | ngoài scope | ABSTAIN |
| T5 · cổng không nhận bool | negative-bool-guard | có lợi | ADMIT | ADMIT | ADMIT | **ADMIT** (18 task) |
| T6 · bool được tính là 0/1 | negative-bool-guard | **có hại** | ADMIT | **ADMIT** | REJECT | **QUARANTINE** |
| T7 · ghi DB | retry-write | có lợi | ADMIT | ADMIT | ADMIT | QUARANTINE |
| T7 · ghi DB | async-write | có lợi | ADMIT | ADMIT | ADMIT | QUARANTINE |

Số đếm thô: cặp có hại bị admit — B2 2/2, B6-R 2/2, B8 0/2, Gatekeeper 0/2. Cặp có lợi được admit — B8 4/4, Gatekeeper 2/4. Chi phí: B8 278 lượt chạy task, Gatekeeper 226.

**Composition (T7):** retry-write và async-write đều có lợi khi dùng riêng (Z = −0,14 và −0,21), nhưng ghép lại có hại (Z = +0,64: ghi trùng khi ack bị mất sau commit). Footprint giao nhau (`func:save`, `call:write`…). B6-R admit từng skill riêng nên không bắt được; Gatekeeper coi skill ghép là bài toán riêng và QUARANTINE.

**Retirement (T1):** đổi `clicklike` 8.1.7 → 8.2.0 làm fingerprint đổi → thu hồi mà không cần test fail; kiểm lại với alpha nhỏ hơn và chưa đủ bằng chứng nên QUARANTINE. Đổi sang 9.0.1 → DRIFT → ngoài scope.

**Cách đọc đúng:** Gatekeeper không an toàn hơn B8 (B8 cũng chặn 2/2 ca có hại), đúng như paper dự phóng. Điểm khác là B8 phải chạy mọi task, còn Gatekeeper dừng sớm khi đủ bằng chứng; đổi lại Gatekeeper bỏ lỡ 2 ca có lợi vì ngân sách và ngưỡng chặt. Đây là sự đánh đổi an toàn–lợi ích–chi phí, không phải chiến thắng tuyệt đối.

## Thí nghiệm trên mã Click thật (job `real-click`)

Job thứ hai chạy cùng pipeline trên mã Click thật, chấm bằng **test gốc của Click** (`tests/test_options.py`, không sửa assertion). Hai skill cùng một phép sửa (thêm `isinstance(x, str)` trước `x == ""`), được học từ bản sửa Click #3298 (`04ef3a6f` → `14588004`):

- `click-empty-default-guard`: binder neo theo hàm của Gatekeeper-Lite;
- `click-guard-v3`: **binder v3 của P7.3**, chạy nguyên bản đã đóng băng qua `p7/p73_binder_cli.py` (từ chối chạy nếu hash khác `BINDER_FREEZE.json`).

| Target | Revision | Vai trò |
|---|---|---|
| R1 | `04ef3a6f` (commit cha của #3298), test lấy từ bản sửa `14588004` | Nguồn của skill, đã thấy (P7.3) |
| R2 | tag `8.1.7` | Chưa xem, chọn trước khi chạy |
| R3 | tag `8.2.1` | Chưa xem, chọn trước khi chạy |

Kiểm tra ngoại tuyến trên mã Click lấy từ artifact P7: cả hai binder đều bind ở `get_help_extra` của R1, B6-R replay khớp đúng hàm đã sửa của bản chính thức, và 4 file của v3 khớp hash đóng băng.

**Cách đọc:** ở R1 test của bản sửa chạm đúng biên, nên paired trial có tín hiệu. Ở R2, R3, test của chính bản phát hành không có ca đối tượng so sánh chặt, nên nhiều khả năng "không quan sát thấy khác biệt dưới oracle không chạm biên": B6-R và B8 admit, Gatekeeper không đủ bằng chứng. Đây là kết quả có ích cho paper (độ đủ của oracle), không phải lỗi.

**Bản v3 của thí nghiệm (mới):**

- *Oracle biên dùng chung* `real/oracle_templates/test_gk_boundary.py`, mô phỏng đúng test chính thức #3298, được chèn nguyên vẹn vào mọi target (hash ghi trong `FETCH_RECEIPT.json`). Các nhóm: đối tượng so sánh chặt (8), array-like (4), chuỗi thường và chuỗi rỗng (3), chuỗi lazy (2), chuỗi lazy rỗng (6). Kỳ vọng do người nghiên cứu khai báo (oracle phát triển, viết sau khi đã nghiên cứu P7), không phải oracle đánh giá độc lập.
- *Lọc task theo khả năng chạm* (`task_filter: reach_baseline`): một lượt pytest **chỉ trên code gốc** ghi lại test nào gọi tới hàm bị sửa (`gatekeeper_lite/pytest_reach.py`). Gatekeeper chỉ lấy mẫu trong các task này, vì task không chạm hàm bị sửa luôn có Z = 0. Bộ lọc được quyết định trước khi xem treatment; chi phí lượt lọc được cộng vào chi phí Gatekeeper.

Kiểm tra ngoại tuyến oracle biên trên mã Click thật lấy từ artifact P7:

| Nhóm | Số ca | Commit cha #3298 | Sau khi áp skill | Bản sửa chính thức |
|---|---|---|---|---|
| Đối tượng so sánh chặt | 8 | 0 pass | 8 | 8 |
| Array-like | 4 | 0 | 0 | 0 |
| Chuỗi thường, chuỗi rỗng, chuỗi lazy | 5 | 5 | 5 | 5 |
| Chuỗi lazy rỗng | 6 | 6 | **0** | **0** |

Array-like hỏng ở một phép so sánh khác (`default_value not in (None, UNSET)`), nằm ngoài phạm vi skill. Bản sửa #3298, kể cả bản chính thức, đổi lỗi với đối tượng so sánh chặt lấy thay đổi hành vi với chuỗi lazy rỗng (theo kỳ vọng đã khai báo).

**Lưu ý lịch sử:** bản sửa nguồn trước đó (`d3e3852`) chính là commit **thêm** nhánh `default_value == ""`; nhánh này về sau gây lỗi #3298 với default không phải chuỗi. P7.1 đã cho thấy skill học từ bản sửa đó có lợi ở ca đã biết nhưng có hại ở đầu vào mới.

## Chuẩn bị Study B (không tốn tiền)

- **Kiểm định dấu trên cặp bất đồng** (`evidence: discordant_sign`): task có Z = 0 không làm mất bằng chứng; có thêm kiểm định tác hại, dừng với `REJECT_HARM`. Có test kiểm tỉ lệ sai lầm loại I của cả hai kiểm định.
- **Thứ tự task theo ưu tiên khai báo trước** (`task_priority`): chỉ phụ thuộc tên task.
- **Phân tích độ nhạy** (`sensitivity_exclude`): nhãn thật tính lại khi bỏ một lớp task, hiện trong REPORT.md.
- **Mô phỏng lực:** `python tools/power_sim.py out_real/RESULT.json [--exclude lazy]`.
- **Quét ứng viên:** workflow `study-b-scan.yml` (chỉ đọc) → artifact `STUDY_B_CANDIDATE_SCAN`.
- **Bản nháp protocol:** `study_b/STUDY_B_PROTOCOL_DRAFT.md` (4 quyết định cần chốt).

## Kịch bản demo 5 phút cho thầy

1. **Vấn đề (1 phút):** `show out_demo/RESULT.json T2_help_lazy`. Cùng một sửa đổi (thêm `isinstance(x, str)`) đúng ở T1 nhưng làm hỏng 16 task ở T2, vì chuỗi lazy không phải `str`. B6-R vẫn ADMIT vì replay ở nguồn pass và fingerprint khớp.
2. **Cơ chế (2 phút):** `show … T1_help_strict`. Diff, bảng task có/không skill, quỹ đạo Eₙ tăng đến ngưỡng 66 thì ADMIT. Với T2, Eₙ giảm và không bao giờ vượt ngưỡng.
3. **Từ chối đúng (30 giây):** T3, T4 bị ABSTAIN với lý do cụ thể.
4. **Composition và retirement (1 phút):** phần cuối `REPORT.md`.
5. **Giới hạn (30 giây):** target dựng sẵn; task là một case trong một target, không phải repository độc lập; B6-R là bản tái dựng.

## Cắm binder v3 và target thật

**Binder v3 của bạn:** khai báo skill với transform `external_command`:

```json
"pi": {"transform": "external_command",
       "params": {"command": "python /path/anchored_binder.py --in {input} --out {output} --receipt {receipt}",
                  "behaviors": ["eq-empty-string"]}}
```

Script cần ghi file đã sửa vào `{output}` và receipt JSON: `{"status": "APPLIED", "sites": [{"line": 12, "function": "...", "snippet": "..."}], "footprint": [...]}` hoặc `{"status": "ABSTAIN", "reason": "..."}`. Nếu CLI của v3 khác, chỉ cần viết một wrapper nhỏ theo hợp đồng này.

**Target thật dùng pytest:** trong `gk_target.json` của target, khai báo:

```json
"oracle": {"kind": "pytest", "tests": ["tests/test_options.py::test_show_default_with_empty_string"]}
```

Runner chạy pytest ở cả hai nhánh và đọc báo cáo JUnit; test bị skip được coi là thiếu, không phải pass. Phần đọc JUnit đã có unit test, nhưng tôi chưa chạy được pytest thật ở môi trường của mình, nên hãy chạy thử một target thật trên Actions trước khi demo.

## Kế hoạch 1 tuần đến buổi demo

| Ngày | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Đưa code vào repo, chạy unit test và demo cục bộ và trên Actions | Đã xong: run `39139075701` |
| 2 | Viết wrapper cho binder v3 theo hợp đồng `external_command`; chạy lại T1–T4 bằng v3 | v3 cho cùng quyết định hoặc ghi rõ khác biệt |
| 3 | Thêm 1 target thật (Click ở revision có #3298) với oracle pytest; ghi exposure: đây là target đã thấy | Một cặp thật ở mức development |
| 4 | Đóng băng P7.4 (file protocol đã gửi) và chọn 2–3 target chưa thấy; chỉ chạy dry-run binder | Danh sách ứng viên + exposure registry |
| 5 | Chạy các cặp P7.4 đã đóng băng; báo cáo số đếm thô | Bằng chứng đầu tiên trên target chưa thấy (có thể là 0 cặp đủ điều kiện) |
| 6 | Tập kịch bản demo, kiểm tra lại giới hạn và claim | Bản demo 5 phút |
| 7 | Dự phòng | — |

## Giới hạn và điều không được claim

- Target là dựng sẵn; tỉ lệ trong demo không đại diện cho repository thật.
- Một "task" là một case trong một target, nên các task không phải mẫu i.i.d. từ nhiều repository như Assumption 3 của paper yêu cầu.
- B6-R là bản tái dựng, không phải B6 của paper. B9 (thử sửa thêm cùng ngân sách) chưa có vì cần backend sinh code.
- Tham số (θ = 0,1, α tổng 0,25, ngân sách 24 task) được chọn cho demo và đã ghi trong `demo/config.json`. Đổi tham số sau khi xem kết quả thì phải ghi rõ.
- Không claim: Gatekeeper-Lite giảm harmful transfer ở mức quần thể, vượt B6 ≥ 5 điểm phần trăm, hay an toàn hơn B8.

## Cấu trúc thư mục

```
gatekeeper_lite/   skill.py screen.py transforms.py runner.py harness.py
                   eprocess.py gatekeeper.py experiment.py report.py __main__.py
demo/config.json   tham số đóng băng, danh sách cặp, composition, retirement
demo/skills/       4 skill JSON
demo/sources/      ví dụ before/after của nguồn (dùng cho replay)
demo/targets/      T1–T7: mã nguồn, oracle_cases.py, gk_target.json
real/              thí nghiệm trên Click thật: skill, 3 target, config_real.json
tools/             fetch_real_targets.py (tải mã nguồn đã đóng băng trên Actions)
p7/                binder v3 của P7.3 (đóng băng) + wrapper
study_b/           protocol nháp, ứng viên, mô phỏng lực
tests/             31 unit test
.github/workflows/ gk-lite-demo.yml
```
