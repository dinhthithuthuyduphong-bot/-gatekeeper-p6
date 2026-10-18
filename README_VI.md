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
python -m unittest discover -s tests -v                              # 21 test
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

Job thứ hai trong workflow chạy cùng pipeline trên mã Click thật, chấm bằng **test gốc của Click** (`tests/test_options.py`, không sửa assertion):

| Target | Revision | Vai trò |
|---|---|---|
| R1 | `c021f05c` (commit cha của bản sửa nguồn), test lấy từ bản sửa `d3e3852e` | Đã thấy (nguồn của skill): kiểm tra pipeline trên code thật |
| R2 | tag `8.1.7` | Chưa xem, chọn trước khi chạy |
| R3 | tag `8.2.1` | Chưa xem, chọn trước khi chạy |

Skill `click-empty-default-guard` là cùng phép sửa với binder v3 (thêm `isinstance(x, str)` trước `x == ""`), neo vào hàm `get_help_record` / `get_help_extra`. B6-R replay so sánh **đúng hàm** `get_help_record` giữa kết quả sinh ra và bản sửa chính thức. Script `tools/fetch_real_targets.py` ghi commit thực tế của từng checkout vào `FETCH_RECEIPT.json`.

**Điều nên chờ đợi và cách đọc:** mỗi target chỉ có rất ít test chạm đúng biên đã sửa, trong khi file test có hàng trăm test. Vì vậy Gatekeeper nhiều khả năng QUARANTINE (bằng chứng không đủ), trong khi B6-R và B8 admit. Đây không phải lỗi: nó cho thấy trên dữ liệu thật, một bản sửa đơn lẻ không tạo đủ bằng chứng thống kê, đúng với phát hiện "evidence adequacy" ở Week 5. Kết quả R2, R3 được ghi nguyên trạng, kể cả khi binder từ chối (ví dụ code đã được sửa sẵn).

Phần này chưa được chạy ở môi trường của tôi (không có mạng và pytest); lần chạy đầu tiên trên Actions là lần kiểm chứng.

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
tests/             21 unit test
.github/workflows/ gk-lite-demo.yml
```
