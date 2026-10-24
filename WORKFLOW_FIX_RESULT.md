# Sửa lỗi runtime của workflow Study I — 24/10/2026

Trạng thái: **bản sửa đã kiểm tra local; chờ chạy workflow mới trên GitHub**.
Không gọi API model, không dùng GCP credit. B9 giữ **HOLD**.

## Nguyên nhân đã xác minh

Run [40081924050](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40081924050)
chạy commit `92af60052d8962d3ba3495ccee7958accae7a7db`.

| Job | Kết quả quan sát từ GitHub |
|---|---|
| SQLAlchemy / 3.12.14 / Ubuntu 24.04 | SUCCESS. Chín regression dự kiến được tái lập; hai scope kiểm tra trạng thái không sai khác. |
| NetworkX / 3.8.20 / Ubuntu 22.04 | FAIL tại setup-python, trước cài dependency và trước mọi test. |
| Audit | SKIPPED vì một job reproduce thất bại. |

Kho runtime mà `actions/setup-python` sử dụng không có Python 3.8.20 cho tổ hợp
runner yêu cầu. Manifest được đọc tại thời điểm kiểm tra có bản 3.8.18, nhưng
không có 3.8.20. Workflow ban đầu đã giả định sai rằng runtime này có sẵn.

Bước `mkdir -p evidence` trước đây nằm sau setup-python. Khi setup lỗi, bước
đó bị bỏ qua, nên upload-artifact không có file để upload. Hai annotation là
một lỗi runtime và một lỗi hệ quả; không phải test NetworkX đã thất bại, cũng
không phải pattern loại `work/**` tự làm mất các file kết quả.

Nguồn chính thức:

* [Python versions manifest](https://github.com/actions/python-versions/blob/main/versions-manifest.json).
* [setup-uv hướng dẫn cài Python bằng uv](https://github.com/astral-sh/setup-uv/blob/07a047e608db84b3d8c06cd9a7c7dcc9c355c18e/README.md).

## Nội dung bản sửa

Chỉ thay **`.github/workflows/study-i-zero-cost.yml`**.

1. Giữ SQLAlchemy và audit dùng setup-python 3.12.14 đã chạy thành công.
2. Riêng NetworkX dùng setup-uv được pin commit, uv **0.13.4**, cài đúng
   **Python 3.8.20**, tạo virtualenv riêng và đưa đường dẫn vào `GITHUB_PATH`.
3. Giữ nguyên sáu dependency NetworkX, source pin, skill, oracle, seed, threshold
   và các kết quả đã ghi. Kiểm tra chính xác patch version trước khi chạy test.
4. Tạo `evidence` trước runtime setup. Thêm bước `always()` ghi trạng thái job
   trước upload, kể cả khi setup thất bại. Audit có bước tương tự.
5. Giữ lỗi thực sự làm workflow đỏ: không dùng `continue-on-error`, không hạ
   mức kiểm tra kết quả, không gộp họ giả thuyết nếu thiếu target.

Workflow vẫn chỉ chạy thủ công, quyền `contents: read`, không dùng secret B9/GCP.
Thư mục source `work/` vẫn bị loại khỏi artifact; JSON, JSONL, XML và log được giữ.

## Kiểm chứng thực tế của bản sửa

Đã chạy các block Bash của workflow mới trong workspace local riêng, cài mới
Python 3.8.20 và virtualenv chỉ có sáu dependency đã khóa. Các action JavaScript
setup/upload của dịch vụ GitHub không được giả lập và chưa được chạy lại trên CI.

| Kiểm tra | Kết quả |
|---|---|
| YAML, trigger, quyền và Bash của mọi bước | PASS; workflow 5.335 byte, dưới giới hạn 500 KB |
| uv cài đúng Python 3.8.20 và virtualenv | PASS |
| NetworkX baseline census | 54 pass × 3 lần |
| NetworkX baseline witness | Một ValueError chức năng dự kiến × 3 lần |
| Skill và gold | 54 census + 1 witness đều pass × 3 lần mỗi nhánh |
| Generator | 600 cặp; cùng trace/outcome với lần xác minh trước |
| State/order check | 0 sai khác / 200 cặp; 0 lỗi harness |
| Kiểm toán XML/JSONL bằng verify.py | PASS: 18 lượt test, 600 cặp draw, 200 cặp kiểm tra trạng thái |
| Mô phỏng setup trả exit 1 | Vẫn sinh job-status.txt ghi failure; lỗi setup không bị bỏ qua |

Generator `given_positions` vẫn đạt ADMIT diagnostic ở draw 80; scope default
vẫn quarantine ở 300. Không có thay đổi kết luận khoa học do bản sửa runtime.
Đây là tái lập thêm của case đã biết, không phải target độc lập hoặc bằng chứng
tiến cứu mới.

Các thời gian đo local trong `evidence/bootstrap_result.json`: cài Python/venv
**7,357 giây**; cài dependency và kiểm tra runtime **16,601 giây**; chạy test,
generator và kiểm tra trạng thái **36,198 giây**. Đây không phải dự báo thời gian
GitHub Actions. Toàn bộ console, XML và JSONL nằm trong gói log đi kèm.

## Cách cập nhật và chạy

1. Mở file hiện tại trên GitHub:
   [.github/workflows/study-i-zero-cost.yml](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/blob/main/.github/workflows/study-i-zero-cost.yml).
2. Thay toàn bộ nội dung bằng file `study-i-zero-cost.yml` mới, commit trực tiếp
   vào **main**. Không cần sửa file nào trong `study_i/` hoặc đóng băng lại study.
3. Vào **Actions → Gatekeeper Study I - zero-cost target validation → Run workflow**,
   chọn **main** để tạo run mới dùng commit đã sửa.
4. Không chọn **Re-run failed jobs** trên run cũ: lượt chạy lại đó vẫn gắn với
   commit cũ, chưa chứa workflow vừa cập nhật.
5. Khi thành công, tải `study-i-networkx`, `study-i-sqlalchemy`, `study-i-verified`.
   Xem `family/FAMILY_RESULT.md` trong artifact verified. Nếu setup còn lỗi,
   artifact sẽ có context/trạng thái; log step trên GitHub vẫn là nguồn chính
   để đọc lỗi action cài đặt.

**Chưa push file hoặc dispatch workflow mới từ phiên hỗ trợ này.** Bản sửa
được bàn giao để bạn cập nhật vào main theo quy trình đã chọn.
