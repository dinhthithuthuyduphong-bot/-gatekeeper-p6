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

## Kết quả lượt chạy phát triển (bản 2.0; nửa A\* đã lộ; 240 trong 250 ứng viên)

Mảnh 18 bị dừng (mã 143) và không để lại artifact, nên 10 ứng viên của nó (vị trí 18, 43, ..., 243) không có kết quả. So sánh dưới đây là trên **cùng 240 ứng viên**.

| | Bản 1 | Bản 2 |
|---|---|---|
| Có test chạy được | 47 | **93** |
| ELIGIBLE | 25 | **57** |
| Tỉ lệ ELIGIBLE | 10,4% | **23,8%** (Wilson 95%: 18,8% đến 29,5%) |
| ELIGIBLE trong số chạy được | 53% | 61% |

34 ca mới đủ điều kiện; 2 ca mất (prowler: cài thêm gói kéo `pydantic` lên bản mới hơn bản dự án cần, một đánh đổi thật của cách cài rộng hơn).

**147 ca vẫn chưa chạy được test:** còn thiếu module 84 (`pkg_resources` 7, `pydantic` 6, `pandas` 6, `charms` 5...), lỗi conftest hoặc fixture 25, lỗi khác 23, cấu hình Django 6, không có thông báo lỗi 5, phiên bản Python hoặc cú pháp 4.

**Hệ quả cho cỡ cohort** (mô hình nhị thức, bỏ qua tương quan theo repo và khác biệt giữa hai nửa): xác suất có ít nhất 40 instance ELIGIBLE là 0,99 với 231 ứng viên ở tỉ lệ đo được (0,74 ở cận dưới); 0,995 với 300 ứng viên ở cận dưới; gần 1 với 400 ứng viên.

## Bản 2.1 (sửa sau lượt chạy này, chưa được đo)

1. **Hết thời gian giết cả nhóm tiến trình.** Đã kiểm chứng: `subprocess.run(timeout=...)` chỉ giết tiến trình con, còn tiến trình cháu (`pip`, `pytest`) tiếp tục chạy tới hết và tranh tài nguyên với các ứng viên sau. Đây là cơ chế có thể làm một mảnh chạm giới hạn 350 phút; không chứng minh được cho riêng mảnh 18 vì không có log.
2. **`pkg_resources`:** chỉ khi không import được sau khi cài, cài `setuptools<70` (phiên bản setuptools bỏ `pkg_resources` chưa được xác minh ở đây).
3. Workflow: mặc định 40 mảnh và 1.500 giây mỗi ứng viên; có thể chạy lại riêng một số mảnh.
