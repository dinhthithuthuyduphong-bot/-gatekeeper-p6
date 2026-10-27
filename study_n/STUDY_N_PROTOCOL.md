# Study N: giao thức đăng ký trước (bản đóng băng)

## 1. Mục đích và quan hệ với Study M

Study M dừng ở cổng M1 (25/250 ELIGIBLE) vì khâu cài môi trường của công cụ kiểm định, không phải vì PR thiếu test. Lượt phát triển trên nửa A\* đã lộ của Study M cho thấy khâu cài đặt bản 2 nâng tỉ lệ ELIGIBLE lên 23,8% (57/240). Study N dùng **cohort chưa lộ** và khâu cài đặt bản 2.1, với cùng câu hỏi nghiên cứu. Study M được báo cáo đầy đủ, kể cả cổng thất bại.

## 2. Câu hỏi nghiên cứu

- **RQ1:** trong patch plausible (qua test fail-to-pass và pass-to-pass ẩn của upstream), tỉ lệ chênh lệch hành vi ĥ phân bố ra sao; bao nhiêu patch nằm trong vùng mà cổng đơn giản dễ sai?
- **RQ2:** ở cùng ràng buộc rủi ro, các cổng (census-only, zero-tolerance B8+, smoke 20, kiểm định cỡ mẫu cố định, Gatekeeper cố định) giữ được bao nhiêu patch chấp nhận được và chặn được bao nhiêu patch không chấp nhận được?
- **RQ3:** phép đo vi sai ở mức test so với bản fix upstream (lọc theo độ phủ) có hợp lệ không: đối chứng dương, tính tất định, độ đồng thuận với test ẩn?
- **RQ4 (thăm dò):** kết quả khác nhau thế nào giữa model nhẹ và model mạnh (nếu nhánh model mạnh được mở theo mục 6)?

**Giả thuyết xác nhận:**
- **H1:** hơn 10% patch plausible có ĥ trong vùng [max(1%, 2/n), 10%], với n là số draw đủ cặp của instance. Kiểm định nhị thức chính xác một phía, H0: p ≤ 0,10, α = 0,05.
- **H2:** smoke 20 lần admit sai hơn 15% patch không chấp nhận được (ĥ > 5%). Nhị thức chính xác một phía, H0: p ≤ 0,15.
- **H3:** kiểm định cỡ mẫu cố định (cùng θ = 0,2, η = 0,05, α = 0,1) admit ít nhất bằng Gatekeeper cố định trên các patch chấp nhận được. McNemar một phía trên quyết định ghép cặp.

Phân tích chính dùng bootstrap theo cụm repo; các con số công suất giả định patch độc lập nên là cận trên.

## 3. Khung mẫu

- **Thứ tự:** thứ tự theo seed drand của Study M giai đoạn S1 (`study_m/config_study_m.json`, seed ghim theo lần đóng băng gốc), cùng truy vấn, cửa sổ, bộ lọc (`study_m/INCLUSION_RULES.md`).
- **500 ứng viên đầu đã lộ một phần:** nửa A\* đã được kiểm định (dùng làm dữ liệu phát triển); nửa RR chưa bị chạm.
- **Phần tiếp theo:** các PR có khoá thứ tự lớn hơn khoá lớn nhất trong 500 ứng viên đầu (`tools/discover_n_continue.py`); định nghĩa bằng khoá chứ không bằng vị trí, nên ổn định khi kết quả tìm kiếm thay đổi.
- **Chia nhánh:** quy tắc của amendment M-A1 (theo repo, cùng seed).
- **Nhánh A\*:** `candidates_astar.json`, chỉ gồm ứng viên A\* của phần tiếp theo, theo thứ tự.
- **Nhánh RR:** `frame_rr.json`, gồm nửa RR của 500 đầu rồi phần RR của phần tiếp theo; **không được kiểm định, chạy hay xem** trước khi có IPA.

## 4. Các giai đoạn của nhánh A\*

| Giai đoạn | Nội dung | Chi phí |
|---|---|---|
| N-S2 | Kiểm định `min(400, n)` ứng viên đầu bằng `tools/vet_target2.py` bản 2.1 | 0 |
| N-S3 | Harness vi sai mức test `tm-dev-v4-reach` trên các instance ELIGIBLE | 0 |
| N-GEN | Sinh patch theo cấu hình đóng băng bằng amendment N-A1 (mục 6) | credit Free Trial |
| N-SCORE | Nhãn ẩn (test fail-to-pass và pass-to-pass của upstream) và draw vi sai cho mỗi patch; quyết định của từng cổng trên cùng draw | 0 |

## 5. Ngân sách

Chỉ credit Free Trial (khoảng 288 USD, hết hạn 20/1/2027) cho nhánh A\*. Tổng chi cho N-GEN không vượt **200 USD**, phần còn lại dự phòng. Giới hạn chi theo từng instance và từng model được đặt trong N-A1.

## 6. Cấu hình sinh patch và quy tắc dùng model mạnh

Cấu hình (model, trần token, `reasoning_effort`, giới hạn chi, số lần lặp) được **đóng băng bằng amendment N-A1 trước khi sinh bất kỳ patch nào cho cohort**, và chỉ dựa trên các lượt thử trên **tập phát triển** (57 instance ELIGIBLE của nửa A\* đã lộ trong Study M). Các lượt thử đó không bao giờ dùng instance của cohort.

- **Model nhẹ bắt buộc:** `google/gemini-3.8-flash`.
- **Thử P0** (chỉ model nhẹ, tối đa 2 USD): 10 instance phát triển × 2 lần lặp. Đạt nếu (a) ít nhất 8 instance chạy trọn chuỗi sinh patch và chấm điểm mà không lỗi harness, và (b) có ít nhất 1 patch plausible.
- **Thử P1** (`google/gemini-4-argon`, chỉ khi P0 đạt, tối đa 3 USD, chạy trước 30/11/2026 khi còn giá khuyến mãi): 6 instance phát triển × 1 lần lặp, trần đầu ra 32.768 token. Đo token suy luận, tỉ lệ bị cắt và tỉ lệ plausible.
- **Nhánh model mạnh được mở trong N-GEN** khi và chỉ khi: tỉ lệ plausible của Argon ở P1 **không thấp hơn** của model nhẹ trên cùng instance, **và** chi phí dự kiến của toàn bộ N-GEN (theo giá tại thời điểm chạy và token đo ở P0, P1) không vượt 200 USD. Nếu không, N-GEN chỉ dùng model nhẹ và Argon không được dùng thêm.
- `gemini-3.1-pro-preview` không được dùng (bản xem trước, có thể bị gỡ hoặc chuyển hướng giữa chừng).

## 7. Báo cáo và sai khác

Mọi sai khác so với giao thức được ghi trong một mục riêng. Không thay thế ứng viên; mọi ca hỏng là kết quả và nằm trong bảng hao hụt. Kết quả của nhánh không được chọn (theo `DECISION_RULE.md`) chỉ được báo cáo như dữ liệu thử nghiệm.

## 8. Giới hạn đã biết

Tập đột biến test-level hữu hạn nhỏ (không đo được ĥ dưới khoảng 1%; draw không hoàn lại nên kiểm định tuần tự chỉ gần đúng). Chỉ Python 3.12. Cohort từ tìm kiếm GitHub không phải mẫu ngẫu nhiên. Khâu cài đặt bản 2 có thể làm hỏng một số ít ca do kéo phiên bản gói mới hơn (2/240 trong lượt phát triển).
