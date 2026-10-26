# Study M, giai đoạn S1: quy tắc khám phá instance (đóng băng trước khi chạy)

**Mục đích.** Tạo cohort instance **chưa lộ** cho một nghiên cứu đo mức độ chênh lệch hành vi còn sót lại trong patch plausible và so sánh các cổng chấp nhận. S1 chỉ khám phá PR sửa lỗi; **không** nhìn kết quả test, skill hay patch nào.

## Quy tắc (bất biến sau khi đóng băng)

1. **Nguồn:** tìm kiếm GitHub công khai, repo ngôn ngữ Python, PR đã merge, tiêu đề chứa `fix` hoặc `bug`; 42 cửa sổ tháng từ 01/2023 đến 06/2026; mỗi truy vấn tối đa 2 trang (200 kết quả).
2. **Bộ lọc, áp dụng theo thứ tự và ghi số lượng loại ở từng bước:** (a) repo không thuộc `EXCLUDED_REPOS.json` (mọi repo đã dùng ở Study D, E, G, L và các lượt chạy phát triển); (b) PR đã merge, không phải draft; (c) tiêu đề không chứa từ bảo trì (typo, docs, ci, bump, lint, format, style, refactor, deps, release, typing…); (d) 1 đến 8 file thay đổi; (e) có ít nhất một file nguồn `.py` không phải test; (f) có ít nhất một file test thay đổi; (g) diff nguồn không quá 60 dòng; (h) không xoá hay đổi tên file nguồn.
3. **Thứ tự:** các ứng viên còn lại được sắp theo SHA-256 của `seed:repo#pr`, với `seed` lấy từ vòng drand xuất hiện **sau** thời điểm đóng băng này. Thứ tự do đó không thể phụ thuộc vào kết quả nào.
4. **Giai đoạn sau (không thuộc S1):** kiểm định (có test fail trước và pass sau), tính đủ điều kiện của harness test-level, rồi mới sinh patch. Mỗi giai đoạn có bảng hao hụt (số instance vào, số bị loại và lý do).

## Giới hạn đã biết, ghi trước

- Tìm kiếm GitHub không phải mẫu ngẫu nhiên của mọi PR sửa lỗi: kết quả nghiêng về repo nhiều PR và có tiêu đề chứa `fix` hoặc `bug`. Kết luận chỉ áp dụng cho tập này.
- Kết quả tìm kiếm thay đổi theo thời gian; ngày chạy và số đếm được ghi lại, danh sách ứng viên được lưu nguyên.
- Bộ lọc loại PR lớn, nên cohort nghiêng về lỗi nhỏ, cục bộ.
