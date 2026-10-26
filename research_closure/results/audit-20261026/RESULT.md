# Research checkpoint and paper alignment — 26/10/2026

## 1. [ĐÁNH GIÁ TRẠNG THÁI & PAPER ALIGNMENT]

**Snapshot:** [`616a67f2bd02`](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/commit/616a67f2bd024b96b24d5de958cfaa69e1fe9926), thêm 12 commit so với `1177d8936ff84`. Đây là kiểm toán mã và artifact có sẵn; không chạy lại project/target tests tại máy hỗ trợ. Thời gian dùng Asia/Bangkok. Run test-mutation đã kết thúc trước khi khóa báo cáo: **failure**; năm job thành công về thực thi và D1 timeout.

**Đánh giá A\*:** hướng nghiên cứu có thể tiếp tục, nhưng hiện chưa đủ bằng chứng để gọi là A\*-ready. Nếu nộp Research Track với tuyên bố tổng quát rằng Gatekeeper thắng các cổng đơn giản, nhận định reviewer của tôi là **Weak Reject**. Đây là phán đoán học thuật, không phải xác suất accept hay quyết định của hội nghị. Artifact tốt là điều kiện hỗ trợ; không thay được novelty và lợi ích trước baseline mạnh. Không có cách bảo đảm accept.

### Những gì đã thêm thực sự

| Hạng mục | Kết quả đã đối chiếu | Diễn giải đúng |
|---|---|---|
| Study L G1 | Run 40221836594 thành công về thực thi; 6 JSON cho **2/6 pass**, ngưỡng **5/6** | **FAIL khoa học**; không chạy tiếp G2/G3 của nhánh này để cứu kết quả |
| Gold-differential replay | G1 D5 pass; D4 pass nhưng candidate là gold; D1 có 300 harness errors | Có một kết quả âm hữu ích về cơ chế replay đã thử; không chứng minh mọi oracle tự động bất khả thi |
| Hướng test-mutation mới | 6 artifact đã tải và khớp SHA-256; 5 JSON đều `all_four=false`; D1 timeout, chỉ có log | Chỉ bằng chứng phát triển trên target đã lộ; không phải cohort tiến cứu |
| Đồ thị pha | Có code và bảng cho smoke, zero-tolerance, fixed-sample, fixed-stake và mixture | Phân tích harm-only một patch; không phải full benefit+harm/FWER multi-cell experiment |
| Kỷ luật báo cáo | Kết quả âm G1 được lưu; không bỏ denominator 6 để nâng tỷ lệ | Điểm mạnh cho reproducibility và minh bạch |
| B9 | `pre_b9/RELEASE_GATE.json` vẫn HOLD | Chưa có evidence model thật, cross-model hoặc kinh tế LLM |

### Kết quả test-mutation mới: không nhầm job xanh với phương pháp đạt

| Target | Kết quả artifact | Vấn đề cần xử lý |
|---|---|---|
| D2 Cerberus | 0 test files; ineligible | `expand_files` bỏ tên legacy `tests.py`; đã xác minh upstream có `cerberus/tests/tests.py` tại pin. Đây là lỗi discovery, chưa phải giới hạn khoa học của target |
| D5 pycubrid | 200 mutant IDs, chỉ 25 cặp đầy đủ, 175 missing; all_four=false | `draws_run=200` đang là số compiled IDs, không phải 200 outcome đầy đủ; phải có raw collection/phase/receipt trước khi biết nguyên nhân |
| D3 spec-kit | 195 compiled IDs, không tất định; help=0, hurt=0 | Không dùng chênh signature này làm chứng cứ cải thiện chức năng |
| D4 openfeature | 200 IDs; không tất định; gold_itself không cho help dù bug_trigger=1 | Self-comparison và nhiễu còn lẫn; không thể chứng nhận oracle đúng |
| A1 spec-kit catalog | 200 IDs; không tất định; gold_itself | Cùng giới hạn; upstream gold không tự động biến mọi mutation thành đầu vào hợp lệ |
| D1 py_ecc | `orig_0` timeout sau 1.800 giây; artifact chỉ có log, thiếu JSON | Lỗi thực thi; chưa có kết luận về tính khả thi khoa học. Baseline test nhanh không bảo đảm test sau mutation nhanh |

### Những thành quả trước đó vẫn giữ

Study I/K vẫn cung cấp SQLAlchemy harmful upstream-test case (9 regression trong các module đã chọn) và hai beneficial compatibility cases NetworkX/python-control. Chúng là hồi cứu, không nâng thành prospective bằng CI xanh. SQLAlchemy đã bị census bắt; NetworkX có tiết kiệm 6,6% so với full-draw benchmark nhưng tốn 2,17 lần census-only. Các con số này là số đã kiểm chứng trước, không phải được chạy mới trong lượt này. Study J vẫn chưa có cohort mới được freeze và thực thi.

### Khoảng cách với bài gốc và hướng A\*

Bài gốc cung cấp riêng ghi rõ các số 180 pairs, 25 repositories, 22,7% → 5,1% là **projected**; tuyệt đối không dùng làm kết quả của repo. Cốt lõi kỳ vọng là admission có lợi so với no-skill, có kiểm soát rủi ro theo scope, và có giá trị trước replay + fingerprint/retest mạnh. Repo mới chứng minh được phần quyết định trong phạm vi hạn chế; chưa chứng minh độ phủ học skill tự động, composition/shift thực tế hoặc hiệu quả qua nhiều model.

