# Python-control — thêm một target có lợi cho skill thứ hai

**Đã tái lập được một trường hợp có lợi bằng test upstream không đổi.** Đây là
kết quả hồi cứu, không phải bằng chứng tiến cứu hoặc khái quát trên mọi repo.
Ngày đóng gói: 25/10/2026. Chi phí API: 0 USD. B9 vẫn HOLD.

| Bằng chứng | Kết quả |
|---|---|
| Baseline, toàn bộ module `control/tests/frd_test.py` | 15 pass, 1 fail chức năng |
| Áp skill `none_identity` đã đóng băng | 16 pass, 0 fail |
| Áp bản sửa upstream cho cùng module nguồn | 16 pass, 0 fail |
| Lặp | Ba tiến trình mới mỗi nhánh; kết quả nhất quán |
| Regression trên 15 test baseline đang pass | 0 |
| Scope cấp mảng tần số | 300 help / 0 tie / 0 hurt; dừng chẩn đoán ở draw 65 |
| Scope tần số mặc định | 0 help / 300 tie / 0 hurt; QUARANTINE |
| Kiểm tra state/thứ tự | 100 draws/scope, worker mới mỗi 25 draws; 0 sai khác |
| Reach của vị trí sửa | 100% draws đi qua một vị trí sửa; tổng cộng 2/3 vị trí được bao phủ |

Nguồn:

- Parent: [fb5ebf6296079229705792cc508ad23d45e326aa](https://github.com/python-control/python-control/commit/fb5ebf6296079229705792cc508ad23d45e326aa).
- Fix: [60aba3ab39cef2ac11c4bc08c2b08a9abd084205](https://github.com/python-control/python-control/commit/60aba3ab39cef2ac11c4bc08c2b08a9abd084205).
- Test gốc: `TestFRD.testNyquist`, có sẵn tại parent. Baseline ném `ValueError`
  tại `omega == None` khi nhận NumPy array; skill đổi thành phép so sánh identity.
- Mã skill tạo ra tương đương AST với file `control/freqplot.py` của fix upstream.
  Chỉ module đã khai báo được sửa, không áp toàn bộ commit upstream.

**Không gộp chất lượng nguồn oracle với độ mạnh của assertion:** test upstream này
là smoke test “chạy không exception”, không kiểm tra giá trị số hay hình đồ thị.
Oracle draw riêng kiểm tra đáp ứng phức theo công thức giải tích và phải được ghi
là do nghiên cứu viên viết. Đã chạy toàn bộ module 16 test, không deselect test lỗi.

Runtime: CPython 3.8.20, NumPy 1.17.5, SciPy 1.4.1, Matplotlib 2.2.5, Slycot
0.4.0.0. Đây là môi trường tương thích được ghim, không phải runtime nguyên gốc
năm 2014. Các lần thất bại khi dựng môi trường đều được giữ trong artifact.

Raw chính: [RESULT.md](results/local-20261025-clean/RESULT.md),
`RESULT.json`, `PRE_EXECUTION.json`, 9 XML + log, `draws.jsonl`,
`statelessness.jsonl`, `skill.patch` và `VERIFIED.json` cùng thư mục.
Runner và bộ kiểm toán không gọi model hoặc mở khóa paid B9.

**Còn thiếu:** cohort mới được đóng băng công khai trước treatment; target gây
hại độc lập tiếp theo; kiểm chứng các API/vị trí ngoài scope (đặc biệt
`gangof4_plot`); so sánh thêm với smoke/census mạnh và kết quả theo model.
Không nâng kết quả này thành chứng nhận triển khai toàn patch trên toàn repo.
