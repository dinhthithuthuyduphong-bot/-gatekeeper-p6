# Trạng thái công việc và kết quả đọc mã nguồn — 25/10/2026

**Gói này chuẩn bị lượt chạy tiếp theo trên GitHub. Chưa chạy các script mới,
unit tests mới, baseline Pydantic, scout mở rộng hay benchmark mới. Không gọi
model, không chi API, B9 vẫn HOLD.** Người dùng chạy workflow rồi cung cấp raw
artifact để quyết định bước tiếp theo. Không tự push hoặc dispatch workflow.

Main được đối chiếu ở commit `fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293`.
Run Study I thành công đã có là `40084717332`; không có run mới của gói này.

## Đã xác minh được gì?

| Hạng mục | Bằng chứng hiện có | Kết luận được phép |
|---|---|---|
| Pydantic-settings | Khảo sát tĩnh trước đây hoàn tất: 3 vị trí bool-guard, 0 none-identity, 0 lượt test/treatment; đọc lại source ở pin bên dưới | Là ứng viên để kiểm tra reach của **skill 1**, chưa giúp chứng minh skill 2 |
| Airflow | Đọc `clean_perms`, `sync_roles` và test upstream trên snapshot sau revert; có chuỗi lời gọi tiềm năng | Lead cho skill 2, chưa có tái lập regression tier-1 |
| pandas, NumPy, sqlalchemy-utils, peewee, Pony | Đã chốt 5 revision trong roster | Chưa chạy lượt quét mới; không có số match/outcome để báo |
| SQLAlchemy | Study I đã tái lập 9 test upstream pass→fail; selected census 1.553 test | Target gây hại bổ sung đã có; census cũng bắt được lỗi này |
| NetworkX | Bằng chứng hồi cứu có lợi Study I đã lưu | Không được tính lại thành kết quả mới của lượt follow-up |
| python-control | Study K đã đo ở lượt trước: 15 pass/1 fail→16 pass; gold cùng kết quả, 3 lần/nhánh | Có lợi hồi cứu; test upstream là smoke test, coverage mới 2/3 vị trí sửa |

**Không có target gây hại/có lợi mới nào được xác nhận trong lượt chuẩn bị này.**
Các log đo ở lượt trước nằm trong `Gatekeeper_Final_ZeroCost_20261025.zip` và
repository sau khi áp dụng gói đó; bản NEXT delta không nén lại các file không
thay đổi. Việc đóng gói không biến chúng thành số đo mới.

### Pydantic-settings: phần bị hiểu là “dừng khảo sát”

Pin: `pydantic/pydantic-settings@7e2dacb6db07b41abb0c80d0608e46e197265554`.
Nguồn khảo sát đã lưu: `research_closure/results/candidate_screen/pydantic__pydantic-settings.json`.
Các vị trí đọc lại:

- `pydantic_settings/sources/providers/cli.py:108`: `_count_option_values`, kiểm tra `action.nargs` là `int`.
- `pydantic_settings/sources/utils.py:385`: `_literal_has_numeric_enum`, kiểm tra kiểu số.
- `pydantic_settings/sources/utils.py:449`: `_get_alias_names`, phần tử của alias path là `int`.

Chưa biết bool có tới các vị trí này hay không, test có assertion phân biệt
ngữ nghĩa đó hay không, và loại bool có vi phạm contract upstream hay không.
Workflow sẽ chạy **nhánh nguyên bản** trong ba tiến trình mới, thu inventory,
setup/call/teardown, JUnit, coverage theo node ID và lỗi môi trường.
Một baseline xanh chỉ đưa tới `BASELINE_STABLE_ORACLE_REVIEW_PENDING`.
Không có nhánh treatment tự động trong runner này.

Môi trường chọn Python 3.12.14; dependency lấy phiên bản từ `uv.lock` của đúng
snapshot. Chỉ dùng wheel; nếu không có wheel hoặc baseline thất bại thì lưu
nguyên lỗi, không tự hạ phiên bản hoặc đổi oracle để có màu xanh.

### Airflow: lead đáng kiểm tra, chưa phải bằng chứng tier-1

