# Pipeline sinh patch cho cohort mới: các chính sách đã cố định (26/10/2026)

Phần này **dùng lại vòng sửa lỗi B9 đã đóng băng** (`gatekeeper_lite/b9.py`, không sửa gì); mọi thứ mới nằm trong `gatekeeper_ext/b9_cohort.py` và `gatekeeper_ext/usage.py`.

## Chính sách (đóng băng cùng cấu hình cohort, trước khi sinh patch nào)

| Mục | Chính sách | Lý do và giới hạn |
|---|---|---|
| Văn bản issue | Tiêu đề và nội dung của issue được PR liên kết (`fixes #N`) nếu có; nếu không, **chỉ tiêu đề PR**. Không bao giờ dùng nội dung PR. Khối mã có một dòng (từ 20 ký tự) trùng với diff của bản fix bị xoá. Tối đa 4.000 ký tự | Nội dung PR thường mô tả cách sửa. Việc xoá khối mã chỉ là heuristic, còn có thể sót gợi ý; tiêu đề PR cũng có thể gợi ý |
| Quyền sửa | Các file `.py` không phải test mà bản fix thay đổi | Giống sáu instance phát triển. **Giới hạn:** nó tiết lộ vị trí lỗi cho mô hình, nên nhiệm vụ dễ hơn tìm lỗi trong cả repo |
| Kiểm tra hiển thị | **Một** test fail-to-pass (đầu tiên theo id), kèm mã nguồn | Mọi test fail-to-pass khác và test pass-to-pass là nhãn ẩn, không bao giờ hiện cho mô hình hay dùng để chọn |
| Gốc để sinh patch và chấm | Commit trước bản fix, cộng các file test của bản fix | Cần để chạy test hiển thị; cùng một gốc cho mọi cánh tay |
| Census | Thư mục chung của các file test của PR | Quyết định thiết kế; có thể nhỏ hơn bộ test đầy đủ của repo |
| Kế toán token | Đầu ra = tổng của nhà cung cấp trừ đầu vào | Xem mục dưới |

## Phát hiện từ smoke test về token suy luận (Vertex, Gemini Pro)

Bản ghi `usage` của Pro **không có `completion_tokens`**; token suy luận chỉ nằm trong `total_tokens` (7 đầu vào, 12 suy luận, tổng 19). Với `max_tokens = 16`, Pro trả lời rỗng và kết thúc bằng `length`.

- Client B9 đã đóng băng coi đó là "thiếu usage" và tính **mọi lời gọi Pro ở mức xấu nhất** (4.000 token đầu ra). An toàn, nhưng chi phí ghi lại bị thổi phồng và hạn mức chi có thể chạm sớm. Không sửa client đó (đã đóng băng).
- Client mới (`CohortClient`) tính đúng và ghi lại `finish_reason` của từng lời gọi.
- **Rủi ro chưa đo:** trần 4.000 token đầu ra gồm cả suy luận. Nếu Pro dùng nhiều token để suy luận, câu trả lời có thể bị cắt rỗng, và nó trông giống "mô hình thất bại" trong khi thực ra là hết ngân sách. Phép thăm dò nhiệm vụ trong `vertex_smoke` đo điều này; kết quả quyết định có tăng `max_output_tokens` (ví dụ lên 8.000) trong cấu hình cohort **trước khi đóng băng nó**. Cấu hình Study F giữ nguyên.

## Chưa làm

- Chạy sinh patch trên Actions cho từng instance (dựng môi trường, ghi và phát lại cassette, giới hạn chi).
- Chấm điểm: vi sai test-level của patch, rồi quyết định của từng cổng trên cùng draw.
