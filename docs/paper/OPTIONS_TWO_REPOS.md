# Ba phương án đi tiếp, dựa trên cả hai repo (06/11/2026)

*Đã đọc: repo `gatekeeper` (commit `d98db9a`): `CLAUDE.md`, `TODO.md`, `docs/direction_final.md`, `paper_plan.md`,
`paper_argument.md`, `paper_review_e2e.md`, `p6_review.md`, `novelty_review.md`, `plan_replication.md`,
`plan_scope_measured.md`, `preregistration_main.md` §1–§22, `results/sskb_probe.json`, `paper/main.tex`, và paper FSE gốc
(`docs/01-FSE-2027-13-paper.pdf`). Repo này (`-gatekeeper-p6`): toàn bộ kết quả T, T2, U, V, TS, B9 và
`docs/paper/CONCEPTS_FIX.md`. Mọi con số dưới đây chép từ các file đó, chưa chạy lại.*

## 1. Paper gốc kỳ vọng gì, và hai repo đã cho gì

| Kỳ vọng của paper FSE gốc (số "projected", chưa chạy) | Repo `gatekeeper` (skill mức agent, SWE-bench, Gemini) | Repo `p6` (phép biến đổi mã tất định, PyPI) |
|---|---|---|
| Admit khi skill **có lợi** so với không skill (STR ≤ −θ); "benefit, not harmlessness" | **Không chứng nhận được skill thật nào.** G1 FAIL; E1: 6 skill × 40 task × 3 seed, mọi CI chứa 0; E2 (XRepoSkill, 109 task Live × 3 seed): +2,1 điểm, CI [−1,0; +5,3]. Chỉ đối chứng dương nhân tạo T4 được admit (trial 20, +0,55) | Đo **hại**, không đo lợi (mâu thuẫn định nghĩa M1 trong `CONCEPTS_FIX.md`) |
| RQ1: thắng replay + fingerprint (B6) 6,4 điểm | So trên placebo A/A: plug-in nhận nhầm 0,46 (0,80 khi nhìn liên tục); GEPA nhận 14% đề xuất no-op; MH của XRepoSkill 0,025 → 0,111 khi nhìn liên tục; Gatekeeper 0,003 | B6-R nhận 9/11 (T) và 17/20 (T2) ô có hại; B6-strong 2 và 4; G 0 và 0. Nhưng smoke 20 draw chỉ bỏ sót 0 (T) và 1 (T2) |
| RQ2: bắt tổ hợp có hại 41/46 | Phản ví dụ chạy được (Định lý 7′), không có dữ liệu thật | 2 cặp file rời footprint mà không giao hoán (R2); không đo tác hại |
| RQ3: B9 (thử lại cùng ngân sách) | — | B9 ở 3 mức model gây hại 9–11 ô (khoảng 7%), đắt hơn G 26–87 lần |
| RQ4: retirement, chi phí | Thu hồi hai bước trên plasmode: thu hồi nhầm 0/1.000, độ trễ 75 trial | Study V (Python 3.12 → 3.13): 0 ô đổi trạng thái; retirement chỉ tốn chi phí. W3 (chi phí) thua ở T và T2 |
| — | **Mới, không có trong paper gốc:** mức nhiễu nền khi chạy lại (7/13 mức tăng đã công bố của XRepoSkill và MemGovern nằm trong nhiễu); quy lỗi của Dong et al. cho số ứng viên như placebo (R = 1,08 [0,68; 1,75]); auditor LLM đổ lỗi cho skill giả 100% (Flash-Lite), 12–20% (Flash, Pro); phép trừ placebo có chứng minh, kiểm định hoán vị mức 0,042, độ nhạy 0,72–0,93 | **Mới:** quy mô thị trường thật (200 dự án chọn trước, 198 có kết quả; 5.185 ô dùng được); hại hiếm nhưng không tất định; TS (lần 1): test suite của package nhận cả 3/3 ô có hại |
| — | **Phép thử §22** (đang chạy, 39/40 lần chạy, 0,997 USD): `viper-configuration` D = +0,015 (họ công bố +17,7 điểm) → **không lặp lại**; `asyncio-patterns` D = −0,126 trên 9 yêu cầu (họ công bố −17,0) → **lặp lại chiều hại**. G ≈ 0,07 < 0,10, nên theo quy tắc đã đăng ký, gần chắc **dừng** track C | — |

**Đọc trung thực:** kỳ vọng trung tâm của paper gốc ("chứng nhận skill có lợi, theo scope, thắng B6") **không đạt được ở mức
agent**, vì tác dụng thật của skill nhỏ hơn nhiễu chạy lại. Điều hai repo làm được chắc chắn là **đo**: (a) các quy tắc
đánh giá skill đang dùng thất bại dưới placebo; (b) replay ở nguồn không đủ, nhưng thử trên đích thì đủ hay không là tùy chế độ
nhiễu.

