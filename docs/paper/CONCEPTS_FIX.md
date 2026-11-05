# Sửa chỗ mơ hồ giữa khái niệm, baseline và phương pháp (đề xuất, 0 USD)

*Viết ngày 05/11/2026 sau nhận xét của thầy: "quá mơ hồ giữa các khái niệm, baseline và phương pháp". Mọi việc ở đây là
viết lại và tính lại từ dữ liệu đã có, chạy trên GitHub Actions, không gọi model, không tốn tiền.*

## 1. Chẩn đoán: thầy đúng, và chỗ mơ hồ nằm ngay ở định nghĩa

| # | Chỗ mơ hồ | Bằng chứng trong bài | Vì sao reviewer bắt |
|---|---|---|---|
| M1 | **Bài định nghĩa một đại lượng nhưng thí nghiệm đo một đại lượng khác.** Mục Problem nói cell *admissible* khi STR ≤ −θ (skill **giúp** ít nhất θ). Nhưng ở Study T, T2, U, V, loss là "hành vi khác bản gốc", nên ℓ(x,∅) = 0 luôn luôn, STR ≥ 0, và **không skill nào có thể admissible** theo định nghĩa đó. Thực tế các study dùng Proposition `prop:harm` (tỉ lệ đổi hành vi < η), là một giả thuyết khác | `sections/problem.tex` (Definition STR), `sections/theory.tex:31` (prop:harm "used in the experiments"), `tools/market_analyze.py` `gatekeeper()` chỉ dùng chứng nhận hại | Phương pháp được chứng minh cho bài toán A, thực nghiệm chạy bài toán B |
| M2 | **"Gatekeeper" là ba quy tắc khác nhau.** Studies D–H: min(e-process lợi ích, chứng nhận hại) + e-Holm. Study T/T2/V: chỉ chứng nhận hại + e-Holm. T2/U còn có G-FDR (e-BH) | `theory.tex:103–108`, `market_analyze.py` | Không rõ "phương pháp của bài" là cái nào |
| M3 | **"Skill" có bốn nghĩa.** Định nghĩa: bộ năm ⟨π, D, I, P, K⟩. Study T: một rule autofix của Ruff (không có D, I, P). Study U: một bản vá của agent cho một issue (không tái sử dụng). B9: model tự viết lại hàm | `problem.tex`, `evaluation.tex` | Bản vá SWE-bench không phải skill tái sử dụng |
| M4 | **"Context / task / draw" lẫn nhau.** Định nghĩa: context = (repo, revision, environment, task). Thí nghiệm: một draw = một input sinh ra cho một hàm | `problem.tex` | Không rõ phép thử độc lập là gì, i.i.d. trên cái gì |
| M5 | **Baseline là một "vườn thú" không có trục so sánh.** U, RS, B6-R, B6-strong, B6-majority, LJ, S20, FS, B8, TS, B9, G, G-FDR; tên khác với B1–B9 của bài FSE gốc; TS vừa là baseline vừa là oracle; B9 không phải quy tắc nhận mà là một hành động khác | `evaluation.tex`, `tab:market` | Không biết mỗi baseline đại diện cho giả thuyết nào |
| M6 | **Ground truth và phương pháp dùng chung một công cụ đo** (cùng harness sinh input, chỉ khác seed) | Study T, T-A1 | Dễ bị xem là vòng tròn; T-A4 (test suite) mới là oracle độc lập đầu tiên |

## 2. Phương án cứu vãn: một bài toán, một phương pháp, một bảng baseline

### 2.1 Thu hẹp và gọi đúng tên bài toán (sửa M1, M3, M4)

**Bài toán (duy nhất):** *nhận có kiểm soát rủi ro một phép biến đổi mã tái sử dụng được* (reusable code transformation)
vào một đích cụ thể.

