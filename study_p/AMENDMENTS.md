# Study P: amendments

## P-A1 (2/11/2026): sửa công cụ RQ3, không đụng tới cohort

**Thay đổi:** `tools/rq3_target.py` đăng ký phép biến đổi mở rộng `none_identity` trước khi nạp kỹ năng (giống `tools/run_study_g.py`); `.github/workflows/rq3.yml` cho phép chạy lại riêng một số target; `research_closure/results/RQ3_PLAN.md` ghi chú lần chạy lại.

**Lý do:** ở lượt RQ3 đầu, ba target dùng kỹ năng `none-identity` (G1_pydal, G2_emmett, K1_hera_pspec) dừng với lỗi `unknown transform 'none_identity'`, **trước** khi đo bất kỳ đầu vào nào của chúng. Chỉ ba target này được chạy lại.

**Không thay đổi:** khung mẫu, giao thức, công cụ của cohort (vet, oracle mức hàm, sinh và chấm patch, phân tích), mọi ngưỡng.

Nếu văn bản này đã có mặt lúc đóng băng, bản sửa có trước khi đóng băng và mục này chỉ để truy vết; khi đó không cần chạy amendment.

## P-A2 (2/11/2026): xử lý 35 ứng viên của hai mảnh có job bị dừng

**Bằng chứng:** cohort chạy trên 200 mảnh; 198 mảnh có artifact, 3.527 trên 3.562 ứng viên của khung có bản ghi. Job của mảnh 151 thất bại sau khoảng 36 phút và job của mảnh 181 bị dừng (mã 143); không có artifact của hai mảnh này, nên **35 ứng viên** (18 và 17) không có kết quả nào, và **không ai nhìn thấy kết quả của chúng**.

**Thay đổi:** thêm `tools/p_stream_resume.py` (sha256 `2133251ecf0ca601bfdb3a244fbf46d2ea4668794a962a9a50732ff2097e475f`) và workflow `Gatekeeper Study P stream resume (amendment P-A2)`. Công cụ dùng nguyên `tools/p_stream.py` (không sửa), cùng thứ tự và cùng cách chia mảnh, chỉ xử lý ứng viên **chưa có bản ghi** (danh sách `research_closure/results/p_stream/DONE.json`, sha256 `9a23dc8e5e28bac57d1aefb6a3482efb911b4bcbf7a3d4acda1982c04a1ab99e`, 3.527 tên), và ghi lỗi của một ứng viên vào chính ứng viên đó thay vì làm dừng cả mảnh.

**Không thay đổi:** khung, các giai đoạn, mọi ngưỡng, kế hoạch phân tích. Kết quả chính **chưa được tính** khi viết amendment này; quyết định chỉ dựa vào việc hai mảnh không có artifact.

## P-A3 (3/11/2026): mỗi ứng viên của mảnh 151 chạy trong một job riêng

**Bằng chứng:** mảnh 181 đã hoàn tất dưới P-A2 (17/17 ứng viên). Mảnh 151 bị dừng thêm một lần dưới P-A2: lần đầu (lượt cohort) sau ứng viên thứ 7, lần này khi đang xử lý ứng viên thứ 15; cả hai lần bước bị dừng bằng SIGTERM (mã 143) **và** bước tải artifact (chạy cả khi thất bại) cũng không chạy, nên **không ai thấy kết quả** của bất kỳ ứng viên nào trong mảnh. Hai lần dừng ở hai ứng viên khác nhau, và công cụ kiểm định đã dọn thư mục tạm, nên đây không phải lỗi ổn định của một ứng viên. Giải thích phù hợp nhất: mã của một repo gửi tín hiệu dừng ra ngoài nhóm tiến trình của nó.

**Thay đổi:** workflow `Gatekeeper Study P stream isolate (amendment P-A3)` (sha256 `ac346a78134c66a6bc964bc4897d5ee6e8f9912bb5c7bb296c6b343e4bf0ba52`): mỗi ứng viên chưa có bản ghi của mảnh 151 (18 ứng viên) được xử lý trong **một job riêng**, bằng `tools/p_stream_resume.py` của P-A2 **không sửa** (job nhận mọi ứng viên khác của mảnh như đã xong).

