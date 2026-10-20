# Study D — protocol nghiên cứu chính (BẢN NHÁP, đóng băng dự kiến 30/10/2026)

Bản này thay thế thiết kế thống kê của Study B/C. Các quyết định dưới đây đã đối chiếu với một bản đánh giá phản biện độc lập (20/10/2026), và các lỗi mà bản đánh giá chỉ ra đều được sửa.

## 0. Đóng góp nghiên cứu (cách phát biểu)

Một quy trình admission cho skill sửa lỗi, có **kiểm soát sai số trên scope đã khai báo**, có **phân biệt scope**, và có **đo chi phí thực tế**. Các thành phần thống kê (e-process betting, e-Holm) là phương pháp có sẵn. Giá trị nghiên cứu nằm ở: cách xây oracle và scope kiểm tra được, bằng chứng chuyển giao giữa repository, và so sánh với B2/B6-R/B8/B9.

## 1. Trạng thái của Study B/C: hạ xuống bằng chứng pilot

Study B/C đếm các ca gần như trùng lặp thành bằng chứng độc lập (6 ca chuỗi lazy rỗng giống hệt nhau, 12 ca so sánh chặt chỉ khác nhãn), ưu tiên thứ tự task theo oracle, và dùng FDR. Vì vậy e-value của chúng bị thổi phồng. Kết quả Study B/C được giữ nguyên làm **minh hoạ cơ chế và pilot**, không dùng làm bằng chứng thống kê chính.

## 2. Estimand và cách lấy mẫu

- **Scope là một bộ sinh đầu vào đã khai báo** G_s, gồm một điều kiện sử dụng kiểm tra được (hàm bị sửa và lớp kiểu của đầu vào) cùng một bộ sinh ngẫu nhiên. Mỗi task là một **lần rút i.i.d.** từ G_s; giả định i.i.d. được thỏa **do cách xây dựng**. Estimand: μ_s = E_{x~G_s}[Z] và h_s = P_{x~G_s}(regression). Không còn đơn vị gần trùng lặp: phân phối của bộ sinh xác định trọng số.
- **Z theo từng lần rút** ∈ {−1, 0, +1}, chấm bằng oracle metamorphic hoặc oracle đặc tả của scope.
- **Tác hại theo từng lần rút** (có regression hay không), tách riêng khỏi lợi ích, không dùng tác hại ròng.
- **Bộ test gốc của target là cổng toàn bộ (census):** chạy đủ một lần ở mỗi nhánh. Có bất kỳ regression mới nào thì không admit ở mọi scope. Kết quả cổng này là **chính xác**, không cần thống kê.
- **Phạm vi khái quát:** chỉ áp dụng cho G_s trên target ở commit đã ghim. Không có tuyên bố suy luận về "mọi repository".

## 3. Quy tắc quyết định (mỗi ô = skill × target × scope)

- **Lợi ích:** e-process betting cho H0: μ_s ≥ −θ, với **θ = 0,2**.
- **Chứng nhận ít tác hại:** e-process cho H0: h_s ≥ η, với **η = 0,05** (mức chọn trước, không chỉnh theo kết quả).
- **Báo động tác hại** (dừng sớm): e-process cho H0: h_s ≤ η, ngưỡng 1/0,05.
- **Dừng:** REJECT_HARM khi báo động vượt ngưỡng; ADMIT khi min(e_lợi ích, e_chứng nhận) ≥ K/α (mức e-Bonferroni, mà e-Holm luôn chấp nhận). Nếu không, dừng ở **n_max = 300** lần rút.
- **Đa ô:** **e-Holm, FWER α = 0,1** trên min(e_lợi ích, e_chứng nhận) tại điểm dừng. Phân tích phụ: e-BH q = 0,1 và kiểm định dấu, đều gắn nhãn thăm dò.
- **Không có nhánh "dưới 7 lớp thì không thể admit".** Nếu scope là quần thể hữu hạn được chạy hết (census), kết luận là chính xác trên quần thể đó.

**Mô phỏng toàn bộ quy tắc** (`tools/decision_sim.py`; K = 8, α = 0,1):

| Kịch bản | Nên admit? | P(ADMIT) | P(REJECT_HARM) | Số lần rút (trung vị) |
|---|---|---|---|---|
| Tốt, không hại | có | 1,000 | 0 | 95 |
| Tốt, 60% hòa | có | 1,000 | 0 | 95 |
| Tốt, hại hiếm 2% | có | 0,439 | 0,002 | 300 (chạm ngân sách) |
| Biên h = η = 5% | không | 0,013 | 0,021 | 300 |
| Biên μ = −θ | không | 0,001 | 0 | 300 |
| Hỗn hợp 30% hại | không | 0 | 1,000 | 8 |
| Toàn hại | không | 0 | 1,000 | 2 |

