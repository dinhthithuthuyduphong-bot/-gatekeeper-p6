# archive/

Chỉ để truy vết; không có workflow, công cụ hay test nào đọc các tệp ở đây.

`root_packages/` chứa script áp dụng (`APPLY_*.py`), manifest (`*_MANIFEST.json`, `SHA256.json`, `UPDATE_PATHS.txt`, …) và kết quả kiểm tra (`PACKAGE_CHECKS/`) của các gói cập nhật cũ từng bị giải nén vào gốc repo. Chúng được chuyển vào đây ngày 31/10/2026, xem [`docs/PROCESS_LOG.md`](../docs/PROCESS_LOG.md). Các đường dẫn ghi bên trong những tệp này là đường dẫn **lúc đó** (tương đối từ gốc repo hoặc từ thư mục gói), không phải vị trí hiện tại.
