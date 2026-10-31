# Giai đoạn 1: đoạn nào trong bản nháp được thay bằng đoạn nào

Số thứ tự định lý dưới đây là số trong `build/theory_sections.pdf`; khi dán vào bài, số sẽ đổi theo mục.

Các tệp LaTeX trong `sections/` là **câu chữ tiếng Anh để dán thẳng vào bài**.
- `main.tex` chỉ dùng để biên dịch thử: workflow `Gatekeeper paper LaTeX build` dựng PDF ở `build/theory_sections.pdf`.
- Nguồn chuẩn của mọi phát biểu và chứng minh: [`../THEORY.md`](../THEORY.md).
- Phép kiểm bằng số: workflow `Gatekeeper theory checks` ([kết quả](../../../research_closure/results/theory/THEORY_CHECKS.md)).

| Việc (PAPER_TODO) | Vị trí trong bản nháp (PDF) | Thay bằng | Điểm thay đổi chính |
|---|---|---|---|
| 1.1 | §4 Problem formulation (Definition 1, 2; "Assumptions declared"; "Admission problem") | `sections/problem.tex` | Thêm khái niệm **ô** (gồm ô tổ hợp); loss **chặn tại 1**; Assumption 1 (rút task có hoàn lại, i.i.d.), Assumption 2 (TV ≤ ξ); bài toán admission nói rõ bảo đảm cần 2ξ < θ |
| 1.2 | §6.1 Theorem 4 và chứng minh | `sections/theory.tex`: Lemma 2.1 (e-process), Theorem 2.2 (admission), Lemma 2.3 (shift) | Sổ cái α **theo ô** gồm admit lại 6/(π²(k+1)²) và ô tổ hợp; hằng số **2ξ**; đoạn "Why the budget is per cell" dẫn số kiểm (45% so với 5%) |
| 1.3 | Remark 5, Proposition 6 | Assumption 3 (rich target class), Proposition 2.4 (a)(b) | (a) có điều kiện "admit với xác suất dương"; (b) **mới:** số hạng 2ξ là cần thiết và chặt |
| 1.4 | §6.2 Theorem 7 và chứng minh | Theorem 2.5 (composition) | Cận chặt 1 + min(a, b); bỏ "≥ 1 − ε với mọi ε" và "no g"; chứng minh không dùng ví dụ retry/async (ví dụ đó tự mâu thuẫn, PAPER_AUDIT N1) |
| 1.5 | Corollary 8 | Assumption 4 (non-interaction), Corollary 2.6 | Nêu rõ giả định cần cho việc chỉ kiểm cặp giao nhau; số cặp là \|L\|·d̄/2; **bỏ con số 0,34** cho tới khi có số đo thật |
| 1.6 | §6.3 Proposition 9 ("1 + σT²/σS²", "net win 1.55×") | Proposition 2.7 (pairing) | R = (V_π + V_∅)/(V_π + V_∅ − 2C); mô hình cộng tính cho 1 + 2σT²/σS²; hai thiết kế cùng tốn 2n lần chạy nên bỏ phép chia đôi |
| 1.7 | §3.3 Risk control and conformal methods | `sections/related_stats.tex` | FWER qua hợp cận (không phải BH); BH chỉ cho so sánh phụ; thêm Ville 1939, Wang & Ramdas 2022, Ramdas et al. 2023 |
| 1.8 | — | workflow `Gatekeeper theory checks` | Đã chạy (run 41206524576): C1–C6 đúng, C7 xác nhận số của bản nháp không khớp |
| 1.9 | — | — | **Còn lại: cần một người đọc độc lập** (thầy hoặc bạn cùng lab) kiểm từng chứng minh |

## Những chỗ khác trong bản nháp phải sửa theo, vì chúng nhắc tới phần lý thuyết

| Vị trí | Câu cũ | Sửa thành |
|---|---|---|
| Abstract | "prove a finite-sample admission bound for adaptively chosen scopes under bounded shift, prove that composition risk is not bounded by individual risks" | "prove an anytime-valid, library-wide admission bound with a per-cell error ledger that covers compositions and re-admission, show that its 2ξ shift term is necessary and tight, and characterise composition risk exactly" |
| §2 / §10.3 | "trial-sampling failures … the residual ξ_s term" | Lỗi lấy mẫu trong P_s thuộc ngân sách α, **không** phải ξ_s (PAPER_AUDIT S4) |
| §10.3 | "low-effect harms … within the benefit margin θ, so admission is technically correct" | Bỏ: admit một ô có hại luôn là sai lầm loại I (PAPER_AUDIT S3) |
| §5.2 "reduces the trials needed by roughly 3×" | | Dùng R của Proposition 2.7, với số đo thật nếu có |
| §5.4 Retirement | không nói về α | "re-admission draws the next entry of the cell's ledger (Theorem 2.2)" |
| §7 Implementation "α_s pre-allocated proportional to expected reuse frequency" | | "α_c pre-allocated per cell (proportional to expected reuse frequency), with the 6/(π²(k+1)²) schedule across epochs" |
| Threats, theory | "where the scope is coarse the shift term dominates" | thêm "the guarantee excludes harmful admissions only when 2ξ_s < θ (Theorem 2.2); ξ_s is declared, not estimated" |
| Keywords | "conformal prediction" | "e-processes, anytime-valid inference" |

## Giai đoạn 2 (31/10/2026)

| Việc | Tệp | Thay cho |
|---|---|---|
| 2.2 | `sections/evaluation.tex` | §9–§10 của bản nháp (Bảng 1, 2, 3, Hình 3, RQ1–RQ4): toàn bộ số projected thay bằng 5 tiểu mục số đo được: đồ thị pha + Study H; kỹ năng trên target thật (D, E, G); patch LLM (P, RQ5); SWE-bench Verified (Q, Q-A1); oracle (RQ3). Bảng đối chiếu từng số: [`../NUMBERS_MAP.md`](../NUMBERS_MAP.md) |
| 2.3 | `sections/threats.tex` | Threats của bản nháp: thêm các giả định của định lý, Assumption 4 chưa kiểm, luật thực thi, đối tượng giả do G2 dựng, người chấm cùng họ model, 19/55 không tái tạo |
| Theory | Remark "Harm certificate" | Nối lý thuyết với chứng chỉ tác hại mà thí nghiệm dùng (0,39η; 110 lần rút) |

## Giai đoạn 4 (31/10/2026): bản bài đầy đủ, khung A

`main.tex` giờ là bản bài đầy đủ (tên mới: *Scope before Reuse: Risk-Controlled Admission of Reusable Code Changes*). Thứ tự các mục:
Abstract → `intro` → `motivation` (ví dụ **minh hoạ**, đã sửa chỗ tự mâu thuẫn retry/async) → `problem` → `approach` → `theory` → `implementation` (số thật: khoảng 4.800 dòng, 359 test) → `evaluation` (RQ1–RQ4) → `threats` → `related` (trích dẫn đã kiểm) → `conclusion` + Data availability.

Bỏ khỏi bản nháp: banner "projected", benchmark SkillShift-SE, Bảng 1–3, Hình 3, RQ về tổ hợp, B9 và hoà vốn (không có dữ liệu thật).
