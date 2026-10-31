# Lý thuyết của bài FSE-2027-13: phát biểu đúng, chứng minh, kiểm bằng số

Bản thảo ([`source/01-FSE-2027-13-paper.pdf`](source/01-FSE-2027-13-paper.pdf)) do AI sinh. File này làm lại phần lý thuyết từ đầu:

- với mỗi ý, nêu **bài viết gì**, **sai hoặc thiếu ở đâu**, **phát biểu đúng**, **chứng minh đầy đủ** và **phép kiểm bằng số**;
- danh sách lỗi ngắn gọn ở [PAPER_AUDIT](PAPER_AUDIT.md); file này là bản chi tiết;
- phép kiểm bằng số: [`tools/theory_checks.py`](../../tools/theory_checks.py), chạy trên GitHub Actions bằng workflow `Gatekeeper theory checks`; kết quả ở [`research_closure/results/theory/`](../../research_closure/results/theory/).

**Mục tiêu "để thắng":** giữ những ý đúng và mạnh của bài, sửa những chỗ sai sao cho người phản biện không bắt được, và biến hai chỗ yếu (Định lý 7, Remark 5) thành kết quả **chặt** (tight), mạnh hơn bản gốc.

---

## 0. Mô hình và ký hiệu

| Ký hiệu | Nghĩa |
|---|---|
| S = ⟨π, D, I, P, K⟩ | kỹ năng: thủ tục π, fingerprint D, điều kiện I, hậu điều kiện P, footprint K |
| s ∈ 𝒮 = {s₁, …, s_L} | phạm vi, một phân hoạch các ngữ cảnh được khai báo trước |
| c = (S, s) | một **ô**; ô tổ hợp c = (S∘S′, s) cũng là một ô |
| P_s, Q_s | phân phối ngữ cảnh lúc **thử nghiệm** và lúc **triển khai** trong phạm vi s |
| ℓ(x, π), ℓ(x, ∅) ∈ [0, 1] | loss của task x khi có / không có kỹ năng (**phải chặn tại 1**, xem T9 của PAPER_AUDIT) |
| Z = ℓ(x, π) − ℓ(x, ∅) ∈ [−1, 1], Y = −Z | hiệu ghép cặp |
| STR_P(c) = E_{x∼P_s}[Z] | rủi ro chuyển giao chọn lọc |
| θ > 0 | biên lợi ích; admit nghĩa là khẳng định STR ≤ −θ |

**Giả định A (thử nghiệm).** Với mỗi ô c tồn tại một dãy vô hạn task x₁ᶜ, x₂ᶜ, … i.i.d. theo P_s. Thủ tục đọc dãy này theo thứ tự; các ô khác nhau có thể phụ thuộc nhau.

> Ghi chú: tập task của một repo là hữu hạn. Giả định A đúng nếu rút **có hoàn lại**; nếu rút không hoàn lại phải dùng e-process cho quần thể hữu hạn. Bài phải nói rõ là dùng cách nào.

**Giả định B (dịch chuyển bị chặn).** TV(P_s, Q_s) ≤ ξ_s, với TV(P, Q) = sup_A |P(A) − Q(A)|.

---

## 1. Bổ đề 1: e-process cược là hợp lệ cho từng ô

**Phát biểu.** Xét giả thuyết không H₀ᶜ: E[Y] ≤ θ (tức STR_P(c) ≥ −θ, kỹ năng **không** đạt biên lợi ích). Đặt

  K₀ = 1, K_n = ∏_{i≤n} (1 + λ_i (Y_i − θ)),

với λ_i chỉ phụ thuộc Y₁, …, Y_{i−1} (dự đoán được) và λ_i ∈ [0, 1/(1+θ)). Khi đó dưới H₀ᶜ, với mọi β ∈ (0, 1):

  Pr[∃ n: K_n ≥ 1/β] ≤ β.

