# Nhật ký tìm target — không che các trường hợp bị loại

Ngày tổng hợp: 24/10/2026. Đây là tìm kiếm khám phá, không phải benchmark được
lấy mẫu ngẫu nhiên, không phải tìm kiếm đầy đủ mọi thư viện. Không dùng tỷ lệ
ứng viên giữ lại để ước lượng tỷ lệ chuyển giao của skill.

## Họ ORM/DSL

| Repo | Pin | Kết quả |
|---|---|---|
| sqlalchemy/sqlalchemy | `10f4d1e2d706a7722ca78e79ce05b00333a7aa5b` | 4 matcher sites; harmful được xác minh bằng test upstream. |
| coleifer/peewee | `beae2f0cf902841c8f72038b1e6f57faa8870ac4` | 0 production matcher sites tại pin đã quét; OUT_OF_SCOPE. |
| ponyorm/pony | `07136c853b180a5987523877a471a90296a5e2d8` | 0 production matcher sites; OUT_OF_SCOPE. |
| kvesteri/sqlalchemy-utils | `fbffdaca45a7835f128b79d392602a3c088df794` | 0 production matcher sites; OUT_OF_SCOPE. |
| sqlobject/sqlobject | `1dfb07bca80c35f2575e00e05fc9bdf6a40d6421` | 0 production matcher sites; OUT_OF_SCOPE. |

Quy tắc quét production loại thư mục test/testing/docs/examples; xem các JSON
`selection*` và `applicability_scan*` được lưu nguyên trạng. Các trường heuristic
như `bool_tests_referencing_function` của công cụ quét cũ **không được dùng làm
oracle hay bằng chứng hành vi cho skill 2**. Chỉ các lần chạy upstream test thực
sự mới dùng để xác nhận SQLAlchemy. Không tìm thấy matcher không có nghĩa là
chứng nhận an toàn của thư viện.

## Phía có lợi: các quyết định đáng chú ý

| Ứng viên / nguồn | Quyết định và lý do |
|---|---|
| NetworkX fix `2ae63c50fe8eb6647db18ee352bed08b21f21d91` | GIỮ. Ba sửa đổi đúng frozen transform. Test hành vi từ release 1.11 tái hiện lỗi array truth value; skill sửa được và khớp AST gold. |
| [PyMBAR PR #201](https://github.com/choderalab/pymbar/pull/201) | BLOCKED. Pin trước fix `681406bfecbe6660b0be63e0df397076fc708672`; thiếu compatibility ở nose/NumPy/testing hoặc fixture upstream. Python 3.8 + NumPy 1.17.5 vẫn cho 2 pass/13 failure không xác lập được lỗi mục tiêu. Không tính F→P hay harmful. |
| [ONNX #6588](https://github.com/onnx/onnx/pull/6588) | Loại khỏi đúng skill này: thay guard/getattr, không phải chỉ đổi phép so sánh None. |
| [ONNX Runtime #13103](https://github.com/microsoft/onnxruntime/pull/13103) | Truthiness → kiểm tra None; không khớp frozen Eq/NotEq transform. |
| [proto-plus-python #477](https://github.com/googleapis/proto-plus-python/pull/477) | Thay logic equality/Iterable, không đúng transform. |
| [GPyOpt #104](https://github.com/SheffieldML/GPyOpt/pull/104), [#106](https://github.com/SheffieldML/GPyOpt/pull/106) | Có mẫu array/None phù hợp nhưng chưa có witness upstream được tái lập trong lượt này; không tính là kết quả. |
| [Matplotlib #4057](https://github.com/matplotlib/matplotlib/pull/4057) | Cách sửa liên quan ndarray/list, không phải frozen None-identity transform. |
| [kartothek #106](https://github.com/JDASoftwareGroup/kartothek/pull/106) | Thêm guard quanh equality của Arrow; không đúng transform. |
| [attrs #1374](https://github.com/python-attrs/attrs/pull/1374) | Guard cho đối tượng falsey; không đúng transform. |
| [scikit-image #1026](https://github.com/scikit-image/scikit-image/pull/1026) | Hướng array/None khả dĩ nhưng chưa tái lập build lịch sử; không tính thêm một positive. |

Đây là ledger các quyết định tiêu biểu có nguồn, không phải bảng chấm điểm cho
mọi hit tìm kiếm. Chưa có số liệu chạy cho một ứng viên thì không suy ra nó an
toàn, có lợi hay có hại.

## Lỗi môi trường được giữ lại

* NetworkX: lượt đầu thiếu `decorator`; bổ sung dependency upstream vào môi
  trường, không sửa test. Log `networkx_baseline_pilot.log` được giữ.
* Khi tiếp tục phiên làm việc, Python 3.8 được quản lý ngoài workspace bị mất;
  log `networkx_initial_environment_failure.log` có exit 127. Cài lại interpreter
  đúng phiên bản rồi chạy ở thư mục output mới. Không tính lần này vào outcome.
* PyMBAR: giữ log nose/NumPy/fixture thất bại. Không biến failure do môi trường
  thành evidence rằng skill sửa lỗi hoặc gây hại.
* Việc thử nhiều ứng viên trước khi chốt NetworkX là lý do bắt buộc gắn nhãn
  khám phá/hồi cứu cho phần bổ sung này.

Các chi tiết và quyết định BLOCKED của Study G cũ được giữ nguyên trong
`study_g/VETTING_DECISIONS.md`. Bằng chứng mới không viết lại lịch sử đó.
