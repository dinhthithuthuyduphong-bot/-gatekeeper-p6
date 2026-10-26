# Cập nhật trực tiếp main và chạy bước kế tiếp

Base đã kiểm tra: `616a67f2bd024b96b24d5de958cfaa69e1fe9926`.

## Files cần cập nhật

| Path tại root repo | Loại | Vai trò |
|---|---|---|
| `.github/workflows/tm-dev.yml` | Update | Chọn một target hoặc unit-only; chạy contract tests trước; luôn xuất summary/artifact |
| `gatekeeper_ext/testmut.py` | Update | Runner receipts, raw signatures, completeness veto, legacy tests.py discovery |
| `gatekeeper_ext/testmut_evidence.py` | New | Ghi evidence, inventory và RESULT.md |
| `tools/tm_check.py` | Update | Giữ dữ liệu trước cleanup, kết quả kể cả exception, kiểm tra dependency command |
| `tools/tm_summary.py` | Update | Báo missing/pending/duplicate đúng, không đếm pass thiếu outcome |
| `tests/test_testmut_evidence.py` | New | 7 regression checks cho hợp đồng evidence |
| `README.md`, `START_HERE_VI.md` | Update | Trỏ checkpoint mới; sửa đường dẫn gói đã bị copy nhầm vào hướng dẫn root |
| `research_closure/results/audit-20261026/` | New | Báo cáo, correction, nguồn, audit và 6 TM artifact đã kiểm tra |

## Cách đưa vào repo

1. Giải nén ZIP. Copy **nội dung `main_update/`** vào repo root, giữ cấu trúc và ghi đè đúng các file liệt kê. Không upload `main_update` như một thư mục con. Không mang theo các file của gói FINAL/NEXT cũ.
2. Kiểm tra danh sách diff với `FILE_MANIFEST.json`. Nếu main đã sửa cùng file sau base trên, ghép thay đổi thay vì ghi đè mù. Không sửa `study_l/FREEZE.json`, `GATES.md`, `AMENDMENTS.md`, kết quả G1 hay `pre_b9/RELEASE_GATE.json`.
3. Commit trực tiếp main theo lựa chọn của bạn. Gói không tự push, không tự dispatch.

## Thứ tự chạy trên GitHub Actions

1. Mở **Gatekeeper test-mutation development check** (`tm-dev.yml`) → Run workflow → branch `main` → `target=unit-only`.
2. Nếu contract tests PASS, chạy lại workflow với `target=D5_pycubrid`. Budget vẫn 200 mutant IDs để đối chiếu development, không phải 200 cặp được đảm bảo đầy đủ.
3. Chạy `target=D2_cerberus` để kiểm tra discovery `tests.py`. Tìm được file không có nghĩa treatment sẽ có lợi hoặc oracle sẽ hợp lệ.
4. Sau khi raw đủ, chạy `target=D4_openfeature` để phân biệt nhiễu signature/fixture với sai khác ngữ nghĩa. Chưa cần chọn `all`; D1 cũ đã timeout và chưa nên chạy lại trước khi có giới hạn chi phí test mutation phù hợp.

Không chạy G2/G3 của Study L, không thay release gate, không chạy B9. Không cần model key. Không gọi API trả phí; GitHub runner/storage vẫn tiêu tài nguyên theo quota tài khoản, nên không khẳng định mọi phút CI luôn miễn phí.

## Output cần giữ và gửi lại

- `TM_contracts` gồm `RESULT.md` và `tests.log`.
- `TM_<target>` gồm `TM_<target>.json`, `RESULT_<target>.md`, `RESULT_SUMMARY.md`, `log_<target>.txt` và `evidence/<target>/`.
- Trong evidence: inventory SHA-256, test inventory, XML/JSON, command receipts, stdout/stderr, mutation catalog, mutated test source, per-arm signatures, input/commit/environment provenance.
- Gửi URL run là đủ nếu artifact còn truy cập được; nếu không, gửi ZIP artifact. Không cần copy raw log lên chat.
- Kết quả missing/nondeterministic/failure phải giữ nguyên. `all_four=false` có thể đi cùng job thực thi thành công; đọc RESULT, không chỉ badge xanh.

## Tiêu chí đóng bước này

Đủ raw để giải thích mọi missing/error; không ghi 200 completed pairs khi chỉ có 25; unit checks không bị bỏ qua; kết quả per-arm có thể tính lại từ record. Đây là đóng lỗi evidence, **không** phải chứng nhận A* hoặc đóng oracle validity. Công đoạn tiếp theo dựa trên raw, không thay protocol theo kết quả mong muốn.
