# Study L — kết quả cổng G1 (ngưỡng đã đóng băng: ≥ 5/6 instance đạt)

**Kết luận: G1 KHÔNG ĐẠT (2/6).** Quy tắc dừng trong `GATES.md` được áp dụng: dừng hướng oracle tự động; G2 và G3 không chạy; không chi tiền cho bất kỳ lượt gọi mô hình nào.

Amendment L-A1 đã áp dụng (tag `study_l-l-a1`); mỗi job G1 chạy `freeze_study.py verify study_l` trước khi chạy và đều tạo được kết quả, nên danh sách hash khớp.

| Instance | Đủ điều kiện | (a) thấy lỗi | (b) không hồi quy | (c) tất định | (d) bắt đột biến | Tỉ lệ kích hoạt lỗi | Đạt |
|---|---|---|---|---|---|---|---|
| D1 py_ecc | có | không | có | có | không | 0,0% | không |
| D2 Cerberus | **không** | | | | | | không |
| D3 spec-kit | **không** | | | | | | không |
| D4 openfeature | có | có | có (vô nghĩa) | có | có | 0,7% | có (sát ngưỡng) |
| D5 pycubrid | có | có | có | có | có | 8,7% | **có** |
| A1 spec-kit catalog | có | không | có (vô nghĩa) | có | có | 0,0% | không |

## Phân loại nguyên nhân (bằng chứng phân biệt với giả thuyết)

| Instance | Nguyên nhân | Mức chắc chắn |
|---|---|---|
| D1 | Cả 300 draw ở mọi arm trả lỗi harness; log không lưu nội dung lỗi nên **chưa biết nguyên nhân**. Đây là lỗi công cụ (thiếu ghi lại thông báo lỗi) | Đo được là 300/300 lỗi; nguyên nhân chưa biết |
| D2 | Bộ ghi thấy 32 lần gọi nhưng **cả 32 đối tượng `self` đều không pickle được** | Đo được |
| D3 | Bộ ghi **không thấy lần gọi nào** (0 lần gọi, 0 lần pickle lỗi). Giả thuyết: hàm là lệnh CLI được đăng ký bằng decorator lúc import, nên việc thay tên hàm sau đó không chặn được lần gọi | Giả thuyết, chưa kiểm chứng |
| A1 | 15 lần gọi được ghi, nhưng không draw nào kích hoạt lỗi. Giả thuyết: giá trị gây lỗi nằm sâu trong cấu trúc lồng nhau, còn đột biến chỉ thay đối số cấp ngoài cùng | Đo được là 0 lần kích hoạt; nguyên nhân là giả thuyết |
| D4 | Qua cổng nhưng chỉ có 2 draw kích hoạt lỗi (0,7%), và skill không gắn được nên tiêu chí (b) không có ý nghĩa | Đo được |

## Quyết định không phụ thuộc vào D1

Dù D1 được sửa và đạt, tối đa chỉ có D1, D4, D5 = **3/6 < 5/6**, vì D2 và D3 không đủ điều kiện (L-A1 đã ghi trước rằng instance không ghi được lần gọi nào "tính là không đạt") và A1 thất bại do kết quả đo. Kết luận G1 vì vậy không đổi, và không có lý do sửa công cụ để cứu cổng này.

## Ý nghĩa

Hai trong sáu thất bại (D2, D3) và có thể cả D1 nằm ở **độ phủ của bộ ghi lần gọi cấp hàm**: đối tượng nhận không pickle được và hàm được đăng ký trước khi bị thay là những dạng rất thường gặp trong mã thật. Điều này báo trước rằng cổng G2 (≥ 40 instance trong 300) nhiều khả năng cũng không đạt với cơ chế này. Một lần thất bại (A1) đến từ giới hạn của đột biến cấp ngoài cùng. Chỉ D5 là ca đạt rõ ràng.