**Chứng minh.**
1. *Không âm:* Y_i ≥ −1 nên Y_i − θ ≥ −(1+θ), suy ra 1 + λ_i(Y_i − θ) > 1 − λ_i(1+θ) > 0.
2. *Siêu martingale:* gọi ℱ_{i−1} là thông tin đến bước i−1. Vì λ_i là ℱ_{i−1}-đo được và Y_i độc lập với quá khứ (Giả định A),
   E[K_i | ℱ_{i−1}] = K_{i−1}(1 + λ_i(E[Y_i] − θ)) ≤ K_{i−1}, do E[Y_i] ≤ θ và λ_i ≥ 0.
3. *Ville:* với siêu martingale không âm có K₀ = 1, bất đẳng thức Ville (1939) cho Pr[sup_n K_n ≥ 1/β] ≤ β. ∎

**Hệ quả.** Quy tắc "admit khi K_n ≥ 1/β" có xác suất admit sai ≤ β **ở mọi thời điểm dừng**, kể cả khi dừng phụ thuộc dữ liệu hay hết ngân sách. Đây là lý do dùng e-process thay cho khoảng tin cậy cỡ mẫu cố định.

**Kiểm bằng số (C1):** e-process của repo (`gatekeeper_lite/eprocess.py`), ở đúng biên H₀ (E[Y] = θ = 0,1), α = 0,1, n = 300 bước: tỉ lệ admit sai ≈ 5,7% ≤ 10%.

---

## 2. Định lý 4 (đã sửa): bảo đảm cho cả thư viện

### Bài viết gì, sai ở đâu

Bài cấp ngân sách α_s **cho mỗi phạm vi**, Σ_s α_s ≤ α, và mọi kỹ năng trong phạm vi s dùng ngưỡng 1/α_s. Kết luận: Pr[∃ admitted (S, s): STR_{Q_s} > −θ + ξ_s] ≤ α.

Có ba lỗi:
- **(a) Ngân sách sai đơn vị.** Hợp cận phải lấy trên **ô**. Với L_s kỹ năng trong một phạm vi, sai số có thể lên tới L_s·α_s. **Kiểm bằng số (C2):** 10 kỹ năng dùng chung ngưỡng 1/0,1 cho tỉ lệ admit sai cho cả họ là **48%**, không phải ≤ 10%; chia α/10 cho mỗi ô cho 4%.
- **(b) Admit lại và tổ hợp không được tính** vào ngân sách.
- **(c) Hằng số dịch chuyển** phải là 2ξ_s, không phải ξ_s (C3).

### Phát biểu đúng

**Định lý 4′.** Cho một tập ô 𝒞 (đếm được, gồm cả ô tổ hợp) và một sổ cái α được **cấp trước**: α_{c,k} ≥ 0 cho ô c ở epoch k (k = 0 là lần admit đầu, k ≥ 1 là admit lại sau retirement), với

  Σ_{c∈𝒞} Σ_{k≥0} α_{c,k} ≤ α.

(Ví dụ: α_{c,k} = α_c · 6/(π²(k+1)²) với Σ_c α_c ≤ α, như trong `AlphaLedger` của repo.)

Mỗi epoch dùng một dãy task mới, và thủ tục chỉ admit c ở epoch k khi e-process của Bổ đề 1 cho epoch đó vượt 1/α_{c,k}. Thủ tục được tự do chọn ô nào để thử, thứ tự thử và lúc dừng, theo bất kỳ cách nào phụ thuộc dữ liệu. Dưới Giả định A, B:

  Pr[∃ (c, k) được admit: STR_{Q_s}(c) > −θ + 2ξ_s] ≤ α.

Đặc biệt, nếu 2ξ_s < θ với mọi s, thì Pr[∃ ô có hại (STR_Q > 0) được admit] ≤ α. Đây chính là mục tiêu của bài toán admission ở mục 4 của bài.

### Chứng minh

