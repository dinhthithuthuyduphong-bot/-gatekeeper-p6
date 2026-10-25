# Kết quả 1 — SQLAlchemy: harmful target mới, oracle upstream cấp 1

Ngày: **24/10/2026**. Trạng thái: **ĐÃ TÁI LẬP LOCAL — EXPLORATORY**.
API model: **0 lượt gọi, 0 USD**. B9: **HOLD**.

**Cập nhật CI:** run [40084717332](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40084717332) đã tái lập thành công. Raw evidence và audit ở `results/ci-40084717332/`; chênh nhãn phiên bản SQLite đã được ghi rõ. Thời gian gốc dưới đây là số đo local ban đầu. Benchmark dừng thật bổ sung ở `../research_closure/results/cost/sqlalchemy/`.

## Kết luận được bằng chứng hỗ trợ

Áp nguyên skill `none-identity` đã đóng băng làm **9 test hành vi upstream của
SQLAlchemy chuyển từ pass sang fail**, ổn định trong ba lần chạy ở tiến trình mới.
Đây là target có hại bổ sung ngoài pydal, với oracle cấp 1 theo tiêu chí test
hành vi do upstream viết, được giữ nguyên và thực thi trực tiếp.

Target là **ORM/associationproxy của SQLAlchemy**. Các test Core metadata đã
chọn không xuất hiện regression; không gọi đây là kết quả harmful của pure Core.

## Pin và cách áp skill

* Gatekeeper main được kiểm tra: `13edea776af145ec897a1a992e9d7e054043ca25`.
* [SQLAlchemy source](https://github.com/sqlalchemy/sqlalchemy/tree/10f4d1e2d706a7722ca78e79ce05b00333a7aa5b):
  `10f4d1e2d706a7722ca78e79ce05b00333a7aa5b`.
* Python 3.12.14; dependency được khóa trong `requirements-sqlalchemy.txt`.
* Skill gốc: `study_g/skills/none-identity.json`; không chỉnh matcher/transform.
* Có 4 binding ở `lib/sqlalchemy/ext/associationproxy.py`,
  `lib/sqlalchemy/orm/relationships.py`, `lib/sqlalchemy/sql/schema.py`.
* Source replay và environment screen đều pass; các test được kiểm tra hash
  trước/sau để bảo đảm không đổi. Giấy phép upstream: MIT.

Ba module upstream chạy nguyên trạng:

1. [test_associationproxy.py](https://github.com/sqlalchemy/sqlalchemy/blob/10f4d1e2d706a7722ca78e79ce05b00333a7aa5b/test/ext/test_associationproxy.py)
2. [test_query.py](https://github.com/sqlalchemy/sqlalchemy/blob/10f4d1e2d706a7722ca78e79ce05b00333a7aa5b/test/orm/test_query.py)
3. [test_metadata.py](https://github.com/sqlalchemy/sqlalchemy/blob/10f4d1e2d706a7722ca78e79ce05b00333a7aa5b/test/sql/test_metadata.py)

## Kết quả thực thi

| Nhánh | Pass | Fail | Error | Skip | Số lần lặp |
|---|---:|---:|---:|---:|---:|
| Không skill | 1.552 | 0 | 0 | 1 | 3 |
| Có skill | 1.543 | 9 | 0 | 1 | 3 |

Cả ba lần có cùng danh tính test và cùng outcome. Đây là **1.553 test được thu
thập trong ba module đã chọn**, không phải toàn bộ test suite SQLAlchemy. Ba
lần chạy không được tính thành ba target hoặc ba quan sát thống kê độc lập.

Chín regression:

```text
ComparatorTest::test_filter_column_eq_None_nul
ComparatorTest::test_filter_eq_null_nul_nul
ComparatorTest::test_filter_object_eq_None_nul
ComparatorTest::test_filter_scalar_column_eq_nul
OperatorTest::test_m2o_compare_instance_aliased
OperatorTest::test_m2o_compare_instance_negated
OperatorTest::test_m2o_compare_instance_negated_warn_on_none
OperatorTest::test_selfref_relationship
WithTransientOnNone::test_negated_contains_or_equals_plain_m2o
```

Cơ chế lỗi: trong DSL này, `x == None` được overload để tạo biểu thức SQL
`IS NULL`. Đổi sang `x is None` tạo boolean Python, làm mất nhánh SQL xử lý NULL
trong các truy vấn quan hệ/association proxy. Đây không chỉ là thay phong cách
code; nó làm thay đổi truy vấn và các hàng được trả về.

## Gatekeeper diagnostic, tách khỏi tier-1 witness

Generator SQLite do nghiên cứu viên viết chạy 300 cặp mỗi scope. Oracle kiểm
tra danh sách ID thực tế trả về; nó không thay thế các test upstream nói trên.

| Scope | Help / tie / hurt trên 300 draw | Quyết định tuần tự | Quyết định sau census |
|---|---|---|---|
| null_semantics | 0 / 69 / 231 | REJECT_HARM sau 3 draw | REJECT_CENSUS |
| plain_queries | 0 / 300 / 0 | UNDECIDED ở 300 | REJECT_CENSUS |

Census có regression nên phủ quyết **toàn target đã patch**, kể cả scope plain.
Cả hai cell vẫn được giữ trong họ 4 cell với e-value bằng 0. Không báo admit
cho một scope chỉ vì riêng generator của scope đó chưa tìm thấy hại.

Kiểm tra đổi thứ tự, worker mới mỗi 25 draw: 100 draw/scope, **0/200 sai khác,
0 lỗi harness**. Đây là kiểm tra thực nghiệm, không phải chứng minh độc lập.

## Thời gian đo thực tế

Wall-clock trung bình mỗi lần chạy ba module: baseline **28,018 giây**
(19,048–39,260); treated **22,516 giây** (21,180–23,973).
Thời gian đến báo hại của generator: **3,094 giây**; chạy đủ scope NULL:
**20,926 giây**. Thời gian này phụ thuộc máy và gồm chi phí import/khởi tạo
phát sinh trong execute; không suy ra skill làm hệ thống nhanh hơn.

Lượt này vẫn chạy đủ 300 draw, toàn census và các lần lặp để kiểm chứng. Vì vậy
không lấy phần chênh lệch trên để tuyên bố tiết kiệm end-to-end trong triển khai.

## Bằng chứng và giới hạn

Trong gói cập nhật, xem `results/2026-10-24/sqlalchemy/`:
`RESULT.json`, `PRE_EXECUTION.json`, `skill.patch`, sáu file `.log` và `.xml`,
`draws.jsonl`, `statelessness.jsonl`, `STATELESSNESS.json`, `RESULT.md`.
Log tổng: `results/2026-10-24/sqlalchemy_execution.log`.

**Ý nghĩa:** giải quyết được nhu cầu có thêm một harmful target ngoài pydal với
test upstream mạnh. **Chưa chứng minh:** Gatekeeper vượt full retest, vì chính
census upstream đã bắt được chín regression. `9/1553` cũng không phải ước lượng
tỷ lệ hại của generator hoặc tỷ lệ hại ngoài thực tế.

Case được chọn qua tìm kiếm có quan sát outcome; ghi nhận là khám phá/hồi cứu.
Không chèn vào kết quả tiến cứu cũ và không tuyên bố đã giải quyết mọi weakness.
