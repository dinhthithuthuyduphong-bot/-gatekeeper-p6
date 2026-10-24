# Study I — kết quả kiểm toán lượt GitHub Actions 40084717332

Ngày báo cáo: **24/10/2026**. Kết luận: **PASS — tái lập CI thành công**.
Không chạy thêm model hoặc thí nghiệm trả phí trong lần kiểm toán này. B9 giữ HOLD.

## 1. Lượt chạy và nguồn bằng chứng

* [GitHub run 40084717332](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40084717332).
* Commit thực thi: `5292b6a16ab4e68a62c24032e44c2d99b327498e`, attempt 1.
* Ba job `reproduce (networkx)`, `reproduce (sqlalchemy)` và `audit` đều được
  GitHub xác nhận `completed / success`.
* Nguồn kiểm toán: ba ZIP người dùng gửi, không dùng kết quả local cũ làm dữ
  liệu thay thế cho CI. Các log cũ chỉ được dùng để so sánh tái lập.

NetworkX đã chạy thực sự bằng **Python 3.8.20** trong virtualenv uv trên runner;
SQLAlchemy dùng **Python 3.12.14**. Lỗi setup-python trước đó đã được khắc phục
trong lượt CI này. Không còn tình trạng NetworkX bị bỏ qua trước khi chạy test.

## 2. Hai yêu cầu nghiên cứu đã đạt đến đâu?

| Yêu cầu | Bằng chứng CI đã xác minh | Kết luận phù hợp |
|---|---|---|
| Thêm harmful target có oracle cấp 1 ngoài pydal | SQLAlchemy: 9 test upstream nguyên trạng P→F, ổn định qua 3 lần chạy | Đã có thêm một target harmful với oracle hành vi upstream và tái lập CI |
| Thêm beneficial cell cho skill 2 | NetworkX: một upstream witness F→P; 54 test gốc giữ xanh; nhánh gold cùng kết quả; một scope admit diagnostic | Đã có case beneficial chạy thật và tái lập CI; vẫn là hồi cứu/khám phá |

Đây là tiến bộ về **bằng chứng thực nghiệm**, không chỉ thêm script hoặc workflow.
Hai yêu cầu hẹp đã có kết quả khả thi được tái lập trên GitHub. Chưa thể suy ra
toàn bộ các weakness của paper đã được giải quyết.

## 3. Đối chiếu test upstream

| Target / nhánh / nhóm | Pass | Fail | Error | Skip | Lặp |
|---|---:|---:|---:|---:|---:|
| SQLAlchemy baseline census | 1.552 | 0 | 0 | 1 | 3 |
| SQLAlchemy treated census | 1.543 | 9 | 0 | 1 | 3 |
| NetworkX baseline census | 54 | 0 | 0 | 0 | 3 |
| NetworkX baseline witness | 0 | 0 | 1 | 0 | 3 |
| NetworkX treated census | 54 | 0 | 0 | 0 | 3 |
| NetworkX treated witness | 1 | 0 | 0 | 0 | 3 |
| NetworkX gold census | 54 | 0 | 0 | 0 | 3 |
| NetworkX gold witness | 1 | 0 | 0 | 0 | 3 |

`Error` của baseline witness NetworkX là cách Nose ghi exception trong thân
test: ValueError do truth value của NumPy array tại phép so sánh `pos == None`.
Traceback đã được kiểm tra; không phải lỗi import, collection hoặc môi trường.

Chín `Fail` của SQLAlchemy sau skill là regression cần quan sát trong harmful
control. Workflow xanh vì tái lập đúng kết quả nghiên cứu và kiểm toán đúng;
không có nghĩa bản patch SQLAlchemy an toàn để triển khai.

Census chỉ bao gồm các module đã khai báo, không phải toàn bộ suite của hai repo.
Ba lần chạy kiểm tra ổn định, không được tính thành ba target độc lập.

## 4. Bốn cell và quyết định cuối

