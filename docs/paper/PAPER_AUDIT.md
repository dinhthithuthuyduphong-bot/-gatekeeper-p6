# Kiểm tra toàn bộ bài FSE-2027-13 và đề xuất sửa

**Đối tượng:** ba tệp trong [`source/`](source/): bài báo (`01-…-paper.pdf`), reading list (`02-…`) và summary (`03-…`). SHA-256 của ba tệp khớp với [`PRIVATE_SOURCE_DIGESTS.json`](../../research_closure/PRIVATE_SOURCE_DIGESTS.json).

**Bối cảnh:** theo người nghiên cứu, bản thảo do AI sinh và chưa được kiểm chứng. Trang 1 của bài cũng ghi rõ mọi số liệu là **projected**, chưa chạy thí nghiệm nào. Vì vậy bản kiểm tra này xem xét cả **toán**, **tính nhất quán nội bộ của số liệu**, **lập luận** và **trích dẫn**.

**Cách làm:** đọc toàn văn bằng `pdftotext`, tính lại mọi phép tính có thể tính lại (mục 9), đối chiếu với mã của repo (`gatekeeper_lite/`). Không sửa các PDF. Mỗi lỗi có đề xuất sửa, nhiều chỗ kèm câu chữ dán được vào LaTeX.

**Bản chi tiết có chứng minh đầy đủ:** [THEORY.md](THEORY.md) (kèm phép kiểm bằng số, workflow `Gatekeeper theory checks`).

**Mức độ:** 🔴 sai, phải sửa trước khi nộp · 🟠 thiếu hoặc mơ hồ, có thể bị phản biện bắt · 🟡 trình bày.

---

## Tóm tắt

| # | Mục | Vấn đề | Mức |
|---|---|---|---|
| T1 | Định lý 4 | Hằng số sai: đúng là 2ξ_s, không phải ξ_s | 🔴 |
| T2 | Định lý 4 | Ngân sách α cấp **theo phạm vi** nhưng phép hợp cận lấy **theo ô (kỹ năng, phạm vi)** | 🔴 |
| T3 | Định lý 4 + mục 5.4 | Admit lại sau retirement và các tổ hợp tiêu thêm α mà không có cơ chế chia | 🔴 |
| T4 | Định lý 7 | "STR(S₁∘S₂) ≥ 1 − ε với mọi ε" là không thể khi ε < θ; chứng minh tự mâu thuẫn | 🔴 |
| T5 | Định lý 7 | "Không có g nào" sai: g(a, b) = 1 + min(a, b) là một cận đúng và chặt | 🔴 |
| T6 | Mệnh đề 9 | Tỉ lệ phương sai sai; phép tính "lợi ròng 1,55×" đếm số lần chạy sai | 🔴 |
| T7 | Mệnh đề 6 | Lượng từ α thừa; cần thêm điều kiện thủ tục có admit; phạm vi áp dụng chưa rõ | 🟠 |
| T8 | Hệ quả 8 | d̄ = 0,34 mâu thuẫn với 11,4% cặp giao nhau (suy ra d̄ ≈ 10,6) | 🔴 |
| T9 | Giả định 3 | i.i.d. trong khi task lấy từ một tập hữu hạn; loss có thể vượt 1 mà không nói là chặn | 🟠 |
| S1 | RQ1 | CI [3,1; 9,8] **không** chứng minh "vượt biên 5 điểm" | 🔴 |
| S2 | Bảng 2, mục 10 | Tỉ lệ 5,1%, 11,5%, 22,7% không ứng với số nguyên nào trên 63 cặp có hại | 🔴 |
| S3 | Mục 10.3 | "58% là hại nhỏ trong biên θ nên admit là đúng": sai logic | 🔴 |
| S4 | Mục 10.3 | Gán lỗi lấy mẫu trong P_s cho số hạng dịch chuyển ξ_s: nhầm khái niệm | 🔴 |
| S5 | RQ1 | Endpoint là "ở cùng mức clean reuse" nhưng 84,3% ≠ 86,0% | 🟠 |
| S6 | RQ4 | Admission tốn 0,61 lần validation mà hoà vốn ở 2,4 lần tái sử dụng: thiếu giả định chi phí | 🟠 |
| S7 | Mục 3.3 | BH kiểm soát FDR, còn bài cần FWER; Howard et al. không phải "multiple testing" | 🟠 |
| N1 | Hình 1, mục 3, bước chứng minh Định lý 7 | Ví dụ retry/async tự mâu thuẫn: handler không khớp thì không thể nuốt lỗi | 🟠 |
| N2 | Hình 1 | "31/33 biến khớp" nhưng vẫn qua screen D | 🟡 |
| N3 | Keyword | "conformal prediction" trong khi phương pháp là e-process | 🟡 |
| N4 | Trích dẫn | 7 mục có tác giả placeholder hoặc mã arXiv chưa kiểm | 🟠 |
| N5 | Data availability, banner | Nhắc artifact, `PLAN.md`, `REVIEWS.md` không tồn tại | 🟠 |

