# Study B — amendments

## A1 (19/10/2026) — sửa lỗi kỹ thuật khi tải target, không đổi quy tắc

**Lý do:** lần chạy #4 (run `39218140976`, commit `c571174`) qua được kiểm tra đóng băng nhưng dừng ở bước tải target. Nguyên nhân khả dĩ nhất: repo upstream chứa symlink trỏ tới file không có trong checkout nông, và lệnh sao chép đi theo symlink nên báo lỗi.

**Thay đổi:**
- `tools/fetch_real_targets.py`: sao chép giữ nguyên symlink (`symlinks=True`); in tên target trước khi tải; báo lỗi git rõ ràng.
- `gatekeeper_lite/runner.py`: tạo snapshot của mỗi nhánh cũng giữ nguyên symlink.

**Không đổi:** skill, binder, target và commit đã ghim, oracle, quy tắc bằng chứng (D1–D4), ngân sách, seed.

**Kết quả đã quan sát trước amendment:** không có. Các lần chạy #1–#4 đều dừng trước khi chạy bất kỳ cặp nào (chỉ có `PIP_FREEZE.txt`).

**Đóng băng lại:** `FREEZE.json` được tính lại sau amendment; tag mới `study-b-freeze-a1`.

## A2 (19/10/2026) — chạy oracle cô lập và ghi lỗi kỹ thuật theo từng cặp, không đổi quy tắc

**Lý do:** lần chạy sau A1 vẫn dừng trước khi tạo kết quả (artifact chỉ có `PIP_FREEZE.txt`, không có log). Nguyên nhân khả dĩ: cấu hình pytest hoặc `conftest.py` của repo upstream cần plugin chưa cài, làm pytest thoát trước khi ghi báo cáo; khi đó một target lỗi làm sập cả thí nghiệm.

**Thay đổi:**
- Oracle metamorphic (nội dung **không đổi**) được chèn vào thư mục riêng `gk_oracle/` kèm `pytest.ini` trống, và chạy trong **phiên pytest riêng** (`-c gk_oracle/pytest.ini --rootdir gk_oracle`), nên cấu hình, plugin và conftest của upstream không ảnh hưởng. Bộ test gốc của target chạy trong phiên thứ hai, như trước.
- Một nhóm oracle không chạy được thì được **ghi lại** (`harness_errors`), các nhóm khác vẫn được dùng. Một cặp không chạy được thì được ghi `HARNESS_ERROR` và **không tính** vào kết quả; các cặp khác vẫn chạy.
- Workflow lưu log tải target và log chạy vào artifact (`logs/`), kể cả khi lỗi.

**Không đổi:** skill, binder, target và commit, nội dung oracle, quy tắc D1–D4, ngân sách, seed.

**Kết quả đã quan sát trước amendment:** không có (chưa cặp nào được chạy).

**Đóng băng lại:** `FREEZE.json` tính lại; tag mới `study-b-freeze-a2`.
