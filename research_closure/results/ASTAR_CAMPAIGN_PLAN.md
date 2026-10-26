# Kế hoạch nhắm A\* (chốt 26/10/2026): Study M, cohort mới với patch LLM

## 1. Quyết định và lý do

Hướng có cơ hội A\* cao nhất là **một nghiên cứu cohort tiến cứu trả lời câu hỏi mà cả bốn bản đánh giá đều chưa thấy bằng chứng**: *trong patch plausible thật, hành vi chênh lệch còn sót lại nằm ở đâu, và cổng nào chấp nhận đúng?* Gatekeeper-Lite trở thành **một trong các cổng được so sánh**, không còn là phương pháp phải thắng.

| Hướng bị loại | Lý do |
|---|---|
| "Gatekeeper thắng cổng đơn giản" | Đồ thị pha đã bác bỏ lợi thế công suất so với kiểm định cỡ mẫu cố định |
| Thêm skill viết tay hoặc dữ liệu tổng hợp | Không trả lời phê bình về oracle do người viết và quy mô |
| ISSTA đầu 2027 | Không phải A\*, và phản hồi (tháng 4/2027) đến sau hạn ASE |

## 2. Câu hỏi và đóng góp dự kiến

1. **RQ1:** trong patch plausible, tỉ lệ chênh lệch hành vi h phân bố ra sao; bao nhiêu patch rơi vào vùng cần cổng thống kê (0,25–10%)?
2. **RQ2:** ở cùng ràng buộc rủi ro, cổng nào (census, smoke test, zero-tolerance, cỡ mẫu cố định, Gatekeeper cố định và mixture) giữ được nhiều patch đúng nhất, với chi phí đo thật?
3. **RQ3:** giao thức oracle không do người viết (vi sai so với bản fix upstream, test-level, lọc theo độ phủ) có hợp lệ không? Đo bằng đối chứng dương, tính tất định và độ đồng thuận với test ẩn của upstream.
4. **RQ4:** kết quả khác nhau thế nào giữa các model?

Đóng góp: phép đo trên cohort chưa lộ; giao thức oracle-free có kiểm chứng; so sánh công bằng các cổng (kể cả khi cổng đơn giản thắng); phương pháp tiền đăng ký.

## 3. Thiết kế

- **Cohort:** PR sửa lỗi Python khám phá theo quy tắc đóng băng (`study_m/INCLUSION_RULES.md`), thứ tự theo seed drand; loại 64+ repo đã dùng hoặc đã lộ. Các giai đoạn: S1 khám phá, S2 kiểm định (có test fail trước, pass sau), S3 đủ điều kiện harness (test chạy tới code bị sửa, đủ cặp, tất định, bản gốc khác bản fix), rồi mới sinh patch. Mỗi giai đoạn có bảng hao hụt.
- **Patch:** sinh bằng pipeline B9 đã đóng băng; model dự kiến Gemini Pro và Flash trên Vertex, thêm một model trên AI Studio. Ước tính chi phí với giá đã đóng băng: 60 instance × 3 lần lặp × 2 model = 360 lần sửa, trần khoảng 198 USD, ước tính thực khoảng 31 USD.
- **Nhãn thật:** hai nhãn độc lập nhau: test ẩn của upstream, và ước lượng h từ nhiều draw held-out (seed lấy sau khi đóng băng, không dùng cho quyết định admit).
- **Đối chứng đăng ký trước:** census-only, B8+, smoke 20, cỡ mẫu cố định (n = 300 và 1000, cùng θ, η, α), Gatekeeper và Gatekeeper-mixture; quyết định ở mức patch (quy tắc F-A2).

## 4. Cổng dừng (bản nháp, đóng băng trong `study_m/GATES.md` trước giai đoạn tương ứng)

| Cổng | Điều kiện đề xuất | Nếu không đạt |
|---|---|---|
| M1 kiểm định | ≥ 40 instance có test fail trước, pass sau từ 250 ứng viên đầu | Mở rộng khám phá một lần, đăng ký trước; nếu vẫn không đạt thì dừng |
| M2 harness | ≥ 40 instance đủ điều kiện (đủ cặp, tất định, bản gốc khác bản fix) | Dừng hướng test-level; báo cáo kết quả âm |
| M3 thử nghiệm | Trên 10 instance đầu, 1 model rẻ, 2 lần lặp: ≥ 10 patch plausible | Sửa pipeline; không tiêu credit chính |
| M4 vùng tác hại | ≥ 15 patch plausible trong vùng 0,25–10%, và ≥ 8 patch mà quyết định của Gatekeeper hoặc cỡ mẫu cố định khác cổng đơn giản | Không có câu chuyện "cổng thống kê có giá trị"; chuyển thành bài đo đạc, đánh giá lại đích nộp |

Các ngưỡng là phán đoán, không phải chuẩn khoa học; được chọn để đủ cho so sánh ghép cặp.

## 5. Mốc thời gian

Hạn dưới đây lấy từ **danh sách không chính thức, cần xác minh khi CFP công bố**: ASE 2027 khoảng 26/3/2027; ICSE 2028 khoảng 30/6/2027; ICSE 2027 đã đóng từ 30/6/2026.

| Thời gian | Việc | Chi phí |
|---|---|---|
| 27/10 – 10/11 | Đóng băng S1, khám phá, sắp thứ tự, kiểm định (S2) | 0 |
| 11/11 – 30/11 | Đủ điều kiện harness (S3), bảng hao hụt, đóng băng cohort, `GATES.md` và kế hoạch phân tích | 0 |
| 12/2026 | Thử nghiệm M3, củng cố pipeline | dưới 5 USD |
| 01/2027 | Sinh patch chính và chấm điểm | khoảng 30–200 USD |
| 02/2027 | Phân tích, độ nhạy, viết | 0 |
| 03/2027 | Nộp ASE nếu các cổng đạt và hạn đúng; nếu chậm, chuyển sang ICSE 2028 | 0 |

**Phụ thuộc quan trọng:** credit Vertex 300 USD thường hết hạn sau 90 ngày kể từ lúc đăng ký. Nếu hết hạn trước tháng 1, phải đưa bước sinh patch lên sớm hoặc dùng tiền thật.

## 6. Rủi ro, nói thẳng

- **Tính mới so với công trình đã có:** Wang, Pradel và Liu (ICSE 2026) đã thấy 29,6% patch plausible khác bản gốc về hành vi. Bài phải cho thấy phần mới: phân bố tỉ lệ chênh lệch, phân tích theo vùng, so sánh cổng, giao thức tiền đăng ký.
- Kết quả có thể âm (ít patch trong vùng tác hại một phần). Kết quả âm có kỷ luật vẫn đáng báo cáo, nhưng khó vào A\*.
- Cohort từ tìm kiếm GitHub không phải mẫu ngẫu nhiên; kết luận chỉ áp dụng cho tập này.
- Hạ tầng test-level còn thô ở quy mô lớn (thời gian chạy từng test, repo nặng); cần xử lý trước S3.
- **Không có cách nào bảo đảm chấp nhận.**
