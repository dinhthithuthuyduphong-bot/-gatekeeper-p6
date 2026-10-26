# Kế hoạch hai nhánh chạy song song: A\* và RR (một nhánh git `main`, hai thư mục study), 26/10/2026

## 1. Cấu trúc đã chọn và lý do

```
study_m/          thân chung, đóng băng: S1 (khám phá + thứ tự theo seed) và amendment M-A1 (quy tắc chia)
study_m_astar/    nhánh A*: GATES.md, DECISION_RULE.md, candidates.json; S2 (kiểm định), S3 (harness)
study_m_rr/       nhánh RR: STAGE1_DRAFT.md; nửa cohort RR không được xem tới khi có IPA
```

Một nhánh git `main` chứ không phải hai: mọi workflow hiện trong tab Actions và chạy từ một nơi; không có ô chọn nhánh để bấm nhầm; không lệch công cụ dùng chung; tag không trùng. Sự tách biệt nằm ở **hash đóng băng của từng thư mục**, ở **chốt chặn `check_track.py`** (workflow kiểm định dừng nếu bất kỳ ứng viên nào không thuộc nhánh A\*), và ở việc **không có workflow nào cho nửa RR** cho tới khi có IPA.

## 2. Chia cohort

Mỗi repo được gán vào RR hoặc A\* theo tính chẵn lẻ của SHA-256 của `seed:track:repo` (amendment M-A1), nên hai nửa rời nhau theo repo. Nửa A\* được kiểm định ngay; nửa RR **không** được kiểm định, chạy hay xem kết quả tới khi có IPA.

## 3. Việc chạy song song và mỗi việc cho biết điều gì về tiềm năng (trước khi tốn tiền)

| Khi nào | Nhánh | Việc | Cho biết gì |
|---|---|---|---|
| 27/10 – 12/11 | RR | Hoàn thiện giả thuyết, biến, kế hoạch phân tích, báo cáo 6 trang | Thiết kế có đứng vững không |
| 27/10 – 12/11 | A\* | Chia cohort, đóng băng `GATES.md` và `DECISION_RULE.md`, chạy S2 | **M1**: có đủ instance có test fail trước, pass sau không |
| 13/11, 20/11 | RR | Nộp tóm tắt, rồi báo cáo Stage 1 | |
| 20/11 – 30/11 | A\* | S3 (harness) | **M2**: có đủ instance đủ điều kiện cho phép đo không |
| 23/12 | RR | Nhận phản biện (4 người) | **F2**: có thuộc phạm vi MSR không, có phản đối căn bản không |
| **10/1/2027** | cả hai | **Chọn theo `DECISION_RULE.md`, trước mọi lượt gọi mô hình trả phí** | |
| 15/1, 4/2 | RR | Bản sửa; thông báo Stage 1 | |

**Điều không đo được trước khi tốn tiền:** cổng M4, tức patch thật có nằm trong vùng tác hại một phần không. Vì vậy chọn nhánh dựa trên **tính khả thi**, không dựa trên xác suất của kết quả.

## 4. Quy tắc chọn (đã đăng ký trước, đóng băng cùng nhánh A\*)

F1 cohort khả thi (M1 và M2 đạt); F2 báo cáo RR không bị loại về phạm vi và không bị phản đối căn bản; F3 luận văn cần kết quả trước 4/2/2027; F4 credit còn hiệu lực; F5 đi được Dublin. Luật theo thứ tự: F1 không đạt thì **cả hai dừng**; F3 = có thì **A\***; F2 không đạt hoặc F5 = không thì **A\***; còn lại thì **RR**.

## 5. Sau ngày quyết định

- **Chọn RR:** `study_m_rr` là nhánh làm việc; nửa RR bắt đầu được kiểm định sau IPA. Dữ liệu của nhánh A\* chỉ là dữ liệu thử nghiệm, khai báo rõ; không công bố riêng.
- **Chọn A\*:** gắn tag lưu trữ cho `study_m_rr` và dừng; nửa RR không bao giờ được mở và không dùng để chọn tham số nào; rút báo cáo RR (hỏi chair sớm về quy định rút bài).

## 6. Xung đột đã xử lý

| Xung đột | Cách xử lý |
|---|---|
| RR cấm thu dữ liệu trước IPA, A\* cần dữ liệu sớm | Hai nửa cohort rời nhau theo repo; nửa RR không bị chạm |
| RR cấm nộp đồng thời nơi khác | Nhánh A\* không nộp gì trước ngày quyết định |
| Trùng lặp xuất bản | Chỉ một nhánh được công bố; nửa còn lại là dữ liệu thử nghiệm, khai báo rõ |
| Danh sách nửa RR nằm trong kho | Danh sách ứng viên không phải dữ liệu thu được; việc không chạm được bảo đảm bằng hash, guard và việc không có workflow cho nửa RR |

## 7. Giới hạn

Các xác suất đã nêu (RR khoảng 25–40% cho chuỗi đến EMSE, A\* khoảng 5–10%) là phán đoán độ tin cậy thấp. Phần thống kê tuần tự mỏng ở quy mô test-level (vài trăm draw duy nhất, không đo được tác hại dưới khoảng 1%).

## 8. Việc của bạn

1. Khai báo F3 và F5 trước 13/11/2026.
2. Gửi artifact `STUDY_M_DISCOVERY` để chia cohort.
3. Kiểm tra xem project AI Studio không bật thanh toán có dùng được free tier cho Gemini Flash không (xem mục "đo tiềm năng miễn phí" trong câu trả lời).
