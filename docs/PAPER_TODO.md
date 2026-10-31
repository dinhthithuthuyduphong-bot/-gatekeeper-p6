# To-do list hoàn thành bài báo, từ đầu tới lúc nộp

Dành cho người **chưa có kinh nghiệm nghiên cứu**. Làm từ trên xuống. Mỗi việc có: **làm gì**, **vì sao**, **xong khi nào** (tiêu chí kiểm được), **ở đâu** (tệp, workflow). Đánh dấu `[x]` khi xong, và ghi một dòng vào [`docs/PROCESS_LOG.md`](PROCESS_LOG.md) mỗi lần hoàn thành một việc.

Trạng thái tổng hợp: [TRACKING_FSE](TRACKING_FSE.md). Lý thuyết: [THEORY](paper/THEORY.md). Lỗi của bản nháp: [PAPER_AUDIT](paper/PAPER_AUDIT.md). API và lỗi khi chạy: [API_AND_FAILURES](API_AND_FAILURES.md).

---

## Quy tắc chung (đọc trước khi bắt đầu)

1. **Không viết con số nào vào bài nếu nó không có trong một tệp kết quả của repo.** Mỗi con số phải trỏ được tới một tệp JSON hoặc MD trong `research_closure/results/` và một run trên GitHub Actions.
2. **Kế hoạch trước, dữ liệu sau.** Mọi phân tích xác nhận phải được commit trước khi chạy. Phân tích làm sau khi thấy dữ liệu phải ghi rõ "sau khi thấy dữ liệu", như Q-A1.
3. **Kết quả âm vẫn báo cáo.** HQ1 không được ủng hộ là một kết quả, không phải thất bại.
4. **Mỗi lần chạy trên GitHub Actions:** ghi run id vào PROCESS_LOG. Nếu thất bại, chạy workflow `Gatekeeper failure audit` để xem nguyên nhân gốc trước khi chạy lại.
5. **Không sửa tệp đã đóng băng** (có trong `study_*/FREEZE.json`). Muốn đổi thì viết amendment.

---

## Giai đoạn 0: chốt câu chuyện của bài (1 tuần, cần thầy duyệt)

- [ ] **0.1 Đọc lại ba tài liệu theo thứ tự:** [TRACKING_FSE](TRACKING_FSE.md) mục 2 (đối chiếu kỳ vọng), [STUDY_Q_RESULT](../research_closure/results/study_q/STUDY_Q_RESULT.md), [THEORY](paper/THEORY.md) mục 7.
  *Xong khi:* tự viết được, trong 5 câu, bài này khẳng định gì và không khẳng định gì.
- [ ] **0.2 Chọn khung bài.** Có hai khung hợp lý theo dữ liệu hiện có:
  - **(A) Bài phương pháp và lý thuyết:** chấp nhận thay đổi mã có kiểm soát rủi ro (Định lý 4′, 6′, 7′ đã sửa) cộng bằng chứng thực nghiệm trung thực, gồm kết quả âm của Study D–H và đồ thị pha các cổng.
  - **(B) Bài thực nghiệm về oracle:** "khoảng 11% patch resolved trên SWE-bench Verified khác hành vi bản fix trên đầu vào hợp lệ" (Study Q, Q-A1), với lý thuyết là phần phụ.
  *Xong khi:* thầy chọn một khung, ghi vào TRACKING_FSE mục 4.
- [ ] **0.3 Chọn hội nghị hoặc tạp chí và hạn nộp** (FSE, ICSE, ISSTA, ASE, EMSE, TOSEM). Ghi hạn, giới hạn số trang, double-blind hay không.
  *Xong khi:* có một dòng trong TRACKING_FSE: tên venue, hạn, số trang.
- [ ] **0.4 Liệt kê 3 đến 5 câu hỏi nghiên cứu (RQ) cuối cùng.** Mỗi RQ phải có tệp kết quả tương ứng; RQ nào chưa có dữ liệu thì đưa sang giai đoạn 2.

## Giai đoạn 1: sửa lý thuyết trong bài (1 đến 2 tuần)

> **Trạng thái 31/10/2026:** 1.1–1.8 xong. Câu chữ LaTeX ở [`paper/latex/sections/`](paper/latex/sections/), PDF ở [`paper/latex/build/theory_sections.pdf`](paper/latex/build/theory_sections.pdf), bảng thay thế ở [`paper/latex/CHANGES.md`](paper/latex/CHANGES.md). Còn **1.9** (người đọc độc lập) và việc dán vào bản bài chính khi có.

