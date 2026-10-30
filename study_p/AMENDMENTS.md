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
