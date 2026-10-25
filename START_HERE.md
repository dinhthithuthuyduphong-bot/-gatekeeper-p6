# NEXT evidence — chỉ phần thay đổi so với FINAL

Đây là gói delta, không phải gói đầy đủ. Có **16 file mới + 5 file sửa**.
**444 file không đổi không được nén lại**, kể cả raw log/kết quả cũ trong FINAL.

1. Áp dụng `Gatekeeper_Final_ZeroCost_20261025.zip` và commit vào main trước.
   Nếu đã làm rồi thì bỏ qua bước này; không upload lại các file không đổi.
2. Mở `main_update/next_evidence/RUN_ON_GITHUB_VI.md` để cập nhật 21 file NEXT.
   Đường dẫn bên trong `main_update/` là đường dẫn ở gốc repo.
   Helper `APPLY_NEXT_UPDATE.py` chỉ kiểm hash rồi chép file; không compile,
   test, commit, push hoặc gọi API. Giải nén gói ở ngoài repo.
3. Chạy **Gatekeeper next evidence - zero-cost**, branch main, bật `run_cost`
   nếu muốn cả số đo census-only. Gửi URL run và artifact `next-evidence-return-a1`
   (hoặc attempt mới nhất).

Xem `FILE_CHANGES.md` để biết từng file. Báo cáo hiện tại nằm trong
`main_update/next_evidence/STATUS_AND_SCAN_VI.md`; khó khăn còn lại nằm trong
`main_update/next_evidence/REMAINING_GAPS.md`.

Lượt này chỉ đổi cách đóng gói và hướng dẫn; không chạy thêm thực nghiệm.
Code nghiên cứu của NEXT giữ nguyên. B9 vẫn HOLD, không phát sinh API trả phí.

`PACKAGE_CHECKS/DELTA_CHECK.json` ghi việc đối chiếu checksum, loại file trùng,
áp dụng thử file vào bản sao FINAL, kiểm việc chạy lại và từ chối file xung đột.
Đó là kiểm tra tính toàn vẹn file, không phải kết quả unit test/benchmark dự án.
