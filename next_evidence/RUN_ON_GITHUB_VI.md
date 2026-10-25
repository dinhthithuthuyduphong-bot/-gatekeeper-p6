# Cách cập nhật main và gửi kết quả lượt tiếp theo

Gói NEXT hiện tại là **bản cập nhật chênh lệch (delta)** so với
`Gatekeeper_Final_ZeroCost_20261025.zip`: chỉ có **16 file mới và 5 file thay đổi**.
444 file không đổi, các raw log và kết quả cũ không được nén lại.

**Áp dụng gói FINAL trước**, commit lên main, rồi mới áp dụng NEXT. Nếu gói FINAL
đã có trên main thì không cần upload lại. NEXT không phải gói cài đặt độc lập.
Không cần tạo nhánh hoặc PR. Helper kiểm nội dung file của gói FINAL bằng SHA-256;
không yêu cầu HEAD vẫn là commit gốc `fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293`,
vì việc commit gói FINAL đã tạo HEAD mới. Không ép ghi đè nếu helper báo file
thiếu hoặc nội dung khác cả bản FINAL và bản NEXT.

## 1. Đưa file vào main

Giải nén ZIP. Nội dung **bên trong** `main_update/` là các đường dẫn cần cập nhật
ở gốc repo, bao gồm `.github/workflows/`. Không upload cả ZIP thành một file vào
repo và không tạo thư mục `main_update` trong repo.

Khuyến nghị dùng bản clone local và helper chỉ sao chép file (không compile,
test, commit, push hay gọi model). Sửa đường dẫn gói trong các lệnh bên dưới:

```bash
git switch main
git pull --ff-only
python /duong-dan/goi/APPLY_NEXT_UPDATE.py --repo . --check-only
python /duong-dan/goi/APPLY_NEXT_UPDATE.py --repo .
git diff --stat
git add --pathspec-from-file=/duong-dan/goi/UPDATE_PATHS.txt
git commit -m "Add zero-cost source, baseline reach and census-first cost follow-up"
git push origin main
```

Helper yêu cầu main sạch, đủ file nền FINAL và đúng checksum trước khi chép. Nếu dừng do
xung đột, không dùng force/reset để vượt qua kiểm tra. Bọc đường dẫn bằng dấu
ngoặc kép nếu có dấu cách. Giữ thư mục giải nén ở ngoài repo để không tạo file
untracked. Helper không thay các file không thuộc danh sách 21 file cập nhật.
Không chép PDF riêng hoặc credential vào repo.

F-A3 và archive cũ đã nằm trong gói FINAL; NEXT không nén lại và **không chạy lại amendment**. Giữ nguyên
`pre_b9/RELEASE_GATE.json` ở HOLD, không chạy workflow paid B9.

## 2. Chạy đúng một workflow trên GitHub

1. Mở repository → **Actions**.
2. Chọn **Gatekeeper next evidence - zero-cost**.
3. Bấm **Run workflow**, chọn branch **main**.
4. Lượt đầy đủ: bật **run_cost = true** để lấy cả bảng chi phí còn thiếu. Nếu chỉ
   muốn lấy source/baseline trước thì để false; phần cost khi đó là SKIPPED,
   chưa được coi đã giải quyết. Không cần chạy workflow closure riêng vì job
   audit đã gọi cùng kiểm tra.
5. Chờ các job kết thúc. Workflow không sửa main, không gọi LLM, không cần API
   key hoặc GCP secret. Chỉ dùng runner Ubuntu tiêu chuẩn; workflow chặn repo
   private để tránh tự dùng quota trả phí của trường hợp đó. Chi phí API là 0;
   không bật runner lớn hoặc dịch vụ trả phí bên ngoài.

Các job:

| Job | Tác dụng | Điều gì chưa được chứng minh khi job xanh |
|---|---|---|
| audit | Unit tests hiện tại, frozen artifacts, raw evidence cũ, paid HOLD | Không chứng minh target mới có ích |
| source_scout ×7 | Match tĩnh và test/assertion tham chiếu trên các pin | Không chứng minh reach động, oracle tier-1 hoặc direction |
| pydantic_baseline | Ba lần nguyên bản, coverage theo test/phase | Không có treatment hoặc claim lợi/hại |
| cost ×2 (tùy chọn) | Đo ba policy, ba lần/target, audit raw | Không khái quát ngoài hai target đã biết |
| collect | Gom output, kể cả run lỗi | Collect xanh không có nghĩa mọi job xanh |

Python 3.8.20 cho NetworkX được phục hồi bằng uv; không yêu cầu
`actions/setup-python` tìm bản 3.8.20 trên Ubuntu 22.04 nữa. Evidence envelope
được tạo trước setup để lỗi môi trường vẫn có file upload.

## 3. Gửi lại gì?

Tại cuối trang workflow run → **Artifacts** → tải **next-evidence-return-a1**
(hoặc `a2`, `a3` tương ứng attempt mới nhất). Các raw artifact cũng có hậu tố
attempt, không ghi đè log của lần thất bại trước; collector gom raw của mọi
attempt trong cùng run.
Gửi lại **file ZIP đó + URL của workflow run**. Đây là bộ dữ liệu cần để ra
quyết định; không cần dán code hoặc chỉ gửi ảnh màu xanh/đỏ.

Trong artifact có:

- `JOB_STATUS.json`, `RUN_CONTEXT.txt`: commit, run ID, attempt, job nào fail/skip.
- `artifacts/next-raw-audit-a*/`: log kiểm toán, kết quả PASS/FAIL thực tế trên main mới.
- `artifacts/next-raw-scan-*-a*/run/SCAN_RESULT.json` và `.md`: source pin, site, assertion,
  lỗi parse/matcher; không có treatment result.
- `artifacts/next-raw-pydantic-baseline-a*/`: dependency/setup logs, nguyên bản source
  receipts, `BASELINE_RESULT.json/.md`, raw test logs, XML và coverage contexts.
- Nếu bật cost: `artifacts/next-raw-cost-*-a*/run/`: `COST_RESULT.json/.md`,
  `RAW_AUDIT.json`, 9 arm results/target, XML, stdout/stderr, draw journals.

Nếu job dừng trước khi tạo RESULT, vẫn gửi artifact: `context.txt`, `install.log`,
`execution.log`, progress hoặc XML còn lại là bằng chứng chẩn đoán. Nếu collect
thất bại, tải các artifact `next-*` riêng. Nếu setup bị lỗi trước khi có log,
gửi thêm toàn bộ workflow logs từ menu của run. Không sửa expected output,
loại case fail hoặc đổi pin để ép pass; giữ run lỗi và chạy attempt mới sau
khi có sửa môi trường được ghi lại.

## 4. Sau khi có output

Từ Pydantic: đối chiếu test reach → bool input → assertion → contract upstream
trước khi quyết định treatment. Nó thuộc skill 1; không đếm cho mục tiêu skill 2.
Từ source scout: chọn candidate skill 2 theo oracle độc lập và khả năng dựng
môi trường; chưa chạy skill trên cohort Study J trước public freeze.
Từ cost: tính delta với census-only; báo cả kết quả không tiết kiệm hoặc âm.

Chưa có output thì các bước này vẫn PENDING. B9 vẫn HOLD, không có paid pilot
được ngầm cho phép bởi workflow xanh.
