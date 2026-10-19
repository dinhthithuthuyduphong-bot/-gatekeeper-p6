# Ablation hậu kiểm trên dữ liệu `study-c-v1` (không chạy thêm)

| Biến thể | Ô (có hại / có lợi) | Có hại bị admit | Có lợi được admit | Từ chối vì tác hại | Lượt chạy thử |
|---|---|---|---|---|---|
| Đầy đủ (như đã chạy) | 24 (12/12) | 0 | 12 | 12 | 528 |
| Bỏ chia scope (gộp mọi task) | 12 (12/0) | 0 | 0 | 12 | 96 |
| E-process trung bình θ=0,1 thay kiểm định dấu | 24 (12/12) | 0 | 12 | 0 | 1056 |
| Bỏ lọc theo khả năng chạm | 24 (12/12) | 0 | 12 | 12 | 528 |
| Bỏ ưu tiên oracle (thứ tự ngẫu nhiên) | 24 (12/12) | 0 | 0 | 6 | 948 |
| Bonferroni thay e-BH (ngưỡng 1/(α/K)) | 24 (12/12) | 0 | 6 | 12 | 540 |
