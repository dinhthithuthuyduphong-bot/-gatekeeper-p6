# Study N, nhánh A\*: cổng (bất biến sau khi đóng băng)

| Cổng | Điều kiện đạt | Nếu không đạt |
|---|---|---|
| **N1** (N-S2) | Trong `min(400, n)` ứng viên đầu của `candidates_astar.json`, **≥ 60** ELIGIBLE theo `vet_target2.py` bản 2.1. Nếu có **ít hơn 200** ứng viên thì không đạt | Dừng nhánh; không thay thế ứng viên |
| **N2** (N-S3) | **≥ 40** instance đủ điều kiện harness: test nền qua, có test chạy tới code bị sửa, ≥ 100 draw đủ cặp, tất định, bản gốc khác bản fix ở ít nhất 1 draw | Dừng nhánh |
| **N3** (N-GEN) | **≥ 30** patch plausible trên toàn cohort (mọi model gộp lại) | Báo cáo kết quả âm về số patch; không kiểm định H1 đến H3 |
| **N4** (N-SCORE) | **≥ 15** patch plausible có ĥ trong vùng [max(1%, 2/n), 10%], và **≥ 8** patch mà quyết định của Gatekeeper hoặc kiểm định cỡ mẫu cố định khác quyết định của B8+ hoặc smoke 20 | Không có câu chuyện "cổng thống kê có giá trị"; báo cáo như nghiên cứu đo đạc |

Ngưỡng là phán đoán của người nghiên cứu, không phải phân tích công suất chính thức. N1 được đặt từ tỉ lệ đo ở lượt phát triển (23,8%, cận dưới 18,8%): ở cận dưới, 400 ứng viên cho trung bình khoảng 75.
