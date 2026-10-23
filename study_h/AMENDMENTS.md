# Study H — amendments

## H-A1 — oracle file in the repository did not match the reviewed file (before any draw)

**Phát hiện:** lượt chạy đầu tiên dừng **trước lần rút đầu tiên** với `AttributeError: module 'gk_draw_oracle_coord' has no attribute 'scopes'`. File `study_h/oracles/rare_missing.py` trên repo lúc đóng băng không phải file đã soát (file đúng có sha256 `7d624ccee0bcb78158cefcfa129534497de53173ff74e810cc26a3cfaadec893` và định nghĩa `scopes`, `execute`, `judge`). Không có lần rút, kết quả hay quyết định nào được tạo ra.

**Thay đổi:**
- Thay `study_h/oracles/rare_missing.py` bằng file đã soát (sha256 ở trên).
- `tools/run_study_h.py`: in đường dẫn, mã băm và kích thước của oracle; dừng ngay nếu oracle thiếu `scopes`, `execute` hoặc `judge`; ghi `oracle_sha256` vào kết quả.

**Không đổi:** thiết kế, ô, tham số, số lần lặp, so sánh, dự đoán ghi trước. Seed được ghim theo hash đóng băng gốc (`seed_freeze_sha256`), nên không đổi.
