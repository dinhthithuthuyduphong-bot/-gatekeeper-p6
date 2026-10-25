# Study L — amendments

## L-A1 (trước khi chạy bất kỳ cổng nào) — thêm công cụ cho G1; không đổi ngưỡng

**Thay đổi:** chỉ thêm công cụ vào danh sách hash. **Không file nào của `GATES.md` bị sửa; mọi ngưỡng giữ nguyên** (có thể kiểm tra bằng cách so hash `study_l/GATES.md` giữa tag `study-l-freeze` và bản hiện tại).

| File | Vai trò |
|---|---|
| `gatekeeper_ext/golddiff.py` | tìm hàm bị sửa, sinh draw theo thuật toán cố định, chạy nhiều snapshot, chấm tiêu chí G1 |
| `gatekeeper_ext/golddiff_oracle.py` | phía worker: phát lại lần gọi đã ghi, đột biến nhầm kiểu một tham số, canonical hoá kết quả |
| `gatekeeper_ext/record_run.py` | ghi lại lần gọi thật của các hàm bị sửa khi chạy test của chính repo |
| `gatekeeper_ext/mutants.py` | đột biến AST xác định của bản fix (so sánh, phủ định `if`, hằng bool, `and`/`or`); lấy tối đa 5 đầu tiên theo thứ tự nguồn, không nhìn kết quả |
| `tools/g1_check.py`, `tools/g1_summary.py` | điều phối G1 cho từng instance và tổng hợp quyết định cổng |
| `tests/test_golddiff.py` | kiểm thử đơn vị và đầu cuối trên repo giả |

**Diễn giải cụ thể hoá cho G1 (không phải đổi ngưỡng):**
1. "Patch đúng đã biết" là bản viết lại của skill đóng băng khi skill gắn được vào instance; nếu không gắn được (D4) thì dùng chính bản fix upstream, và tiêu chí (b) khi đó **vô nghĩa** (ghi rõ trong kết quả).
2. Thuật toán generator cố định: chọn đều một hàm bị sửa có lần gọi đã ghi, chọn đều một lần gọi; với xác suất 0,5, thay một đối số (không phải `self`/`cls`) bằng một giá trị từ danh sách cố định 12 giá trị (None, True, False, 0, 1, −1, 2³¹, 1,5, "", "a", [], {}). Seed của mỗi instance suy từ tên instance, không phụ thuộc kết quả.
3. So sánh đầu ra dùng kiểu và giá trị của kết quả (hoặc **kiểu** ngoại lệ, không so thông báo) cùng trạng thái đối số sau lần gọi.
4. Hàm không dùng được (static/class method, generator, coroutine, không chọn được hàm bị sửa trong cả hai phiên bản) bị loại khỏi tập draw và được ghi lại; instance không có lần gọi nào được ghi là **không đủ điều kiện**, tính là không đạt.

**Hạn chế đã biết, ghi trước khi xem kết quả:**
- Tỉ lệ draw kích hoạt lỗi của generator tự động thấp (khoảng 9% trên fixture thử, vì chỉ một phần giá trị thay thế là kiểu gây lỗi). Do đó **biên lợi ích θ = 0,2 của Gatekeeper không phù hợp** với generator này. Trong Study L, điều kiện lợi ích của một patch là **vượt bộ test fail-to-pass của chính instance**; các cổng được so sánh trên **phía tác hại** (certificate, cỡ mẫu cố định, smoke, zero-tolerance). Quyết định "Gatekeeper admit" ở G3 vì vậy nghĩa là "certificate tác hại đạt ngưỡng", không phải "e-process lợi ích đạt θ".
- Chỉ phát hiện được chênh lệch hành vi qua các hàm bị sửa mà test của repo có gọi; chênh lệch ở nơi test không gọi không được đo.
- Phát lại lần gọi cần đối số pickle được; instance có đối số không pickle được bị loại, có thể làm lệch tập instance (đo ở G2).
