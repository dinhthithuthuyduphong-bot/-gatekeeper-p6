# Study F — hiệu ứng của Gatekeeper theo từng model (BẢN NHÁP, chưa đóng băng)

**Trạng thái và thời điểm đóng băng:** ghi trong `config_study_f.json`, do workflow đóng băng đặt; hash trong `FREEZE.json`. Study F phải được đóng băng **trước** lượt B9 trả phí đầu tiên, vì seed held-out lấy từ drand sau thời điểm đóng băng này.

## 1. Câu hỏi

Study D/E không có model trong vòng lặp: skill là một phép biến đổi AST cố định. Vì vậy **chưa thể trả lời "đổi model thì kết quả có như vậy không"**. Study F hỏi: với mỗi model sinh patch, **Gatekeeper thay đổi kết quả triển khai tới đâu?**

## 2. Thiết kế

- **Giữ cố định:** 6 target có lỗi của Study D, oracle đã đóng băng, mô tả lỗi, quyền sửa, ngân sách B9 (5 lần gọi, 4.000 token ra, 5 lần kiểm tra công khai), 3 lần lặp.
- **Thay đổi duy nhất:** model sinh patch. Bốn model: DeepSeek Flash (nhà cung cấp khác Google), Gemini 3.1 Flash-Lite (AI Studio), và hai model Gemini qua Vertex AI (Flash, Pro). Model ID chính xác được ghi khi đóng băng. Hai model Gemini đầu tiên đến từ cùng một họ; kết luận ngoài họ Gemini chỉ dựa trên DeepSeek.
- **Điều kiện cho mỗi model:**
  - **B9 thô:** triển khai patch qua được kiểm tra công khai.
  - **B9 + Gatekeeper:** triển khai cùng patch đó **chỉ khi** quy tắc Gatekeeper admit ít nhất một scope trên seed **admission** (seed của Study D) và census không có regression.
- **Chấm điểm độc lập:** mọi trạng thái cuối (skill + Gatekeeper/B6-R/B8, B9 thô, B9 + Gatekeeper) được chấm trên seed **held-out** lấy từ drand sau thời điểm đóng băng Study F. Seed held-out không được dùng cho bất kỳ quyết định admit nào.

## 3. Chỉ số (khai báo trước)

Theo từng model, trên 6 target × 3 lần lặp:
- tỉ lệ SUCCESS, HARMFUL, NO_EFFECT, NO_PATCH, BUDGET_CAP của **B9 thô** và **B9 + Gatekeeper**;
- **hiệu ứng trong cùng model:** Δ_success = success(B9+GK) − success(B9 thô) và Δ_harm = harmful(B9+GK) − harmful(B9 thô);
- chi phí: USD thực tế (từ `usage` của nhà cung cấp), số lần gọi, số lần rút.

## 4. Cách diễn giải (đối xứng, khai báo trước)

- Báo cáo bảng theo từng model và từng target; không công bố "người thắng" duy nhất.
- So sánh skill + Gatekeeper với B9 theo **cùng một tiêu chí**: một cách tiếp cận "tốt hơn ở target X" khi có tỉ lệ SUCCESS cao hơn **và** tỉ lệ HARMFUL không cao hơn ở target đó. Áp dụng cho cả hai chiều.
- Nếu Gatekeeper không làm thay đổi kết quả của model nào (ví dụ mọi patch đều vô hại), báo cáo đúng như vậy: khi đó Gatekeeper chỉ thêm chi phí.
- 6 target × 3 lần lặp **không** phải 18 target độc lập; lần lặp chỉ đo biến động sinh mẫu của model.

## 5. Ngân sách

Cận trên và kỳ vọng tính từ kích thước prompt thật (342.312 ký tự cho 6 target):

| Model | Xấu nhất | Kỳ vọng | Nguồn tiền |
|---|---|---|---|
| DeepSeek Flash | ≈ 53.000 đ | ≈ 7.000 đ | tiền mặt (trả trước) |
| Gemini 3.1 Flash-Lite | ≈ 49.000 đ | ≈ 7.000 đ | credit Google Developer Program (AI Studio) |
| Vertex Gemini Flash | ≈ 140.000 đ | ≈ 19.000 đ | credit Free Trial Google Cloud |
| Vertex Gemini Pro | ≈ 394.000 đ | ≈ 55.000 đ | credit Free Trial Google Cloud |

Giá lấy theo bản đánh giá tháng 10/2026, phải kiểm tra lại trên trang giá chính thức khi đóng băng.

## 6. Rủi ro đã biết

- Patch của model có thể đều vô hại trên 6 target này; khi đó Study F không đo được tác dụng chặn tác hại theo model, chỉ đo được tác dụng chặn thay đổi vô ích.
- Credit Free Trial hết hạn 90 ngày kể từ ngày đăng ký; phải chạy trước hạn.
