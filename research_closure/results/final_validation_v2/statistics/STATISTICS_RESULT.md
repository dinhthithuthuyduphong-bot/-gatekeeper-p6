# Kết quả kiểm toán baseline và power (0 API)

Phân tích hậu kiểm trên cùng 50 họ Study H; không phải nghiên cứu tiến cứu mới. Các bảng gốc được giữ nguyên.

| Phương pháp | Họ admit sai | h=0% | h=1% | h=2% | h=3% | h=5% | h=10% | Draw/họ |
|---|---|---|---|---|---|---|---|---|
| GK original | 0/50 | 50 | 45 | 17 | 11 | 0 | 0 | 1300.50 |
| GK adaptive (post hoc) | 0/50 | 50 | 41 | 14 | 8 | 0 | 0 | 1342.34 |
| GK balanced mixture (post hoc) | 0/50 | 50 | 44 | 21 | 11 | 0 | 0 | 1362.54 |
| Fixed 100, IUT Bonferroni | 0/50 | 34 | 13 | 2 | 2 | 0 | 0 | 600.00 |
| Fixed 100, IUT Holm | 0/50 | 34 | 15 | 3 | 2 | 0 | 0 | 600.00 |
| Fixed 200, IUT Bonferroni | 0/50 | 50 | 42 | 16 | 12 | 0 | 0 | 1200.00 |
| Fixed 200, IUT Holm | 0/50 | 50 | 42 | 19 | 15 | 0 | 0 | 1200.00 |
| Fixed 300, IUT Bonferroni | 0/50 | 50 | 50 | 35 | 16 | 0 | 0 | 1800.00 |
| Fixed 300, IUT Holm | 0/50 | 50 | 50 | 35 | 16 | 0 | 0 | 1800.00 |

Fixed IUT dùng max(p_benefit,p_harm), không chia đôi alpha trong một ô. Holm kiểm soát FWER trên cả họ với p-value hợp lệ; không cần độc lập giữa các ô.
P-value lợi ích vẫn dùng Hoeffding nên đây chưa phải baseline fixed-size tối ưu. Mỗi n là một chính sách riêng; không được chọn n hậu kiểm rồi tuyên bố còn cùng bảo đảm.
Số draw là replay trên trace; không phải đo tiết kiệm wall-clock. Các chứng chỉ mới chưa thay primary rule.
Nếu quan sát 0/50 họ có lỗi, cận trên nhị thức một phía 95% là 5.8155%; không gọi đó là chứng minh FWER=0.

## Cỡ mẫu cho riêng chứng chỉ ít hại

Tính chính xác theo mô hình Binomial với mức alpha/K. Đây là xác suất qua riêng cổng harm ở fixed n; xác suất admit đầy đủ không thể cao hơn khi còn cổng benefit/census.

| n | Số harm tối đa được chứng nhận | Power h=0% | h=1% | h=2% | h=3% |
|---|---|---|---|---|---|
| 100 | 0 | 100.0% | 36.6% | 13.3% | 4.8% |
| 200 | 3 | 100.0% | 85.8% | 43.1% | 14.7% |
| 300 | 7 | 100.0% | 98.9% | 74.5% | 32.0% |
| 500 | 14 | 100.0% | 100.0% | 91.9% | 46.4% |
| 1000 | 35 | 100.0% | 100.0% | 99.9% | 84.6% |
| 2000 | 79 | 100.0% | 100.0% | 100.0% | 99.3% |
