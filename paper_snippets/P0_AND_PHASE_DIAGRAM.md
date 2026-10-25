# Đoạn văn và số liệu cần dán vào bài báo (không ghi đè main.tex; bài của bạn đã có Study I/K)

## A. Sửa số liệu sai hoặc dễ gây hiểu lầm

1. **Admit sai ở biên tác hại.** Bảng 3 (0,9%) và Mục 9 (0,2% khi i.i.d.) là hai ước lượng của cùng một đại lượng với nhiễu Monte Carlo. Chạy lại 12.000 lần mỗi công cụ: 0,63% ± 0,14% và 0,56% ± 0,13%. Báo cáo **một số: 0,6%**. FWER 0,040 là đại lượng cấp họ 16 ô, khác hai số trên.
2. **Cận trên của h.** Confidence sequence kiểu hedged-capital cho D1 là [0; 0,065] sau 300 lần rút sạch, rộng hơn η = 5% và làm người đọc nghi chứng chỉ. Thay bằng cận suy từ chính bằng chứng:
   - tại thời điểm admit (110 lần rút sạch, mức 1/160): h ≤ 4,5% (đúng bằng cách chứng chỉ được xây dựng, ngay dưới η);
   - sau 300 lần rút sạch: h ≤ 1,7% ở mức 1/160, và h ≤ 0,99% theo Clopper–Pearson 95% một phía.
   (Ở lượt trước tôi nói "khoảng 3%" cho 110 lần rút; số đúng là 4,5%.)
3. **Ngưỡng chịu hại thực tế.** Với mức cược c = 0,9, chứng chỉ chỉ có tăng trưởng dương khi h < 0,39η ≈ 2%. Nói rõ trong tóm tắt và trong mục tham số, thay vì để người đọc hiểu dung sai là 5%.

## B. Baseline đơn giản phải vào bảng chính (kể cả khi nó thắng)

Trên D/E/G, cổng **B8+** (census sạch, 300 lần rút, 0 lần hại ở mọi scope, ≥ 1 lần có lợi) cho kết quả: admit **D1, D3 và D5**; từ chối mọi ca có hại (E1–E3, pydal) và mọi ca trung tính. Tức 3 thành công, 0 có hại, 0 không hiệu quả, so với 2 thành công của Gatekeeper. Trên Study H nó an toàn nhưng chỉ admit 1/50 ở ρ = 1% và 0/50 ở ρ = 2–10%.

> Trên các target thật hiện có, tác hại thường xuyên và tất định nên một cổng đơn giản đủ dùng; ưu thế của chứng chỉ chỉ xuất hiện khi tác hại một phần.

## C. Đoạn mới: đồ thị pha của các cổng (dán vào Mục Results hoặc Discussion)

\paragraph{Where simple gates fail.} For a patch that always helps, Table~\ref{tab:phase} gives the probability that each gate admits it as a function of the true harm rate $h$ ($\eta=5\%$, $\alpha=0.1$; exact for the smoke, zero-tolerance and fixed-sample gates, Monte Carlo for the sequential rules). A zero-tolerance gate with 300 draws keeps fewer than half of acceptable patches once $h>0.23\%$; a 20-draw smoke test still admits more than 10\% of inadmissible patches until $h\approx 11\%$; outside $[0.25\%,10\%]$ a simple gate suffices. A fixed-sample test with the same $\theta,\eta,\alpha$ is as safe as the sequential rule and, at 300 draws, more powerful (92\% versus 65\% at $h=2\%$): the fixed-stake certificate matches it only with about 1{,}000 draws under a mixture of stakes. What the sequential rule buys is early stopping (110 draws instead of 300 when $h\approx0$ in a 16-cell family, and a few draws when harm is frequent) and validity under data-dependent stopping, not statistical power.

\begin{table}[t]
\centering\footnotesize
\caption{Probability that a gate admits an always-helpful patch, by true harm rate $h$ ($h\ge\eta$: admitting is an error).}
\label{tab:phase}
\begin{tabular}{@{}lccccc@{}}
\toprule
$h$ & smoke 20 & zero-tol.\ 300 & fixed 300 & GK $c{=}0.9$, 300 & mixture, 1000 \\
\midrule
0.3\%  & 0.94 & 0.41 & 1.00 & 1.00 & 1.00 \\
1\%    & 0.82 & 0.05 & 1.00 & 0.95 & 1.00 \\
2\%    & 0.67 & 0.00 & 0.92 & 0.65 & 1.00 \\
3\%    & 0.54 & 0.00 & 0.59 & 0.36 & 0.78 \\
5\% (error)  & 0.36 & 0.00 & 0.06 & 0.10 & 0.10 \\
10\% (error) & 0.12 & 0.00 & 0.00 & 0.01 & 0.00 \\
\bottomrule
\end{tabular}
\end{table}

## D. Thu hẹp tuyên bố (thay trong tóm tắt, mở đầu, kết luận)

- "learned code-repair skills" → "frozen code transformations" (cả hai skill là AST rewrite viết tay).
- Không viết "Gatekeeper outperforms simple gates". Viết: "simple gates suffice when harm is frequent; a statistical gate matters in a band of partial harm whose prevalence in real patches is the question of Study L".
- Gỡ câu về SWE-bench "6,4 điểm phần trăm… consistent with our census results" nếu chưa gắn được với dữ liệu của bài.
- Thay URL GitHub có tên người dùng bằng artifact ẩn danh khi nộp (double-blind).
