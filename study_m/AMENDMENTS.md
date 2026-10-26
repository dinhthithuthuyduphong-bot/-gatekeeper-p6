# Study M, giai đoạn S1: amendments

## M-A1 (trước mọi giai đoạn S2, trước khi xem kết quả của bất kỳ instance nào): chia cohort thành hai nhánh rời nhau

**Thay đổi:** thêm quy tắc chia cohort và công cụ thực hiện (`split_candidates.py`) cùng công cụ kiểm tra (`check_track.py`, từ chối danh sách không thuộc đúng nhánh). Không sửa `INCLUSION_RULES.md`, `EXCLUDED_REPOS.json` hay công cụ khám phá: hash của chúng không đổi.

**Quy tắc chia (đóng băng ở đây):** `track(repo) = RR` nếu SHA-256 của `"{seed}:track:{repo}"` chẵn, ngược lại `ASTAR`; `seed` là seed drand của Study M. Chia **theo repository**, không theo PR, nên hai nhánh không có repo chung. Thứ tự trong mỗi nhánh giữ nguyên thứ tự theo seed của S1. Công cụ: `tools/split_candidates.py`; kết quả chia và hash của đầu vào được ghi trong `SPLIT_SUMMARY.json`.

**Hệ quả:**
- Nhánh **A\*** (thư mục `study_m_astar`) được kiểm định (S2) và chạy harness (S3) ngay.
- Nhánh **RR** (thư mục `study_m_rr`, Registered Report) **không** được kiểm định, chạy hay xem kết quả cho tới khi có thông báo IPA.
- Dữ liệu của nửa A\* nếu cuối cùng chọn RR chỉ được dùng như dữ liệu thử nghiệm, khai báo rõ ràng.

**Lý do:** Registered Report yêu cầu thu dữ liệu sau Stage 1; nhánh A\* cần dữ liệu sớm. Chia theo repo để hai cohort độc lập, và để một nhánh không làm mất tư cách của nhánh kia.

**Cấu trúc kho:** cả hai nhánh nằm trong **một nhánh git `main`**, tách bằng hai thư mục study có đóng băng và hash riêng. Không dùng nhánh git riêng cho RR.