| Cell | Help / tie / hurt trên 300 cặp | Điểm dừng tuần tự | Quyết định cuối |
|---|---|---|---|
| SQLAlchemy / null_semantics | 0 / 69 / 231 | REJECT_HARM tại draw 3 | REJECT_CENSUS |
| SQLAlchemy / plain_queries | 0 / 300 / 0 | UNDECIDED tại 300 | REJECT_CENSUS |
| NetworkX / given_positions | 300 / 0 / 0 | ADMIT tại draw 80 | ADMIT_DIAGNOSTIC |
| NetworkX / default_positions | 0 / 300 / 0 | UNDECIDED tại 300 | QUARANTINE |

SQLAlchemy có census regression nên cả hai cell bị phủ quyết, kể cả scope
plain không có draw bị hại. Cả bốn cell được giữ trong họ e-Holm; cell bị veto
có e-value bằng 0. NetworkX given_positions có e-min tại dừng
**40,5469355317**, vượt ngưỡng K/alpha = 40.

Kiểm tra đổi thứ tự và khởi động worker mới mỗi 25 draw: **0 sai khác trên
400 cặp**, 0 lỗi harness. Đây là kiểm tra thực nghiệm trên các draw đã chọn,
không phải chứng minh tổng quát rằng mọi đầu vào đều độc lập hoặc không có trạng thái.

## 5. Những kiểm tra đã thực hiện lại trên artifact

1. Kiểm tra CRC ZIP, đường dẫn và tính toàn vẹn các file được giải nén.
2. Đối chiếu run ID, commit và trạng thái job trong các artifact với GitHub.
3. So byte toàn bộ `run/` của hai target với `inputs/` trong verified artifact:
   **47 file NetworkX + 23 file SQLAlchemy = 70 file giống hệt**.
4. Đối chiếu hash mã đo đạc với bản code đã kiểm chứng.
5. Chạy lại verifier từ **XML và JSONL thực tế của CI**: 24 lượt test, 1.200
   cặp draw và 400 cặp kiểm tra trạng thái. Tính lại label, count, stopped
   e-value, census veto và e-Holm.
6. `FAMILY_RESULT.json` tính lại **giống hoàn toàn** file trong verified artifact.
7. So với lần local trước: cùng 1.200 đầu vào draw và cùng Z. NetworkX có cùng
   danh tính/outcome test. SQLAlchemy có 87 test ID mỗi lượt khác hậu tố phiên
   bản SQLite: CI là `3.45.1`, local là `3.53.1`. Sau khi chỉ ánh xạ hậu tố
   phiên bản này để đối chiếu, toàn bộ outcome trùng nhau; không bỏ test nào.
   Lượt CI là bằng chứng tái lập, không cộng thêm thành mẫu khoa học độc lập.

Vì vậy không nên mô tả hai máy là môi trường giống hệt nhau. Trong từng lượt
CI, baseline/treated và ba lần lặp có cùng inventory như verifier yêu cầu.
Khác biệt SQLite giữa local và CI không làm đổi chín regression quan sát được;
phiên bản thư viện hệ thống này nên được ghi rõ trong bảng môi trường của paper.

`AUDIT_CHECKS.json`, `copy_and_code_integrity.json`, `GITHUB_RUN_CHECK.json`
và `RECHECK_LOCAL.log` lưu chi tiết kiểm toán.

## 6. Điểm cần chỉnh về tổ chức artifact

Hai artifact target còn chứa `networkx_local/`, `bootstrap_console.log`,
`networkx_github_failure.log` và các log từ lần sửa workflow trước. Kiểm tra
commit chạy cho thấy các file đó đã được commit dưới **`evidence/` ở root repo**;
workflow dùng cùng thư mục làm output nên upload cả dữ liệu cũ.

**Điều này không làm sai kết quả đã xác minh:** dữ liệu mới nằm trong `run/`,
được verifier đọc và khớp byte với verified artifact. Những log local cũ không
được tính vào số test/draw hoặc dùng để thay kết quả CI.

