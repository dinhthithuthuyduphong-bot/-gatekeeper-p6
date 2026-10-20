# Tài liệu review phương pháp với Thầy/Cô (28/10/2026)

Mục đích buổi review: một người ngoài rà lại phương pháp **trước khi** đóng băng Study D (30/10). Chi tiết đầy đủ: `study_d/STUDY_D_PROTOCOL_DRAFT.md`; bằng chứng từng bước: `EVIDENCE_LEDGER.md`.

## 1. Câu hỏi nghiên cứu (một câu)

Một skill sửa lỗi học từ một nguồn (bool lọt qua kiểm tra `isinstance(x, int)`), khi tái dùng trên repository khác, Gatekeeper-Lite có admit đúng chỗ an toàn và có lợi, chặn đúng chỗ có hại, tốt hơn các cách dựa trên replay + fingerprint (B6-R), với chi phí thấp hơn kiểm tra toàn bộ (B8) không?

## 2. Thiết kế (tóm tắt)

| Thành phần | Lựa chọn | Vì sao |
|---|---|---|
| Đơn vị lấy mẫu | Lần rút i.i.d. từ **bộ sinh đầu vào khai báo trước** cho mỗi scope | Thỏa giả định i.i.d. của paper do cách xây dựng; không đếm ca trùng lặp |
| Scope | *bool* (đầu vào là bool) và *int/number* (đầu vào hợp lệ) | Cùng skill có thể có lợi ở scope này, vô ích hoặc có hại ở scope kia |
| Oracle | Kỳ vọng lấy từ **test và fixture của upstream**; scope int dùng oracle vi sai (hành vi không được đổi) | Không tự đặt kỳ vọng |
| Cổng census | Bộ test gốc của target, baseline 3 lần, treatment 1 lần + chạy lại | Chặn mọi regression đã biết |
| Quyết định | Lợi ích (θ = 0,2) **và** chứng nhận ít tác hại (η = 0,05); báo động tác hại để dừng sớm | An toàn được chứng nhận, không chỉ "chưa thấy hại" |
| Đa ô | **e-Holm, FWER α = 0,1** trên 16 ô; e-BH là phân tích phụ | Mỗi lần admit sai là một rủi ro thật |
| Seed | drand, vòng sau thời điểm đóng băng 60 phút | Không thể chọn lại seed sau khi thấy kết quả |
| Baseline | B2, B6-R (bind + replay + fingerprint), B8 (chạy đủ), B9 (LLM, sau 31/10) | So sánh với các cách tiếp cận khác nhau |

## 3. Bộ dữ liệu

8 target trên 7 repository (spec-kit có hai target: D3 và A1): 5 dương (py_ecc, Cerberus, spec-kit, open-feature, pycubrid — đều là fix đã merge, có test fail trước/pass sau), 1 đối chứng khả năng áp dụng (spec-kit #2589), 1 đối chứng no-op (jsonschema), 1 đối chứng ngữ nghĩa (voluptuous). Dự đoán từ diff (chưa chạy): skill khớp dạng ở 3 target, không khớp ở 2 target dương (bí danh, biến kiểu).

## 4. Những gì đã kiểm chứng

- Tính hợp lệ của từng e-process: test Monte Carlo tại đúng biên (tỉ lệ sai ≤ α).
- Cả họ 16 ô dưới e-Holm: FWER quan sát 0,040 (KTC 95% 0,021–0,059) khi mọi ô null ở biên.
- Toàn bộ chuỗi chạy trên Actions (smoke, dữ liệu phát triển): tải repo, cài đặt, census 3 baseline, rút mẫu, dừng thật, tổng hợp, ablation, báo cáo.
- Tái lập từ môi trường sạch: 4/4.

## 5. Sáu quyết định đã chốt (Thầy/Cô chỉ cần phản đối nếu không đồng ý)

Study D sẽ được đóng băng ngày 30/10 với các quyết định dưới đây, dù buổi review có diễn ra hay không. Mục đích review là bắt lỗi trước khi đóng băng, vì sau đó mọi thay đổi phải ghi thành amendment.

| # | Quyết định đã chốt | Lý do | Cái giá đã chấp nhận |
|---|---|---|---|
| 1 | Kết luận chỉ áp dụng cho các bộ sinh đã khai báo trên target ở commit đã ghim | Đây là điều dữ liệu thật sự chứng minh được; khái quát rộng hơn sẽ không bảo vệ được | Không tuyên bố về "mọi repository" |
| 2 | e-Holm kiểm soát FWER α = 0,1 trên 16 ô (khác α riêng từng ô của paper) | Mỗi lần admit sai là một rủi ro thật; FWER chặt hơn FDR và hợp với số ô nhỏ; kiểm tra bằng mô phỏng: FWER 0,040 ở kịch bản xấu nhất | Mất một chút power so với ngưỡng riêng từng ô |
| 3 | Mức tác hại chấp nhận η = 0,05, chọn trước | Một skill sửa lỗi gây regression ở hơn 5% đầu vào trong scope thì không nên được dùng lại | Skill có hại hiếm (khoảng 2%) chỉ được admit khoảng 32–44% số lần |
| 4 | Endpoint chi phí chính là số lần chạy thử; wall-clock là phụ; không claim tiết kiệm thời gian nếu dữ liệu không cho thấy rõ | Smoke đã cho thấy census dùng chung chiếm phần lớn thời gian (tỉ lệ 0,92); khai báo trước để không chọn chỉ số theo kết quả | Lợi thế chi phí có thể chỉ thể hiện ở số lần thử |
| 5 | "Có hại" ở voluptuous theo hợp đồng của chính target (maintainer coi chấp nhận bool là đúng) | Đối chứng ngữ nghĩa phải dùng hợp đồng của target, không dùng ý muốn của người nghiên cứu | Kết luận ở ô này phụ thuộc hợp đồng đó, được ghi rõ |
| 6 | Study B/C trình bày là pilot, minh hoạ cơ chế | Chúng đếm ca gần trùng lặp thành bằng chứng độc lập; giữ lại để minh bạch quá trình | Không dùng số liệu B/C làm bằng chứng thống kê chính |

**Việc duy nhất cần ở Thầy/Cô:** rà lại phần thống kê (mục 2 và quyết định 2–3) như một người kiểm tra độc lập. Đây là phần mục GK-08 của checklist không thể tự hoàn thành.

## 6. Câu hỏi có thể gặp và câu trả lời ngắn

| Câu hỏi | Trả lời |
|---|---|
| Tại sao không dùng trực tiếp test của target làm task? | Test hữu hạn và gần trùng lặp, vi phạm i.i.d.; test gốc được dùng làm cổng census chính xác thay vì làm mẫu thống kê. |
| Oracle có bị "thiết kế để Gatekeeper thắng" không? | Kỳ vọng lấy từ test upstream viết trước khi dự án tồn tại; oracle viết trước khi chạy skill lên target và được băm khi đóng băng. |
| Skill có được chỉnh theo target không? | Không. Skill học từ PySStuBs (tuần 3); không thêm phân giải bí danh dù diff Cerberus cho thấy cần, vì đó là rò rỉ từ target. |
| Nếu kết quả xấu thì sao? | Kết quả nào cũng được báo cáo nguyên trạng; lỗi kỹ thuật được ghi là `CENSUS_INVALID` hoặc `HARNESS_ERROR`, không tính và không thay target. |
| B6-R có phải B6 của paper? | Không, là bản tái dựng (bind + replay + fingerprint), được ghi rõ. |