## 2. Ba phương án (mọi phương án đều 0 USD: chỉ dùng dữ liệu đã có)

### Phương án A: "A Placebo Test for Agent-Skill Evaluation" (phương pháp đánh giá; trục chính là repo `gatekeeper`)

- **Câu hỏi duy nhất:** các cách đánh giá skill đang được công bố (so một lần, minibatch kiểu GEPA, MH của XRepoSkill, quy lỗi của Dong et al., auditor LLM) có qua được đối chứng placebo A/A trên nhiễu thật không, và cách nào qua được?
- **Một khái niệm trial:** một cặp lần chạy agent trên cùng task, khác nhau đúng một điều kiện (có/không skill, hoặc A/A).
- **Đóng góp:**
  1. Bảng placebo cho 8 quy tắc trên 221 task thật.
  2. Placebo cho quy lỗi: R = 1,08; auditor đổ lỗi cho skill giả.
  3. Phép trừ placebo có chứng minh, cộng kiểm định hoán vị.
  4. Mức nhiễu nền: 7/13 mức tăng đã công bố nằm trong nhiễu.
  5. Bộ dữ liệu chạy lặp có A/A.
- **p6 dùng thế nào:** một mục Discussion "khi nào một lần chạy là đủ": phép biến đổi tất định, hại hiếm, smoke gần đủ.
- **Vì sao tỉ lệ thành công cao nhất:**
  - Gần như mọi kết quả đã có và đã đăng ký trước.
  - Kết quả theo chiều nào cũng có giá trị.
  - Đúng xu hướng 2026: độ tin cậy của đánh giá agent.
  - Không phụ thuộc việc chứng nhận được skill có lợi.
- **Rủi ro reviewer:**
  - Một model agent, một loại tác vụ. Lặp lại trên model thứ hai cần khoảng 48 USD (P2), hiện tạm dừng theo lệnh dừng chi phí.
  - Gần các công trình Agent Evaluation Reliability, Randomness, Dong et al.: phải trích đúng bản gốc (việc F0 còn mở).
  - Auditor là LLM, chưa có người audit.
  - Bị đọc là "bài bác bỏ": phải viết như một giao thức đánh giá.
- **Venue phù hợp:** ICSE/FSE/ASE research track, mảng empirical/evaluation methodology; ISSTA nếu nhấn mạnh phần kiểm định.
- **Việc còn lại (0 USD):** F0; viết lại `paper/main.tex` theo `paper_plan.md`; sửa L4 đã làm (§21); bảng và hình sinh tự động.

### Phương án B: "Behaviour-Preserving Admission of Reusable Code Transformations" (kỹ thuật + thực nghiệm lớn; trục chính là p6, đã thu hẹp theo `CONCEPTS_FIX.md`)

- **Câu hỏi duy nhất:** nhận một phép biến đổi mã tái sử dụng (rule autofix, refactoring, bản vá) vào một đích sao cho P(nhận cell có tỉ lệ đổi hành vi ≥ 5%) ≤ α trên cả thư viện.
- **Đóng góp:**
  1. Chứng nhận hại anytime-valid + e-Holm/e-BH + execution rule cho tổ hợp + retirement theo epoch. Đã có chứng minh.
  2. Thực nghiệm trên 200 dự án PyPI chọn trước (198 có kết quả), 5.185 ô.
  3. Bảng baseline theo nguồn bằng chứng: replay ở nguồn (B6) nhận 9/11 và 17/20 ô có hại; LLM judge 6 và 10; test suite của chính package bỏ sót hại; B9 gây hại khoảng 7% và đắt hơn 26–87 lần.
- **Vì sao vẫn cạnh tranh:**
  - Quy mô lớn, skill có thật trên thị trường (Ruff).
  - So trực tiếp với baseline quyết định của paper gốc (B6).
  - Đã đăng ký trước, có nhân rộng (T2).
- **Rủi ro reviewer (đã lộ rõ):**
  - Smoke 20 draw gần ngang G ở T và T2: G chỉ hơn ở U (hại hiếm một phần: smoke nhận 10/33 ô ở vùng 5–20%).
  - W3 (chi phí) thua.
  - Ground truth dùng chung harness với phương pháp; TS là oracle độc lập duy nhất và đang phải chạy lại (lỗi harness T-A4a).
  - Bài **xa câu chuyện "skill của agent"** của paper gốc.
- **Venue phù hợp:** ISSTA, ICSE (testing / program transformation), ASE.
- **Việc còn lại:** viết lại theo `CONCEPTS_FIX.md` (0 USD). Chạy lại TS và 2 package T2 cần runner GitHub Actions, đang dừng.

### Phương án C: "When Does Reusing a Change Need Statistical Admission? A Regime Map" (hợp nhất hai repo)

