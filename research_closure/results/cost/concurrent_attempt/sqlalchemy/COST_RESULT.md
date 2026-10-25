# Chi phí chạy thật: I1_sqlalchemy

Hậu kiểm trên target đã biết; 0 lượt gọi model. Cả hai chính sách trả cùng census và worker/snapshot setup.

| Chính sách | Tổng giây TB | Census giây TB | Draw pipeline giây TB | Paired draws TB |
|---|---|---|---|---|
| sequential | 42.5601 | 27.6401 | 13.9129 | 303 |
| full_draws | 53.0479 | 29.5966 | 22.4693 | 600 |

Chênh lệch tổng thời gian trung bình: 19.77% ít hơn khi sequential (âm nghĩa là chậm hơn).
Ba lần lặp thời gian trên cùng workload/seed không phải ba target độc lập; không suy ra speedup tổng quát.
So sánh này đo dừng thật với tiếp tục đủ draws, không chứng minh thắng baseline chỉ chạy census.
Census-only đã bắt được SQLAlchemy; phần draw bổ sung vẫn là overhead so với census-only trên case đó.
Không cộng thời gian download/install vào warm evaluation. Raw log, XML, paired outcomes và số đo từng lần được giữ cạnh báo cáo.
