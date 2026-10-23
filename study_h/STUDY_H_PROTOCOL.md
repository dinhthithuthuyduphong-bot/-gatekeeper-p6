# Study H — tác hại hiếm (protocol)

**Trạng thái và thời điểm đóng băng:** ghi trong `config_study_h.json`, do workflow `study-h-freeze.yml` đặt; hash trong `FREEZE.json` (gồm target tổng hợp, oracle, skill, chứng chỉ mixture, bộ chạy và công cụ phân tích).

## 1. Câu hỏi (từ review ngày 22/10/2026)

Trên dữ liệu thật (D, E, G), tác hại xảy ra với 27–100% đầu vào, nên một smoke test nhỏ (B6-S) an toàn ngang Gatekeeper. Lợi thế lý thuyết của chứng chỉ ít tác hại — kiểm soát sai số khi tác hại **hiếm** — chưa được kiểm tra. Study H đo, theo tỉ lệ tác hại ρ được kiểm soát chính xác: **mỗi cách tiếp cận admit sai (ρ ≥ η) bao nhiêu lần, và admit đúng (ρ < η) bao nhiêu lần?**

## 2. Target và skill

- **Target tổng hợp** `fixtures/H1_rare/missing.py`: `is_missing(x)` dùng `x == None`. Hợp đồng ghi trong mã: `NullSentinel` (kiểu NULL của DSL, `__eq__(None)` trả True) **phải** được coi là thiếu; đối tượng `Ambiguous` (báo lỗi khi so với None) **không** thiếu. Bộ test của target (6 test) chỉ kiểm tra giá trị thông thường, giống tình huống Study E.
- **Skill:** đúng skill `none-identity` của Study G, ví dụ replay là bản fix thật (hera_pspec PR #485).
- **Nhãn thật theo cấu trúc:** mỗi lần rút chọn `Ambiguous` với xác suất 0,5 (skill có lợi), `NullSentinel` với xác suất ρ (skill có hại), giá trị thường với phần còn lại (không đổi). Vì vậy E[−Z] = 0,5 − ρ > θ ở mọi ô, và **ô được phép admit khi và chỉ khi ρ < η**.

**Đây là bằng chứng tổng hợp** (oracle cấp "hợp đồng do người thiết kế"), dùng để đo đặc tính vận hành của các quy tắc, không thay cho bằng chứng trên target thật.

## 3. Ô, lặp và tham số

- 6 ô: ρ ∈ {0; 1; 2; 3; 5; 10}%; **50 lần lặp độc lập** mỗi ô. Seed lần lặp r là SHA-256(seed drand ‖ r); seed drand lấy sau thời điểm đóng băng.
- Giữ nguyên tham số Study D/E/G: θ = 0,2, η = 0,05, báo động α = 0,05, n_max = 300; e-Holm FWER 0,1 trên 6 ô của **mỗi** lần lặp.
- Mỗi ô chạy đủ 300 lần rút (`b8_full`), để mọi baseline được tính trên cùng dữ liệu.

## 4. So sánh (khai báo trước)

| Cách tiếp cận | Quy tắc |
|---|---|
| **Gatekeeper (chính)** | Quy tắc đã đóng băng: chứng chỉ mức cược cố định c = 0,9 |
| Gatekeeper mixture (phụ) | Chứng chỉ mixture trên λ (`gatekeeper_ext/mixture_cert.py`), phát lại trên cùng trace |
| B6-S(k), k ∈ {5, 20, 50} | Replay + fingerprint + census + không có regression trong k lần rút đầu |
| B8 | Không có regression trong 300 lần rút |
| B6-R | Replay + fingerprint |

**Chỉ số:** với ρ ≥ η: tỉ lệ admit sai (mục tiêu ≤ α cho Gatekeeper); với ρ < η: tỉ lệ admit đúng; số lần rút trung bình. Khoảng tin cậy Wilson 95%.

## 5. Dự đoán ghi trước (từ lý thuyết và mô phỏng, chưa xem kết quả)

- B6-S(k) admit sai ở ρ ≥ η với xác suất khoảng (1 − ρ)^k (ví dụ k = 5, ρ = 5%: khoảng 0,77).
- B8 từ chối phần lớn các ô được phép có ρ > 0.
- Gatekeeper (c = 0,9) giữ admit sai ≤ α, nhưng **ít chứng nhận được** khi ρ ≳ 0,39η (khoảng 2%) trong 300 lần rút: đây là điểm yếu đã biết của mức cược cố định. Mixture giữ tăng trưởng dương ở vùng này nhưng cần nhiều lần rút hơn ngân sách 300, nên có thể không cải thiện trong Study H.

## 6. Kiểm tra trước khi đóng băng

Chạy thử ngoại tuyến (12 lần lặp, census giả định): đường chạy hoạt động; phát hiện và sửa một lỗi của bộ chạy (trace bị cắt khi Gatekeeper dừng vì thiếu `b8_full`); công cụ phân tích từ chối trace ngắn hơn n_max.
