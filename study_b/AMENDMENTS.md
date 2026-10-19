# Study B — amendments

## A1 (19/10/2026) — sửa lỗi kỹ thuật khi tải target, không đổi quy tắc

**Lý do:** lần chạy #4 (run `39218140976`, commit `c571174`) qua được kiểm tra đóng băng nhưng dừng ở bước tải target. Nguyên nhân khả dĩ nhất: repo upstream chứa symlink trỏ tới file không có trong checkout nông, và lệnh sao chép đi theo symlink nên báo lỗi.

**Thay đổi:**
- `tools/fetch_real_targets.py`: sao chép giữ nguyên symlink (`symlinks=True`); in tên target trước khi tải; báo lỗi git rõ ràng.
- `gatekeeper_lite/runner.py`: tạo snapshot của mỗi nhánh cũng giữ nguyên symlink.

**Không đổi:** skill, binder, target và commit đã ghim, oracle, quy tắc bằng chứng (D1–D4), ngân sách, seed.

**Kết quả đã quan sát trước amendment:** không có. Các lần chạy #1–#4 đều dừng trước khi chạy bất kỳ cặp nào (chỉ có `PIP_FREEZE.txt`).

**Đóng băng lại:** `FREEZE.json` được tính lại sau amendment; tag mới `study-b-freeze-a1`.