Mọi bản sửa đã có sẵn câu chữ trong [THEORY](paper/THEORY.md); việc ở đây là **đưa vào bài và kiểm lại**.

- [x] **1.1 Mục Problem formulation:** thêm Giả định A (rút task có hoàn lại, i.i.d.), Giả định B (TV ≤ ξ), nói rõ loss chặn tại 1.
- [x] **1.2 Thay Định lý 4 bằng Định lý 4′:** sổ cái α theo ô, gồm admit lại (6/(π²(k+1)²)) và ô tổ hợp; hằng số 2ξ; câu "bảo đảm có nghĩa khi 2ξ < θ". Chép chứng minh mục 2 của THEORY.
  *Xong khi:* có thêm câu "Corollary: if 2ξ_s < θ for all s, Pr[∃ harmful admission] ≤ α".
- [x] **1.3 Thay Mệnh đề 6 bằng 6′(a) và 6′(b);** viết lại Remark 5 thành "the 2ξ term is necessary and tight (Prop. 6′b)".
- [x] **1.4 Thay Định lý 7 bằng Định lý 7′** (cận chặt 1 + min(a, b)) và chứng minh; bỏ câu "no g".
- [x] **1.5 Hệ quả 8:** thêm Giả định D (không tương tác khi footprint rời nhau), sửa số d̄ (10,6, không phải 0,34), hoặc bỏ số nếu không có dữ liệu thật.
- [x] **1.6 Mệnh đề 9:** công thức R = (V_π + V_∅)/(V_π + V_∅ − 2C), mô hình cộng tính cho 1 + 2σ_T²/σ_S²; bỏ "1,55×".
- [x] **1.7 Mục 3.3 Related work:** sửa câu về BH, vì BH là FDR còn bài dùng FWER và hợp cận; thêm trích dẫn Ville 1939, Wang & Ramdas 2022, Ramdas et al. 2023.
- [x] **1.8 Chạy lại phép kiểm bằng số:** workflow `Gatekeeper theory checks` (0 USD).
  *Xong khi:* C1 đến C6 `held = True`, C7 `held = False` (số của bản nháp không khớp), và `research_closure/results/theory/THEORY_CHECKS.md` được commit.
- [ ] **1.9 Nhờ một người khác đọc từng chứng minh** (bạn cùng lab hoặc thầy). Ghi lại mọi câu hỏi họ đặt ra và câu trả lời.

## Giai đoạn 2: thay số projected bằng số đo được (2 đến 4 tuần)

- [ ] **2.1 Lập bảng "số trong bài → tệp nguồn":** mỗi con số của Bảng 1, 2, 3 và Hình 3 trong bản nháp đi kèm (a) tệp kết quả thật, hoặc (b) "BỎ".
  *Xong khi:* không còn con số projected nào trong bài. Mọi số của SkillShift-SE (180 cặp, 22,7% → 5,1%, 41/46, …) đều là projected, nên phải bỏ, trừ khi thật sự xây benchmark đó.
- [ ] **2.2 Đưa các kết quả đã có vào bài:**
  - Study D–H: 0/2.400 khác biệt (kết quả âm về kỹ năng);
  - đồ thị pha các cổng (`paper_snippets/P0_AND_PHASE_DIAGRAM.md`);
  - Study P: 16/205 = 7,8%, RQ5;
  - Study Q: Q2 = 43,1%, Q4 = 11,1%, HQ1 không ủng hộ, Q5 = 3,88;
  - Q-A1: 8/36 = 22,2%, đồng thuận 87,7%;
  - RQ3: `D2_cerberus`.
- [ ] **2.3 Quyết định về Giả định D:** hoặc đo trên một mẫu cặp kỹ năng có footprint rời nhau (cần thiết kế study mới, có đăng ký trước), hoặc nêu nó là giả định chưa kiểm trong Threats.
- [ ] **2.4 (Nếu chọn khung B)** Giới hạn "bản fix trả giá trị ≠ đầu vào hợp lệ": đếm số đơn vị HQ1 mà mọi mục là đối tượng giả do G2 dựng. Đây là phân tích sau khi thấy dữ liệu, phải ghi nhãn rõ.
- [ ] **2.5 Ghi vào EVIDENCE_LEDGER** run id và commit cho mọi kết quả đưa vào bài.

## Giai đoạn 3: dọn nợ kỹ thuật ảnh hưởng tới tính tin cậy (song song với giai đoạn 2)