Chứng nhận ít tác hại chiếm phần lớn chi phí của một lần admit (khoảng 95 lần rút sạch). Đây là cái giá thật của yêu cầu an toàn, và được báo cáo như vậy. Độ nhạy với η = 0,10 và n_max = 600: `DECISION_SIM_eta010_n600.md`.

## 4. Ngẫu nhiên hoá

Đóng băng bộ sinh, oracle và danh sách target trước. Sau đó seed được tính bằng `sha256(hash FREEZE.json ‖ randomness của vòng drand quicknet đầu tiên sau thời điểm đóng băng T)`, với T ghi trong protocol. Seed không thể được chọn lại sau khi thấy kết quả.

## 5. Lỗi và dừng

- **Trước treatment:** chạy bộ test gốc ở nhánh không skill 3 lần. Test nào lỗi collection, fail hoặc không ổn định thì bị loại khỏi cổng census, theo quy tắc ghi sẵn.
- **Sau treatment:** lỗi theo giai đoạn (collection, setup, call). Lỗi chỉ ở nhánh có skill được kiểm lại một lần; nếu vẫn còn thì tính là tác hại. Lỗi ở cả hai nhánh là lỗi có sẵn và được báo cáo riêng.
- **Dừng chủ động vì đã quyết định** được ghi là `STOPPED_DECIDED`, không bị phân loại thành lỗi môi trường (exit code 2 của pytest).
- Không loại task hay scope sau khi đã thấy kết quả.

## 6. Target và tiêu chí nghiệm thu benchmark

Họ lỗi thứ hai: **loại bool khỏi kiểm tra kiểu int**.

