# Quy tắc chọn giữa nhánh RR và nhánh A\* (đóng băng cùng nhánh A\*, TRƯỚC khi chạy S2)

**Ngày quyết định: 10/1/2027 là hạn cuối.** Nếu phản biện của RR (nhận 23/12/2026) đã đủ rõ thì có thể quyết định sớm hơn. Nếu thiếu thông tin vào ngày đó thì chờ tới 15/1/2027 (hạn nộp bản sửa của RR).

## Dữ liệu đầu vào (đều có được trước khi chọn)

| Mã | Nội dung | Nguồn |
|---|---|---|
| F1 | Tính khả thi của cohort: **M1 và M2 cùng đạt** trên nửa A\* | Kết quả S2 và S3 |
| F2 | Báo cáo RR **không** bị loại sớm vì không thuộc phạm vi MSR, và phản biện (nhận 23/12/2026) **không** nêu phản đối căn bản về phạm vi hay độ vững. Nguyên văn phản biện được lưu vào repo kèm hash; người hướng dẫn cùng đánh giá | Phản biện của RR |
| F3 | Luận văn **cần kết quả trước 4/2/2027**: có hoặc không (khai báo trước 13/11/2026) | Người nghiên cứu và người hướng dẫn |
| F4 | **Đủ tiền cho nhánh được chọn.** *A\*:* credit Free Trial còn hiệu lực tới ngày sinh patch (hết hạn 20/1/2027) và đủ cho thiết kế (đầy đủ 60 instance × 3 lần lặp × 2 model: kỳ vọng khoảng 31 USD, trần khoảng 198 USD). *RR:* sinh patch chỉ sau 4/2/2027 nên **không dùng được Free Trial**; cần **ít nhất 28 USD** (gấp đôi chi phí kỳ vọng khoảng 13,7 USD của thiết kế vừa 40 × 2 × 2) từ credit Developer (khoảng 9,6 USD, hết hạn 21/10/2027) cộng tiền mặt | Billing và người nghiên cứu |
| F5 | Có thể trình bày trực tiếp báo cáo tại MSR 2027 (Dublin, cuối tháng 4/2027) | Người nghiên cứu |

**Kết quả của M3 và của lượt sinh patch chính KHÔNG là đầu vào của luật**, kể cả khi chúng đã có trước ngày quyết định.

## Luật (áp dụng theo thứ tự, dừng ở luật đầu tiên khớp)

1. **F1 không đạt:** cả hai nhánh dừng. Quay về bài ở tầng 1 và đường tạp chí.
2. **F3 = có:** chọn nhánh **A\*** (RR chỉ cho phép thu dữ liệu sau IPA ngày 4/2/2027).
3. **F2 không đạt, hoặc F5 = không, hoặc F4 của RR không đạt:** chọn nhánh **A\***.
4. Còn lại: chọn nhánh **RR**.

## Hệ quả của lựa chọn

- Chọn **RR**: dữ liệu của nửa A\* (kể cả lượt sinh patch bằng credit Free Trial) chỉ còn là dữ liệu thử nghiệm, khai báo rõ trong bản sửa và bài đầy đủ; **không** công bố riêng. Nửa RR bắt đầu được kiểm định sau IPA; thư mục `study_m_rr` trở thành nhánh làm việc.
- Chọn **A\***: **rút** báo cáo RR trước khi có quyết định của chair (quy định rút bài chưa rõ, hỏi chair sớm); `study_m_rr` được lưu trữ bằng tag và dừng; nửa RR **không bao giờ** được xem, và không dùng để chọn bất kỳ tham số nào.
- Cả hai trường hợp: ngưỡng trong `GATES.md` giữ nguyên.

## Giới hạn, ghi thẳng

- Không thể đánh giá cổng **M4** (có đủ patch thật trong vùng tác hại một phần không) trước khi có dữ liệu sinh patch, nên quyết định này **dựa vào tính khả thi, không dựa vào xác suất kết quả**.
- Điều kiện F2 có phần chủ quan; vì vậy nguyên văn phản biện được lưu lại và người hướng dẫn cùng đánh giá.
- Credit Developer có tên loại là "MONTHLY" nhưng bảng credit chỉ hiện một khoản; **chưa xác minh** nó có được cấp lại hằng tháng không. Nếu có, F4 của RR dễ đạt hơn.
