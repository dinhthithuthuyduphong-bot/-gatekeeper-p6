# Hướng A: kết quả âm G1 trong bài, và kế hoạch cho ISSTA 2027

## 1. Đoạn LaTeX báo cáo kết quả âm (dán vào Mục Results hoặc Threats, sau Study H)

\subsection{A negative result: oracle-free admission by call replay (Study~L, gate G1)}
To remove researcher-written oracles we pre-registered gate G1 (frozen before any run, with an immutable threshold): on the six instances that have an upstream fix, a gold-differential harness fed by an automatic generator had to detect the original bug with a known-good patch, show no regression for it, be deterministic in three fresh runs, and catch at least one of at most five pre-specified AST mutants of the fix, on at least five of six instances. The generator records real calls of the functions the fix edited while the repository's own tests run, and replays them with an optional type-confusion mutation of one argument. \textbf{Two of six instances passed, so the gate failed and the route was stopped} (Table~\ref{tab:g1}).

\begin{table}[t]
\centering\footnotesize
\caption{Gate G1 (threshold: at least 5 of 6). ``Trigger'' is the fraction of draws on which the original differs from the fix.}
\label{tab:g1}
\begin{tabular}{@{}llcl@{}}
\toprule
Instance & Result & Trigger & Cause \\
\midrule
D5 pycubrid & pass & 8.7\% & --- \\
D4 openfeature & pass (marginal) & 0.7\% & only 2 draws; criterion (b) vacuous \\
D2 Cerberus & ineligible & --- & 32 calls seen, receivers not picklable \\
D3 spec-kit & ineligible & --- & no call seen (hypothesis: decorator-registered callback) \\
A1 spec-kit & fail & 0.0\% & bug input nested in a config (hypothesis) \\
D1 py\_ecc & fail & 0.0\% & 300/300 harness errors, cause not recorded \\
\bottomrule
\end{tabular}
\end{table}

Even if the D1 harness error were fixed, at most three of six instances could pass, so the verdict does not depend on it. The observed failure modes (receivers that cannot be serialised, callbacks bound before instrumentation, deeply nested inputs) are common in real code, so we expect function-level call replay not to scale; we therefore did not run the sampling gate (G2). We report this as a limitation of the attempt, not of the admission rule.

## 2. Ý nghĩa cho định vị

- Đây là kết quả âm **được đăng ký trước**; nó trả lời trực tiếp phê bình "oracle viết tay/vòng tròn" bằng một nỗ lực thật và một giới hạn được đo.
- Không viết "oracle-free admission is feasible". Viết: "a first attempt at oracle-free evaluation failed on 4 of 6 instances for identifiable engineering reasons".
- Hướng B (test-level) chỉ được nhắc trong bài nếu nó chạy trên cohort mới đã đóng băng; đừng mô tả nó như kết quả khi mới có dữ liệu phát triển.

## 3. ISSTA 2027: những gì đã xác minh và chưa xác minh

Đã xác minh (từ trang công khai): ISSTA 2027 ở Singapore, 7–10/9/2027; **tóm tắt bắt buộc 8/1/2027, bài đầy đủ 11/1/2027**; phản hồi tác giả 22–25/3/2027; có đường "major revision" (nộp lại 20/5/2027). ISSTA xếp CORE A, **không phải A\***.

Từ CFP ISSTA 2026 và 2025 (chỉ là chỉ dẫn; **CFP 2027 chưa được xác minh, hãy đọc lại khi nó công bố**): xét duyệt ẩn danh kép; mẫu `\documentclass[acmsmall,screen,review,anonymous]{acmart}`; giới hạn **18 trang gồm cả phụ lục, không tính tài liệu tham khảo**; **bắt buộc mục "Data Availability"**; ba loại bài: Research, Experience, Replicability Studies; chính sách open science.

Hệ quả thực tế:
1. Bản 18 trang hiện tại đã gần đúng giới hạn, nhưng phụ lục tính vào giới hạn; cần rà lại khi chuyển sang mẫu `acmart`.
2. **Ẩn danh:** bỏ tên sinh viên và người hướng dẫn, thay URL GitHub có tên người dùng bằng bản ẩn danh, không để tên tác giả trong tên file artifact.
3. **Data Availability:** trỏ tới artifact ẩn danh (kho mã, hash đóng băng, dữ liệu thô, workflow tái tạo).
4. Loại bài: Research Paper hoặc Experience Paper; đừng chọn Replicability Studies trừ khi CFP 2027 nói rõ nó dành cho tái lập của bản chưa công bố (bài gốc FSE-2027-13 chưa công bố).

## 4. Việc cần làm cho hướng A (không tốn tiền)

| Việc | Trạng thái |
|---|---|
| Sửa số liệu biên, cận h theo chứng chỉ đảo ngược, B8+ vào bảng chính, đoạn đồ thị pha, thu hẹp tuyên bố | Đã có đoạn dán sẵn trong `paper_snippets/P0_AND_PHASE_DIAGRAM.md` |
| Đoạn kết quả âm G1 | Mục 1 ở trên |
| Cổng độ phủ vị trí sửa; đối chứng dương cho kiểm tra không trạng thái | Chưa làm |
| Chuyển sang mẫu `acmart` ẩn danh, mục Data Availability | Làm sau khi chốt nội dung (cuối tháng 11 đến đầu tháng 12) |