| Khái niệm | Định nghĩa duy nhất trong bài | Trong Study T đo bằng |
|---|---|---|
| Skill | Phép biến đổi mã tất định π, kèm footprint K (vùng mã π đọc/ghi) | Một rule autofix của Ruff, hoặc một họ R2 |
| Đích (target) | Một phiên bản package + môi trường (fingerprint: Python, `pip freeze`) | 60 + 140 package PyPI |
| Cell | (skill, đích) | 1.559 + 3.626 cell dùng được |
| Draw | Một input sinh ngẫu nhiên cho một hàm π chạm vào, chạy trên bản gốc và bản đã biến đổi | 200–240 draw mỗi luồng |
| Hại của một cell | h = tỉ lệ draw mà hành vi (giá trị trả về, ngoại lệ) khác bản gốc | Luồng tham chiếu, seed riêng |
| Cell có hại | h ≥ η (η = 5%) | 12 (T), 29 (T2) |
| Nhận (admit) | Chứng nhận hại đạt K/α (Prop. `prop:harm`) và e-Holm trên mọi cell | — |
| Bảo đảm | P(tồn tại cell được nhận có h ≥ η) ≤ α trên cả thư viện | α = 0,1 |
| Retirement | Fingerprint đổi thì chứng nhận hết hạn, chứng nhận lại ở epoch k với phần α·6/(π²(k+1)²) | Study V |

- Định lý chính viết lại cho đúng giả thuyết này. Đây là trường hợp riêng của Theorem `thm:admission` với "hại ≥ η" thay cho "không admissible", và chứng minh đã có sẵn (`prop:harm`, `rem:eholm`).
- STR với lợi ích −θ chuyển thành một mục "mở rộng": cùng máy móc, áp cho loss có lợi ích. Bài không tuyên bố đã kiểm thực nghiệm phần này.

### 2.2 Một phương pháp, một khung thuật toán (sửa M2)

Gatekeeper trong bài chỉ còn **một** quy tắc chính, đúng như code đã chạy ở T, T2, V:

1. **Census:** tìm mọi cell (skill có site trên đích).
2. **Paired trials:** mỗi draw chạy bản gốc và bản đã biến đổi trên cùng input; hai luồng có seed riêng.
3. **Chứng nhận hại** (`prop:harm`) cộng báo động sớm; dừng khi đạt K/α, khi báo động, hoặc khi hết ngân sách.
4. **e-Holm** trên mọi cell → FWER ≤ α.
5. **Execution rule:** chỉ chạy tổ hợp khi mỗi thành phần liên thông của footprint đã được nhận.
6. **Retirement:** fingerprint đổi thì chứng nhận lại ở epoch mới.

G-FDR (e-BH) là **biến thể có bảo đảm yếu hơn** (FDR), luôn ghi rõ như vậy. Quy tắc min(lợi ích, hại) của Studies D–H chuyển
sang phần mở rộng hoặc phụ lục.

### 2.3 Bảng baseline theo nguồn bằng chứng (sửa M5, M6)

Mỗi baseline trả lời một câu hỏi: *"nếu thay bằng loại bằng chứng này thì sao?"*

| Nhóm bằng chứng | Baseline | Tên trong bài FSE gốc | Có chạy trên đích? | Bảo đảm thống kê |
|---|---|---|---|---|
| Không có bằng chứng | U: áp dụng hết | B2 | Không | Không |
| Nhãn của nhà cung cấp | RS: nhãn *safe* của Ruff | — | Không | Không |
| Bằng chứng ở nguồn (replay) | B6-R: ví dụ tài liệu; **B6-strong: replay trên mọi package khác** | B5/B6 | Không | Không |
| Phán đoán tĩnh | LJ: LLM đọc diff | — | Không | Không |
| Bằng chứng trên đích, không có bảo đảm | S20 (smoke 20 draw), B8 (thử lại mọi draw), **TS (test suite của chính package = "CI xanh")** | B8 | Có | Không |
| Bằng chứng trên đích, có bảo đảm | FS (mẫu cố định, Bonferroni) | — | Có | FWER |
| **Phương pháp của bài** | **G (chứng nhận hại + e-Holm)**, G-FDR | Gatekeeper | Có | FWER / FDR |

