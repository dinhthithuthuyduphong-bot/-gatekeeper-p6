# Study G — quy tắc chọn target (khai báo trước khi xem bất kỳ kết quả nào của skill trên target)

1. **Nguồn ứng viên:** chỉ từ `tools/discover_g_candidates.py` (các truy vấn ghi sẵn trong file). Mọi kết quả, kể cả bị loại, được lưu trong `G_CANDIDATES.json`.
2. **Ô có lợi:** PR đã merge, có đổi `== None`/`!= None` thành `is None`/`is not None` trong mã nguồn, có đổi file test; qua kiểm định (`vet-targets`): ít nhất một test fail trước và pass sau bản merge. Oracle lấy từ test đó.
3. **Ô có hại:** mã cố ý giữ `== None` (ghi `noqa: E711` hoặc là biểu thức ORM/DSL), skill binding được vào module chứa nó, và có **test upstream** khẳng định hành vi của biểu thức (oracle **cấp 1**); nếu chỉ có `noqa` mà không có test thì là cấp 2b, báo cáo riêng.
4. **Ô đối chứng:** target có `== None` với đối tượng thông thường (không ghi đè `__eq__`).
5. **Điều kiện chung:** bộ test chạy được trên runner tiêu chuẩn (không cần máy chủ ngoài; SQLite trong bộ nhớ được chấp nhận), pin được commit, giấy phép mã nguồn mở.
6. **Giới hạn:** tối đa 8 target; ưu tiên theo thứ tự xuất hiện trong kết quả tìm kiếm (không chọn theo kết quả của skill). Nếu không đủ ô có hại cấp 1 chạy được, ghi `BLOCKED` cho phần đó, không hạ tiêu chuẩn.
7. **Baseline đăng ký cùng lúc:** B2, B6-R (ví dụ replay là một PR có lợi **không** thuộc tập đánh giá), **B6-S(k = 1, 5)**, B8; quy tắc chính có **futility** (dừng khi cận trên CS 95% của lợi ích < θ) và họ e-Holm chỉ gồm các ô skill binding được.
