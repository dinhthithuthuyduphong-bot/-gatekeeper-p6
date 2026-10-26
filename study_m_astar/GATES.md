# Study M, nhánh A\*: cổng quyết định (đóng băng TRƯỚC khi chạy giai đoạn S2)

**Nhánh này làm gì:** thực hiện nghiên cứu cohort cho một bản nộp A\* (ASE 2027 hoặc ICSE 2028), trên **nửa A\*** của cohort (xem amendment M-A1 của `study_m`). Nửa RR **không được kiểm định, chạy hay xem** cho tới khi có IPA.

**Quy tắc bất biến:** ngưỡng dưới đây không được sửa bằng amendment; muốn đổi phải mở study mới. Amendment chỉ được thêm công cụ.

## Giai đoạn và "giai đoạn tốn tiền"

S2 (kiểm định) và S3 (đủ điều kiện harness) **không tốn tiền**.

**"Tiền" ở đây là tiền mặt hoặc khoản credit không hết hạn sớm** (credit Developer Program, hết hạn 21/10/2027). Credit **Free Trial** (₫7.791.151, tương đương khoảng 289 USD, hết hạn **20/1/2027**) là khoản **dùng-hay-mất** và không thể dùng cho nhánh RR (nhánh RR chỉ được sinh patch sau 4/2/2027). Vì vậy chi bằng khoản này **không tính là chi tiền**, với điều kiện Vertex Gemini nằm trong phạm vi sử dụng của khoản đó (kiểm chứng bằng `tools/vertex_smoke.py` và báo cáo Credits trong Cloud Billing).

M3 và lượt sinh patch chính của **nửa A\*** được phép chạy trước ngày quyết định, **nếu và chỉ nếu** chỉ dùng credit Free Trial. Kết quả của chúng **không** là đầu vào của `DECISION_RULE.md` (luật chỉ dùng F1–F5), để việc chọn nhánh không thể phụ thuộc vào việc kết quả nào trông đẹp hơn.

## Cổng

| Cổng | Điều kiện đạt | Nếu không đạt |
|---|---|---|
| **M1** (S2, kiểm định) | Trong `min(250, số ứng viên)` ứng viên đầu của nhánh theo thứ tự đã đóng băng, **≥ 40** instance có test fail trước và pass sau (kết quả `ELIGIBLE` của `vet_target.py`). Nếu nhánh có **ít hơn 80** ứng viên thì cổng **không đạt** (khung mẫu không đủ) | Dừng nhánh. Không thay thế hay bổ sung ứng viên |
| **M2** (S3, harness) | **≥ 40** instance đủ điều kiện: test nền qua; có test chạy tới code bị sửa; ≥ **200** draw đủ cặp; tất định; bản gốc khác bản fix ở ít nhất 1 draw | Dừng nhánh |
| **M3** (dùng credit Free Trial, dưới 5 USD) | Trên 10 instance đủ điều kiện đầu tiên, một model rẻ, 2 lần lặp: ≥ **10** patch plausible (qua test fail-to-pass và pass-to-pass) | Sửa pipeline; không chi credit chính |
| **M4** (sau lượt sinh patch chính) | ≥ **15** patch plausible có ĥ trong **[1%, 10%]**, và ≥ **8** patch mà quyết định của Gatekeeper hoặc kiểm định cỡ mẫu cố định khác quyết định của cổng đơn giản (B8+ hoặc smoke 20) | Không có câu chuyện "cổng thống kê có giá trị"; chuyển thành bài đo đạc |

## Định nghĩa

- **ĥ:** tỉ lệ draw đủ cặp mà patch khác bản fix trong khi bản gốc giống bản fix (hồi quy R), tính trên toàn bộ draw của instance (≥ 200).
- **Vì sao dải là [1%, 10%], không phải [0,25%, 10%] như Study L:** tập đột biến test-level chỉ có vài trăm draw duy nhất (dữ liệu phát triển: 91 đến 200). Ở 200 draw, một patch có h = 0,5% chỉ cho trung bình 1 sự kiện, nên **không đo được tác hại dưới khoảng 1%**. Phần dải thấp hơn nằm ngoài độ phân giải của phép đo.
- **So sánh:** census-only, B8+, smoke 20, kiểm định cỡ mẫu cố định với n bằng số draw đủ cặp của instance (cùng θ = 0,2, η = 0,05, α = 0,1), Gatekeeper cố định. Gatekeeper-mixture cần khoảng 1.000 draw nên **không áp dụng** ở quy mô này và không được báo cáo như đã so sánh.

## Giới hạn đã biết, ghi trước

- Draw lấy không hoàn lại từ một tập hữu hạn nhỏ, không phải mẫu độc lập đồng phân phối. Các kiểm định tuần tự được coi là mô tả gần đúng và kết quả so sánh cổng mang tính mô tả, không có bảo đảm sai số chính xác.
- Tính hợp lệ của oracle phụ thuộc vào test của repo chạy tới code bị sửa; chênh lệch ở nơi test không chạy tới không được đo.
- Cohort từ tìm kiếm GitHub không phải mẫu ngẫu nhiên.

## Mốc thời gian

M1, M2: trước 30/11/2026. M3: trong tháng 12/2026 nếu pipeline sinh patch cho cohort mới đã sẵn sàng. Lượt sinh patch chính của nửa A\*: khoảng 5/1 đến 18/1/2027, **trước khi Free Trial hết hạn ngày 20/1/2027**.
