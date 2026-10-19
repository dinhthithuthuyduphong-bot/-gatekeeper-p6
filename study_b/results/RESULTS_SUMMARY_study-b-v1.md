# Study B v1 — kết quả (run `39219880641`, 19/10/2026)

**Loại bằng chứng:** PROSPECTIVE_FROZEN_REAL_TARGETS — hai repository thật, chưa từng chạy trước khi protocol được đóng băng (tag `study-b-freeze-a2`, 30 file trong `FREEZE.json`, amendment A1–A2 chỉ sửa lỗi kỹ thuật, không có kết quả nào được quan sát trước đó).
**Artifact:** `STUDY_B_OUTPUT` (sha256 `fe28cc2896dc5bcae18c4ef8a6fcb87d4103f4217bac3264721bb60a0bd54722`); bản lưu trong repo: `RESULT_study-b-v1.json`.

## 1. Kết quả chính (endpoint đã đăng ký trước)

| Target | Binder | Bind | Nhãn thật | B2 | B6-R | B8 | Gatekeeper |
|---|---|---|---|---|---|---|---|
| rich-click v1.9.9 | họ skill (neo theo hàm) | `_get_parameter_default` | có hại (sửa 8, hỏng 6) | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** (9 task) |
| rich-click v1.9.9 | v3 (P7.3) | từ chối (ngoài phạm vi) | — | ngoài scope | REJECT | — | ngoài scope |
| asyncclick 8.3.0.6 | họ skill | `get_help_extra` | có hại (sửa 8, hỏng 6) | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** (9 task) |
| asyncclick 8.3.0.6 | v3 (P7.3) | `get_help_extra` | có hại (sửa 8, hỏng 6) | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** (9 task) |

| Comparator | Cặp có hại bị admit | Chi phí (lượt chạy task) |
|---|---|---|
| B2 | 3/3 | 0 |
| B6-R (replay + fingerprint) | **3/3** | 0 |
| B8 (luôn retest) | 0/3 | 2.224 |
| Gatekeeper-Lite | **0/3** | 1.166 (gồm lượt lọc task) |

Ở cả 3 cặp, các ca được sửa đều là đối tượng so sánh chặt (8/8), các ca bị hỏng đều là chuỗi lazy rỗng (6/6) — đúng như quan sát trên Click ở giai đoạn phát triển, nay lặp lại trên **hai repository khác** chưa từng xem.

## 2. Phân tích độ nhạy (đã đăng ký trước): bỏ lớp chuỗi lazy

Cả 3 cặp thành **có lợi** (sửa 8, không hỏng ca nào). Khi đó B6-R admit là đúng.

## 3. Phân tích thăm dò (KHÔNG đăng ký trước)

Chạy lại đúng quy tắc Gatekeeper đã đóng băng (cùng thứ tự task, cùng ngưỡng) trên dữ liệu đã thu, nhưng bỏ các task chuỗi lazy: mỗi cặp có 8 lần có lợi, 0 lần có hại, E = 25,6; e-BH (FDR 0,1, K = 4) **admit cả 3 cặp**. Nghĩa là quyết định của Gatekeeper đi theo bằng chứng của oracle, không phải lúc nào cũng từ chối. Đây là kết quả thăm dò, không dùng làm kết luận chính.

## 4. Hạn chế

- **Bộ test gốc của rich-click không chạy được:** `tests/conftest.py` cần `typer`, chưa được khai báo trong requirements của target. Nhờ A2, oracle metamorphic vẫn chạy trong phiên riêng; nhưng với rich-click, mọi quyết định chỉ dựa trên 20 task metamorphic. Ghi trong `harness_errors`.
- **Nhãn có hại phụ thuộc lớp chuỗi lazy,** một lớp hành vi do nhóm khai báo (đăng ký trước Study B, nhưng chưa có xác nhận độc lập). Luôn báo kèm mục 2.
- **Ba cặp không độc lập hoàn toàn:** hai cặp asyncclick dùng chung target; hai binder cho cùng bản sửa ở asyncclick.
- **Quy mô nhỏ:** 2 repository, 3 cặp đánh giá được. Không suy ra tỉ lệ quần thể; không claim vượt B6 theo mốc điểm phần trăm.
- **e-BH kiểm soát FDR,** khác với ngân sách α theo ô (FWER) của paper (quyết định D2).

## 5. Điều được nói

Trên hai repository thật chưa từng xem, với protocol đóng băng trước: replay + fingerprint (B6-R) admit cả 3 lần tái sử dụng mà paired trial cho thấy gây hỏng một lớp hành vi đã khai báo; Gatekeeper-Lite từ chối cả 3 vì phát hiện tác hại sau 9 task mỗi cặp, với chi phí khoảng một nửa B8. Binder v3 phạm vi hẹp từ chối đúng ở repository có cấu trúc khác (rich-click).
