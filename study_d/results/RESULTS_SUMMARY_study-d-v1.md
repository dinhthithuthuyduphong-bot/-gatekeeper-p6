# Study D v1 — kết quả và diễn giải

**Loại bằng chứng:** prospective, protocol đóng băng trước khi chạy (tag `study-d-freeze`; Amendment A1, tag `study-d-freeze-a1`, chỉ sửa hai lỗi kỹ thuật và chạy lại hai target chưa có kết quả). Seed từ drand quicknet vòng 33229360, giữ nguyên qua amendment. 8 target trên 7 repository, 16 ô. Báo cáo sinh tự động: `REPORT_study-d-v1.md`; dữ liệu gốc: `RESULT_*.json`.

## 1. Kết quả chính

**Nhãn thật của từng ô** được lấy từ toàn bộ 300 lần rút của B8 cộng cổng census: **3 ô có lợi** (D1/bool, D3/bool, D5/bool), **9 ô không đổi** (skill áp dụng nhưng không làm đổi hành vi được đo), **4 ô ngoài scope** (D4, A1: skill từ chối), **0 ô có hại**.

| Comparator | Ô được admit | Trong đó có lợi | Trong đó không đổi (thay đổi vô ích) | Có hại |
|---|---|---|---|---|
| B2 (dùng khi bind được) | 12 | 3 | 9 | 0 |
| B6-R (bind + replay + fingerprint) | 12 | 3 | 9 | 0 |
| B8 (chạy đủ, admit khi không có regression) | 12 | 3 | 9 | 0 |
| **Gatekeeper-Lite (e-Holm, FWER 0,1)** | **2** | **2** | **0** | 0 |

- **Gatekeeper admit đúng hai ô có lợi rõ** (D1/bool: lợi ích trung bình −0,78; D3/bool: −0,50), mỗi ô sau 110 lần rút.
- **Gatekeeper không admit ô nào chỉ là thay đổi vô ích.** B2, B6-R và B8 đều admit 9 ô như vậy, ví dụ: skill sửa hàm `_validate_allowed`/`_validate_forbidden` của Cerberus (không phải chỗ có lỗi), một hàm không liên quan của voluptuous, và một guard thừa trong jsonschema.
- **Một ô có lợi bị bỏ lỡ:** D5/bool (pycubrid). Skill sửa đúng lỗi và không gây hại, nhưng trong scope bool đã khai báo chỉ 11% đầu vào chạm lỗi, nên lợi ích trung bình (−0,11) **nhỏ hơn biên θ = 0,2**. Đây là hệ quả trực tiếp của quy tắc đã đóng băng.

## 2. Chuyển giao của skill

| Target | Skill áp dụng ở đâu | Kết quả |
|---|---|---|
| D1 py_ecc | 23 vị trí, gồm mọi chỗ upstream đã sửa | Có lợi rõ |
| D3 spec-kit | Đúng chỗ upstream đã sửa, cùng dạng | Có lợi rõ |
| D5 pycubrid | Đúng chỗ upstream đã sửa, cùng dạng | Có lợi nhưng nhỏ trên scope |
| D2 Cerberus | Hai hàm khác, **không** phải chỗ có lỗi (kiểm tra kiểu qua bí danh) | Không đổi |
| D4 open-feature | Từ chối (kiểu kiểm tra qua biến) | Ngoài scope |

Skill học từ một nguồn (PySStuBs) chuyển giao **có lợi ở 3/5 target dương**, khớp đúng các dự đoán ghi trước từ diff.

## 3. Chi phí

- **Số lần chạy thử (endpoint chính):** Gatekeeper 3.220, B8 3.600 (ít hơn 11%). Tiết kiệm chỉ ở hai ô được admit sớm; các ô không có lợi ích chạy đến hết ngân sách vì quy tắc không có điểm dừng sớm cho "không có lợi ích".
- **Wall-clock (endpoint phụ):** Gatekeeper/B8 = 0,99. Census dùng chung chiếm gần toàn bộ thời gian (riêng py_ecc 741 giây).
- Theo khai báo trước (protocol mục 8b), **không claim tiết kiệm thời gian**.

## 4. Ablation đăng ký trước

| Biến thể | Ô được admit | Ghi chú |
|---|---|---|
| Đầy đủ | D1/bool, D3/bool | — |
| Bỏ chứng nhận ít tác hại | Như trên | Admit nhanh hơn nhiều (26 và 44 lần rút thay vì 110): đây là chi phí đo được của yêu cầu an toàn |
| Bỏ cổng census | Như trên | Census không chặn ô nào |
| e-Bonferroni thay e-Holm | Như trên | — |
| Kiểm định dấu thay e-process trung bình | **Thêm D5/bool** (158 lần rút) | Kiểm định dấu bỏ qua các lần rút không đổi, nên bắt được lợi ích tập trung ở ít đầu vào |
| η = 0,10 | Như trên | Admit sau 54 lần rút |

## 5. Điều được kết luận và không được kết luận

**Được:** trên 16 ô thật, đã đăng ký trước, Gatekeeper-Lite chỉ admit các lần tái sử dụng có lợi ích đo được và không có hại (2/2 admit đúng, 0 admit sai), và từ chối 9 thay đổi vô ích mà B2, B6-R và B8 đều chấp nhận. Kiểm soát FWER được thiết kế ở mức 0,1 và đã kiểm tra bằng mô phỏng.

**Không được:**
- **So sánh an toàn với B6-R trên dữ liệu này.** Study D không có ô nào có hại, nên câu hỏi "Gatekeeper chặn được lần tái sử dụng có hại mà B6-R bỏ lọt" **không được kiểm tra** ở Study D. Bằng chứng duy nhất về điểm này đến từ pilot B/C (hạ cấp) với lớp chuỗi lazy do nhóm khai báo.
- **Tiết kiệm chi phí đáng kể**, cả về số lần thử lẫn thời gian.
- **Khái quát** ra ngoài các bộ sinh đã khai báo trên target ở commit đã ghim.

## 6. Hạn chế

- Ba ô có lợi đến từ ba repository; hai ô được admit. Quy mô nhỏ, kết luận là mô tả trên ô cụ thể, không phải tỉ lệ quần thể.
- Đối chứng ngữ nghĩa voluptuous không kiểm tra được tác hại như dự định, vì skill áp dụng ở một hàm không nằm trên đường xử lý `Schema(int)`.
- Biên θ = 0,2 tính theo trung bình trên scope làm Gatekeeper bỏ lỡ lợi ích tập trung (D5). Đây là đánh đổi của thiết kế, đã thấy rõ qua ablation kiểm định dấu.