1. *Sự kiện tiềm năng.* Với mỗi (c, k), gọi A_{c,k} = {sup_n K_n^{c,k} ≥ 1/α_{c,k}}, tính trên **toàn bộ** dãy vô hạn của epoch đó, kể cả khi thủ tục không bao giờ đọc hết.
2. *Admit sai kéo theo sự kiện tiềm năng.* Nếu thủ tục admit (c, k) thì ở một thời điểm nào đó K_n^{c,k} ≥ 1/α_{c,k}, nên A_{c,k} xảy ra. Việc chọn ô hay dừng thích nghi chỉ **bỏ bớt** cơ hội admit, không tạo thêm. Vì vậy

   {admit sai} ⊆ ∪_{(c,k) với H₀ᶜ đúng} A_{c,k}.
3. *Hợp cận.* Bổ đề 1 cho Pr[A_{c,k}] ≤ α_{c,k} với mọi (c, k) mà H₀ᶜ đúng. Hợp cận không cần độc lập:

   Pr[∃ admit sai dưới P] ≤ Σ α_{c,k} ≤ α.
4. *Chuyển sang Q (Bổ đề 2 bên dưới).* |STR_{Q_s}(c) − STR_{P_s}(c)| ≤ 2ξ_s. Nếu STR_{Q_s}(c) > −θ + 2ξ_s thì STR_{P_s}(c) > −θ, tức H₀ᶜ đúng. Theo bước 3, xác suất admit một ô như vậy ≤ α. ∎

**Bổ đề 2 (dịch chuyển).** Với f: 𝒳 → [a, a+b], ta có |E_Q f − E_P f| ≤ b · TV(P, Q). Áp dụng cho Z ∈ [−1, 1] (b = 2): |STR_Q − STR_P| ≤ 2·TV ≤ 2ξ.

*Chứng minh.* Đặt g = f − a − b/2, nên |g| ≤ b/2 và E_Q f − E_P f = E_Q g − E_P g. Khi đó |E_Q g − E_P g| ≤ (b/2) Σ|Q(x) − P(x)| = (b/2) · 2·TV = b·TV. (Trường hợp liên tục: thay tổng bằng tích phân.) ∎

**Tính chặt.** Lấy hai loại task, a có Z = +1 và b có Z = −1, với P(a) = 0,1 và Q(a) = 0,2. Khi đó TV = 0,1 và |STR_Q − STR_P| = 0,2 = 2·TV, nên hằng số 2 không giảm được (C3). Trên 20.000 phân phối ngẫu nhiên, tỉ số lớn nhất là 1,59 ≤ 2.

---

## 3. Mệnh đề 6 (đã sửa) và tính cần thiết của ξ: biến Remark 5 thành định lý

### Bài viết gì, sai ở đâu

Bài phát biểu: "với mọi α < 1 tồn tại R† ∉ R_obs và S được admit với STR(S, {R†}) = 1". Có ba vấn đề:
- α không xuất hiện trong kết luận;
- thiếu điều kiện "thủ tục admit S với xác suất dương";
- mệnh đề chỉ nói về thủ tục **không** thử trên đích, trong khi Gatekeeper có thử trên đích. Remark 5 nói ξ_s là "cần thiết" nhưng không chứng minh.

### Phát biểu đúng (hai phần)

**Giả định C (lớp repo đủ giàu).** Với mọi bộ đặc trưng mà thủ tục quan sát được (fingerprint, vị từ, kết quả thử nghiệm trên R_obs), tồn tại một repo có đúng các đặc trưng đó mà loss của mọi task là tuỳ ý trong [0, 1].

**Mệnh đề 6′(a) (không thử trên đích thì không có bảo đảm).** Cho một thủ tục mà quyết định là hàm (có thể ngẫu nhiên) của dữ liệu từ R_obs, và một kỹ năng S được admit với xác suất dương. Dưới Giả định C tồn tại R† ∉ R_obs với STR(S, {R†}) = 1, mà xác suất admit S **không đổi**.

*Chứng minh.* Theo Giả định C, chọn R† trùng với dữ liệu quan sát được và có ℓ(x, π) = 1, ℓ(x, ∅) = 0 với mọi task x của R†. Phân phối của dữ liệu mà thủ tục đọc không đổi, nên xác suất admit không đổi và dương. Trên R†, Z ≡ 1, nên STR = 1. ∎

