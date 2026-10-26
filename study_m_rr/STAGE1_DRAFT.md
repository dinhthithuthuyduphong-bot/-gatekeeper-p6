# Bản nháp báo cáo Stage 1 (MSR 2027 Registered Reports; tối đa 6 trang + 1 trang tài liệu tham khảo, mẫu IEEE)

Hạn: tóm tắt 13/11/2026; báo cáo 20/11/2026. **Đây là nháp nội dung, chưa phải bản nộp.** Loại: **nghiên cứu xác nhận** (confirmatory), vì chỉ loại này nhận IPA.

## Khung theo hướng dẫn tác giả của MSR

**Tiêu đề (tạm):** When does a statistical admission gate beat a simple one? A pre-registered study of behavioural divergence in plausible LLM patches.

**Tóm tắt có cấu trúc (khoảng 200 từ).** *Bối cảnh:* patch do mô hình ngôn ngữ sinh ra thường được chấp nhận khi qua bộ test; nhưng nhiều patch plausible vẫn khác bản fix của upstream về hành vi. *Mục tiêu:* đo mức độ chênh lệch hành vi còn sót lại và so sánh các cổng chấp nhận ở cùng ràng buộc rủi ro. *Phương pháp:* cohort PR sửa lỗi Python chưa lộ, khám phá theo quy tắc đóng băng; patch sinh bằng pipeline đã đóng băng; chênh lệch hành vi đo bằng vi sai ở mức test so với bản fix của upstream.

## Giả thuyết xác nhận (nháp)

| Mã | Giả thuyết | Cơ sở | Kiểm định |
|---|---|---|---|
| H1 | Hơn 10% patch plausible có tỉ lệ chênh lệch ĥ trong [1%, 10%] | Wang, Pradel và Liu (ICSE 2026) thấy 29,6% patch plausible khác bản gốc về hành vi; đồ thị pha cho thấy cổng đơn giản chỉ sai trong dải này | Nhị thức chính xác một phía, H0: p ≤ 0,10, α = 0,05 |
| H2 | Smoke test 20 lần admit sai hơn 15% patch không chấp nhận được (ĥ > 5%) | Mô phỏng: (1 − h)^20 là 36% ở h = 5% | Nhị thức chính xác một phía, H0: p ≤ 0,15 |
| H3 | Kiểm định cỡ mẫu cố định (cùng θ, η, α) admit **ít nhất bằng** Gatekeeper cố định trên các patch chấp nhận được | Mô phỏng: ở 300 draw, cỡ mẫu cố định mạnh hơn (h = 2%: 0,92 so với 0,64) | McNemar một phía trên quyết định ghép cặp |

**Khám phá (không xác nhận):** khác biệt giữa các model; phân bố ĥ; thời gian chạy.

**Phân tích công suất cho H1** (nhị thức chính xác, p₀ = 0,10, p₁ = 0,20, α = 0,05): n = 60 patch: 0,68; n = 100: 0,87; n = 150: 0,96; n = 200: 0,99. Các con số giả định patch độc lập; vì patch cùng instance và cùng repo tương quan nhau, đây là **cận trên** của công suất. Phân tích chính dùng bootstrap theo cụm repo.

## Biến

| Biến | Loại | Thao tác hoá |
|---|---|---|
| Cổng (độc lập) | danh mục: census-only, B8+, smoke 20, cỡ mẫu cố định, Gatekeeper | quy tắc đã đóng băng |
| ĥ (phụ thuộc) | liên tục | tỉ lệ draw mà patch khác bản fix trong khi bản gốc giống bản fix |
| Quyết định admit (phụ thuộc) | nhị phân | theo từng cổng |
| Số draw dùng (phụ thuộc) | đếm | theo từng cổng |
| Instance, repo, model (nhiễu) | danh mục | hiệu ứng cụm; bootstrap theo repo |

## Dữ liệu

Nửa RR của cohort (chia theo repo bằng quy tắc đã đóng băng, amendment M-A1); mục tiêu ≥ 40 instance đủ điều kiện; 2–3 model, 3 lần lặp. Nhãn độc lập: test ẩn fail-to-pass và pass-to-pass của upstream. Seed lấy từ drand sau thời điểm đóng băng.

## Kiểm tra không phụ thuộc kết quả (đối chứng dương, kiểm tra chất lượng)

Mỗi instance: (a) đột biến AST của bản fix phải bị bắt (đối chứng dương); (b) kết quả tất định qua hai lần chạy mới; (c) không thiếu cặp kết quả; (d) có ít nhất một draw mà bản gốc khác bản fix. Instance không qua bị loại **và được ghi trong bảng hao hụt**, không được thay thế. Nếu dưới 40 instance đủ điều kiện, giả thuyết xác nhận không được kiểm định và kết quả được báo cáo là thiếu khung mẫu.

## Dữ liệu thử nghiệm được khai báo trong Stage 1 (không phải dữ liệu của cohort)

Sáu instance phát triển đã lộ (D1–D5, A1): chỉ để chứng minh phép đo chạy được (đột biến bản fix bị bắt ở 5/5 instance đã chạy; thấy lỗi ở 4/5 instance với tỉ lệ 0–6,6%); kết quả âm của Study L (call replay 2/6); đồ thị pha; số hao hụt của S1.

## Giới hạn

Tập đột biến hữu hạn nhỏ (vài trăm draw duy nhất), không đo được ĥ dưới khoảng 1%; draw không hoàn lại nên các kiểm định tuần tự chỉ gần đúng; cohort từ tìm kiếm GitHub không phải mẫu ngẫu nhiên; chỉ lỗi nhỏ, cục bộ (diff nguồn ≤ 60 dòng). **Rủi ro phạm vi:** báo cáo có thể bị coi là ngoài phạm vi MSR.

## Sai khác so với kế hoạch

Mọi sai khác được ghi trong một mục riêng của bài đầy đủ, theo yêu cầu của track.