Gói bàn giao sạch chỉ giữ toàn bộ 70 file kết quả CI, family, context môi trường
của từng job và báo cáo kiểm toán. **Không bỏ test/draw nào của lượt CI mới**;
chỉ tách các log lịch sử không thuộc lượt này. Các ZIP gốc vẫn được giữ nguyên.

Để tránh lặp lại ở những lượt sau, nên dùng thư mục output riêng trong
`RUNNER_TEMP` hoặc một thư mục theo run ID không được commit vào repo. Không
cần sửa hay chạy lại thí nghiệm chỉ để xử lý việc đóng gói này. Lần kiểm toán
này chưa sửa workflow hoặc xóa file trên GitHub.

## 7. Chi phí và giới hạn khoa học

Log ghi 0 model calls; B9 vẫn HOLD. Không dùng credit API cho lần chạy này.
GitHub Actions và local verification vẫn tiêu tài nguyên runner/CPU.

Một số wall-clock đo được trên CI:

| Phép đo | Giây |
|---|---:|
| SQLAlchemy baseline census, trung bình 3 lượt | 6,4516 |
| SQLAlchemy treated census, trung bình 3 lượt | 7,2706 |
| SQLAlchemy null_semantics đến báo hại / đủ 300 draw | 1,1842 / 5,0379 |
| NetworkX baseline census, trung bình 3 lượt | 1,0778 |
| NetworkX treated census, trung bình 3 lượt | 1,0937 |
| NetworkX given_positions đến admit / đủ 300 draw | 1,4600 / 1,7949 |

Lượt chạy đã cố ý đi hết 300 draw để chẩn đoán và lặp test để kiểm chứng.
Không dùng chênh lệch thời gian trên làm claim tiết kiệm end-to-end cho production.

Giữ ba giới hạn trong paper:

* SQLAlchemy harm đã bị test upstream phát hiện: case này không chứng minh
  Gatekeeper hơn full retest.
* NetworkX là code lịch sử trong môi trường dependency khai báo; witness lấy
  từ bản phát hành upstream sau fix. Không mô tả nó thành test đi cùng commit fix.
* Target/scope đã được tìm và xem outcome: vẫn là **retrospective/exploratory**.
  CI thành công không biến thành study tiến cứu hoặc chứng minh độc lập với model.

## 8. Cập nhật main và bước tiếp theo

Không cần chạy lại workflow để xác nhận lượt này. Việc nên làm ngay là lưu
bằng chứng CI đã kiểm toán và cập nhật tiến độ bằng phạm vi claim đúng.

1. Giải nén gói `Study_I_CI_40084717332_Clean_Update.zip`.
2. Copy nội dung `main_update/` vào root repo. Gói chỉ thêm thư mục:
   `study_i/results/ci-40084717332/`.
3. Commit trực tiếp vào `main` nếu muốn lưu lâu dài trong repo. Không ghi đè
   `study_i/results/2026-10-24/` hoặc sửa các study đã đóng băng.
4. Không đưa thêm thư mục `evidence/` từ gói sửa workflow cũ vào root repo.

Muốn kiểm toán lại bản lưu, từ root repo chạy:

```bash
python3.12 study_i/verify.py --results study_i/results/ci-40084717332/inputs --output out-study-i-ci-recheck
```

Lệnh chỉ tính lại từ dữ liệu thô, không gọi model và không chạy target test mới.
Không cần mở B9 để hoàn tất hai mục tiêu hẹp đã xác minh. Nếu bước tiếp theo
là claim tiến cứu hoặc khái quát rộng hơn, cần protocol và dữ liệu đánh giá
mới trước khi mở rộng kết luận.

**Mẫu câu báo cáo phù hợp:** “Trong phần mở rộng hồi cứu của skill None-identity,
chúng tôi tái lập trên GitHub Actions một target harmful với test upstream
(SQLAlchemy) và một target beneficial với upstream behavioral witness
(NetworkX); các quyết định diagnostic và raw traces khớp lượt chạy local.”