**Thay đổi kèm theo trong `tools/p_analyze.py`:** phễu RQ1 đếm thêm hai dòng, `stage_errors` (ứng viên có lỗi giai đoạn dưới P-A2) và `job_lost` (ứng viên của khung không có bản ghi); không phép tính nào khác thay đổi.

**Quy tắc cho job bị mất:** nếu job của một ứng viên vẫn không có artifact, ứng viên đó được ghi là `JOB_LOST` trong phễu, không chạy lại thêm, và không đóng góp patch nào vào phân tích chính.

**Không thay đổi:** khung, các giai đoạn, mọi ngưỡng, kế hoạch phân tích. Kết quả chính vẫn **chưa được tính**.

## P-A4 (3/11/2026): sửa lỗi chia cho 0 trong công cụ phân tích

**Bằng chứng:** lượt chạy đầu của `tools/p_analyze.py` trên cohort hoàn chỉnh **dừng trước khi in ra bất kỳ kết quả nào** (ZeroDivisionError trong `in_band_rate`): hàm kiểm tra `n > 0` **sau** khi đã tính cận 3/n. Khi sửa, **chưa ai thấy kết quả**.

**Thay đổi:** `in_band_rate` trả về False cho patch không có đầu vào nào được chấm, **trước** khi tính cận (sha256 mới `5c5ff441a91b6f7e387d6d0d1d609cab3cc0fafbd0fd8a353bb460c3980c1ae1`); thêm test.

**Ảnh hưởng:** 251 lần sinh có 0 đầu vào được chấm đều không có patch (`NO_PATCH` 220, `GENERATION_ERROR` 31) và **không lần nào plausible**; phân tích chính chỉ dùng patch plausible, nên bản sửa không đổi con số nào, chỉ ngăn chương trình sập.

## P-A5 (3/11/2026): RQ5, chế độ ghi lại và kế hoạch kiểm tra tính hợp lệ

**Lý do:** kết quả chính đã có (7,8%); kiểm tra sau khi thấy kết quả cho thấy một phần "hồi quy" có thể là khác biệt trên đầu vào mà bản fix cũng từ chối. RQ5 đã có trong giao thức (mục 1) nhưng chưa có kế hoạch chi tiết; bản ghi cohort không lưu nội dung patch.

**Thay đổi:**
- `gatekeeper_ext/fn_draws.py` (sha256 `b78b1fee034524fd9ecce3fc16e8865163fbceb19b0c722c47eb4c19ced88b0a`), `tools/cohort_inner.py` (`b660ce40eebb2fefbef0551adcb9bd3515891b256e7ee1ad1e4aa0f81fe339f9`), `tools/cohort_instance.py` (`c7e465eae7afabd6e4d9f8b12c41bb55a5d5228eafa3f2765bd66f640831fbe3`): thêm **chế độ ghi lại, mặc định tắt**, lưu diff của patch và đầu ra trên từng đầu vào. Khi tắt, mọi kết quả giống hệt (có test).
- Kế hoạch `research_closure/results/rq5/RQ5_PLAN.md` (`c541196f2417210e1648adde93300b6294b3f1d9bd17adc94f6cde4d8498cc88`), danh sách 29 mục tiêu `RQ5_TARGETS.json` (`072b1003a5fce07ef357a87abbaec3707611d41a72afd1d3448f62c2b98125c6`), công cụ `tools/rq5_classify.py` (`dcf9179d68a6166b476782a98290f06d52a5ac297a154f61e93938b81d99c75b`), workflow `rq5.yml` (`83f255589cf6c57d826513b8c5d6cb7919d8e840ba077e040b2b26394da4ce15`), **commit trước khi xem bất kỳ ví dụ chênh lệch nào**.

**Không thay đổi:** kết quả đã đăng ký (7,8%) giữ nguyên; RQ5 chỉ bổ sung.
