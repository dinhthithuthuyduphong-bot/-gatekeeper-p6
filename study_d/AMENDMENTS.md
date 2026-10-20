# Study D — amendments

## A1 (sau lượt chạy chính) — hai lỗi kỹ thuật, không đổi quy tắc

**Lượt chạy gốc:** cả 8 job dùng bản đóng băng có `FREEZE.json` sha256 `6d964eb1a64791233523b54b036692c3e8f8ed7149e9d2cff55d813b8686ef6a`, seed từ drand quicknet vòng 33229360. Sáu target (D1, D3, D4, D5, A1, C2) chạy xong. Hai target dừng vì lỗi kỹ thuật **trước khi có bất kỳ kết quả nào** cho chúng:

- **C1 jsonschema:** `pip install` thất bại vì jsonschema lấy số phiên bản qua setuptools-scm từ `.git`, mà bộ chạy đã xoá `.git`. Lỗi xảy ra trước bước áp skill.
- **D2 Cerberus (Python 3.8):** `ast.unparse` chưa có trên Python 3.8, nên bước áp skill dừng khi ghi footprint. Lỗi xảy ra trước census và trước mọi lần rút.

**Thay đổi:**
- `gatekeeper_lite/transforms.py`: hàm `_unparse` dùng `ast.unparse` khi có (Python ≥ 3.9, nên kết quả của 6 target đã xong **không đổi**), và một hàm tương đương cho Python 3.8.
- `tools/run_study_d.py`, `tools/run_b9.py`: đặt `SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0` khi cài gói (gói được gỡ ngay sau đó; chỉ giữ dependency).
- **Seed không đổi:** seed luôn được tính từ hash đóng băng **gốc** (`seed_freeze_sha256`), nên việc đóng băng lại sau amendment không thể làm đổi seed.

**Không đổi:** skill, target, commit, oracle, bộ sinh, quy tắc quyết định, θ, η, α, n_max, ô.

**Phạm vi chạy lại:** chỉ C1 và D2. Kết quả của 6 target đã xong được giữ nguyên từ lượt gốc, không chạy lại.
