# Study B — bản nháp protocol (CHƯA ĐÓNG BĂNG)

**Ngày soạn:** 19/10/2026 · **Trạng thái:** DRAFT. Chỉ đóng băng (commit + hash + tag `study-b-freeze`) sau khi các mục ở phần 6 đã được quyết định và Thầy/Cô đã xem.

## 1. Câu hỏi

Trên các target **chưa từng dùng để phát triển**, khi tái sử dụng skill guard (Click #3298) qua binder đã đóng băng, các comparator B2, B6-R, B8 và Gatekeeper-Lite admit bao nhiêu lần tái sử dụng có hại, có lợi và không đổi, với chi phí bao nhiêu?

## 2. Đã đóng băng từ trước (không đổi trong Study B)

- Skill: `click-empty-default-guard` (binder neo theo hàm) và `click-guard-v3` (binder P7.3, hash trong `p7/p7_3/BINDER_FREEZE.json`).
- Oracle: test gốc của từng target ở đúng revision, cộng `real/oracle_templates/test_gk_boundary.py` (hash ghi trong `FETCH_RECEIPT.json`).
- Pipeline: commit Gatekeeper-Lite được tag trước khi chạy.

## 3. Khung chọn target

- Nguồn: kết quả `STUDY_B_CANDIDATE_SCAN` (workflow quét chỉ đọc). Một repo vào danh sách nếu có ít nhất một site `== ""` **chưa guard** trong hàm help/default, có bộ test chạy được và có giấy phép mở.
- Mỗi target được ghim theo **commit** (không theo nhánh). Loại trừ mọi revision của Click đã dùng ở P7.x và real-click v1–v4 (exposure registry).
- Regime: B (khác repository). Các target "mã có nhưng có thể không chạy tới được" (ví dụ Click vendor trong Typer) được báo riêng.

## 4. Bằng chứng và quyết định

- **Lọc task:** chỉ các task chạm tới hàm bị sửa trên code gốc (`reach_baseline`).
- **Thứ tự task:** ưu tiên task của oracle biên, rồi tới phần còn lại, thứ tự ngẫu nhiên theo seed cố định. Thứ tự chỉ phụ thuộc tên task, không phụ thuộc kết quả.
- **E-process chính (đề xuất):** kiểm định dấu trên cặp bất đồng (`discordant_sign`, q0 = 0,6, q1 = 0,9). Task không đổi (Z = 0) không làm mất bằng chứng.
- **Kiểm định tác hại:** dừng với REJECT_HARM khi e-value tác hại ≥ 1/α (ε = 0,05, thay thế 0,5).
- **Ngân sách:** 24 task mỗi cặp (sau khi lọc).

## 5. Báo cáo

Số đếm thô theo comparator (có hại bị admit, có lợi được admit, có lợi bị bỏ lỡ, chi phí), báo riêng từng regime, kèm phân tích độ nhạy **có và không có** lớp chuỗi lazy. Không báo tỉ lệ quần thể; không claim vượt B6 theo một mốc điểm phần trăm.

## 6. Cần quyết định trước khi đóng băng

| # | Quyết định | Phương án | Ảnh hưởng (theo mô phỏng trên dữ liệu real-click v3) |
|---|---|---|---|
| D1 | E-process chính | (a) kiểm định dấu (đề xuất) · (b) trung bình θ = 0,1 như hiện tại | (b) không ra quyết định ở mọi cặp thật; (a) phát hiện tác hại ở R1/R3 sau khoảng 7–11 task |
| D2 | Phân bổ α | (a) α/ô = 0,015 (ngưỡng ≈ 110, cần 12 cặp bất đồng có lợi liên tiếp) · (b) α/ô = 0,05 với e-BH giữa các ô (ngưỡng ≈ 33, cần khoảng 9) | Với (a), R1 không thể admit dù bỏ lớp lazy (chỉ có 9 cặp có lợi); với (b) thì có thể |
| D3 | Lớp chuỗi lazy | (a) giữ làm lớp hành vi đối kháng đã khai báo (regime C), nhờ người độc lập xác nhận kỳ vọng `[default: ""]` · (b) bỏ khỏi oracle chính, chỉ báo ở độ nhạy | Quyết định nhãn có hại/có lợi của mọi cặp hỗn hợp |
| D4 | Danh sách target | Chọn từ kết quả quét | — |

Mô phỏng chi tiết: `POWER_SIM_REAL_CLICK_V3.md` và `POWER_SIM_REAL_CLICK_V3_NO_LAZY.md`.
