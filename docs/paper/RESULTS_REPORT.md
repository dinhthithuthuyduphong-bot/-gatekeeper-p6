# Báo cáo kết quả: số liệu thống kê trước, đánh giá sau

*Sinh tự động bởi `tools/results_report.py` từ tệp kết quả trong `research_closure/results/`. Không có con số nào gõ tay. Khoảng tin cậy là Wilson 95%. Cột cuối là đánh giá của Gatekeeper (G) so với từng luật.*

### Study T: kỹ năng thị trường (rule Ruff) trên 60 gói PyPI — ô rule Ruff, 1531 ô dùng được

| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |
|---|---|---|---|---|---|---|
| Áp dụng tất cả (U) | 11/11 | 100.0% [74.1%, 100.0%] | 1520/1520 | 100.0% [99.7%, 100.0%] | 0 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Nhãn safe của Ruff (RS) | 0/11 | 0.0% [0.0%, 25.9%] | 677/1520 | 44.5% [42.1%, 47.0%] | 0 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| Replay ví dụ tài liệu (B6-R) | 9/11 | 81.8% [52.3%, 94.9%] | 996/1520 | 65.5% [63.1%, 67.9%] | 0 | G **thắng** cả hai chiều |
| Replay trên mọi gói nguồn (B6-strong) | 2/11 | 18.2% [5.1%, 47.7%] | 1256/1520 | 82.6% [80.6%, 84.5%] | 0 | G **thắng** cả hai chiều |
| B6-majority | 10/11 | 90.9% [62.3%, 98.4%] | 1503/1520 | 98.9% [98.2%, 99.3%] | 0 | G **thắng** cả hai chiều |
| LLM judge (LJ) | 6/11 | 54.5% [28.0%, 78.7%] | 1128/1520 | 74.2% [72.0%, 76.3%] | 0 | G **thắng** cả hai chiều |
| Smoke 20 draw | 0/11 | 0.0% [0.0%, 25.9%] | 1518/1520 | 99.9% [99.5%, 100.0%] | 20 | G **thua** |
| Fixed-sample (199 draw) | 0/11 | 0.0% [0.0%, 25.9%] | 1492/1520 | 98.2% [97.4%, 98.7%] | 199 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| Always-retest B8 | 0/11 | 0.0% [0.0%, 25.9%] | 1506/1520 | 99.1% [98.5%, 99.5%] | 199.5 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| **Gatekeeper (G), e-Holm** | 0/11 | 0.0% [0.0%, 25.9%] | 1512/1520 | 99.5% [99.0%, 99.7%] | 198.5 | — |
| Gatekeeper, e-BH (G-FDR) | 0/11 | 0.0% [0.0%, 25.9%] | 1517/1520 | 99.8% [99.4%, 99.9%] | 198.5 | G **thua** |

Tiêu chí đăng ký trước: W1 THUA, W2 THẮNG, W3 THUA, W4 THẮNG. LLM judge chấm 1559 ô.

### Study T2: nhân rộng trên 140 gói PyPI hạng 61–200 (G-FDR đăng ký trước) — ô rule Ruff, 3351 ô dùng được

| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |
|---|---|---|---|---|---|---|
| Áp dụng tất cả (U) | 20/20 | 100.0% [83.9%, 100.0%] | 3331/3331 | 100.0% [99.9%, 100.0%] | 0 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Nhãn safe của Ruff (RS) | 3/20 | 15.0% [5.2%, 36.0%] | 1537/3331 | 46.1% [44.5%, 47.8%] | 0 | G **thắng** cả hai chiều |
| Replay ví dụ tài liệu (B6-R) | 17/20 | 85.0% [64.0%, 94.8%] | 2211/3331 | 66.4% [64.8%, 68.0%] | 0 | G **thắng** cả hai chiều |
| Replay trên mọi gói nguồn (B6-strong) | 4/20 | 20.0% [8.1%, 41.6%] | 2432/3331 | 73.0% [71.5%, 74.5%] | 0 | G **thắng** cả hai chiều |
| B6-majority | 20/20 | 100.0% [83.9%, 100.0%] | 3309/3331 | 99.3% [99.0%, 99.6%] | 0 | G **thắng** cả hai chiều |
| LLM judge (LJ) | 10/20 | 50.0% [29.9%, 70.1%] | 2377/3331 | 71.4% [69.8%, 72.9%] | 0 | G **thắng** cả hai chiều |
| Smoke 20 draw | 1/20 | 5.0% [0.9%, 23.6%] | 3326/3331 | 99.8% [99.6%, 99.9%] | 20 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Fixed-sample (218 draw) | 0/20 | 0.0% [0.0%, 16.1%] | 3281/3331 | 98.5% [98.0%, 98.9%] | 218 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| Always-retest B8 | 0/20 | 0.0% [0.0%, 16.1%] | 3312/3331 | 99.4% [99.1%, 99.6%] | 239.2 | G **thua** |
| **Gatekeeper (G), e-Holm** | 0/20 | 0.0% [0.0%, 16.1%] | 3309/3331 | 99.3% [99.0%, 99.6%] | 238.0 | — |
| Gatekeeper, e-BH (G-FDR) | 0/20 | 0.0% [0.0%, 16.1%] | 3320/3331 | 99.7% [99.4%, 99.8%] | 238.0 | G **thua** |

Tiêu chí đăng ký trước: W1 THẮNG, W2 THẮNG, W3 THUA, W4 THẮNG. LLM judge chấm 3361 ô. **Gói chưa có kết quả (9):** colorama, docstring-parser, joblib, anthropic, deprecated, sqlparse, paramiko, azure-storage-blob, python-docx.

### Study T2: nhân rộng trên 140 gói PyPI hạng 61–200 (G-FDR đăng ký trước) — mọi ô, gồm R2, 3426 ô dùng được

| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |
|---|---|---|---|---|---|---|
| Áp dụng tất cả (U) | 29/29 | 100.0% [88.3%, 100.0%] | 3397/3397 | 100.0% [99.9%, 100.0%] | 0 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| LLM judge (LJ) | 10/29 | 34.5% [19.9%, 52.7%] | 2391/3397 | 70.4% [68.8%, 71.9%] | 0 | G **thắng** cả hai chiều |
| Smoke 20 draw | 1/29 | 3.4% [0.6%, 17.2%] | 3391/3397 | 99.8% [99.6%, 99.9%] | 20 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Fixed-sample (218 draw) | 0/29 | 0.0% [0.0%, 11.7%] | 3345/3397 | 98.5% [98.0%, 98.8%] | 218 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| Always-retest B8 | 0/29 | 0.0% [0.0%, 11.7%] | 3376/3397 | 99.4% [99.1%, 99.6%] | 239.2 | G **thua** |
| **Gatekeeper (G), e-Holm** | 0/29 | 0.0% [0.0%, 11.7%] | 3374/3397 | 99.3% [99.0%, 99.5%] | 238.0 | — |
| Gatekeeper, e-BH (G-FDR) | 0/29 | 0.0% [0.0%, 11.7%] | 3385/3397 | 99.6% [99.4%, 99.8%] | 238.0 | G **thua** |

Tiêu chí đăng ký trước: W1 THẮNG, W2 THẮNG, W3 THUA, W4 THẮNG. LLM judge chấm 3361 ô. **Gói chưa có kết quả (9):** colorama, docstring-parser, joblib, anthropic, deprecated, sqlparse, paramiko, azure-storage-blob, python-docx.

### Study T-A6/T-A7: B9 (model tự áp dụng thay đổi) theo 3 mức model, so với Gatekeeper

