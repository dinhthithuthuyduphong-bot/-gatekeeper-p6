# Study P: amendments

## P-A1 (2/11/2026): sửa công cụ RQ3, không đụng tới cohort

**Thay đổi:** `tools/rq3_target.py` đăng ký phép biến đổi mở rộng `none_identity` trước khi nạp kỹ năng (giống `tools/run_study_g.py`); `.github/workflows/rq3.yml` cho phép chạy lại riêng một số target; `research_closure/results/RQ3_PLAN.md` ghi chú lần chạy lại.

**Lý do:** ở lượt RQ3 đầu, ba target dùng kỹ năng `none-identity` (G1_pydal, G2_emmett, K1_hera_pspec) dừng với lỗi `unknown transform 'none_identity'`, **trước** khi đo bất kỳ đầu vào nào của chúng. Chỉ ba target này được chạy lại.

**Không thay đổi:** khung mẫu, giao thức, công cụ của cohort (vet, oracle mức hàm, sinh và chấm patch, phân tích), mọi ngưỡng.

Nếu văn bản này đã có mặt lúc đóng băng, bản sửa có trước khi đóng băng và mục này chỉ để truy vết; khi đó không cần chạy amendment.