- **Câu hỏi duy nhất:** cùng một quy trình, tức một cặp chạy trên đích có/không thay đổi, lặp lại nhiều lần, có đối chứng A/A. Với từng chế độ nhiễu, cổng nào là đủ?
- **Ba chế độ, đều đã có số đo:**
  1. Thay đổi tất định, hại hiếm (p6 T/T2): replay ở nguồn và LLM judge thất bại; smoke gần đủ.
  2. Hại một phần, hiếm (p6 U): smoke thất bại (10/33); cổng tuần tự có bảo đảm cần thiết; G-FDR ngang B8.
  3. Skill mức agent, tác dụng nhỏ hơn nhiễu chạy lại (repo `gatekeeper`): mọi quy tắc so một lần hoặc nhìn liên tục thất bại placebo; chỉ quy tắc anytime-valid giữ mức; chứng nhận lợi ích là không khả thi ở n hiện có.
- **Đóng góp:** một bản đồ "dùng cổng nào khi nào" có số đo ở cả ba chế độ, cùng một định nghĩa trial; giao thức placebo; lý thuyết chung (chứng nhận hại/lợi là hai giả thuyết của cùng một máy móc e-process).
- **Vì sao hấp dẫn cho A\*:** rộng; trả lời đúng câu "honest competitor" của paper gốc (retest hay replay?) bằng số đo; dùng hết dữ liệu.
- **Rủi ro:**
  - `p6_review.md` đã cảnh báo hai miền "rời rạc". Nếu không giữ được **một** định nghĩa trial và **một** câu hỏi, reviewer sẽ lặp lại đúng lời chê của thầy.
  - Bài dài; khó vừa 10–12 trang IEEE.
- **Venue:** ICSE/FSE (tầm rộng); hoặc TOSEM/TSE nếu dài.

### (Phụ, cần tiền, chỉ khi bạn mở lại ngân sách) Phương án D: "Do Published Skill Gains Survive?"

`plan_replication.md`, trần 60 USD. Phép thử §22 cho thấy `viper` không lặp lại, `asyncio` lặp lại chiều hại. Đây là bằng
chứng scope rất đắt giá cho A hoặc C, nhưng track chứng nhận skill có lợi gần như chắc sẽ dừng theo quy tắc đã đăng ký.

## 3. So sánh và khuyến nghị

| Tiêu chí | A (placebo) | B (biến đổi mã) | C (bản đồ chế độ) |
|---|---|---|---|
| Dữ liệu đã đủ, 0 USD | Gần đủ (F0 còn mở) | Gần đủ (TS và 2 package cần chạy lại trên Actions) | Đủ, cần viết hợp nhất |
| Khớp kỳ vọng paper gốc | Trung bình (đổi trục sang đánh giá) | Thấp (đổi đối tượng sang phép biến đổi tất định) | Cao nhất (trả lời câu "retest hay replay" bằng số đo) |
| Nguy cơ bị chê "mơ hồ" | Thấp | Thấp sau khi sửa theo `CONCEPTS_FIX.md` | **Cao** nếu không giữ một định nghĩa |
| Điểm yếu reviewer lớn nhất | Một model agent | Smoke gần ngang; W3 thua | Hai miền khác nhau |
| Khả năng có một bài nộp kịp, chắc | **Cao nhất** | Cao | Trung bình |
| Tầm ảnh hưởng nếu được nhận | Cao | Trung bình | Cao nhất |

**Khuyến nghị:**
- **Paper:** đi **A**.
  - A có tỉ lệ thành công cao nhất với dữ liệu đã có.
  - Hai thành phần chắc nhất của C (chế độ tất định từ p6, và câu hỏi "retest hay replay") được đưa vào A như một mục Discussion có số đo, nên A giữ được phần lớn tầm của C mà không gánh rủi ro "rời rạc".
- **Luận văn:** luận văn có chỗ cho cả ba, nên tỉ lệ thành công của luận văn không phụ thuộc vào một bài được nhận. Cấu trúc gợi ý:
  - Chương lý thuyết (e-process, sổ α, tổ hợp, retirement): dùng chung.
  - Chương A.
  - Chương B (p6 đã sửa khái niệm).
  - Chương tổng hợp C.
- **Để A từ "cạnh tranh được" lên "cạnh tranh tốt":**
  - Cần đúng một khoản tiền: lặp lại A/A trên model thứ hai (P2, khoảng 48 USD theo ước tính của repo `gatekeeper`; giá chưa xác minh). Việc này chờ bạn quyết vì lệnh dừng chi phí.
  - Người audit khoảng 20 cặp (P-E) không tốn tiền nhưng cần người.

**Không hứa được nhận:** mọi mức "cạnh tranh" ở trên là định tính; không có dữ liệu để tính xác suất được nhận.
