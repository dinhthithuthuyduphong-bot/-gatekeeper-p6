# Study Q: amendments

## Q-A1 (31/10/2026): chấm tay các hồi quy theo hợp đồng của HQ1 — BỔ SUNG SAU KHI ĐÃ THẤY KẾT QUẢ

**Bối cảnh, nói rõ:** amendment này được viết **sau khi** đã có kết quả chính của Study Q (`research_closure/results/study_q/STUDY_Q_RESULT.md`, commit `7cb432f`): HQ1 không được ủng hộ (6/55). Mọi kết quả của Q-A1 là **phân tích bổ sung**, không thay thế và không làm thay đổi kết quả đã đăng ký. Người nghiên cứu chọn hướng này ngày 31/10/2026.

**Lý do:** giao thức mục 3 yêu cầu "chế độ ghi lại bật: lưu patch và mọi đầu ra", nhưng `tools/q_instance.py` chỉ lưu số đếm theo loại (`q_classify.summarise`) và xoá thư mục tạm. Vì vậy chưa kiểm được một ca C1 ("bản fix trả giá trị, patch khác") có phải hồi quy thật hay chỉ khác biểu diễn, như RQ5 của Study P đã làm.

**Đối tượng:** 55 instance của HQ1 (`study_q/QA1_TARGETS.json`, sha256 `67a09c3f6896a960af798a7c21a68384fd81ba0a261d76431e8eb1a761534cb9`). Danh sách được suy ra tự động từ bản ghi cohort (`Q_RECORDS.jsonl.gz`, sha256 `9b2c207071b1243356fe2d39739e0165a5d77bf4b8cbe77d675d75d765b64bc8`): với mỗi instance, patch đầu tiên theo thứ tự seed có khác biệt ngây thơ.

**Bước 1, chạy lại có lưu:** workflow `Gatekeeper Study Q review capture (amendment Q-A1)` chạy `tools/q_review_capture.py` (sha256 `4682cf4f714b7735ab746e7eedc3c6c526ccdbe7a84f73a7aab3b81d9ed0895b`).
- Công cụ gọi nguyên `tools/q_instance.run` **không sửa**, cùng seed (drand, gắn với hash đóng băng gốc).
- Nó chỉ chặn hai giá trị trả về để lưu thêm: mọi đầu ra theo từng đầu vào, tệp lời gọi G0, chương trình sinh G2, và nội dung patch.
- Mỗi instance chạy trong một job.

**Quy tắc tái tạo:** chương trình sinh G2 được model viết lại, nên có thể khác lần cohort. Một đơn vị **tái tạo được** khi lần chạy lại chấm cùng patch (cùng sha), trên cùng hàm đích, và bản tóm tắt phân loại (`scored`, `categories`, `divergent`, `naive_harm`, `contract_harm`) **trùng hệt** bản ghi cohort (`tools/q_review_items.py`, sha256 `b26f94b718644ad90ed08b9b1e1b1c0f3307be941bada136743866e10ac0e0a3`). Đơn vị không tái tạo được được báo cáo riêng và đưa vào dưới dạng hai cận, như RQ5.

**Bước 2, mục chấm:** với mỗi đơn vị tái tạo được có hồi quy theo hợp đồng, lấy tối đa **5** đầu vào loại C1 hoặc C2-D, theo thứ tự `sha256`-seed `q-a1:<seed>:<instance>`.
- Mỗi mục gồm: hàm, diff của patch, diff của bản fix, đầu ra của bản fix và của patch, và đầu vào. Với G0, đầu vào là lời gọi đã mã hoá; với G2, là số thứ tự trong chương trình sinh đã lưu.
- Mục được xếp theo id băm, **không** kèm loại hay kết quả của instance.

**Bước 3, hai người chấm độc lập**, cùng bộ mã R / B / U của RQ5 (`research_closure/results/rq5/RQ5_PLAN.md`):
1. trợ lý chấm trước và commit;
2. `vertex-gemini-argon` chấm mù bằng `tools/rq5_rate_llm.py` **không sửa** (sha256 `71832f669588beaee8601a0f9ce01e28becafcdf78b38051432e12c7d6527cf6`).

Báo cáo độ đồng thuận và kappa [Cohen 1960]. Một đơn vị được coi là **hồi quy đã xác nhận** khi có ít nhất một mục được cả hai người chấm mã R.

**Báo cáo:**
- tỉ lệ đơn vị của HQ1 **không** có hồi quy đã xác nhận, trên số đơn vị tái tạo được, kèm khoảng Wilson 95% và hai cận cho đơn vị không tái tạo được;
- **mô tả**, không kiểm định: đây là phân tích sau khi thấy dữ liệu.

**Ngân sách:** sinh lại G2 khoảng 0,01 USD mỗi instance (dưới 1 USD); người chấm thứ hai dưới 1 USD.

**Không thay đổi:** khung, giao thức, công cụ đã đóng băng, kết quả đã đăng ký và kết luận về HQ1. Seed giữ nguyên.
