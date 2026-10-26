# Quy tắc chọn giữa nhánh RR và nhánh A\* (đóng băng cùng nhánh A\*, TRƯỚC khi chạy S2)

**Ngày quyết định: 10/1/2027, trước mọi lượt gọi mô hình trả phí.** Nếu thiếu thông tin vào ngày đó thì chờ tới 15/1/2027 (hạn nộp bản sửa của RR), vẫn không chi tiền.

## Dữ liệu đầu vào (đều có được mà không tốn tiền)

| Mã | Nội dung | Nguồn |
|---|---|---|
| F1 | Tính khả thi của cohort: **M1 và M2 cùng đạt** trên nửa A\* | Kết quả S2 và S3 |
| F2 | Báo cáo RR **không** bị loại sớm vì không thuộc phạm vi MSR, và phản biện (nhận 23/12/2026) **không** nêu phản đối căn bản về phạm vi hay độ vững. Nguyên văn phản biện được lưu vào repo kèm hash; người hướng dẫn cùng đánh giá | Phản biện của RR |
| F3 | Luận văn **cần kết quả trước 4/2/2027**: có hoặc không (khai báo trước 13/11/2026) | Người nghiên cứu và người hướng dẫn |
| F4 | Credit còn hiệu lực tới ngày dự kiến sinh patch, hoặc có tiền thật | Billing |
| F5 | Có thể trình bày trực tiếp báo cáo tại MSR 2027 (Dublin, cuối tháng 4/2027) | Người nghiên cứu |

## Luật (áp dụng theo thứ tự, dừng ở luật đầu tiên khớp)

1. **F1 không đạt:** cả hai nhánh dừng. Quay về bài ở tầng 1 và đường tạp chí. Không chi tiền.
2. **F3 = có:** chọn nhánh **A\*** (RR chỉ cho phép thu dữ liệu sau IPA ngày 4/2/2027).
3. **F2 không đạt hoặc F5 = không:** chọn nhánh **A\***.
4. Còn lại (F1 đạt, F2 đạt, F3 = không, F5 = có): chọn nhánh **RR**.

## Hệ quả của lựa chọn

- Chọn **RR**: nửa A\* chỉ còn là dữ liệu thử nghiệm, khai báo rõ trong bản sửa và bài đầy đủ; **không** công bố riêng kết quả của nửa A\* (tránh trùng lặp xuất bản). Nhánh RR (`study_m_rr`) trở thành nhánh làm việc; nửa RR bắt đầu được kiểm định sau IPA.
- Chọn **A\***: **rút** báo cáo RR trước khi có quyết định của chair (quy định rút bài chưa rõ, hỏi chair sớm); thư mục `study_m_rr` được lưu trữ bằng tag và dừng; nửa RR **không bao giờ** được xem, và không dùng để chọn bất kỳ tham số nào.
- Cả hai trường hợp: ngưỡng trong `GATES.md` giữ nguyên.

## Giới hạn, ghi thẳng

- Không thể đánh giá cổng **M4** (có đủ patch thật trong vùng tác hại một phần không) trước khi tốn tiền, nên quyết định này **dựa vào tính khả thi, không dựa vào xác suất kết quả**.
- Điều kiện F2 có phần chủ quan; vì vậy nguyên văn phản biện được lưu lại và người hướng dẫn cùng đánh giá.