**Mệnh đề 6′(b) (số hạng dịch chuyển là cần thiết và chặt).** Với mọi θ ∈ (0, 1), δ > 0 với θ + δ < 1, mọi ξ ∈ (0, 1/2] và mọi thủ tục, tồn tại một phạm vi với cặp phân phối (P, Q), TV(P, Q) = ξ, và một ô c sao cho:
- STR_P(c) = −θ − δ (có lợi rõ ràng dưới P);
- STR_Q(c) = STR_P(c) + 2ξ;
- xác suất thủ tục admit c không phụ thuộc Q.

*Chứng minh.* Lấy hai loại task: u có Z = +1 và d có Z = −1. Đặt P(d) = (1 + θ + δ)/2, nên E_P Z = −θ − δ. Vì P(d) ≥ 1/2 ≥ ξ, ta lấy Q bằng cách chuyển khối lượng ξ từ d sang u: TV(P, Q) = ξ và E_Q Z − E_P Z = ξ·(1 − (−1)) = 2ξ. Thủ tục chỉ đọc task rút từ P (Giả định A), nên phân phối dữ liệu và xác suất admit không đổi. ∎

**Ý nghĩa.** Không thủ tục nào chỉ dùng dữ liệu từ P có thể bảo đảm về STR_Q tốt hơn STR_P + 2ξ. Vì vậy số hạng 2ξ_s trong Định lý 4′ là **không bỏ được và chặt**. Đây là phiên bản chặt của Remark 5 và là một **đóng góp có thể nêu**: bài gốc chỉ khẳng định suông.

---

## 4. Định lý 7 (đã sửa): rủi ro của tổ hợp, phát biểu chặt

### Bài viết gì, sai ở đâu

Bài viết: "∀ε > 0 ∃ S₁, S₂ với STR(S₁), STR(S₂) ≤ −θ và STR(S₁∘S₂) ≥ 1 − ε", và "không có g nào". Cả hai sai:
- STR(S₁) ≤ −θ kéo theo E ℓ(∅) ≥ θ, nên STR(S₁∘S₂) ≤ 1 − θ;
- g(a, b) = 1 + min(a, b) **là** một cận đúng.

### Phát biểu đúng

**Định lý 7′.** Với a, b ∈ [−1, 0), đặt 𝒢(a, b) là tập mọi bộ (S₁, S₂, s) có STR(S₁) = a và STR(S₂) = b. Khi đó

  sup_{𝒢(a,b)} STR(S₁∘S₂) = 1 + min(a, b), và sup đạt được.

Hệ quả: hai kỹ năng cùng đạt biên −θ có thể ghép thành STR = 1 − θ > 0. Không có cận nào **tốt hơn** cận hiển nhiên do ℓ ∈ [0, 1], nên rủi ro riêng lẻ không cho thông tin gì có ích về tổ hợp.

*Chứng minh.*
- **Cận trên (với mọi bộ):** STR(S₁∘S₂) = E ℓ(π₁∘π₂) − E ℓ(∅) ≤ 1 − E ℓ(∅). Vì STR(S₁) = E ℓ(π₁) − E ℓ(∅) = a và E ℓ(π₁) ≥ 0, ta có E ℓ(∅) ≥ −a. Tương tự E ℓ(∅) ≥ −b. Vậy E ℓ(∅) ≥ −min(a, b) và STR(S₁∘S₂) ≤ 1 + min(a, b).
- **Đạt được:** lấy loss hằng: ℓ(∅) = c := −min(a, b) ∈ (0, 1], ℓ(π₁) = c + a ≥ 0, ℓ(π₂) = c + b ≥ 0, ℓ(π₁∘π₂) = 1. Khi đó STR(S₁) = a, STR(S₂) = b, STR(S₁∘S₂) = 1 − c = 1 + min(a, b). ∎

