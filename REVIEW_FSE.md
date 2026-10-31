# Review kiến thức và công thức của bài FSE-2027-13

**Bài:** *Scope before Reuse: Risk-Controlled Admission of Learned Coding Skills* (FSE-2027-13), kèm reading list và summary.

**Nguồn của bản review này.** Ba PDF gốc **không có trong repo** (repo công khai; chỉ lưu SHA-256 ở [`PRIVATE_SOURCE_DIGESTS.json`](research_closure/PRIVATE_SOURCE_DIGESTS.json)). Mọi phát biểu về bài dưới đây lấy từ những gì repo đã ghi lại khi đọc PDF ngày 24/10/2026 ([PAPER_EXPECTATION_AUDIT](research_closure/PAPER_EXPECTATION_AUDIT.md), [README_VI](README_VI.md), [ALIGNMENT_WITH_FSE](research_closure/results/ALIGNMENT_WITH_FSE.md)). Phần cài đặt lấy từ mã nguồn. Chỗ nào cần đối chiếu lại với PDF thì ghi **[đối chiếu PDF]**.

Mọi phép tính số trong file này đã được chạy lại ngày 31/10/2026, mục 9. Tiến độ review nằm ở mục 10 và ở [TRACKING_FSE](TRACKING_FSE.md).

---

## 1. Ý tưởng chính

Một **kỹ năng lập trình học được** là một phép biến đổi mã tái sử dụng được, cùng họ với Getafix, Genesis, Refazer, LASE. Kỹ năng được học ở một phạm vi rồi đem **tái sử dụng** ở phạm vi khác. Câu hỏi của bài: trước khi cho phép kỹ năng chạy ở phạm vi mới, có nên đòi một **chứng chỉ thống kê** rằng nó có lợi và không gây hại, thay vì dựa vào replay ở nguồn và fingerprint môi trường không?

Theo audit, tiêu chí quan trọng nhất của proposal là **lợi thế so với replay + fingerprint mạnh, ở cùng mức giữ lại các lần tái sử dụng có lợi**. B9 (sửa trực tiếp) là đồng-chính (co-primary). Composition và retirement là các câu hỏi riêng.

## 2. Các khái niệm

| Khái niệm | Định nghĩa | Cài đặt trong repo |
|---|---|---|
| Gói kỹ năng S = ⟨π, D, I, P, K⟩ | π: thủ tục (phép biến đổi); D: mô tả môi trường; I: điều kiện áp dụng; P: ví dụ before/after ở nguồn; K: footprint (vùng mã bị đụng tới) | `gatekeeper_lite/skill.py`, `transforms.py` |
| Scope screen | Chỉ xét khi I(x) ∧ Compatible(D, x). Quan hệ môi trường có ba giá trị MATCH / DRIFT / UNRESOLVED; thiếu thông tin thì không admit | `screen.py` |
| Binder | Gắn π vào đúng một chỗ trong mã đích; **abstain** khi mơ hồ (`NO_MATCH`, `MULTIPLE_MATCHES`, `ALREADY_GUARDED`, …) | `gatekeeper.py: bind` |
| Paired trial | Mỗi task chạy hai lần, có và không có kỹ năng, trên cùng snapshot, cùng seed | `runner.py`, `harness.py` |
| Quyết định | ADMIT / QUARANTINE / ABSTAIN / OUT_OF_SCOPE | `gatekeeper.py` |
| Retirement | Fingerprint môi trường đổi thì thu hồi chứng chỉ, rồi kiểm lại bằng alpha của epoch mới | `retirement_check` |
| Comparator | B1, B2, B6-R (bind + replay nguồn + fingerprint, bản tái dựng), B8 (chạy lại mọi task) | `comparators` |

## 3. Đại lượng chính: STR

Với mỗi task i, gọi **Z_i = loss(có kỹ năng) − loss(không kỹ năng)**, với Z_i ∈ [−1, 1].

- Loss của bộ test là (1 − tỉ lệ pass) + 0,5 cho mỗi regression, chặn trong [0, 1]. Đây là quy ước của repo **[đối chiếu PDF]**.
- **STR = E[Z]** (skill transfer risk). STR âm nghĩa là kỹ năng có lợi.
- **Tiêu chí admit:** STR ≤ −θ, với θ là biên lợi ích tối thiểu.
- Đặt Y = −Z. Khi đó tiêu chí là E[Y] ≥ θ, và giả thuyết không là **H₀: E[Y] < θ**.

