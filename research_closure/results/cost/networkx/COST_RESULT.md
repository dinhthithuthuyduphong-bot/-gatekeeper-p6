# Chi phí chạy thật: I2_networkx

Hậu kiểm trên target đã biết; 0 lượt gọi model. Cả hai chính sách trả cùng census và worker/snapshot setup.

| Chính sách | Tổng giây TB | Census giây TB | Draw pipeline giây TB | Paired draws TB |
|---|---|---|---|---|
| sequential | 5.8268 | 2.4754 | 3.1435 | 380 |
| full_draws | 6.4333 | 2.5327 | 3.6331 | 600 |

Chênh lệch tổng thời gian trung bình: 9.43% ít hơn khi sequential (âm nghĩa là chậm hơn).
Ba lần lặp thời gian trên cùng workload/seed không phải ba target độc lập; không suy ra speedup tổng quát.
So sánh này đo dừng thật với tiếp tục đủ draws, không chứng minh thắng baseline chỉ chạy census.
Census-only đã bắt được SQLAlchemy; phần draw bổ sung vẫn là overhead so với census-only trên case đó.
Không cộng thời gian download/install vào warm evaluation. Raw log, XML, paired outcomes và số đo từng lần được giữ cạnh báo cáo.