**Kiểm bằng số (C4):** 20.000 bộ loss ngẫu nhiên: 0 vi phạm cận; construction với θ = 0,1 cho STR tổ hợp 0,9 = 1 − θ.

### Hệ quả 8 (đã sửa) và một giả định bài thiếu

Bài chỉ sàng lọc các cặp có footprint **giao nhau**. Điều đó chỉ đúng nếu các cặp **không** giao nhau thì không tương tác. Định lý 7′ không phụ thuộc footprint: construction trên không nói gì về vị trí các chỉnh sửa. Vì vậy cần một giả định riêng.

**Giả định D (không tương tác khi footprint rời nhau).** Nếu K ∩ K′ = ∅ thì với mọi x:
  ℓ(x, π∘π′) − ℓ(x, ∅) = [ℓ(x, π) − ℓ(x, ∅)] + [ℓ(x, π′) − ℓ(x, ∅)].

**Hệ quả 8′.** Dưới Giả định D, nếu S, S′ có footprint rời nhau và cùng đạt STR ≤ −θ, thì STR(S∘S′) ≤ −2θ: tổ hợp tự động đạt biên, khỏi phải kiểm. Khi đó chỉ cần kiểm các cặp giao nhau, và số cặp phải kiểm là |L_s| · d̄ / 2, với d̄ là số bạn giao nhau trung bình.

*Chứng minh.* Lấy kỳ vọng hai vế của Giả định D. ∎

**Bài phải sửa:**
1. nêu Giả định D, vì đây là giả định, không phải định lý;
2. đo xem nó có đúng trên dữ liệu không (ví dụ chạy một mẫu cặp rời nhau);
3. sửa số: 11,4% cặp giao nhau trên 94 kỹ năng cho d̄ ≈ 10,6, không phải 0,34 (C7).

---

## 5. Mệnh đề 9 (đã sửa): lợi ích của ghép cặp

**Phát biểu chung, không cần mô hình.** Gọi V_π = Var ℓ(x, π), V_∅ = Var ℓ(x, ∅) và C = Cov(ℓ(x, π), ℓ(x, ∅)) trên cùng một task.
- Ghép cặp: Var(Z) = V_π + V_∅ − 2C.
- Không ghép cặp, hai nhánh độc lập, mỗi nhánh n task: phương sai của hiệu trung bình là (V_π + V_∅)/n.
- Tỉ số

  R = (V_π + V_∅) / (V_π + V_∅ − 2C).

**Trường hợp mô hình cộng tính** ℓ(∅) = T, ℓ(π) = T + S, với T, S độc lập, Var T = σ_T², Var S = σ_S²: ta có V_π + V_∅ = 2σ_T² + σ_S² và C = σ_T², nên **R = 1 + 2σ_T²/σ_S²**. Bài viết 1 + σ_T²/σ_S² là sai.

**Đếm lần chạy.** Cả hai thiết kế đều tốn hai lần chạy cho mỗi "task" (một có, một không kỹ năng), nên lợi ròng **bằng R**. Phép chia đôi "1,55×" của bài là sai.

**Từ phương sai tới số task.** Với kiểm định cỡ mẫu cố định (xấp xỉ chuẩn), số task cần thiết tỉ lệ với phương sai, nên tỉ số số task bằng R. Với e-process cược, thời gian dừng kỳ vọng cũng tăng theo phương sai trên bình phương khoảng cách (Waudby-Smith & Ramdas 2024). Bài chỉ nên phát biểu "cùng bậc", không đưa hằng số chính xác.

**Kiểm bằng số (C5):** với σ_T²/σ_S² = 2,1, mô phỏng 200.000 task cho R = 5,20 (công thức đúng 5,2; công thức của bài 3,1).

---

## 6. Các chỗ cần nói rõ thêm (không sai nhưng dễ bị bắt)