| Mức | Model | Ô đánh giá được | Có hại được áp dụng [Wilson 95%] | …trên ô vốn an toàn | Không parse được | USD/ô | Giây/ô | G có hại | G USD/ô | B9 đắt hơn G | **Đánh giá** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rẻ | google/gemini-3.8-flash (low) | 148 | 10 (6.8% [3.7%, 12.0%]) | 2 | 6 | 0.0080 | 16.9 | 0 | 0.00031 | ×26 | G **thắng** |
| vừa | google/gemini-3.8-flash (high) | 123 | 9 (7.3% [3.9%, 13.3%]) | 1 | 52 | 0.0246 | 36.4 | 0 | 0.00028 | ×87 | G **thắng** |
| mạnh | google/gemini-4-argon (low) | 148 | 11 (7.4% [4.2%, 12.8%]) | 2 | 3 | 0.0147 | 32.5 | 0 | 0.00030 | ×49 | G **thắng** |

### Study U: tác hại hiếm, 693 patch agent đã resolved trên SWE-bench — tác hại = contract regression (chính)

| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |
|---|---|---|---|---|---|---|
| Test pass (U) | 44/44 | 100.0% [92.0%, 100.0%] | 649/649 | 100.0% [99.4%, 100.0%] | 0 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Smoke 20 draw | 10/44 | 22.7% [12.8%, 37.0%] | 639/649 | 98.5% [97.2%, 99.2%] | 20 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Fixed-sample (173 draw) | 0/44 | 0.0% [0.0%, 8.0%] | 299/649 | 46.1% [42.3%, 49.9%] | 173 | G **thắng** (giữ nhiều hơn, hại không hơn) |
| Always-retest B8 | 0/44 | 0.0% [0.0%, 8.0%] | 621/649 | 95.7% [93.8%, 97.0%] | 148.6 | G **thua** |
| **Gatekeeper (G), e-Holm** | 0/44 | 0.0% [0.0%, 8.0%] | 303/649 | 46.7% [42.9%, 50.5%] | 143.6 | — |
| Gatekeeper, e-BH (post hoc, U-A1) | 0/44 | 0.0% [0.0%, 8.0%] | 626/649 | 96.5% [94.7%, 97.6%] | 143.6 | G **thua** |

Dải tác hại 5–20%: 33 patch; admit: U 33, S20 10, FS 0, B8 0, G 0, G_FDR 0. Tiêu chí: U1 THẮNG, U2 THUA, U3 THẮNG.

### Study U: tác hại hiếm, 693 patch agent đã resolved trên SWE-bench — tác hại = khác biệt naive (phụ)

| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |
|---|---|---|---|---|---|---|
| Test pass (U) | 245/245 | 100.0% [98.5%, 100.0%] | 448/448 | 100.0% [99.1%, 100.0%] | 0 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Smoke 20 draw | 21/245 | 8.6% [5.7%, 12.7%] | 429/448 | 95.8% [93.5%, 97.3%] | 20 | G an toàn hơn, giữ ít hơn (**đánh đổi**) |
| Fixed-sample (173 draw) | 0/245 | 0.0% [0.0%, 1.5%] | 197/448 | 44.0% [39.4%, 48.6%] | 173 | hoà |
| Always-retest B8 | 0/245 | 0.0% [0.0%, 1.5%] | 400/448 | 89.3% [86.1%, 91.8%] | 148.6 | G **thua** |
| **Gatekeeper (G), e-Holm** | 0/245 | 0.0% [0.0%, 1.5%] | 197/448 | 44.0% [39.4%, 48.6%] | 119.1 | — |
| Gatekeeper, e-BH (post hoc, U-A1) | 0/245 | 0.0% [0.0%, 1.5%] | 408/448 | 91.1% [88.1%, 93.4%] | 119.1 | G **thua** |

Dải tác hại 5–20%: 104 patch; admit: U 104, S20 21, FS 0, B8 0, G 0, G_FDR 0. Tiêu chí: U1 THẮNG, U2 THUA, U3 THẮNG.

