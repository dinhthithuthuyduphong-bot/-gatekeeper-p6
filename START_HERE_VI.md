# Bản bổ sung sau run 40176555227

Gói này chỉ chứa file mới hoặc thay đổi so với `main@d2078d9895938b7e411bc95417959af5370db555`. Không cần chép lại FINAL, NEXT hoặc CI_FIX cũ; không chứa file cũ giữ nguyên. Không tạo branch hoặc PR mới. Không thay đổi B9 `HOLD`, không có lời gọi model trả phí.

## Đọc kết quả

Mở `main_update/next_evidence/results/ci-40176555227/RESULT_VI.md`.

- Run cũ: 12 job xanh; 135 unit tests PASS; baseline Pydantic ổn định 3 lần.
- Sửa lỗi coverage dòng 449 và thu gọn artifact cần gửi lại.
- Chưa có target lợi/hại mới được xác nhận từ đợt quét này.
- NetworkX tiết kiệm 6,60% thời gian so với full draws nhưng vẫn tốn 2,17× census-only.
- Mã sửa mới chỉ được phân tích tĩnh. Chưa chạy unit tests hoặc target runtime tại đây.

## Cập nhật thẳng main

Giải nén gói **ở ngoài thư mục repo**. Từ checkout của bạn, cập nhật main bằng cách bình thường; không reset/hard reset hay force-push. Helper yêu cầu main đúng commit đã kiểm tra và working tree sạch. Nếu main đã thay đổi, helper sẽ dừng để bảo vệ công việc mới.

Chạy helper từ thư mục gói đã giải nén; thay `/duong/dan/gatekeeper` bằng đường dẫn checkout thật:

```bash
python3 APPLY_UPDATE.py --repo /duong/dan/gatekeeper --check-only
python3 APPLY_UPDATE.py --repo /duong/dan/gatekeeper
```

Helper chỉ kiểm tra hash và chép file. Nó không compile, không chạy test, không commit/push và không gọi API. `UPDATE_PATHS.txt` liệt kê đầy đủ các đường dẫn thay đổi. `UPDATE_MANIFEST.json` ghi hash trước/sau.

Nếu dùng upload thủ công: chỉ đưa **nội dung bên trong `main_update/`** vào đúng đường dẫn ở root repo. Đặc biệt giữ nguyên `.github/workflows/next-evidence-zero-cost.yml`; đừng tạo thêm thư mục `main_update` trong repo. Không upload đè cả gói FINAL cũ. Không cần đưa helper và metadata ngoài `main_update/` vào GitHub.

Sau khi chép, kiểm tra diff rồi commit/push trực tiếp main. Các đường dẫn để stage:

```bash
git add .github/workflows/next-evidence-zero-cost.yml next_evidence/baseline.py next_evidence/pytest_probe.py next_evidence/site_coverage.py next_evidence/review_bundle.py next_evidence/results/ci-40176555227 tests/test_site_coverage.py tools/closure_verify.py tools/review_saved_site_trace.py
git diff --cached --stat
git commit -m "Fix raw site coverage reporting and add CI evidence review"
git push origin main
```

## Chạy workflow trên GitHub

1. Vào **Actions → Gatekeeper next evidence - zero-cost → Run workflow**.
2. Chọn branch **main**.
3. Đặt **run_scout = false**, **run_cost = false**. Không cần quét lại cùng source hoặc đo cost lại cho bản sửa reporting này.
4. Chạy workflow. Audit → Pydantic baseline → collect là phần cần chạy; scout/cost skipped là đúng.
5. Gửi URL run và artifact **next-evidence-return-a&lt;attempt&gt;**. Đây là gói review nhỏ, có `REVIEW_SCOPE.json` công khai phần đã bỏ qua. Raw coverage vẫn nằm ở artifact riêng **next-raw-pydantic-baseline-a&lt;attempt&gt;**.

Nếu thất bại, gửi artifact vẫn có cùng URL job lỗi. `COLLECT_STATUS.txt` và `JOB_STATUS.json` giúp phân biệt upload thành công với thí nghiệm thành công. B9 vẫn HOLD kể cả khi mọi job xanh.

## Tái kiểm toán dữ liệu cũ, khi cần

Không phải bước bắt buộc để cập nhật. Đã có kết quả kiểm toán trong `PYDANTIC_REACH_CORRECTION.json` và log đi kèm. Muốn tự tái hiện, tải artifact baseline gốc của run 40176555227, dùng `tools/review_saved_site_trace.py --baseline <BASELINE_RESULT.json> --coverage <probe_1/coverage.data> --out <file_moi.json>` sau khi cập nhật repo. Đây chỉ là đọc dữ liệu lưu sẵn, không chạy test hay model.

Giữ raw artifact của run cũ trước khi hết hạn lưu trên GitHub. ZIP này chứa báo cáo và log gốc chọn lọc, không phải bản sao toàn bộ artifact 420 MB.