- [ ] **3.1 Freeze lệch của Study B, C, N, P** (xem PROCESS_LOG): viết amendment hoặc giải thích trong EVIDENCE_LEDGER cho từng study.
  *Xong khi:* `python tools/freeze_study.py verify study_<x>` cho kết quả đã giải thích được với mọi study.
- [ ] **3.2 Q5 trong `q_analyze.py`** tính khác định nghĩa của giao thức: ghi chú trong bài là dùng số tính lại (3,88).
- [ ] **3.3 Lỗi `FileNotFoundError`** của 4 instance trong Study Q (patch tạo tệp mới): ghi trong Threats; sửa công cụ cho study sau.
- [ ] **3.4 Token Vertex hết hạn sau khoảng 1 giờ:** mọi workflow gọi model chạy lâu nên chia job (như `study-q-review-rate.yml`). Xem API_AND_FAILURES mục 3.
- [ ] **3.5 Chạy `Gatekeeper failure audit`** và kiểm rằng mọi lần thất bại đều có nguyên nhân được ghi trong API_AND_FAILURES.

## Giai đoạn 4: viết bài (2 đến 3 tuần)

Thứ tự viết nên đi từ phần chắc nhất tới phần khó nhất:
- [ ] **4.1 Phần Method / Theory** (từ THEORY.md, đã có chứng minh).
- [ ] **4.2 Phần Evaluation:** mỗi RQ một tiểu mục; mỗi tiểu mục gồm câu hỏi, cách đo, kết quả kèm khoảng tin cậy, và giới hạn.
- [ ] **4.3 Threats to validity:** ít nhất các mục sau:
  - người chấm thứ hai cùng họ model;
  - 19/55 đơn vị không tái tạo được;
  - G2 xem diff của bản fix;
  - đối tượng giả do G2 dựng;
  - khung là các bản nộp công khai lấy được;
  - Giả định D chưa kiểm;
  - ξ_s không đo được.
- [ ] **4.4 Related work:** đọc lại reading list. **Kiểm từng trích dẫn** qua DBLP, arXiv hoặc DOI; bảy mục có tác giả "Authors" (PAPER_AUDIT, N4) phải được thay bằng tác giả thật hoặc bỏ.
  *Xong khi:* không còn mục nào có tác giả placeholder.
- [ ] **4.5 Introduction và Abstract viết sau cùng**, chỉ dùng số đã có ở 4.2.
- [ ] **4.6 Bỏ banner "projected"** chỉ khi giai đoạn 2.1 đã xong.

## Giai đoạn 5: kiểm trước khi nộp (1 tuần)

- [ ] **5.1 Kiểm tái lập:** người khác clone repo, chạy `python -m unittest discover -s tests` (343+ test pass) và workflow `theory checks`, rồi được cùng số.
- [ ] **5.2 Artifact ẩn danh** (double-blind): repo hiện công khai và có tên người dùng. Tạo bản ẩn danh (ví dụ anonymous.4open.science), bỏ tên và email trong commit.
- [ ] **5.3 Kiểm số lần cuối:** mỗi con số trong PDF có trong bảng 2.1.
- [ ] **5.4 Kiểm định dạng:** số trang, template ACM, mục Data availability chỉ mô tả những gì thật sự có trong artifact (bản nháp mô tả nhiều thứ không có, PAPER_AUDIT N5).
- [ ] **5.5 Thầy duyệt bản cuối;** ghi vào PROCESS_LOG ngày nộp và mã bài.

## Giai đoạn 6: sau khi nộp

- [ ] **6.1 Lưu bản nộp** (PDF, commit hash của artifact) vào `docs/paper/submitted/`.
- [ ] **6.2 Khi có phản biện:** mỗi ý kiến một dòng trong `docs/paper/REVIEW_RESPONSE.md`: ý kiến, đồng ý hay không, đã sửa ở đâu.

---

## Bảng tham chiếu nhanh: muốn làm X thì chạy gì

| Muốn | Chạy | Chi phí |
|---|---|---|
| Kiểm lại toán | workflow `Gatekeeper theory checks` | 0 |
| Biết vì sao một run thất bại | workflow `Gatekeeper failure audit` (ô `runs` = id) | 0 |
| Tính lại kết quả Study Q | workflow `Gatekeeper Study Q analyze` | 0 |
| Chạy test cục bộ | `python -m unittest discover -s tests` | 0 |
| Kiểm freeze một study | `python tools/freeze_study.py verify study_q` | 0 |
| Gọi model (sinh G2, chấm) | các workflow có bước "Vertex access token" | tốn tiền, xem API_AND_FAILURES |