Pin: `apache/airflow@b35972fc9c727065097f0654a40a0fe39890b204`.
`airflow/www/security.py` có `clean_perms` và hai phép so sánh None trong query;
`sync_roles` gọi `clean_perms`. Test không sửa đổi
`tests/www/test_security.py::test_no_additional_dag_permission_views_created`
gọi `sync_roles` và kiểm số lượng association permission/view/role không tăng.
Chuỗi này **chưa chứng minh** fixture chứa orphan permission mà đổi sang `is None`
sẽ làm kết quả khác đi. Kết nối theo tên hàm chỉ là overapproximation.

Lượt này chuẩn bị source scout giữ nguyên assertion/hash để review; không cài
Airflow lịch sử hoặc tự viết assertion rồi gọi nó là upstream tier-1.
Tài liệu upstream về PR #6109/#6222 đã lưu trong `study_k/search_evidence/`.

## Phần đã bổ sung để chạy tiếp

1. `next_evidence/source.py`: quét 7 source snapshot cố định, giữ site, assertion
   tham chiếu, lỗi parse và matcher. Không import/chạy code của target. Loại
   examples và test khỏi số production match; lỗi parse không bị gọi là zero-match.
2. `next_evidence/baseline.py` và `pytest_probe.py`: 3 baseline Pydantic có raw
   phase logs, JUnit, coverage, kiểm source/test hash và module thực sự được import.
3. `next_evidence/cost.py`: cùng census ở cả ba policy, dừng ngay khi census veto,
   ba lần lặp với thứ tự cân bằng; lưu thời gian thật và raw draw journals.
4. `next_evidence/verify_cost.py`: tính lại từ XML/journal, kiểm hash, số draw,
   prefix/decision của hai policy có generator, thành phần thời gian và mean.
5. Workflow `Gatekeeper next evidence - zero-cost`: chạy audit trước, lưu artifact
   khi lỗi và gom thành **next-evidence-return-a1** (số cuối là run attempt). Chỉ chạy thủ công trên main
   của repo public; không dùng secret model hoặc quyền ghi repository.

Đối chiếu census-only rất cần thiết: SQLAlchemy dự kiến bị cả ba policy từ chối
ngay sau census, nên khác biệt thời gian còn lại không chứng minh lợi thế thống kê.
NetworkX sẽ cho biết phần chi phí thêm để có chứng nhận theo generator.
Ba policy không cung cấp cùng bảo đảm; không được dùng bảng thời gian để che mất
khác biệt này. Dữ liệu mới vẫn là exploratory trên target đã biết.

## Tình trạng kiểm tra của gói

- **Trước lượt này:** gói trước đã có log 129 unit tests và 12 nhóm audit PASS.
- **Lượt này:** chỉ đọc source, kiểm cấu trúc Python/JSON/YAML và tính toàn vẹn
  file đóng gói. Không chạy compiler, unit tests, target tests, benchmark hoặc
  cài dependency. Các test mới chỉ được chuẩn bị để GitHub chạy.
- Các kiểm tra của gói trước **không chứng nhận** code mới đã chạy đúng. Xem
  `PACKAGE_CHECKS/DELTA_CHECK.json` trong NEXT cho việc so sánh và đóng gói.
  Log 129 tests / 12 audits ở `PACKAGE_CHECKS/validation/` của gói FINAL,
  không được sao chép lại và không chứng nhận runtime của code mới.

### Cập nhật cách đóng gói

NEXT chỉ chứa 21 file repository khác FINAL: 16 file mới và 5 file sửa. Không
chứa lại 444 file repository giống hệt FINAL, PDF riêng hoặc log thực nghiệm
cũ. Script/workflow giữ nguyên như lần chuẩn bị NEXT trước; chỉ sửa hướng dẫn
áp dụng delta và bổ sung helper kiểm các hash nền FINAL. Không phát sinh
thí nghiệm mới từ lần đóng gói này.

Các receipt fetch source mới nằm ở
`research_closure/results/next_evidence_source_review/`. Những phần chưa có
outcome được giữ là `PREPARED_NOT_EXECUTED`, không thêm số liệu giả vào bảng paper.
