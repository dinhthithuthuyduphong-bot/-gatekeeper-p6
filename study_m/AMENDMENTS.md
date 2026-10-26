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

## M-A2 (trước khi xem bất kỳ kết quả nào): sửa công cụ khám phá để hoàn tất trong giới hạn tốc độ

**Bằng chứng lỗi:** lượt chạy S1 đầu tiên để lại một artifact chỉ có một file `log.txt` rỗng: không có `M_CANDIDATES.json`, không có nhật ký hao hụt, không có seed. Phân tích công cụ cũ: nó gọi API hai lần cho mỗi kết quả tìm kiếm (tối đa 16.800 PR, tức 33.600 lời gọi), chỉ ghi file và in ở cuối, trong khi workflow giới hạn 180 phút. Ở mức giới hạn 1.000 lời gọi mỗi giờ của `GITHUB_TOKEN` (theo hiểu biết của tôi, chưa kiểm chứng), việc đó cần khoảng 34 giờ, nên lượt chạy bị dừng giữa chừng và không để lại gì. Tôi không có log của workflow, nên đây là nguyên nhân **rất có thể**, chưa phải chắc chắn.

**Thay đổi (chỉ công cụ và workflow; `INCLUSION_RULES.md` và `EXCLUDED_REPOS.json` không đổi):**
1. Các bộ lọc (a)-(c) chỉ dùng trường có sẵn trong kết quả tìm kiếm.
2. Danh sách được sắp theo SHA-256 của `seed:repo#pr` **trước** bước tốn kém, và các bộ lọc (d)-(h) (cần danh sách file thay đổi) được đánh giá **theo thứ tự đó** cho tới khi đủ số ứng viên. Vì thứ tự băm là thuộc tính của riêng từng PR và không phụ thuộc việc PR khác có qua bộ lọc hay không, kết quả là **đúng tiền tố** của danh sách đã sắp mà quy trình ban đầu sẽ tạo ra.
3. Một lời gọi API cho mỗi PR được kiểm tra (bỏ lời gọi chi tiết PR); điều kiện "đã merge" được kiểm tra bằng `merged_at` của kết quả tìm kiếm. Việc có commit merge được kiểm tra ở S2 bởi `vet_target`.
4. Máy khách chờ tới thời điểm reset khi hết hạn mức; ghi điểm kiểm tra sau mỗi 25 PR; hỗ trợ `--start` để tiếp tục.
5. Có thể dùng token riêng `GH_SEARCH_TOKEN` (hạn mức cao hơn) nếu đặt làm secret.

**Không đổi:** quy tắc chọn, mọi bộ lọc, danh sách loại trừ, thứ tự theo seed. Chưa có kết quả nào được xem.