| Target | Vai trò | Căn cứ đối chiếu |
|---|---|---|
| py_ecc: merge-base → PR #161 | Dương (tái phát hiện độc lập) | PR đã merge 7/10/2026; thêm `is_integer()`, sửa nhiều vị trí, có test |
| Cerberus: d25ae8f^ → d25ae8f | Dương (tái phát hiện độc lập) | Sửa `_validate_type_number` (kiểu *number*, **không phải** *integer*) |
| voluptuous (HEAD) | Đối chứng ngữ nghĩa | Maintainer coi việc chấp nhận bool là đúng (issue #443): skill **được kỳ vọng gây hại** |
| jsonschema (HEAD) | Đối chứng no-op | Đã có guard; skill phải không đổi gì |
| packaging #1425 | **Loại** khỏi nhóm dương | Đóng nhưng không merge; ngữ nghĩa còn tranh luận |

**Kết quả kiểm định lần 1:** Cerberus **đạt** (`test_boolean_is_not_a_number` fail trước/pass sau; 146 test giữ pass). py_ecc chưa kết luận vì một file test import helper mới làm dừng cả phiên pytest; công cụ đã được sửa để tiếp tục chạy các file khác.

**Kết quả kiểm định lần 2 (đã sửa công cụ):** py_ecc **đạt**: 5 test fail trước/pass sau qua API công khai (`FQ(True)`, `FQ(1) + True`, `FQ2([True, 2])`, `FQ2([1, 2]) * True` trên 4 đường cong; `G2Basic.SkToPk(True)`), 96 test giữ pass; 5 test import helper mới bị loại đúng quy tắc. Cerberus **đạt** như lần 1. Diff cho thấy Cerberus kiểm tra kiểu qua bí danh `_int_types`; skill đã đóng băng (học từ PySStuBs ở tuần 3) chỉ nhận `int` viết trực tiếp, nên **dự kiến từ chối ở Cerberus**. Không thêm khả năng phân giải bí danh vào skill chính, vì thông tin này đến từ diff của target; nếu có, chỉ làm biến thể thăm dò, ghi rõ.

**Oracle rút mẫu (đã viết, chưa chạy trên target đánh giá):** `oracles/py_ecc_bool.py` (scope *bool*: kỳ vọng `TypeError`/`ValidationError` theo test upstream; scope *int*: oracle vi sai, hành vi không đổi) và `oracles/cerberus_bool.py` (scope *bool*: `validate` trả False; scope *number*: vi sai).

**Harness đã nghiệm thu trên dữ liệu phát triển** (`DrawHarnessAcceptanceTests`): skill có lợi được ADMIT sau 80 lần rút và dừng thật trước ngân sách; skill có hại bị REJECT_HARM sau 2 lần rút; B8 chạy tiếp tới ngân sách và được ghi riêng.

**Nghiệm thu một target dương:** (1) có test **fail trước fix, pass với gold fix** (`tools/vet_target.py`, workflow `vet-targets.yml`); (2) oracle dùng API công khai, chạy được trên cả bản trước và sau fix (test import helper mới bị loại); (3) bộ regression cũ vẫn pass; (4) test oracle cuối không dùng để chỉnh skill hay chọn patch B9.

Họ Click giữ vai trò dữ liệu phát triển và pilot. Hai bản kế thừa requests (niquests, pip vendored) chỉ dùng làm đối chứng no-op và **không** tính là hai bằng chứng chuyển giao độc lập.

**Điểm kiểm tra 25/10:** nếu có ít hơn 2 target dương đã qua nghiệm thu ngoài repository nguồn, thu hẹp tuyên bố chuyển giao hoặc đổi họ lỗi. Không bù bằng các biến thể test gần giống nhau.

## 6b. Bộ dữ liệu Study D (chốt 20/10/2026): 8 target, 16 ô

Mọi target đều là fix **đã được upstream merge** và đã qua kiểm định (có test fail trước fix, pass với bản merge; bộ test cũ giữ pass). Mọi oracle viết từ mã test và fixture upstream, trước khi chạy skill lên target.

| Mã | Target (commit trước fix) | Vai trò | Kiểm định | Dạng mã so với skill |
|---|---|---|---|---|
| D1 | py_ecc `5cb90f33` (PR #161) | Dương | 5 F→P, 96 P→P | `isinstance(x, int)` trực tiếp, nhiều file |
| D2 | Cerberus `2b63c1b9` (d25ae8f) | Dương | 1 F→P, 146 P→P | qua bí danh `_int_types`: skill dự kiến từ chối |
| D3 | spec-kit `f6f35404` (PR #3268) | Dương | 1 F→P, 342 P→P | trùng đúng dạng skill |
| D4 | open-feature `93296c6e` (PR #621) | Dương | 11 F→P, 80 P→P | qua biến `py_type`; fix còn đổi giá trị trả về |
| D5 | pycubrid `068325e7` (PR #479) | Dương | 1 F→P, 50 P→P | trùng đúng dạng skill |
| A1 | spec-kit `7fda89de` (PR #2589) | Đối chứng khả năng áp dụng | 1 F→P, 245 P→P | bool lọt vào `int(...)`, không qua `isinstance` |
| C1 | jsonschema v4.23.0 | Đối chứng no-op | — | đã loại bool |
| C2 | voluptuous 0.15.2 | Đối chứng ngữ nghĩa | — | chấp nhận bool là có chủ ý |

Với K = 16 ô (`DECISION_SIM_K16.md`): skill tốt, không hại được admit 100% sau khoảng 110 lần rút; admit sai ở sát biên ≤ 0,9%; skill có hại bị chặn sau 2–8 lần rút.

Oracle của D3–D5 được viết **sau** kiểm định, chỉ từ mã nguồn các test fail-trước/pass-sau mà công cụ kiểm định thu về, và trước khi đóng băng. Target nào không đạt kiểm định thì bị loại, ghi rõ lý do; không bù bằng biến thể gần giống.

**Ablation đăng ký trước** (`tools/ablation_study_d.py`, chạy lại trên kết quả từng lần rút đã ghi, không chạy thêm): đầy đủ; bỏ chứng nhận ít tác hại; bỏ cổng census; e-Bonferroni thay e-Holm; kiểm định dấu thay e-process trung bình; η = 0,10. Trên dữ liệu phát triển, bỏ chứng nhận ít tác hại làm số lần rút để admit giảm từ 80 xuống 13: đây là chi phí đo được của yêu cầu an toàn.

**Composition và retirement (GK-16):** chỉ minh hoạ trên dữ liệu phát triển (demo T7 và retirement trên Click). Study D không đưa ra claim nào về hai cơ chế này.

**Báo cáo cuối** được sinh hoàn toàn từ file kết quả gốc (`tools/report_study_d.py`): bộ dữ liệu, quyết định theo ô (B2, B6-R, B8, Gatekeeper e-Holm, e-BH phụ), chi phí đo được, B9, ablation và giới hạn.

## 7. B9 (sửa lỗi bằng LLM, khớp ngân sách)

1. **Một repair instance sinh một patch**, rồi patch đó được đánh giá trên các scope, giống skill.
2. **Cùng quyền sửa và cùng thông tin đầu vào với skill:** được sửa nhiều hàm hoặc thêm helper nếu skill được phép.
3. **Lọc bằng test công khai, chấm bằng oracle kín.**
4. **Ngân sách định nghĩa trước:** số lần gọi model, token, số lần chạy test. Quy định trước cách xử lý khi hết ngân sách trước khi đủ số mẫu.
5. **Chỉ số chính:** tỉ lệ thành công của **patch thực sự được nộp** trong ngân sách. pass@k chỉ là chỉ số phụ.
6. Trước 30/10 chỉ kiểm tra đường đi bằng phản hồi ghi sẵn và model giả; kết quả này **không** tính là bằng chứng B9.

**Cài đặt (đã nghiệm thu bằng model giả, `B9AcceptanceTests`):** `gatekeeper_lite/b9.py`, `tools/run_b9.py`, `study_d/b9_config.json`, `study_d/b9_instances/`.
- **Đầu vào cho model:** mô tả lỗi (diễn đạt lại từ issue/PR upstream, không chứa mã của bản fix), toàn bộ các module được phép sửa, và một kiểm tra công khai (một ca của test hồi quy upstream, viết qua API công khai).
- **Ngân sách:** tối đa 5 lần gọi, 4.000 token đầu ra mỗi lần, 5 lần chạy kiểm tra công khai. Lần gọi đầu temperature 0, các lần sau 0,8. Mỗi cặp (target, model) lặp lại 3 lần.
- **Chấm điểm:** patch được nộp được chấm bằng **đúng** oracle rút mẫu đã đóng băng (đủ n_max lần rút) và cổng census.
- **Model:** DeepSeek `deepseek-flash` và Gemini 3.1 Flash-Lite qua endpoint tương thích OpenAI; khoá API lấy từ secret của repo. Giá ghi theo tháng 10/2026 và được ghi lại vào ngày chạy.
- **Chặn chi tiền sớm:** chế độ `record` (gọi trả phí) chỉ chạy khi config là FROZEN và sau 31/10/2026. Cassette lưu mọi phản hồi, nên chạy lại ở chế độ `replay` không tốn thêm tiền.
- **Trần đợt pilot trả phí:** 400.000 đồng.
- **Khớp ngân sách:** báo cáo theo hai đơn vị (lần gọi/token/USD và lần chạy test); không tuyên bố một tỉ giá quy đổi duy nhất giữa chi phí Gatekeeper và B9.

## 8. Đo chi phí

- Hai worker riêng (hai môi trường Python), mỗi worker chạy một nhánh, có bộ điều phối ghép cặp kết quả. Gatekeeper chạy thật từng lần rút và dừng thật; B8 chạy đủ theo cùng quy ước.
- Ghi số lần rút, số test, thời gian, tách chi phí cố định (khởi tạo, cổng census, lọc) và chi phí biên. Báo cáo **điểm hòa vốn** nếu tiết kiệm chỉ xuất hiện sau nhiều lần tái dùng.

## 9. Mốc nghiệm thu đến 30/10

| Mốc | Kết quả phải có |
|---|---|
| 20–22/10 | Protocol này nhất quán; mô phỏng quy tắc quyết định (đã có) |
| 23–25/10 | Target có commit cụ thể, oracle fail-trước/pass-sau, nguồn chứng cứ; loại target còn tranh luận |
| 26–28/10 | Harness hai worker chạy được; B9 qua các tình huống chấp nhận với model giả; đo chi phí thật so với chạy đủ |
| 29–30/10 | Tái lập từ môi trường sạch, đóng băng, chốt dự toán và tiêu chí chi tiền |

## 9b. Quy trình đóng băng và tái lập

- **Chạy khói (smoke)** trước khi đóng băng (workflow `study-d-smoke.yml`): toàn bộ bộ chạy (seed drand, hash, áp skill nhiều module, census, rút mẫu, tổng hợp, ablation, báo cáo) trên target phát triển `demo/targets/T5_port_bool`, không đụng dữ liệu đánh giá.

- **Kiểm tra tái lập từ môi trường sạch** (workflow `clean-room.yml`, `tools/clean_room_check.py`): unit test, quyết định demo khớp `demo/EXPECTED_DECISIONS.json`, mô phỏng tái tạo đúng `DECISION_SIM_default.md`, hash đóng băng.
- **Đóng băng một lần bấm** (workflow `study-d-freeze.yml`): chạy unit test; đặt `FROZEN`, `frozen_on` và `seed_time_utc` = thời điểm đóng băng + 60 phút; tính lại `FREEZE.json` (41 file); commit và gắn tag `study-d-freeze`. Từ chối đóng băng lần hai.
- **Chạy Study D** (workflow `study-d-run.yml`) sau `seed_time_utc`: kiểm tra trạng thái và hash, rồi chạy hai target; `tools/aggregate_study_d.py` tổng hợp e-Holm và e-BH.

## 10. Không được claim

Khái quát sang repository hoặc nhiệm vụ ngoài scope đã khai báo; vượt B6 theo một mốc điểm phần trăm; tỉ lệ quần thể; tiết kiệm chi phí khi chưa đo trên harness thật.
