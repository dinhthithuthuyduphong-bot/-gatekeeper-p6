# Study B — protocol (ĐÃ ĐÓNG BĂNG 19/10/2026)

**Trạng thái:** FROZEN. Hash của mọi đầu vào nằm trong `study_b/FREEZE.json`; workflow kiểm tra lại hash trước khi chạy và dừng nếu có file thay đổi. Commit đóng băng được gắn tag `study-b-freeze`. Mọi thay đổi sau thời điểm này phải ghi thành amendment có lý do, và không áp dụng cho kết quả đã chạy. Danh sách amendment: `study_b/AMENDMENTS.md` (A1: sửa lỗi kỹ thuật khi tải target; A2: chạy oracle cô lập và ghi lỗi kỹ thuật theo cặp; tag hiện hành `study-b-freeze-a2`).

## 1. Câu hỏi

Trên các target **chưa từng dùng để phát triển**, khi tái sử dụng skill guard (Click #3298) qua binder đã đóng băng, các comparator B2, B6-R, B8 và Gatekeeper-Lite admit bao nhiêu lần tái sử dụng có hại, có lợi và không đổi, với chi phí bao nhiêu?

## 2. Đã đóng băng từ trước (không đổi trong Study B)

- Skill: `click-empty-default-guard` (binder neo theo hàm) và `click-guard-v3` (binder P7.3, hash trong `p7/p7_3/BINDER_FREEZE.json`).
- Oracle chính: `test_gk_metamorphic.py`. Tính chất thay thế: help của option có default D phải giống hệt help khi default là `str(D)`. Không phụ thuộc định dạng output, nên dùng nguyên vẹn cho click, asyncclick, rich-click. Đã kiểm tra trên Click thật: commit cha #3298 hỏng 8/8 ca so sánh chặt; skill và bản chính thức sửa 8/8 nhưng hỏng 6/6 ca chuỗi lazy rỗng; ca array-like hỏng ở cả ba (ngoài phạm vi skill).
- Skill Study B: `empty-default-guard-family` neo vào `get_help_record`, `get_help_extra` và hàm có tên chứa `default`, chỉ với biến `default_value`. Đây là phạm vi khai báo trước, rộng hơn binder v3 (v3 chỉ nhận `Option.get_help_record/get_help_extra`, nên dự kiến từ chối ở rich-click).
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

## 6. Quyết định đã chốt

- **D1 — e-process chính:** kiểm định dấu trên cặp bất đồng (q0 = 0,6, q1 = 0,9). Task không đổi không mang bằng chứng.
- **D2 — đa ô:** admission quyết định chung bằng **e-BH, FDR = 0,1** trên 4 ô (Wang & Ramdas 2022). Một ô dừng sớm khi E ≥ K/FDR = 40; nếu không, chạy hết 24 task và lấy e-value tại điểm dừng đó. Kiểm định tác hại dừng riêng từng ô khi e-value tác hại ≥ 20 (α = 0,05). Lưu ý: e-BH kiểm soát tỉ lệ phát hiện sai (FDR), khác với ngân sách α theo ô (FWER) của paper; đây là sai khác thiết kế có chủ đích để có lực kiểm định với số task thật.
- **D3 — lớp chuỗi lazy:** được **khai báo trước** cho Study B (target chưa từng chạy), nằm trong endpoint chính; kết quả khi bỏ lớp này luôn được báo kèm. Đề nghị Thầy/Cô xác nhận độc lập kỳ vọng "giá trị bằng chuỗi rỗng thì hiển thị như chuỗi rỗng"; xác nhận này không làm đổi quy tắc đã đóng băng.
- **D4 — target:** B1 rich-click v1.9.9 (`30ac1778e609`) và B2 asyncclick 8.3.0.6+async (`4e5fea9cc5a3`).

### Lý do lựa chọn (lưu lại nguyên bản thảo trước khi chốt)

| # | Quyết định | Phương án | Ảnh hưởng (theo mô phỏng trên dữ liệu real-click v3) |
|---|---|---|---|
| D1 | E-process chính | (a) kiểm định dấu (đề xuất) · (b) trung bình θ = 0,1 như hiện tại | (b) không ra quyết định ở mọi cặp thật; (a) phát hiện tác hại ở R1/R3 sau khoảng 7–11 task |
| D2 | Phân bổ α | (a) α/ô = 0,015 (ngưỡng ≈ 110, cần 12 cặp bất đồng có lợi liên tiếp) · (b) α/ô = 0,05 với e-BH giữa các ô (ngưỡng ≈ 33, cần khoảng 9) | Với (a), R1 không thể admit dù bỏ lớp lazy (chỉ có 9 cặp có lợi); với (b) thì có thể |
| D3 | Lớp chuỗi lazy | (a) giữ làm lớp hành vi đối kháng đã khai báo (regime C), nhờ người độc lập xác nhận kỳ vọng `[default: ""]` · (b) bỏ khỏi oracle chính, chỉ báo ở độ nhạy | Quyết định nhãn có hại/có lợi của mọi cặp hỗn hợp |
| D4 | Danh sách target (đề xuất, đã ghim commit trong config nháp) | **B1 rich-click v1.9.9** (`30ac1778e609`): site chưa guard ở `_get_parameter_default`; oracle = bộ test của rich-click + metamorphic. **B2 asyncclick 8.3.0.6+async** (`4e5fea9cc5a3`): bản phát hành asyncclick cuối cùng trước bản sửa, site chưa guard ở `get_help_extra`; oracle = `tests/test_options.py` + metamorphic. Mỗi repo một phiên bản (các phiên bản gần nhau cùng một cụm). Các tag 8.3.1/8.3.2 trong repo asyncclick có đường dẫn `src/click/` nên là tag của Click gốc, bị loại. | 2 target × 2 binder = 4 cặp; v3 dự kiến từ chối ở rich-click |

**Khoá an toàn:** `study_b/config_study_b.json` có `status: DRAFT` và `requires_freeze: true`. Pipeline từ chối chạy cho tới khi đổi thành `FROZEN`, nên không thể vô tình xem kết quả trước khi đóng băng.

**Kết quả real-click v5 (phát triển, oracle metamorphic):** B6-R admit 5/5 cặp có hại; B8 reject 5/5; Gatekeeper REJECT_HARM 4 cặp, QUARANTINE 1 cặp (v3 trên 8.1.7). Riêng v3 trên 8.1.7: v3 thêm cả nhánh `""` vào bản cũ, làm help của chuỗi lazy rỗng khác với help của `""` (6 task hỏng) — test gốc của Click 8.1.7 không thấy điều này. Bỏ lớp lazy thì mọi cặp thành có lợi.

**Kết quả real-click v4:** kiểm định dấu cho Gatekeeper REJECT_HARM ở cả 4 cặp có hại sau 14–17 task (B6-R admit cả 4, B8 reject cả 4); cặp có lợi duy nhất (v3 trên 8.1.7, 1 cặp bất đồng) vẫn QUARANTINE.

Mô phỏng chi tiết: `POWER_SIM_REAL_CLICK_V3.md` và `POWER_SIM_REAL_CLICK_V3_NO_LAZY.md`.