---

## 1. Lý thuyết

### T1 🔴 Định lý 4: hằng số của số hạng dịch chuyển

**Bài viết:** "since ℓ ∈ [0, 1], the excess risk changes by at most ‖Q_s − P_s‖_TV ≤ ξ_s", từ đó kết luận Pr[∃ admitted (S, s): STR_{Q_s}(S, s) > −θ + ξ_s] ≤ α.

**Sai ở đâu.** STR = E[ℓ(x, π) − ℓ(x, ∅)], và hiệu này nằm trong [−1, 1], biên độ 2. Với hàm f có biên độ b thì |E_Q f − E_P f| ≤ b·TV. Nói cách khác, mỗi kỳ vọng E ℓ(·, π) và E ℓ(·, ∅) dịch tối đa TV, nên hiệu dịch tối đa 2·TV.

**Phản ví dụ:** Z ∈ {−1, +1}, P(Z = 1) = 0,1, Q(Z = 1) = 0,2. Khi đó TV = 0,1, còn E_P Z = −0,8 và E_Q Z = −0,6, chênh 0,2 = 2·TV.

**Sửa:** thay ξ_s bằng 2ξ_s trong phát biểu và chứng minh. Thêm một câu: bảo đảm chỉ có nghĩa với "có hại" (STR_Q > 0) khi 2ξ_s < θ.

> …the excess risk is a difference of two expectations of $[0,1]$-valued losses, so it changes by at most $2\|Q_s-P_s\|_{TV}\le 2\xi_s$, giving $\Pr[\exists\text{ admitted }(S,s):\mathrm{STR}_{Q_s}(S,s)>-\theta+2\xi_s]\le\alpha$. The guarantee excludes harmful admissions ($\mathrm{STR}_{Q_s}>0$) only when $2\xi_s<\theta$.

### T2 🔴 Định lý 4: α theo phạm vi, nhưng hợp cận theo ô

**Bài viết:** "scope s receiving budget α_s where Σ_s α_s ≤ α … admits S in s only when its e-process crosses 1/α_s". Chứng minh lại nói "Ville … for each (skill, scope) cell … a union bound over cells … gives α overall".

**Sai ở đâu.** Nếu mọi kỹ năng trong phạm vi s cùng dùng ngưỡng 1/α_s, phép hợp cận cho Σ_s |L_s|·α_s, không phải Σ_s α_s. Với 94 kỹ năng, sai số có thể lớn gấp nhiều chục lần α.

**Sửa:** cấp ngân sách **theo ô**, α_{S,s}, với Σ_{S,s} α_{S,s} ≤ α. Tổng này phải gồm cả các tổ hợp (xem T3), và ngân sách phải được cấp trước, không phụ thuộc dữ liệu. Phương án khác là dùng e-BH cho FDR, khi đó phải đổi mục tiêu từ FWER sang FDR.

