# Kế hoạch hai nhánh: RR và A\*, đánh giá song song tới giai đoạn tốn tiền (26/10/2026)

## 1. Cấu trúc

```
study_m/            thân chung, đã đóng băng: S1 (khám phá + thứ tự theo seed) và amendment M-A1 (quy tắc chia)
study_m_astar/      nhánh A*: S2 (kiểm định), S3 (harness), GATES.md, DECISION_RULE.md, candidates.json
study_m_rr/         nhánh RR: STAGE1_DRAFT.md; nửa cohort RR không được xem tới khi có IPA
```

Chia thành **hai thư mục study**, không phải hai nhánh git: cơ chế đóng băng, hash và workflow hiện có đều gắn với từng thư mục; hai nhánh git sẽ làm công cụ dùng chung lệch nhau.

## 2. Chia cohort

Sau khi S1 cho danh sách có thứ tự, mỗi repo được gán vào RR hoặc A\* theo tính chẵn lẻ của SHA-256 của `seed:track:repo`. Chia **theo repo** để hai cohort độc lập. Nửa A\* được kiểm định ngay; nửa RR **không** được kiểm định, chạy hay xem tới khi có IPA. Điều này giữ tư cách "chưa thu dữ liệu" của RR.

## 3. Mỗi nhánh làm gì tới ngày quyết định (10/1/2027)

| Thời gian | Nhánh RR | Nhánh A\* |
|---|---|---|
| 27/10 – 12/11 | Hoàn thiện khung S1; viết giả thuyết, biến, kế hoạch phân tích | Chia cohort; đóng băng `GATES.md`; chạy S2 |
| 13/11 | Nộp tóm tắt | |
| 20/11 | **Nộp báo cáo Stage 1** (6 trang) | |
| 20/11 – 30/11 | Chờ | S3: kiểm tra harness; cổng M1, M2 |
| 23/12 | Nhận phản biện (4 phản biện viên) | |
| **10/1/2027** | **Quyết định theo `DECISION_RULE.md`, trước mọi lượt gọi mô hình trả phí** | |
| 15/1 | Nộp bản sửa (nếu chọn RR) | |
| 4/2 | Thông báo Stage 1 | |

## 4. Tiêu chí "khả thi hơn", đã đăng ký trước

Năm điều kiện F1–F5 và bốn luật trong `study_m_astar/DECISION_RULE.md`, đóng băng trước S2. Tóm tắt: nếu cohort không đủ khả thi thì **không nhánh nào chạy**; nếu luận văn cần kết quả trước 4/2/2027 hoặc RR bị loại về phạm vi hoặc không đi được Dublin thì **A\***; còn lại thì **RR**.

## 5. Xung đột đã được xử lý

| Xung đột | Cách xử lý |
|---|---|
| RR cấm thu dữ liệu trước IPA, A\* cần dữ liệu sớm | Hai nửa cohort rời nhau theo repo; nửa RR không bị chạm |
| RR cấm nộp đồng thời nơi khác | Nhánh A\* không nộp gì trước ngày quyết định |
| Trùng lặp xuất bản nếu cả hai nhánh cho kết quả | Chỉ một nhánh được công bố; nửa còn lại chỉ là dữ liệu thử nghiệm, khai báo rõ |
| Rút báo cáo RR nếu chọn A\* | Quy định rút chưa rõ: hỏi chair của track sớm |

## 6. "Giai đoạn tốn tiền"

Lượt gọi mô hình trả phí đầu tiên (cổng M3, dưới 5 USD). Mọi thứ trước đó, gồm S1, S2, S3 và việc viết báo cáo RR, đều 0 đồng.

## 7. Giới hạn của chính cách so sánh này

- **Không đo được điều quyết định nhất trước khi tốn tiền:** cổng M4 (có đủ patch thật trong vùng tác hại một phần không). Vì vậy việc chọn nhánh dựa trên **tính khả thi**, không dựa trên xác suất của kết quả.
- Các xác suất nêu trước đây (RR khoảng 25–40% cho chuỗi đến EMSE, A\* khoảng 5–10%) vẫn là phán đoán độ tin cậy thấp.
- Tập đột biến test-level nhỏ làm phần thống kê tuần tự mỏng ở quy mô này; kết quả so sánh cổng mang tính mô tả.

## 8. Việc của bạn, theo thứ tự

1. Khai báo F3 (luận văn có cần kết quả trước 4/2/2027 không) và F5 (có đi Dublin được không) **trước 13/11**.
2. Gửi tôi artifact `STUDY_M_DISCOVERY` để tôi chia cohort.
3. Đóng băng nhánh A\*, chạy S2.
4. Cùng Thầy duyệt bản nháp báo cáo Stage 1.