- **B9 (để model tự sửa)** không phải quy tắc nhận mà là một hành động thay thế, nên được so ở một RQ riêng về chi phí và hại.
- **Test suite** có hai vai trò, tách ở hai chỗ: là baseline TS trong bảng chính, và là oracle độc lập trong mục Validity (sửa M6).

### 2.4 Giữ và bỏ study

| Giữ (đúng bài toán trên) | Chuyển phụ lục hoặc bỏ |
|---|---|
| T, T2 (chính); V (retirement); TS (baseline + oracle độc lập); B9; R2/S (tổ hợp, execution rule) | D, E, G, H, P, Q (dùng định nghĩa khác: test suite, lợi ích, harm của bản vá) |
| U chỉ giữ như *stress test* của quy tắc quyết định khi hại hiếm, ghi rõ "bản vá không phải skill" | Phase diagram và mô phỏng: giữ một hình minh hoạ lý thuyết |

## 3. Mượn gì từ to-do của dự án anh em (FSE-2027-13), vẫn 0 USD

1. **Quy tắc R1–R5 và `glossary.md`, `number_provenance.md`.** Mỗi thuật ngữ có đúng một định nghĩa, mỗi con số có nguồn. Bài của mình đã có kiểm tra số tự động (87 claim); còn thiếu bảng thuật ngữ.
2. **Lý do vì sao chứng nhận "không hại" chứ không phải "có lợi"**, lấy từ dữ liệu công khai mà dự án anh em đã phân tích:
   - SWE-Skills-Bench: 92/98 skill không có tác dụng đáng kể, SD thật của hiệu ứng chỉ khoảng 0,03.
   - Chứng nhận lợi ích theo từng (skill, scope) với θ nhỏ cần ≥ 576 task mỗi ô, trong khi scope lớn nhất chỉ có 157.
   - G1 của họ FAIL vì "lời nguyền người thắng".

   Đây là động cơ có số liệu cho cách thu hẹp ở mục 2.1. Phải tái lập phân tích đó trong repo này (dữ liệu MIT, chạy trên
   Actions) và trích dẫn đúng bài gốc, không chép số.
3. **Định vị khiêm tốn:** ý tưởng anytime-valid cho skill đã có ở Qu et al. 2026. Bài không nói "đầu tiên"; đóng góp là bảo đảm toàn thư viện, footprint/execution rule cho tổ hợp, retirement theo epoch, và so sánh trên quy mô thị trường thật.

## 4. Việc cần làm (đều miễn phí), theo thứ tự

1. Thầy duyệt bảng khái niệm (2.1), phương pháp (2.2) và bảng baseline (2.3).
2. Viết lại `problem.tex` và `approach.tex` theo 2.1 và 2.2; đưa định lý chính về giả thuyết hại.
3. Bảng 1 trong bài: thuật ngữ → định nghĩa → cách đo. Bảng 2: baseline theo nguồn bằng chứng.
4. Tái cấu trúc `evaluation.tex`: RQ1 so baseline (T, T2), RQ2 oracle độc lập (TS), RQ3 B9, RQ4 retirement (V), RQ5 tổ hợp (R2/S); phần còn lại vào phụ lục.
5. Tái lập phân tích SWE-Skills-Bench trên Actions để làm động cơ, nếu thầy đồng ý.
6. Cập nhật kiểm tra số tự động cho mọi câu mới.

## 5. Rủi ro còn lại (nói thẳng)

- Thu hẹp làm bài **khiêm tốn hơn**: chứng nhận "không đổi hành vi" của phép biến đổi tất định, không phải "skill của agent có ích".
- Ground truth vẫn dựa trên input sinh tự động. TS (chạy lại sau T-A4a) là oracle độc lập duy nhất.
- W3 (chi phí) vẫn thua: khi hại hiếm, chứng nhận dùng gần hết ngân sách.
- Study V không có ô nào đổi trạng thái: retirement đúng về lý thuyết nhưng chưa có ví dụ thật bắt được lỗi.
