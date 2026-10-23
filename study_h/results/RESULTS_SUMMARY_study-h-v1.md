# Study H v1 — tác hại hiếm: kết quả

**Loại bằng chứng:** prospective, protocol đóng băng trước khi chạy (tag `study-h-freeze`; Amendment H-A1 thay file oracle sai trên repo, trước lần rút đầu tiên; seed giữ nguyên). Seed drand vòng 33305750. Oracle sha256 `7d624cce…c893` đúng file đã soát. 6 ô × 50 lần lặp, mỗi ô 300 lần rút. Target **tổng hợp**: kết quả đo đặc tính vận hành của các quy tắc, không thay cho bằng chứng trên target thật.

## 1. Tỉ lệ admit theo tỉ lệ tác hại ρ (được phép admit khi ρ < η = 5%)

| ρ | Được phép | Gatekeeper | B6-S(5) | B6-S(20) | B6-S(50) | B8 (300) | B6-R |
|---|---|---|---|---|---|---|---|
| 0% | có | 50/50 | 50/50 | 50/50 | 50/50 | 50/50 | 50/50 |
| 1% | có | **45/50** | 44/50 | 35/50 | 26/50 | 1/50 | 50/50 |
| 2% | có | 17/50 | 44/50 | 28/50 | 16/50 | 0/50 | 50/50 |
| 3% | có | 11/50 | 40/50 | 26/50 | 13/50 | 0/50 | 50/50 |
| **5%** | **không** | **0/50** | **38/50** | 16/50 | 2/50 | 0/50 | **50/50** |
| **10%** | **không** | **0/50** | **27/50** | 2/50 | 0/50 | 0/50 | **50/50** |

## 2. Đối chiếu với dự đoán ghi trước

| Dự đoán | Kết quả |
|---|---|
| B6-S(k) admit sai khoảng (1 − ρ)^k | ✓ k = 5: dự đoán 0,77 / 0,59 → quan sát 0,76 / 0,54 (ρ = 5% / 10%); k = 20: 0,36 → 0,32; k = 50: 0,08 → 0,04 |
| B8 từ chối phần lớn ô được phép có ρ > 0 | ✓ 1/50, 0/50, 0/50 ở ρ = 1/2/3% |
| Gatekeeper giữ admit sai ≤ α | ✓ **0/100** ở các ô không được phép (KTC 95% của mỗi ô: [0; 0,07]) |
| Gatekeeper khó chứng nhận khi ρ ≳ 0,39η ≈ 2% | ✓ 17/50 ở ρ = 2%, 11/50 ở ρ = 3% |
| Mixture có thể không cải thiện trong ngân sách 300 lần rút | ✓ hơi kém hơn (14/50, 9/50) |

## 3. Diễn giải

- **Khi tác hại hiếm, smoke test không còn an toàn.** B6-S(5) admit sai 76% ở ρ = 5% và 54% ở ρ = 10%; B6-R admit mọi ô có hại. Gatekeeper không admit sai lần nào.
- **So ở cùng mức an toàn, Gatekeeper giữ được nhiều tái dùng đúng hơn.** B6-S(50) đạt mức admit sai gần với Gatekeeper (2/50 ở ρ = 5%) nhưng chỉ admit đúng 26/50 ở ρ = 1%, so với 45/50 của Gatekeeper; muốn an toàn, smoke test phải dài và khi đó từ chối cả skill tốt.
- **B8 (không chấp nhận regression nào) an toàn nhưng gần như không bao giờ admit khi có tác hại dù rất nhỏ** (1/50 ở ρ = 1%): đó là một chính sách khác (không dung sai), không phải phép kiểm có biên η.
- **Điểm yếu của Gatekeeper:** ở ρ = 2–3% (được phép nhưng gần η), chứng chỉ mức cược cố định ít khi chứng nhận được trong 300 lần rút. Đây là giới hạn đã dự đoán; mixture không khắc phục được trong ngân sách này.
