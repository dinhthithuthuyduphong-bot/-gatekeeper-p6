# Study F — hiệu ứng của Gatekeeper theo từng model (F-A3; paid B9 HOLD)

**Trạng thái và thời điểm đóng băng:** ghi trong `config_study_f.json`, do workflow đóng băng đặt; hash trong `FREEZE.json`. Study F phải được đóng băng **trước** lượt B9 trả phí đầu tiên, vì seed held-out lấy từ drand sau thời điểm đóng băng này.

## 1. Câu hỏi

Study D/E không có model trong vòng lặp: skill là một phép biến đổi AST cố định. Vì vậy **chưa thể trả lời "đổi model thì kết quả có như vậy không"**. Study F hỏi: với mỗi model sinh patch, **Gatekeeper thay đổi kết quả triển khai tới đâu?**

## 2. Thiết kế

- **Giữ cố định:** 6 target có lỗi của Study D, oracle đã đóng băng, mô tả lỗi, quyền sửa, ngân sách B9 (5 lần gọi, 4.000 token ra, 5 lần kiểm tra công khai), 3 lần lặp.
- **Thay đổi duy nhất:** model sinh patch. Bốn model: DeepSeek Flash (nhà cung cấp khác Google), Gemini 3.1 Flash-Lite (AI Studio), và hai model Gemini qua Vertex AI (Flash, Pro). Model ID chính xác được ghi khi đóng băng. Hai model Gemini đầu tiên đến từ cùng một họ; kết luận ngoài họ Gemini chỉ dựa trên DeepSeek.
- **Điều kiện cho mỗi model:**
  - **B9 thô:** triển khai patch qua được kiểm tra công khai.
  - **B9 + Gatekeeper:** triển khai cùng patch đó khi quy tắc F-A2 chứng nhận patch: có lợi ích ở ít nhất một scope, ít hại ở mọi scope, census hợp lệ không có regression. Dùng seed **admission** của D; e-Holm trên toàn bộ 72 patch. Thiếu dữ liệu không được điền ngầm bằng 0.
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
- Đây là bộ lọc cùng patch, nên số SUCCESS sau gate không thể tăng. Báo cáo số SUCCESS giữ lại/mất đi cùng số HARMFUL bị chặn; không tuyên bố tăng khả năng sinh sửa lỗi của model.
- Không có harmful raw patch là trường hợp chưa đánh giá được năng lực chặn hại, không phải tỷ lệ chặn 100%. Các bảng nhỏ không chứng minh model independence.
- Schema F-A3 lưu đủ trace admission và held-out, tính lại e-value khi tổng hợp; thiếu model, repetition, scope, provider usage hoặc có harness error thì dừng với lỗi.
- Fixed skill + Gatekeeper dùng quy tắc patch F-A2 trên sáu fixed patches từ D (họ comparator riêng); B6-R/B8 giữ quyết định gốc. Đây không sửa kết quả chính D/E/G/H.

## 5. Ngân sách

Cận trên và kỳ vọng tính từ kích thước prompt thật (342.312 ký tự cho 6 target):

| Model | Xấu nhất | Kỳ vọng | Nguồn tiền |
|---|---|---|---|
| DeepSeek Flash | ≈ 53.000 đ | ≈ 7.000 đ | tiền mặt (trả trước) |
| Gemini 3.1 Flash-Lite | ≈ 49.000 đ | ≈ 7.000 đ | credit Google Developer Program (AI Studio) |
| Vertex Gemini Flash | ≈ 140.000 đ | ≈ 19.000 đ | credit Free Trial Google Cloud |
| Vertex Gemini Pro | ≈ 394.000 đ | ≈ 55.000 đ | credit Free Trial Google Cloud |

Các số giá/chi phí trên là dự toán lịch sử, **không phải giá được xác minh trong đợt F-A3**. Phải kiểm tra model ID, endpoint, giá và quyền billing tại ngày chạy trước khi mở HOLD. Freeze hash không chứng minh thông tin giá còn đúng.

## 6. Rủi ro đã biết

- Patch của model có thể đều vô hại trên 6 target này; khi đó Study F không đo được tác dụng chặn tác hại theo model, chỉ đo được tác dụng chặn thay đổi vô ích.
- Credit Free Trial hết hạn 90 ngày kể từ ngày đăng ký; phải chạy trước hạn.
