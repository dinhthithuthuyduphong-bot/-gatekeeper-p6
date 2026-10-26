# Khâu cài môi trường bản 2: lượt chạy phát triển (26/10/2026)

**Đây không phải một giai đoạn của study đã đăng ký.** Study M đã dừng ở cổng M1 (25/250), đúng quy tắc. Lượt chạy này đo xem khâu cài môi trường được cải thiện nâng tỉ lệ ELIGIBLE lên bao nhiêu, trên **nửa A\* đã lộ kết quả kiểm định** (dữ liệu phát triển). Nửa RR (231 ứng viên) **không được dùng**; workflow từ chối nếu danh sách có ứng viên không thuộc nhánh A\*.

## Thay đổi so với `vet_target.py` (file đã đóng băng, không sửa)

`tools/vet_target2.py` giữ nguyên cách phân loại (fail trước, pass sau) và chỉ thay khâu cài môi trường, giống hệt cho hai cánh tay:
1. nâng cấp `pip`, `setuptools`, `wheel` (venv của Python 3.12 không có `setuptools`, nên thiếu `pkg_resources`);
2. cài gói với **mọi** extra đã khai báo (trừ docs, lint, typing), rồi chuỗi dự phòng `[test]`, `[dev]`, gói trần, cài editable;
3. dependency groups (PEP 735), nhóm Poetry, môi trường Hatch;
4. file requirements ở gốc repo, trong `requirements/`, trong `tests/` (bỏ file docs);
5. `deps` của `[testenv]` trong tox; 6. pytest;
7. **sửa lỗi thu thập**: tối đa 4 vòng `pytest --collect-only`; module thiếu ở **bất kỳ** cánh tay nào, không phải module của chính repo, được cài vào **cả hai** (bảng ánh xạ tên import sang tên gói cố định).

Test không bao giờ bị sửa; kết quả test không bao giờ được dùng để quyết định cài gì.

## Sẽ dùng kết quả thế nào

Kết quả lượt này (tỉ lệ có test chạy được, tỉ lệ ELIGIBLE) được dùng để **thiết kế và đăng ký trước** một study mới, trên các ứng viên **chưa lộ**: nửa RR (chỉ sau IPA nếu đi RR) và các ứng viên mới khi tiếp tục khám phá theo đúng thứ tự seed từ vị trí 3.285. Ngưỡng của study mới được đóng băng **trước** khi kiểm định cohort của nó.
