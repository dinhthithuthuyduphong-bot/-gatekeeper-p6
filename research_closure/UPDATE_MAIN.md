# Cập nhật trực tiếp main — gói tích lũy 25/10/2026

Gói dựa trên main `fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293`. Gói chưa được push và workflow mới chưa chạy trên GitHub. Không cần tạo nhánh/PR; không cần API key hoặc secret trả phí.

Gói 25/10 chứa toàn bộ cập nhật closure 24/10 cộng Study K và log quét mới. Nếu chưa áp dụng gói 24/10, chỉ dùng gói mới này một lần. Không upload hai gói nối tiếp. Nếu main đã khác base, helper dừng để đối chiếu.

## 1. Đưa file vào repository

Giải nén ZIP. **Nội dung bên trong `main_update/`** đi vào thư mục gốc của repo, không tạo thư mục `main_update` trong GitHub. Giữ nguyên đường dẫn và thư mục `.github/`.

Cách có kiểm tra xung đột, khi dùng một bản clone local:

```bash
git switch main
git pull --ff-only
python /duong-dan/goi-da-giai-nen/APPLY_UPDATE.py --repo .
git diff --stat
git add --pathspec-from-file=/duong-dan/goi-da-giai-nen/UPDATE_PATHS.txt
git commit -m "Add zero-cost evidence audit and retrospective skill-2 transfer"
git push origin main
```

Thay `/duong-dan/goi-da-giai-nen/` bằng đường dẫn thật; bọc bằng dấu ngoặc kép nếu có khoảng trắng. Helper chỉ sao chép file sau khi kiểm tra base commit, nhánh main, working tree sạch và checksum; không commit/push, không gọi model. Nếu main đã thay đổi, helper dừng để đối chiếu thay đổi mới, không force/reset. `UPDATE_PATHS.txt` chỉ stage file của gói.

Nếu chép thủ công, đối chiếu `UPDATE_MANIFEST.json`; tránh ghi đè chỉnh sửa mới hơn. GitHub web có giới hạn upload, nên bản clone local phù hợp hơn cho gói nhiều log. Không upload ZIP thành một file thay cho code. Giữ các log và kết quả âm.

F-A3 đã được áp dụng trong gói; **không chạy lại lệnh amendment F-A3** vì sẽ báo đã áp dụng. Archive F-A2 và seed gốc được giữ. Không mở khóa `pre_b9/RELEASE_GATE.json`.

## 2. Chạy workflow mới

1. GitHub → Actions → **Gatekeeper zero-cost closure audit** → Run workflow → branch `main`.
2. Lần đầu để `cost_recheck = false`. Workflow chạy unit tests, freeze D/E/F/G/H, tính lại raw CI Study I, raw Study K, statistics/cost audit và kiểm tra paid HOLD.
3. Tải artifact **gatekeeper-zero-cost-closure**; mở `VALIDATION.json`, `RESULT.md` và log nếu có lỗi. Kỳ vọng `PASS_ZERO_PAID_API_CHECKS`, B9 `HOLD`; Study J `BLOCKED` vẫn là đúng vì chưa có cohort mới.

Muốn đo thời gian thật trên GitHub runners: chạy lại cùng workflow với `cost_recheck = true`. Sau audit sẽ có hai job `cost`, tạo artifacts **closure-cost-sqlalchemy** và **closure-cost-networkx**. Chúng chỉ chạy test/generator, không model. Python 3.8.20 của NetworkX lấy bằng uv để tránh lỗi setup-python cũ trên Ubuntu 22.04.

Các giá trị giây sẽ khác máy local. Không thay số đo local bằng số đẹp hơn; ghi một run ID/commit mới và báo cả môi trường. Nếu setup thất bại, artifact envelope vẫn giữ thông tin, không báo PASS hoặc giả lập kết quả.

Để tái lập target mới từ source: chạy workflow **Gatekeeper Study K zero-cost reproduction** trên `main`, tải artifact **study-k-python-control**. Nó tạo môi trường lịch sử, chạy nguyên module upstream ở ba nhánh và ba lần lặp, 600 paired draws và 200 state/order rechecks. Tham khảo `study_k/README.md`.

## 3. Tái chạy local (không bắt buộc nếu dùng Actions)

Trong môi trường Python 3.12 có git và PyYAML:

```bash
python -m pip install PyYAML==6.0.2
python tools/closure_verify.py --out out-closure-audit
```

Chọn output mới ở lần chạy khác. Lệnh này không chạy target mới và không gọi provider; đọc dữ liệu đã lưu. Lệnh kiểm tra riêng:

```bash
python tools/verify_cost_evidence.py --out out-cost-check.json
python tools/prospective_preflight.py --report-only --out out-study-j-status.json
python tools/screen_study_j.py --out out-study-j-static-screen
```

Scanner cuối cần mạng để fetch đúng commit nguồn, không import/chạy code upstream và không thực thi treatment. Kết quả scanner không đủ để gọi target eligible hay oracle tier-1.

## 4. Bước tiếp theo sau khi CI xanh

Ưu tiên tìm cohort/oracle cho skill thứ hai và chuẩn bị baseline-only adapters, ghi tất cả exclusions. Chỉ khi cohort, oracle và quy tắc đã đóng băng công khai mới chạy outcome cho Study J. Các PDF riêng không nằm trong gói. B9 paid vẫn `HOLD`; workflow audit xanh không đồng nghĩa đã được phép chi tiền.