> Let each (skill, scope) cell $(S,s)$, including composite cells $(S\circ S',s)$, receive a predictable budget $\alpha_{S,s}$ with $\sum_{(S,s)}\alpha_{S,s}\le\alpha$, fixed before any trial in that cell…

### T3 🔴 Retirement và tổ hợp tiêu thêm α

Mục 5.4: khi fingerprint đổi thì "admission is revoked and the skill returns to quarantine". Mỗi lần admit lại là một phép kiểm định mới trên cùng ô, nên nếu dùng lại α_{S,s} thì tổng sai số qua các epoch không còn bị chặn bởi α. Tương tự, mục 7 nói các tổ hợp "with their own α share" nhưng Định lý 4 không tính phần đó vào tổng.

**Sửa (đã cài trong repo, `gatekeeper_lite/eprocess.py: AlphaLedger`):** epoch k của một ô tiêu α_{S,s}·6/(π²(k+1)²). Vì Σ_{k≥1} 1/k² = π²/6, tổng qua mọi epoch ≤ α_{S,s}. Các ô tổ hợp được cấp trước trong cùng sổ cái.

### T4 🔴 Định lý 7: kết luận không thể đạt

**Bài viết:** với mọi ε > 0 tồn tại S₁, S₂ có STR(S₁, s) ≤ −θ, STR(S₂, s) ≤ −θ và STR(S₁∘S₂, s) ≥ 1 − ε.

**Sai ở đâu.** STR(S₁, s) ≤ −θ kéo theo E ℓ(x, ∅) ≥ θ + E ℓ(x, π₁) ≥ θ. Do đó

  STR(S₁∘S₂, s) = E ℓ(x, π₁∘π₂) − E ℓ(x, ∅) ≤ 1 − θ.

Với ε < θ, kết luận của định lý là không thể. Chính chứng minh cũng mâu thuẫn: nó yêu cầu S₁ "lowering loss by θ′ > θ" (nên ℓ(x, ∅) ≥ θ′ > θ) và đồng thời "ℓ(x, ∅) ≤ ε".

**Sửa (phát biểu đúng và chặt):**

> **Theorem 7 (Composition risk is not controlled by individual risks).** For any $a,b\in[-1,0)$ there are skills $S_1,S_2$ and a scope $s$ with $\mathrm{STR}(S_1,s)=a$, $\mathrm{STR}(S_2,s)=b$ and $\mathrm{STR}(S_1\circ S_2,s)=1+\min(a,b)$, which is the largest value compatible with $\ell\in[0,1]$. In particular two skills that each meet the admission margin $-\theta$ can compose to excess risk $1-\theta>0$.
>
> *Proof.* Take a constant baseline loss $c=-\min(a,b)$, losses $c+a$ and $c+b$ for the single skills, and loss $1$ for the composition. All losses lie in $[0,1]$, and the risks are as stated. The bound $\mathrm{STR}(S_1\circ S_2)\le 1-\mathbb{E}\ell(x,\varnothing)\le 1+\min(a,b)$ holds for any skills, so the construction is tight. $\square$

### T5 🔴 "Không có g nào"

"No bound of the form STR(S₁∘S₂) ≤ g(STR(S₁), STR(S₂)) holds for any g" là **sai**: g(a, b) = 1 + min(a, b) luôn đúng (T4), và đó là cận tốt nhất có thể. Phát biểu đúng là: **không có cận nào tốt hơn cận hiển nhiên do ℓ ∈ [0, 1]**. Vì vậy rủi ro riêng lẻ không đem lại thông tin gì về việc tổ hợp có an toàn hay không. Thông điệp của bài (Hệ quả 8) vẫn giữ được.

### T6 🔴 Mệnh đề 9: lợi ích của ghép cặp

Mô hình hoá ℓ(x, ∅) = T(x), ℓ(x, π) = T(x) + S(x), với Var T = σ_T², Var S = σ_S², T và S độc lập.

- **Ghép cặp:** Var(ℓ_π − ℓ_∅) = σ_S².
- **Không ghép cặp** (hai nhánh độc lập, mỗi nhánh n task): phương sai của ước lượng hiệu, nhân n, là Var(T + S) + Var(T) = **2σ_T² + σ_S²**.
- **Tỉ lệ đúng:** 1 + 2σ_T²/σ_S², không phải 1 + σ_T²/σ_S² như bài viết. Với σ_T²/σ_S² = 2,1, tỉ lệ là 5,2 chứ không phải 3,1.

**Đếm số lần chạy.** Bài viết: "pairing costs two runs per trial and saves a factor of 3.1 in trials — a net win of 1.55×". Nhưng ước lượng không ghép cặp **cũng** cần một lần chạy có kỹ năng và một lần không. Hai thiết kế tốn cùng số lần chạy trên mỗi task, nên không được chia đôi. Lợi ròng bằng đúng tỉ lệ phương sai.

**Sửa:** nêu rõ mô hình (T, S độc lập; không có nhiễu chạy lại), sửa tỉ lệ, bỏ phép chia đôi. Nếu muốn giữ con số đo được 3,1, phải định nghĩa lại σ_T² cho khớp. Thêm nữa, "standard concentration gives the sample counts" là quá sơ sài cho một e-process: nên nói số lần rút kỳ vọng cho đến khi dừng tỉ lệ với phương sai chia θ², theo Waudby-Smith & Ramdas 2024.

### T7 🟠 Mệnh đề 6

1. **"For any α < 1"** không gắn với gì: thủ tục là tuỳ ý và α không xuất hiện trong kết luận. Bỏ lượng từ này, hoặc phát biểu cho thủ tục đạt mức α.
2. **Cần điều kiện** thủ tục admit S với xác suất dương trên dữ liệu quan sát. Thủ tục không bao giờ admit thì không vi phạm gì.
3. **Phạm vi áp dụng:** mệnh đề nói về thủ tục chỉ dùng thử nghiệm trên R_obs. Thuật toán 1 lại chạy thử nghiệm **trên chính phạm vi đích** (x_n ∼ P_s). Cần nói rõ: mệnh đề cho thấy fingerprint và replay ở nguồn không đủ; còn với Gatekeeper, giới hạn tương ứng là khoảng cách giữa phân phối thử nghiệm P_s và phân phối triển khai Q_s, đúng số hạng ξ_s.

### T8 🔴 Hệ quả 8 mâu thuẫn với số liệu

Hệ quả 8 cho chi phí O(|L_s|·d̄) với d̄ = 0,34 "mean number of footprint-overlapping partners". Nhưng bài cũng nói 11,4% cặp kỹ năng có footprint giao nhau, và thư viện có 94 kỹ năng. Suy ra d̄ = 0,114 × 93 ≈ **10,6**, tức khoảng 498 cặp giao nhau trên 4.371 cặp. Một trong hai con số sai, hoặc d̄ được đo trên một tập khác mà bài không nói.

### T9 🟠 Giả định 3 và hàm loss

- **i.i.d.:** "target contexts … drawn i.i.d. from P_s", nhưng task của một repo là một tập hữu hạn, thường rút không hoàn lại. Ville vẫn đúng với rút không hoàn lại nếu e-process được xây cho quần thể hữu hạn, nhưng đó là cách xây khác. Cần nói rõ là rút có hoàn lại, hoặc dùng e-process cho quần thể hữu hạn. Repo đã ghi giới hạn này ở Study N.
- **Hàm loss:** "1 − held-out pass rate plus a 0.5 penalty per regression" có thể vượt 1, mâu thuẫn với ℓ ∈ [0, 1] mà Định lý 4 cần. Phải nói rõ là **chặn tại 1** (repo làm vậy trong `runner.py`), và nói rằng khi đã chặn thì loss không còn phân biệt được các mức hại lớn.

## 2. Số liệu và thống kê

### S1 🔴 Khoảng tin cậy không vượt biên 5 điểm

RQ1: "6.4 points (CI [3.1, 9.8], exceeding the 5-point margin)". Endpoint chính được đăng ký trước với **biên 5 điểm**. Muốn kết luận "vượt biên" thì **cận dưới** của CI phải > 5. Ở đây cận dưới là 3,1, nên kết quả **không** vượt qua cổng go/no-go mà summary nêu: "At least 5 absolute points … over replay verification plus environment fingerprints". Theo chính quy tắc của bài, kết luận đúng là "chưa xác lập".

### S2 🔴 Tỉ lệ không ứng với số nguyên

Bảng 1: số cặp có hại là 14 + 27 + 22 = **63**. Với 63 cặp:

- 5,1% ứng với 3,2 cặp; 11,5% với 7,2 cặp; 22,7% với 14,3 cặp. Không con số nào là số nguyên.
- Với 63 × 6 = 378 lần (3 lần chạy × 2 backend), 5,1% và 11,5% vẫn không đạt được. Chỉ 22,7% là đạt được: 86/378.
- Mục 10.3 chia "5,1% số lần admit có hại" thành 58% / 27% / 15%, tức chia khoảng 3 cặp thành ba phần trăm lẻ.

Đây là dấu hiệu số liệu được sinh ra, không suy từ một bảng đếm. Mọi số projected nên được **sinh từ một bảng đếm giả lập** (số nguyên trên mẫu số đã khai báo) để nhất quán.

### S3 🔴 "Hại nhỏ trong biên θ nên admit là đúng"

Mục 10.3: "58% are low-effect harms: the skill degrades the target slightly, within the benefit margin θ, so admission is technically correct". Tiêu chí admit là STR ≤ −θ, tức **có lợi** ít nhất θ. Một kỹ năng làm xấu đi (STR > 0) thì không bao giờ "admit là đúng": đó chính là sai lầm mà α kiểm soát. Câu này phải bỏ, hoặc viết lại thành: số kỹ năng này được admit là **sai lầm loại I** (trong ngân sách α), hoặc là do dịch chuyển (ξ_s).

### S4 🔴 Nhầm "lỗi lấy mẫu" với ξ_s

"27% are trial-sampling failures … which is the residual ξ_s term of Theorem 4 made concrete". Thử nghiệm rút từ P_s mà không chạm hành vi bị hại là **biến thiên lấy mẫu trong P_s**, phần được α kiểm soát. ξ_s là **khoảng cách giữa P_s và Q_s** (thử nghiệm và triển khai). Muốn quy cho ξ_s thì phải chỉ ra phân phối task khi triển khai khác phân phối thử nghiệm.

### S5 🟠 "Ở cùng mức clean reuse"

Endpoint chính là "harmful acceptance at matched clean-reuse coverage". Bảng 2 so 5,1% (clean reuse 84,3%) với 11,5% (clean reuse 86,0%): hai mức không khớp nhau. Cần báo cáo ở một mức clean reuse chung (ví dụ chỉnh ngưỡng của B6), hoặc bỏ chữ "matched".

### S6 🟠 Hoà vốn ở RQ4

"Admission costs 0.61× a full validation per (skill, scope) cell … break-even against always-retest is 2.4 reuses". Nếu always-retest tốn 1 lần validation mỗi lần dùng, còn admission tốn 0,61 một lần cho mỗi ô, thì hoà vốn ở **dưới 1** lần dùng. Để ra 2,4 phải có chi phí mỗi lần dùng mà bài không nêu. Cần viết công thức chi phí.

### S7 🟠 Bộ máy kiểm định nhiều giả thuyết

Mục 3.3 nói "simultaneous confidence over a finite family and adaptive selection are handled by standard multiple-testing machinery [3, 7]". Nhưng:

- [3] Benjamini–Hochberg kiểm soát **FDR**, còn mục tiêu của bài (Pr[∃ admitted harmful] ≤ α) là **FWER**, và chứng minh dùng hợp cận (Bonferroni).
- [7] Howard et al. là về confidence sequence, không phải kiểm định nhiều giả thuyết.

**Sửa:** trích Bonferroni hoặc hợp cận cho FWER, và Wang & Ramdas 2022 (e-BH) nếu muốn FDR. Giữ BH cho "secondary comparisons BH-corrected".

## 3. Lập luận và trình bày

### N1 🟠 Ví dụ retry/async tự mâu thuẫn

Hình 1 và chứng minh Định lý 7: sau khi S₂ đổi loại ngoại lệ từ X sang X′, "S₁'s handler no longer matches X′ but its bounded retry loop still swallows the failure". Nếu `except X` không khớp X′ thì ngoại lệ **lan ra ngoài**, vòng retry không nuốt được gì. Cách sửa hợp lý:

- S₂ đổi lời gọi thành coroutine, và S₁ bọc lời gọi **chưa được await**: retry "thành công" trên một coroutine object nên lỗi thật không bao giờ được raise; hoặc
- handler của S₁ là `except Exception` với một nhánh `return None` sau khi hết lượt retry.

Ngoài ra, chứng minh toán không nên dựa vào ví dụ này. Dùng construction trừu tượng ở T4.

### N2 🟡 Fingerprint khớp 31/33 mà vẫn qua screen

Hình 1 nói fingerprint khớp 31/33 biến và kỹ năng vẫn qua screen D. Cần nói rõ hai biến lệch là gì, và vì sao Compatible(D, x) vẫn đúng (ví dụ chỉ so một tập con biến "bắt buộc").

### N3 🟡 Từ khoá

"conformal prediction" là keyword, nhưng phương pháp là e-process và Ville; conformal chỉ là công trình liên quan. Thay bằng "e-processes, anytime-valid inference".

### N4 🟠 Trích dẫn

Reading list tự ghi các mục 2026 là "% VERIFY". Các mục có tác giả placeholder hoặc chưa kiểm:

| Mục trong bài | Vấn đề |
|---|---|
| [5] Formal Skill Verification, arXiv:2605.23951 | Tác giả "Authors" |
| [6] GSE, arXiv:2608.06153 | Tác giả "Authors"; đây là baseline quyết định, phải có trích dẫn thật |
| [8] MemCoder, arXiv:2603.13258 | Tác giả "Authors" |
| [9] MemGovern, arXiv:2601.06789 | Tác giả "Authors" |
| [11] TMA-NM | Tác giả "Authors", không có mã arXiv |
| Reading [6] CooperBench, [8] GEM/MemState, [15] ReasoningBank | Tác giả "Authors" |

Các mục kinh điển ([1] LTT, [2] CRC, [3] BH, [4] CaMeL, [7] Howard et al., [10] Progent, [12] Vovk, [13] Voyager, [14] Waudby-Smith & Ramdas; reading: Cameron–Gelbach–Miller, AgentPoison, Monperrus, Weiser, SWE-bench, SWE-bench-Live, OpenHands) có thông tin xuất bản khớp với hiểu biết hiện có. Vẫn nên kiểm qua DBLP / DOI trước khi nộp. Thiếu trích dẫn cho e-BH (Wang & Ramdas 2022) và cho Ville (1939).

### N5 🟠 Tham chiếu tới tài liệu không tồn tại

Banner và summary nhắc `PLAN.md`, `REVIEWS.md`. Mục Data availability mô tả một artifact đầy đủ ("per-task outcomes", "image digests"). Không có tài liệu nào như vậy trong ba tệp được cung cấp hay trong repo. Khi nộp, hoặc đưa vào, hoặc bỏ.

## 4. Đối chiếu với bằng chứng thật của repo

Các số projected của bài cần được thay bằng số đo được, hoặc gỡ bỏ (xem [TRACKING_FSE](../TRACKING_FSE.md), mục 2):

- "Gatekeeper beats simple gates" không được ủng hộ về công suất (đồ thị pha, Study P).
- Hai kỹ năng thử là phép viết lại AST viết tay, không phải kỹ năng "học được": nên thu hẹp thành "frozen code transformations".
- Kết quả âm của Study D đến H (0/2.400 khác biệt) và RQ5 (khác biệt ngây thơ phóng đại 3 đến 15 lần) cần được nêu.

## 5. Những điểm đúng, nên giữ

- Tách quyết định về quyền (capability) khỏi quyết định về chức năng (admission).
- Đòi bằng chứng **có lợi** chứ không chỉ "không hại", và tự báo cáo chi phí của lựa chọn đó.
- E-process cược dự đoán được cộng bất đẳng thức Ville cho từng ô: đúng (repo đã cài và kiểm).
- So với baseline mạnh (B6) chứ không phải B2, và báo cáo cả hai biên độ.
- Báo cáo riêng từng chế độ chuyển giao, không gộp.
- Mệnh đề 6 về ý tưởng là đúng: không có bảo đảm phi phân phối nào cho repo tuỳ ý.

## 9. Phép tính đã chạy lại

```
17.6 - 6.4 = 11.2; 11.2/17.6           = 0.636   ("~64%")        khớp
22.7 - 5.1 = 17.6; 11.5 - 5.1 = 6.4                               khớp
5.1 - 2.4 = 2.7;  3.87/2.02            = 1.92    ("1.9x")        khớp
52.3 - 49.8 = 2.5; 52.3 - 44.1 = 8.2                              khớp
14/68 = 20.6%, 27/74 = 36.5%, 22/38 = 57.9%; 57.9/20.6 = 2.81     khớp
41/46 = 89.1%                                                     khớp
Ablation: 13.9-5.1 = 8.8; 12.6-5.1 = 7.5; 92.1-84.3 = 7.8;
          5.9-5.1 = 0.8; 2.94/2.02 = 1.46; 2.71/2.02 = 1.34       khớp
harmful pairs = 63; 5.1%*63 = 3.2, 11.5%*63 = 7.2, 22.7%*63 = 14.3  KHÔNG nguyên (S2)
d_bar from 11.4% of pairs, 94 skills = 0.114*93 = 10.6 (bài: 0.34)  MÂU THUẪN (T8)
CI lower bound 3.1 < margin 5                                      KHÔNG vượt (S1)
paired variance ratio = 1 + 2*2.1 = 5.2 (bài: 3.1)                 SAI (T6)
```

Các phép tính số học đơn giản đều khớp. Lỗi nằm ở **mô hình** (T6), ở **mẫu số** (S2), ở **diễn giải thống kê** (S1, S3, S4) và ở **toán** (T1 đến T5).