## 4. Chứng chỉ tuần tự: e-process và bất đẳng thức Ville

**Quá trình tài sản (betting e-process):**

  K_n = ∏_{i ≤ n} (1 + λ_i (Y_i − θ)),  λ_i ∈ [0, 1/(1+θ)),

trong đó λ_i chỉ được tính từ Y_1 … Y_{i−1} (**dự đoán được**).

**Vì sao hợp lệ.** Mỗi thừa số ≥ 0. Dưới H₀ thì E[1 + λ_i(Y_i − θ) | quá khứ] = 1 + λ_i(E[Y_i] − θ) ≤ 1. Vậy K_n là siêu martingale không âm, và **bất đẳng thức Ville** cho:

  P(sup_n K_n ≥ 1/α) ≤ α.

Hệ quả: **ADMIT khi K_n ≥ 1/α**. Quy tắc này hợp lệ ở **mọi thời điểm dừng phụ thuộc dữ liệu** (anytime-valid). Cách xây dựng theo tinh thần của Waudby-Smith & Ramdas 2024 và Ramdas et al. 2023. Giả định: các task là mẫu i.i.d. từ phạm vi.

- Cận λ < 1/(1+θ) bảo đảm thừa số dương với mọi Y ∈ [−1, 1], vì Y − θ ≥ −(1+θ).
- Repo dùng cược kiểu Kelly co lại: λ = edge/(var + edge²), với edge = mean − θ, chặn bởi `max_bet_fraction`/(1+θ) (`eprocess.py`).

**Biến thể: kiểm định dấu trên các cặp bất đồng** (McNemar tuần tự, `DiscordantSignEProcess`). Bỏ qua các cặp có Z = 0. Với X = 1 khi kỹ năng giúp:

- admit: H₀: q ≤ q₀, tài sản ∏(1 + λ(X − q₀)), với λ = (q₁ − q₀)/(q₀(1 − q₀)) chặn dưới 1/q₀;
- hại: H₀: h ≤ ε, tài sản ∏(1 + μ((1 − X) − ε)).

**Nhiều ô cùng lúc:** e-BH (Wang & Ramdas 2022) bác bỏ R ô có e-value lớn nhất, với R = max{k : e₍ₖ₎ ≥ K/(fdr·k)}. Kiểm soát FDR dưới mọi kiểu phụ thuộc.

## 5. Alpha ledger: không tái chế alpha

Mỗi ô (kỹ năng, phạm vi) được cấp trước α_cell. Epoch k (k = 0 là lần admit đầu, k ≥ 1 là admit lại sau retirement) chi

  α_k = α_cell · 6 / (π² (k+1)²).

Vì Σ_{k≥1} 1/k² = π²/6, nên Σ_k α_k = α_cell. Tổng sai lầm qua mọi lần admit lại không vượt α_cell. Đã kiểm bằng số: tổng 10⁵ số hạng = 0,99999 α_cell. **Đúng.**

## 6. Hai định lý cần sửa trước khi kế thừa

### 6.1 Định lý 4 (dịch chuyển phân phối bị chặn), trang 4 của bài

**Phát biểu trong bài, theo ghi chép:** chênh lệch kỳ vọng của excess loss giữa phân phối nguồn P và đích Q bị chặn bởi TV(P, Q).

**Vấn đề.** Với quy ước chuẩn TV(P, Q) = sup_A |P(A) − Q(A)| và Z ∈ [−1, 1]:

  |E_Q Z − E_P Z| ≤ 2·TV(P, Q),

không phải TV.

- *Chứng minh ngắn:* với f có biên độ (sup f − inf f) ≤ b thì |E_Q f − E_P f| ≤ b·TV. Ở đây b = 2.
- *Phản ví dụ:* Z ∈ {−1, +1}, P(Z = +1) = 0,1, Q(Z = +1) = 0,2. Khi đó TV = 0,1, còn E_P Z = −0,8 và E_Q Z = −0,6, nên chênh lệch kỳ vọng = 0,2 = 2·TV.

**Sửa:** hoặc ghi 2·TV, hoặc nói rõ TV được hiểu theo chuẩn L1 không chia hai. Repo không thêm bảo đảm nào về dịch chuyển khi triển khai mà không đo được; Lite chỉ chứng nhận generator đã khai báo.

### 6.2 Định lý 7 (composition), trang 4–5 của bài

**Phát biểu trong bài, theo ghi chép:** hai kỹ năng riêng lẻ đều có lợi vẫn có thể ghép lại thành có hại, và STR của bản ghép có thể ≥ 1 − ε với mọi ε > 0 ("no bound … for any g").