Hướng mới thay benefit certificate bằng fail-to-pass tests và chỉ chứng nhận harm là **một estimand/quy tắc khác**, cần tên và protocol riêng. L-A1 mô tả thay đổi này trước chạy, nhưng không nên viết rằng amendment chỉ thêm đường dẫn công cụ. G1 có thể là preregistered feasibility check trên 6 target đã biết; không phải unseen prospective evaluation.

Để nhắm A\*, nên tập trung câu hỏi có thể bị bác bỏ: **Trên các patch thực sự plausible, với oracle không bị chọn theo kết quả, vùng nào cổng đơn giản mất utility và admission tuần tự giữ được utility ở cùng ràng buộc rủi ro, với overhead thực đo?** Nếu không có vùng này trên dữ liệu thật, phải báo kết quả âm thay vì tối ưu dataset để tạo chiến thắng.

Ba nút thắt lớn nhất:

1. **Tính hợp lệ của phép đo:** test mutation hiện sửa cả literal trong assertion, so thông báo failure bị cắt/nguyên văn một phần và khử trùng lặp draws. Không được gọi là upstream oracle nguyên trạng hoặc i.i.d. scope. Sai biệt signature chưa đồng nghĩa functional harm.
2. **Giá trị tăng thêm trước baseline mạnh:** B8+ có thể giữ D5 mà mean-margin gate loại; fixed-sample có thể mạnh hơn fixed-stake ở cùng n. Phải so cùng mục tiêu lợi ích/rủi ro và công bố rõ khi hai chính sách khác estimand.
3. **External validity và model:** 6 instance đã lộ chỉ để sửa harness. Sau ổn định mới freeze tập chưa lộ; patch công khai từ nhiều agent không cô lập tác động model vì scaffold/context/budget khác nhau.

FSE Research Track đánh giá originality, importance, soundness, evaluation và related-work comparison. CFP FSE 2027 hiện ghi gia hạn full-paper tới 03/10/2026 AoE, đã qua thời điểm kiểm tra; không lập kế hoạch mới như còn nộp được vòng đó. Mục tiêu vẫn có thể là một vòng A\* còn mở phù hợp, cần xác minh CFP khi chọn. Nguồn: https://conf.researchr.org/track/fse-2027/fse-2027-papers.

## 2. [HƯỚNG DẪN CẬP NHẬT LÊN GITHUB]

Xem `UPDATE_MAIN.md` và `FILE_MANIFEST.json` cùng thư mục. Gói chỉ chứa file mới hoặc được sửa so với snapshot trên. Copy **nội dung** `main_update/` vào root repo; không tạo thư mục `main_update` trên GitHub. Không có push tự động, không thay frozen Study L hay D/E/F/G/H, không mở B9.

Bản sửa chỉ tăng khả năng kiểm toán của **development runner**: giữ XML/JSON/stdout/stderr/command receipts/signatures/catalog; missing outcome chặn pass; dừng khi runner exit bất thường; ghi `.md` dù lỗi; hỗ trợ legacy `tests.py`. Thêm 7 unit-test cases để chạy trên CI. Chúng **chưa được chạy** trong lượt này; mới kiểm tra AST Python 3.8, cấu trúc YAML, đường dẫn và package manifest.

## 3. [YÊU CẦU INPUT TỪ TÔI CHO BƯỚC TIẾP THEO]

Không cần trả lời để hoàn thành audit và soạn bản sửa này; hai bước đã làm. Bước cần dữ liệu tiếp theo là chạy bản sửa trên GitHub: chọn `unit-only`, rồi D5 và D2 riêng; chỉ sau đó chạy D4 để phân tích nondeterminism. Không chạy lại full 6 target ngay. Gửi URL run hoặc artifact mới khi hoàn tất; đó là dữ liệu cần để xác định nguyên nhân, không phải xin xác nhận lại mục tiêu.

Không cần API key, budget hay model selection. Run D1 cũ đã kết thúc bằng timeout. Chưa nên chạy lại D1 trước khi kiểm tra hiệu quả giới hạn thời gian cho từng test mutation; tăng timeout đơn thuần không giải quyết thiết kế chi phí.

## 4. [KẾT QUẢ, FILE MỚI VÀ LOG]

- Hoàn tất: pin main, diff 12 commit, đối chiếu 6 G1 JSON, tải/hash 6 TM artifact (5 JSON + 1 log-only timeout), kiểm toán code, tính lại công thức, chuẩn bị patch development, kiểm tra tĩnh, đóng gói delta.
- Chưa hoàn tất: runtime CI của patch; giải thích nguyên nhân 175 missing/nondeterminism; unseen cohort; paid B9; bằng chứng đủ cho A\*.
- `SUMMARY.json`: số liệu có cấu trúc, kết luận run failure và D1 timeout.
- `SOURCES.json`: file/commit nguồn và SHA-256 của nội dung đọc.
- `HARNESS_AUDIT.md`: lỗi code, tác động và giới hạn bản sửa.
- `PAPER_ALIGNMENT.md`: correction toán học và roadmap khoa học.
- `UPDATE_MAIN.md`: danh sách thay đổi, cách chạy, output cần trả.
- `VALIDATION.md`: những gì thực sự được kiểm tra, không gọi static check là runtime pass.
- `inputs/tm/`: 5 kết quả JSON + log của cả 6 artifact; không thể tái tạo raw bị runner cũ xóa.

Mọi lượt CI mới được thiết kế xuất `RESULT_<target>.md`, `RESULT_SUMMARY.md` và inventory. Nếu runner bị hủy cứng trước upload, không thể bảo đảm artifact hoàn chỉnh; job/run status vẫn phải được báo là cancelled/incomplete.