1. **Mục tiêu và bảo đảm phải khớp.** Bài toán admission kiểm soát Pr[∃ admit có hại], tức STR_Q > 0. Định lý 4′ chỉ cho điều đó khi 2ξ_s < θ. Phải nói rõ: nếu phạm vi thô (ξ lớn) thì bảo đảm gần như vô nghĩa. Bài có nhắc ở Threats nhưng không gắn với điều kiện 2ξ < θ.
2. **ξ_s không đo được trực tiếp.** Hoặc coi ξ_s là tham số khai báo, báo cáo bảo đảm như một hàm của ξ_s; hoặc ước lượng bằng một tập kiểm riêng (cận trên của TV từ mẫu là khó; nên dùng cách đầu).
3. **Biên lợi ích và "có hại".** H₀ của e-process là "không đạt lợi ích θ", nên bảo đảm là về admit một kỹ năng **không đủ lợi**, chặt hơn "có hại". Đây là điểm mạnh, nên nêu rõ.
4. **Loss chặn tại 1** (đã có trong mã: `gatekeeper_lite/runner.py`) và rút task có hoàn lại (Giả định A).
5. **FWER chứ không phải FDR.** Hợp cận cho FWER. Nếu muốn nhiều admit hơn, có thể dùng e-BH (Wang & Ramdas 2022) cho FDR, nhưng khi đó phải đổi mục tiêu.

---

## 7. Bài nên khẳng định gì (phiên bản "thắng")

| Khẳng định | Trạng thái |
|---|---|
| Bảo đảm cho cả thư viện ở mọi thời điểm dừng, với sổ cái α theo ô gồm cả admit lại và tổ hợp (Định lý 4′) | **Đúng, có chứng minh**; mạnh hơn bản gốc vì bao cả retirement |
| Số hạng 2ξ là cần thiết và chặt (Mệnh đề 6′b) | **Mới, có chứng minh**; thay cho Remark 5 nói suông |
| Không có bảo đảm phi phân phối khi không thử trên đích (Mệnh đề 6′a) | Đúng dưới Giả định C, nêu rõ |
| Rủi ro tổ hợp: cận chặt 1 + min(a, b) (Định lý 7′) | **Đúng và chặt**; thay cho bản gốc sai |
| Chỉ cần kiểm cặp giao nhau | **Chỉ đúng dưới Giả định D**; phải nêu và đo |
| Ghép cặp giảm số task R lần, R = (V_π + V_∅)/(V_π + V_∅ − 2C) | Đúng; bỏ "1,55×" |
| "Gatekeeper mạnh hơn kiểm định cỡ mẫu cố định" | **Bỏ**: đồ thị pha và Study P cho thấy ngược lại về công suất |

---

## 8. Bảng kiểm bằng số

Chạy: `python tools/theory_checks.py OUT --reps 2000` (workflow `Gatekeeper theory checks`, 0 USD).

| Kiểm | Ý | Kỳ vọng |
|---|---|---|
| C1 | Bổ đề 1 | tỉ lệ admit sai ≤ α |
| C2 | Định lý 4′, lỗi (a) | chung ngưỡng theo phạm vi: > α; chia theo ô: ≤ α |
| C3 | Bổ đề 2 | tỉ số đúng bằng 2 ở ví dụ; ≤ 2 trên mẫu ngẫu nhiên |
| C4 | Định lý 7′ | 0 vi phạm; construction đạt 1 − θ |
| C5 | Mệnh đề 9 | R ≈ 1 + 2σ_T²/σ_S² |
| C6 | Sổ cái α | tổng ≤ 1 |
| C7 | Hệ quả 8 | số của bài **không** khớp (kỳ vọng held = False) |

## Tài liệu tham khảo cần thêm vào bài

- Ville, J. (1939). *Étude critique de la notion de collectif.* Gauthier-Villars.
- Wang, R., & Ramdas, A. (2022). False discovery rate control with e-values. *JRSS-B*, 84(3), 822–852.
- Waudby-Smith, I., & Ramdas, A. (2024). Estimating means of bounded random variables by betting. *JRSS-B*, 86(1), 1–27 (đã có).
- Ramdas, A., Grünwald, P., Vovk, V., & Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. *Statistical Science*, 38(4), 576–601.
