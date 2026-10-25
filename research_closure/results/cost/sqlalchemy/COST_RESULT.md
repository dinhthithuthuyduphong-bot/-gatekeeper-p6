# Chi phí chạy thật: I1_sqlalchemy

Hậu kiểm trên target đã biết; 0 lượt gọi model. Cả hai chính sách trả cùng census và worker/snapshot setup.

| Chính sách | Tổng giây TB | Census giây TB | Draw pipeline giây TB | Paired draws TB |
|---|---|---|---|---|
| sequential | 40.7262 | 28.5195 | 11.6738 | 303 |
| full_draws | 47.6469 | 26.3983 | 20.7364 | 600 |

Chênh lệch tổng thời gian trung bình: 14.53% ít hơn khi sequential (âm nghĩa là chậm hơn).
Ba lần lặp thời gian trên cùng workload/seed không phải ba target độc lập; không suy ra speedup tổng quát.
So sánh này đo dừng thật với tiếp tục đủ draws, không chứng minh thắng baseline chỉ chạy census.
Census-only đã bắt được SQLAlchemy; phần draw bổ sung vẫn là overhead so với census-only trên case đó.
Không cộng thời gian download/install vào warm evaluation. Raw log, XML, paired outcomes và số đo từng lần được giữ cạnh báo cáo.
