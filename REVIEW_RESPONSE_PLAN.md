# Trả lời review paperreview.ai lần 2 và kế hoạch cải thiện (0 đồng, B9 vẫn HOLD)

Mọi phân tích dưới đây chạy trên **trace đã đóng băng** của Study D/E và được ghi nhãn **thứ cấp / post hoc**. Không phân tích nào thay đổi kết quả chính đã đăng ký. Kết quả chi tiết: `study_d/results/SECONDARY_ANALYSES_D_E.md` (workflow `secondary-analyses.yml`).

| # | Điểm reviewer nêu | Trạng thái | Bằng chứng / việc còn lại |
|---|---|---|---|
| 1 | Chiến lược betting và λ chưa mô tả | **Xong** | Lợi ích: betting predictable kiểu aGRAPA, λ = (m̂−θ)/(σ̂²+(m̂−θ)²) cắt về [0; 0,5/(1+θ)], m̂ co về prior 0,5 (trọng số 1); không phải mixture. Chứng nhận: λ cố định = 0,9/(1−η). Báo động: Kelly cho h = 0,5 (μ = 9,47). |
| 2 | Độ nhạy theo λ | **Xong (mô phỏng)** | λ/λmax = 0,5/0,7/0,9/0,99: số lần rút để admit khi h = 0 là 196/141/110/100; P(admit) khi h = 2% là 0,20/0,40/0,33/0,20; sai số ở biên h = η ≤ 0,007. 0,7 tốt hơn 0,9 khi tác hại hiếm; cấu hình mới phải đăng ký trước. |
| 3 | Độ nhạy θ, η | **Xong (trên trace thật)** | Mọi tổ hợp θ ∈ {0,05; 0,1; 0,2; 0,3}, η ∈ {0,02; 0,05; 0,1} đều chặn đủ 3 ô có hại; D5 được admit khi θ = 0,05. |
| 4 | `e = 0` cho ô ngoài scope trong e-Holm | **Xong** | Binding xảy ra trước mọi lần rút nên loại ô ngoài scope khỏi họ là hợp lệ. K = 16 → 12: cùng tập ô được admit, admit sớm hơn (104 thay vì 110 lần rút). Thiết kế cho study mới: loại ô ngoài scope khỏi họ. |
| 5 | Confidence sequence | **Xong** | CS 95% kiểu hedged capital tại thời điểm dừng: D1 μ ∈ [−0,87; −0,64], h ∈ [0; 0,06]; D3 μ ∈ [−0,65; −0,37]; D5 μ ∈ [−0,15; −0,06] (dưới biên θ). |
| 6 | Ô trung tính tốn hết ngân sách | **Xong (khám phá)** | Dừng khi cận trên CS cho lợi ích < θ: Study D 3.220 → 540 lần rút, Study E 2.106 → 216; **không đổi quyết định nào**. Phải đăng ký trước trong study tiếp theo. |
| 7 | B6-R quá yếu | **Đã làm phần 0 đồng; kết luận phải chỉnh** | Baseline mạnh hơn **B6-S(k)** (replay + fingerprint + census + k lần smoke test bằng bộ sinh của scope) chặn **cả 3 ô có hại với k = 1**. Trên dữ liệu này, baseline mạnh **an toàn ngang Gatekeeper**; khác biệt còn lại: B6-S admit 13 thay đổi vô ích và không có bảo đảm khi tác hại hiếm. **Luận điểm "an toàn hơn B6-R" phải được giới hạn là "an toàn hơn replay + fingerprint thuần".** |
| 8 | Độ bao phủ của bộ sinh | **Đã có công cụ, chờ chạy** | `tools/coverage_reach.py`, workflow `coverage-reach.yml`: tái tạo đúng chuỗi lần rút bằng seed và đo lần rút nào đi qua dòng bị skill sửa, đối chiếu với có lợi/hoà/có hại. Kỳ vọng ở D5: đi qua nhiều, có tác dụng ít (đi qua ≠ thay đổi hành vi). |
| 9 | Chỉ một skill, một họ lỗi | **Bắt đầu** | Skill thứ hai `none-identity` (E711) trong `gatekeeper_ext/`, có test, không đụng file đã đóng băng. Thiết kế Study G: `study_g/STUDY_G_DESIGN_DRAFT.md`. Ưu điểm: họ lỗi này có ô có hại với **oracle cấp 1** (SQLAlchemy). Việc còn lại: chốt nguồn skill, khung chọn target, quét, kiểm định. |
| 10 | Oracle có hại E2/E3 yếu | **Không sửa được trên D/E** | Đã giới hạn luận điểm an toàn chính vào E1. Cấp 1 chỉ có thể đến từ target mới (Study G). |
| 11 | Trial đắt (LLM trong vòng lặp) | **Thiết kế xong (Study F), chờ ngân sách** | B9 vẫn HOLD. Amendment A3 (cho phép chạy bằng credit trước 31/10, hạn mức theo model) đã chuẩn bị nhưng **chưa áp dụng**. |
| 12 | RTS / baseline kiểm thử lại + ngưỡng lợi ích | **Ghi trong bài** | B6-S chính là "kiểm thử lại + không regression"; thêm ngưỡng lợi ích vào B6-S sẽ biến nó thành Gatekeeper không có bảo đảm sai số. RTS bổ trợ cho census, không thay thế. |

## Sửa sau review ngày 22/10/2026 (commit `6f2d2d2`)

| # | Lỗi reviewer tái hiện | Đánh giá | Đã sửa |
|---|---|---|---|
| 1 | `none-identity`: `(x if flag else y) == None` thành `x if flag else y is None` | **Đúng** | Bọc ngoặc mọi toán hạng không nguyên tử; test so sánh ngữ nghĩa trên 12 dạng biểu thức và 6 giá trị |
| 2 | Công cụ độ bao phủ nuốt exception, ghi 0% khi môi trường hỏng | **Đúng** | Ghi lỗi từng lần rút, kiểm tra module được trace đúng là file trong snapshot, trả `INVALID` và mã thoát 1; **phải chạy lại** `coverage-reach.yml` trước khi dùng bảng độ bao phủ |
| 3 | Nhánh K = 16 thiếu 4 ô ngoài scope | **Đúng** | Nhánh K = 16 có đủ 16 ô (4 ô e = 0), có kiểm tra kích thước họ; kết luận không đổi (admit sau 110 so với 104 lần rút) |
| 4 | Study F: triển khai patch dù scope khác REJECT_HARM; thiếu e-Holm cả họ; công cụ chấm ngoài hash | **Đúng, nghiêm trọng** | Amendment **F-A1**: cổng mới, `aggregate_study_f.py` (e-Holm trên **K = 144**, gồm cả lần lặp), `extra_tracked`, seed held-out ghim theo hash gốc; có test |
| 5 | Hash Study E hỏng (b9.py, run_b9.py) | **Đúng; không ảnh hưởng kết quả** | Amendment **E-A1**: E không dùng B9, đã chạy và tái lập trước A2; chỉ đóng băng lại |
| 6 | B6-S tính lại từ trace | **Đồng ý một phần** | Tính từ trace là chính xác (k lần smoke = k lần rút đầu của cùng bộ sinh); bằng chứng độc lập sẽ đến từ việc đăng ký B6-S trước trong Study G |
| 7 | Khoảng bất định Monte Carlo cho độ nhạy λ | **Đúng** | Thêm khoảng Wilson 95%; ghi rõ đây là kiểm tra từng ô, không phải FWER cả họ |
