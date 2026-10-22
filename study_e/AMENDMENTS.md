# Study E — amendments

## E-A1 — làm mới hash sau thay đổi ở file dùng chung (không đổi kết quả)

**Phát hiện:** sau Amendment A2 của Study D, kiểm tra hash của Study E báo hai file khác: `gatekeeper_lite/b9.py` và `tools/run_b9.py`. Danh sách hash của mọi study gồm cả các file dùng chung trong `gatekeeper_lite/` và `tools/`.

**Ảnh hưởng tới kết quả: không có.**
- Study E không dùng B9: không target nào của E có instance B9, và bộ chạy của E (`tools/run_study_d.py`, harness, module quyết định) không gọi `b9.py` hay `run_b9.py`.
- Lượt chạy chính và lượt tái lập của Study E đều diễn ra **trước** A2 (tag `study-e-freeze`); lượt tái lập cho kết quả giống hệt lượt chính.
- Kết quả lưu trong `study_e/results/` được tái tạo đúng từ dữ liệu gốc bởi `tools/results_check.py`.

**Thay đổi:** chỉ đóng băng lại để danh sách hash phản ánh các file dùng chung hiện tại. Seed được ghim theo hash đóng băng gốc (`seed_freeze_sha256`), nên không đổi. Không có chỉnh sửa nào khác.
