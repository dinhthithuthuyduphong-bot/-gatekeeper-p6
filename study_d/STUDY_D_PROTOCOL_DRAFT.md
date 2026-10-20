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

## 7. B9 (sửa lỗi bằng LLM, khớp ngân sách)

1. **Một repair instance sinh một patch**, rồi patch đó được đánh giá trên các scope, giống skill.
2. **Cùng quyền sửa và cùng thông tin đầu vào với skill:** được sửa nhiều hàm hoặc thêm helper nếu skill được phép.
3. **Lọc bằng test công khai, chấm bằng oracle kín.**
4. **Ngân sách định nghĩa trước:** số lần gọi model, token, số lần chạy test. Quy định trước cách xử lý khi hết ngân sách trước khi đủ số mẫu.
5. **Chỉ số chính:** tỉ lệ thành công của **patch thực sự được nộp** trong ngân sách. pass@k chỉ là chỉ số phụ.
6. Trước 30/10 chỉ kiểm tra đường đi bằng phản hồi ghi sẵn và model giả; kết quả này **không** tính là bằng chứng B9.

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

## 10. Không được claim

Khái quát sang repository hoặc nhiệm vụ ngoài scope đã khai báo; vượt B6 theo một mốc điểm phần trăm; tỉ lệ quần thể; tiết kiệm chi phí khi chưa đo trên harness thật.
