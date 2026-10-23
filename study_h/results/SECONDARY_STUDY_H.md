# Study H — phân tích thứ cấp (post hoc, trên trace đã ghi; 50 họ kiểm định)

**Đơn vị FWER:** một họ = một lần lặp gồm 6 ô. Ô null (không được phép admit): rho_500, rho_1000.

| Cách tiếp cận | Họ có admit sai (trên 50) | ρ = 0% | ρ = 1% | ρ = 2% | ρ = 3% | ρ = 5% | ρ = 10% | Lần rút trung bình mỗi họ |
|---|---|---|---|---|---|---|---|---|
| Gatekeeper | 0 | 50 | 45 | 17 | 11 | 0 | 0 | 1300 |
| B6-S(5) | 45 | 50 | 44 | 44 | 40 | 38 | 27 | 30 |
| B6-S(20) | 18 | 50 | 35 | 28 | 26 | 16 | 2 | 120 |
| B6-S(50) | 2 | 50 | 26 | 16 | 13 | 2 | 0 | 300 |
| B-FS(100) | 0 | 25 | 11 | 2 | 0 | 0 | 0 | 600 |
| B-FS(200) | 0 | 50 | 32 | 11 | 5 | 0 | 0 | 1200 |
| B-FS(300) | 0 | 50 | 48 | 27 | 11 | 0 | 0 | 1800 |
| Lai: smoke 5 + GK | 0 | 50 | 40 | 15 | 10 | 0 | 0 | 1028 |

B-FS(n): cỡ mẫu cố định n, cùng θ, η và α (cận chính xác Clopper–Pearson cho h, cận Hoeffding cho lợi ích, Bonferroni trên 2 giả thuyết × 6 ô). Lai: smoke test 5 lần rút; nếu sạch thì chạy quy tắc Gatekeeper trên các lần rút **tiếp theo** (không dùng lại 5 lần rút smoke), e-Holm trên các ô.
