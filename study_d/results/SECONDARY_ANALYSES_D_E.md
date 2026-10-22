# Phân tích thứ cấp trên trace đã đóng băng (post hoc; không thay kết quả chính)

## 1. Chiến lược betting và λ (lấy từ mã nguồn)

- **Lợi ích** (`BettingEProcess`): Y = −Z, H0: E[Y] ≤ θ; vốn ∏(1 + λᵢ(Yᵢ − θ)); λᵢ = (m̂ − θ)/(σ̂² + (m̂ − θ)²), cắt về [0; 0,5/(1+θ)]; m̂ là trung bình co về prior 0,5 với trọng số 1; σ̂² là phương sai mẫu (0,25 khi n < 2). λᵢ chỉ dùng dữ liệu trước lần rút i (predictable). Đây là chiến lược kiểu aGRAPA của Waudby-Smith & Ramdas, không phải hỗn hợp (mixture). Lần rút hoà có Y = 0 < θ nên làm vốn giảm khi λ > 0; sau vài lần hoà, m̂ < θ và λ = 0.
- **Chứng nhận ít tác hại** (`HarmCertEProcess`): λ **cố định** = 0,9/(1 − η); mỗi lần rút sạch nhân vốn với 1 + 0,9η/(1 − η) = 1,0474; một regression nhân vốn với 0,1.
- **Báo động** (`HarmAlarmEProcess`): cược Kelly cho h = 0,5: μ = min((0,5 − η)/(η(1 − η)), 0,95/η) = 9,47; mỗi regression nhân vốn khoảng 10, nên hai regression vượt 1/0,05 = 20.

## 2. Độ nhạy theo λ của chứng nhận (K = 16, mô phỏng 2.000 lần)

| Tỉ lệ λ/λmax | Lần rút để admit khi h = 0 | P(admit trong 300 lần rút), h = 0,02 | P(admit), h = η = 0,05 (phải thấp) |
|---|---|---|---|
| 0.5 | 196 | 0.199 | 0.001 |
| 0.7 | 141 | 0.399 | 0.003 |
| 0.9 | 110 | 0.333 | 0.007 |
| 0.99 | 100 | 0.201 | 0.005 |

λ lớn hơn admit nhanh hơn khi không có hại, nhưng mỗi regression làm vốn mất nhiều hơn, nên skill có hại hiếm khó được admit hơn. Giá trị 0,9 đã được đóng băng trước Study D/E.

## 3. Họ e-Holm khi loại các ô ngoài scope

Binding xảy ra trước mọi lần rút, nên loại ô ngoài scope khỏi họ không dùng tới kết quả. Study D: K = 16 → 12 (bỏ D4, A1); Study E không có ô ngoài scope.

| Ô | Quyết định (K = 16) | Quyết định (K = 12) |
|---|---|---|
| D1_py_ecc/bool | ADMIT (110) | ADMIT (104) |
| D3_speckit/bool | ADMIT (110) | ADMIT (104) |

Chỉ số lần rút để admit thay đổi; tập ô được admit không đổi.

## 4. Baseline mạnh hơn: replay + fingerprint + k lần smoke test với đầu vào của scope

B6-S(k): admit cả skill cho target khi replay pass, fingerprint khớp, census không có regression, **và** k lần rút đầu tiên ở mọi scope không có regression. Đây là kiểm thử khói không có thống kê, dùng đúng bộ sinh của scope.

| k | Ô có hại bị admit (trên 3) | Ô có lợi được admit (trên 3) | Ô vô ích được admit (trên 16) | Tổng lần rút |
|---|---|---|---|---|
| 1 | 0 | 3 | 13 | 22 |
| 3 | 0 | 3 | 13 | 66 |
| 5 | 0 | 3 | 13 | 110 |
| 10 | 0 | 3 | 13 | 220 |
| 20 | 0 | 3 | 13 | 440 |

Với k ≥ 1, B6-S chặn được cả ba ô có hại vì tác hại xảy ra ở 87–100% đầu vào bool. Một baseline mạnh hơn như vậy **an toàn ngang Gatekeeper trên dữ liệu này**; khác biệt còn lại là B6-S admit mọi thay đổi vô ích và không có bảo đảm sai số khi tác hại hiếm (ví dụ h = 2% cần khoảng 35 lần rút để có 50% xác suất thấy một regression).

## 5. Confidence sequence 95% tại thời điểm dừng (μ = E[Z]; h = P(regression))

| Ô | Lần rút | μ (CS 95%) | h (CS 95%) |
|---|---|---|---|
| D1_py_ecc/bool | 110 | [-0.87; -0.64] | [0.000; 0.060] |
| D3_speckit/bool | 110 | [-0.65; -0.37] | [0.000; 0.060] |
| D5_pycubrid/bool | 300 | [-0.15; -0.06] | [0.000; 0.020] |
| E1_pyyaml/bool | 2 | [-0.92; 1.00] | [0.040; 1.000] |
| E2_packaging/bool | 2 | [-0.92; 1.00] | [0.040; 1.000] |
| E3_databricks/bool | 2 | [-0.92; 1.00] | [0.040; 1.000] |

Ô có hại dừng sau 2 lần rút nên khoảng còn rất rộng; quyết định dựa trên e-process báo động, không trên khoảng này.

## 6. Dừng sớm khi vô vọng (futility, khám phá)

Quy tắc: dừng với QUARANTINE khi cận trên của CS 95% cho E[−Z] nhỏ hơn θ (lợi ích vượt biên là không còn khả dĩ). Quy tắc chỉ dẫn tới không-admit, nên không làm tăng sai số admit.

| Họ | Lần rút (quy tắc chính) | Lần rút (có futility) | Quyết định thay đổi |
|---|---|---|---|
| Study D | 3220 | 540 | không |
| Study E | 2106 | 216 | không |

## 7. Độ nhạy theo θ và η (trên trace thật)

| θ | η | Ô được admit (Study D, K = 16) | Ô REJECT_HARM (Study E) |
|---|---|---|---|
| 0.05 | 0.02 | D1_py_ecc/bool, D3_speckit/bool, D5_pycubrid/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.05 | 0.05 | D1_py_ecc/bool, D3_speckit/bool, D5_pycubrid/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.05 | 0.1 | D1_py_ecc/bool, D3_speckit/bool, D5_pycubrid/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.1 | 0.02 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.1 | 0.05 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.1 | 0.1 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.2 | 0.02 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.2 | 0.05 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.2 | 0.1 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.3 | 0.02 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.3 | 0.05 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |
| 0.3 | 0.1 | D1_py_ecc/bool, D3_speckit/bool | E1_pyyaml/bool, E2_packaging/bool, E3_databricks/bool |