**Vấn đề.** Với loss ∈ [0, 1] và mỗi kỹ năng có STR ≤ −θ, ta có E[loss nền] ≥ θ. Do đó STR của bản ghép ≤ 1 − E[loss nền] ≤ 1 − θ. **Không thể** có STR ≥ 1 − ε khi ε < θ. Câu "không có cận nào cho mọi g" cũng cần loại các cận hiển nhiên này.

**Phần vẫn đúng và đủ để tạo động lực:** lợi ích riêng lẻ không bảo đảm composition an toàn. Construction hợp lệ: loss nền = θ, loss của mỗi kỹ năng = 0, loss của bản ghép = 1. Khi đó STR riêng = −θ, còn STR chung = 1 − θ > 0.

Hai mục 6.1 và 6.2 là **phản ví dụ cho giả định**, không phải bác bỏ ý tưởng. Cần trao đổi với tác giả bản nháp trước khi dùng nguyên văn.

## 7. Chứng chỉ tác hại và đồ thị pha các cổng (repo phát triển thêm từ bài)

Đây là phần repo xây dựng và dùng ở Study D đến P (`gatekeeper_ext/gates.py`), không phải công thức nguyên văn của bài.

**Tham số:** η = 5% (tỉ lệ hại chấp nhận được), α = 0,1, mức cược c = 0,9, λ = c/(1 − η).

**Quá trình tài sản cho H₀: h ≥ η:**

- mỗi lần rút sạch nhân tài sản với 1 + λη;
- mỗi lần rút có hại nhân với 1 + λ(η − 1) = 1 − c.

Ở h = η, kỳ vọng thừa số = (1 − η)(1 + λη) + η(1 − c) = 1. Với h ≥ η kỳ vọng ≤ 1, nên đây là siêu martingale và Ville áp dụng được.

**Hệ quả kiểm được:**

| Đại lượng | Công thức | Giá trị | Khớp với tài liệu |
|---|---|---|---|
| Ngưỡng chịu hại thực tế (tăng trưởng dương) | h < ln(1+λη) / (ln(1+λη) − ln(1−c)) | **1,97% ≈ 0,39η** | ✅ paper snippet A.3 |
| Số lần rút sạch để chứng nhận, họ 16 ô | ⌈ln(16/α) / ln(1+λη)⌉ | **110** | ✅ |
| Như trên, 1 ô | ⌈ln(1/α) / ln(1+λη)⌉ | 50 | |

**Vùng tác hại một phần (Study P, mục 4.1):** [3/n, 1 − 0,1^(1/20)].

- *Cận dưới 3/n* theo quy tắc ba (Hanley & Lippman-Hand 1983): không có sự kiện nào trong n lần rút thì cận trên 95% của tỉ lệ ≈ 3/n. Với n = 400, cận dưới = **0,75%**.
- *Cận trên:* smoke 20 admit một patch có tỉ lệ hại θ với xác suất (1 − θ)²⁰. Xác suất này < 10% khi θ > 1 − 0,1^(1/20) = **10,87%**.

**Xác suất admit của các cổng đơn giản (bảng pha), kiểm lại:**

| Cổng | Công thức | Kiểm tra |
|---|---|---|
| Smoke 20 | (1 − h)²⁰ | h = 11%: 0,097 < 0,1 ✅ |
| Zero-tolerance 300 | (1 − h)³⁰⁰ | h = 0,3%: 0,41 ✅; = 0,5 ở h ≈ 0,23% ✅ |
| Cỡ mẫu cố định | admit khi số lần hại ≤ x\*, với x\* lớn nhất thoả F_Bin(x\*; n, η) < α | `fixed_sample_xstar` |

**Kết luận của repo, khác với bài:** ở cùng số lần rút, kiểm định cỡ mẫu cố định an toàn như Gatekeeper và **mạnh hơn** (ví dụ 92% so với 65% ở h = 2%, n = 300). Lợi thế của quy tắc tuần tự là **dừng sớm** và **hợp lệ khi dừng tuỳ ý**, không phải công suất.

## 8. Kiến thức thống kê dùng trong Study P và Q

