# Báo cáo kết quả: số liệu thống kê trước, đánh giá sau

*Sinh tự động bởi `tools/results_report.py` từ tệp kết quả trong `research_closure/results/`. Không có con số nào gõ tay. Khoảng tin cậy là Wilson 95%. Cột cuối là đánh giá của Gatekeeper (G) so với từng luật.*

### Study T: kỹ năng thị trường (rule Ruff) trên 60 gói PyPI — 1531 ô dùng được

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
| **Gatekeeper (G)** | 0/11 | 0.0% [0.0%, 25.9%] | 1512/1520 | 99.5% [99.0%, 99.7%] | 198.5 | — |

Tiêu chí đăng ký trước: W1 THUA, W2 THẮNG, W3 THUA, W4 THẮNG.

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

### Study T-A6: B9 (model tự áp dụng thay đổi) so với Gatekeeper, 150 ô lấy mẫu

| Đại lượng | B9 (gemini-flash) | Gatekeeper | **Đánh giá** |
|---|---|---|---|
| Ô có hại được áp dụng / admit | 10 / 148 ô đánh giá được | 0 | G **thắng** |
| …trong đó trên ô vốn an toàn (B9 tự gây hại) | 2 | — | |
| Hàm model trả lời không parse được | 6 | 0 | |
| Chi phí mỗi ô (USD) | 0.00801 | 0.00031 (runner) | G rẻ hơn |
| Thời gian mỗi ô (giây) | 16.9 | 2.3 | |

Tiêu chí B9-W: **THẮNG**. Tổng chi phí model: 1.201 USD.

