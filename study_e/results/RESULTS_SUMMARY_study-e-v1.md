# Study E v1 — đối chứng có hại: kết quả

**Loại bằng chứng:** prospective, protocol đóng băng trước khi chạy (tag `study-e-freeze`), dùng **nguyên** skill và bộ chạy đã đóng băng của Study D. Seed drand quicknet vòng 33247360 (722100096351961304). 5 target, 10 ô. Không có lỗi kỹ thuật, không có amendment. Báo cáo sinh tự động: `REPORT_study-e-v1.md`.

## 1. Kết quả theo ô

| Ô | Nguồn oracle | Skill áp dụng ở | Nhãn thật (300 lần rút + census) | B2 | B6-R | B8 | Gatekeeper |
|---|---|---|---|---|---|---|---|
| **E1 pyyaml / bool** | 2b (ý đồ trong mã) | `ignore_aliases` | **Có hại** (275/300 lần rút sinh anchor/alias) | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** sau 2 lần rút |
| **E2 packaging / bool** | 2 (maintainer, tranh cãi) | 6 hàm `_validate_*`, `_cmpkey` | **Có hại** (260/300 đầu vào bị từ chối mới) | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** sau 2 lần rút |
| E3 databricks / bool | 3 (minh hoạ) | `escape_item` | Có hại (300/300) | ADMIT | ADMIT | REJECT | REJECT_HARM sau 2 lần rút |
| Scope int của E1–E3 | vi sai | — | Không đổi | ADMIT | ADMIT | ADMIT | QUARANTINE |
| K1 trino, K2 tomlkit (4 ô) | đối chứng | có áp dụng | Không đổi | ADMIT | ADMIT | ADMIT | QUARANTINE |

**Cả bốn giả thuyết đã đăng ký được xác nhận:**
- **H-E1:** Gatekeeper từ chối E1/bool vì tác hại.
- **H-E2:** B6-R admit E1/bool.
- **H-E3:** báo động tác hại kích hoạt ở E2/bool.
- **H-E4:** ở các đối chứng, không có thay đổi hành vi và Gatekeeper không admit.

## 2. Phát hiện quan trọng: bộ test gốc không bắt được tác hại

Census chạy **toàn bộ bộ test của chính target** ở cả hai nhánh: pyyaml 1.287 test, packaging **51.524 test**, databricks 130 test. Cả ba đều **0 regression mới**, dù skill làm thay đổi hành vi ở 87–100% đầu vào bool. Vì vậy:
- Một cách kiểm tra chỉ dựa vào test sẵn có của target sẽ admit cả ba lần tái dùng có hại.
- B6-R (replay ở nguồn + fingerprint) cũng admit cả ba.
- Chỉ các cách **có kiểm tra hành vi theo scope** (Gatekeeper, và B8 với đủ 300 lần rút) mới phát hiện được.

Điều này khớp với kết luận của các nghiên cứu về overfitting trong sửa lỗi tự động: test suite của dự án không đủ để đánh giá tính đúng của thay đổi.

## 3. Chi phí

- **Ô có hại:** Gatekeeper dừng sau **2** lần rút; B8 chạy đủ 300. Tổng lần rút: Gatekeeper 2.106, B8 3.000.
- **Wall-clock:** Gatekeeper/B8 = 1,00, vì census dùng chung chiếm gần toàn bộ thời gian (riêng packaging 176 giây). Đúng như đã khai báo trước, không claim tiết kiệm thời gian.

## 4. Ablation

Cả 6 biến thể đăng ký trước cho **cùng quyết định ở mọi ô**: phát hiện tác hại không phụ thuộc vào các lựa chọn thiết kế.

## 5. Giới hạn

- Chỉ **hai ô chính** (E1 cấp 2b, E2 cấp 2). E3 là cấp 3, chỉ minh hoạ.
- E2 là trường hợp **tranh cãi**: maintainer bác việc chặn bool ở `Version` (#1425), nhưng chính CHANGELOG lại chặn bool ở `pylock`. Nhãn "có hại" dựa trên lập trường đã đăng ký trước (#1425).
- Cấp 2b được thêm trước khi đóng băng, sau khi xem mã ứng viên (đã ghi trong protocol).
- Các thư viện cố ý coi bool là số nguyên qua `isinstance(x, int)` rất hiếm: 15 ứng viên chỉ cho ra 2 ô chính.