| Công cụ | Công thức / ý | Dùng ở đâu |
|---|---|---|
| Khoảng Wilson [Wilson 1927] | (p̂ + z²/2n ± z·√(p̂(1−p̂)/n + z²/4n²)) / (1 + z²/n) | Tỉ lệ ở P, Q-F1, Q2/Q4 |
| Clopper–Pearson [1934] | Khoảng chính xác từ phân phối nhị thức / beta | RQ3, HQ1 |
| Nhị thức chính xác một phía | Bác bỏ H₀: p ≤ p₀ khi P(X ≥ k \| p₀) ≤ α | H1 (P), HQ1 (Q) |
| Cỡ mẫu HQ1 | p₀ = 0,5, p₁ = 0,8, α = 0,05: n nhỏ nhất có công suất ≥ 0,8 | **18** (k\* = 13, công suất 0,867) ✅ |
| Hiệu ứng thiết kế [Kish 1965] | deff = 1 + (m − 1)ρ | Lý do chọn 1 patch mỗi instance ở P (ρ = 0,87) |
| Cỡ cụm tối ưu [Raudenbush 1997] | m\* = √((c₁/c₂)(1 − ρ)/ρ) → 0 khi ρ → 1 | Study P, mục 4.3 |
| Bootstrap gom cụm [Field & Welsh 2007] | Lấy mẫu lại theo repo hoặc instance | P, Q |
| McNemar chính xác [1947] | Chỉ dùng các cặp bất đồng | H3 (P) |
| Phân loại theo hợp đồng [Meyer 1992] | C1 / C2-D / C2-O / C3 theo phản ứng của bản fix | RQ5, Study Q |

**Lưu ý về cỡ mẫu HQ1:** công suất của kiểm định nhị thức chính xác **không đơn điệu theo n** (răng cưa). Ví dụ n = 16 cho 0,798 < 0,8, còn n = 17 cho 0,758. "18" là n nhỏ nhất đạt ≥ 0,8, và mọi n từ 18 tới 24 đều đạt. Nên ghi rõ điều này trong bài.

## 9. Kiểm tra bằng số (31/10/2026)

```
1 - 0.1**(1/20)                 = 0.10875   (cận trên vùng)
3/400                           = 0.0075    (cận dưới vùng, n = 400)
(1-0.003)**300                  = 0.406     (zero-tol, h = 0.3%)
(1-0.0023)**300                 = 0.501
0.89**20                        = 0.097     (smoke 20, h = 11%)
sum 6/(pi^2 (k+1)^2), k < 1e5   = 0.999994  (alpha ledger)
E[factor] at h = eta            = 1.000     (chứng chỉ tác hại là martingale ở biên)
h_max (growth > 0), c = 0.9     = 0.0197
n_cert, K = 16, alpha = 0.1     = 109.7 -> 110
HQ1: n = 18, k* = 13, power     = 0.867
```

## 10. Trạng thái review (song song với [TRACKING_FSE](TRACKING_FSE.md))

| # | Mục | Kết luận review | Việc tiếp |
|---|---|---|---|
| R1 | STR, tiêu chí STR ≤ −θ | Nhất quán | Đối chiếu quy ước loss với PDF |
| R2 | E-process + Ville, ngưỡng 1/α | **Đúng** (siêu martingale không âm, cược dự đoán được) | |
| R3 | Alpha ledger 6/(π²(k+1)²) | **Đúng** | |
| R4 | Định lý 4 | **Cần sửa:** hằng số 2·TV | Trao đổi với tác giả |
| R5 | Định lý 7 | **Cần sửa:** cận 1 − θ; giữ construction hợp lệ | Trao đổi với tác giả |
| R6 | Số headline (180 cặp / 25 repo, 6,4 điểm, 84,3%, 41/46, 1,9×) | **Projected**, không phải kết quả đo | Không trích như kết quả |
| R7 | "Gatekeeper mạnh hơn cổng đơn giản" | **Không đứng được** về công suất (đồ thị pha, Study P) | Thu hẹp thành "dừng sớm + hợp lệ khi dừng tuỳ ý" |
| R8 | "Learned skills" | Hai kỹ năng thử là AST rewrite viết tay | Thu hẹp thành "frozen code transformations" |
| R9 | Câu SWE-bench "6,4 điểm … consistent with our census" | Chưa gắn với dữ liệu | Gỡ, hoặc thay bằng kết quả Study Q |
| R10 | Trích dẫn VERIFY trong reading list | Chưa xác minh | Kiểm từng mục |
| R11 | Composition / retirement | Chỉ có demo dựng sẵn | Không tuyên bố thực nghiệm |
| R12 | Định nghĩa tác hại (không có trong bài gốc) | RQ5: oracle ngây thơ phóng đại 3 đến 15 lần | **Study Q** kiểm định (đang chạy) |
