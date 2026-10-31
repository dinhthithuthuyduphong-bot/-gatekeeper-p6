# To-do list hoàn thành bài báo, từ đầu tới lúc nộp

Dành cho người **chưa có kinh nghiệm nghiên cứu**. Làm từ trên xuống. Mỗi việc có: **làm gì**, **vì sao**, **xong khi nào** (tiêu chí kiểm được), **ở đâu** (tệp, workflow). Đánh dấu `[x]` khi xong, và ghi một dòng vào [`docs/PROCESS_LOG.md`](PROCESS_LOG.md) mỗi lần hoàn thành một việc.

Trạng thái tổng hợp: [TRACKING_FSE](TRACKING_FSE.md). Lý thuyết: [THEORY](paper/THEORY.md). Lỗi của bản nháp: [PAPER_AUDIT](paper/PAPER_AUDIT.md). API và lỗi khi chạy: [API_AND_FAILURES](API_AND_FAILURES.md).

---

## A. Bảng điểm: bài đã đạt chuẩn A* (FSE/ICSE) hoặc tạp chí Q1 (TOSEM/TSE/EMSE) chưa?

Cập nhật sau **mỗi** lần chạy. Mỗi tiêu chí có trạng thái **THẮNG** (đã đạt, có bằng chứng trong repo) hoặc **THUA** (chưa đạt). Mục nào THUA thì phải có việc tiếp theo.

| # | Tiêu chí mà phản biện A*/Q1 thường dùng | Trạng thái | Bằng chứng / việc còn thiếu |
|---|---|---|---|
| S1 | Lý thuyết đúng, có chứng minh, mọi mệnh đề được kiểm bằng số | **THẮNG** | THEORY.md; C1–C11 `held` (C7 cố ý False: số của bản nháp sai) |
| S2 | Mã thực thi đúng lý thuyết đã chứng minh | **THẮNG** (31/10) | [THEORY_CODE_AUDIT](paper/THEORY_CODE_AUDIT.md) TC1–TC11; C10 chạy đúng luật của D–H |
| S3 | Đóng góp mới, nói rõ cái gì không mới | **THẮNG** | Mục 5 đoạn đầu; Intro "What we do not claim" |
| S4 | Đánh giá trên dữ liệu thật, có đăng ký trước, có kết quả âm | **THẮNG** | Study D, E, G, H, P, Q, R2; FREEZE + submission check |
| S5 | So sánh với baseline mạnh và với công trình gần nhất | **THẮNG một phần** | B2, B6-R (kiểu GSE), B8; PatchDiff. **Thiếu:** chạy chính GSE (A12) |
| S6 | Kỹ năng đa dạng, quy mô thư viện thực tế | **THẮNG một phần** | R2: 12 họ trên 16 repo, chỉ đo footprint và tương tác. **Thiếu:** admit thật với 12 họ (cần oracle) |
| S7 | Tác hại của tổ hợp đo trên dữ liệu thật | **THẮNG một phần** | Study S (sau S-A1): 12 hàm thật, tổ hợp cộng tính, cổng loại đúng 3 ô có hại. **Thiếu:** 11 đơn vị chưa chạy được; input G0 yếu (việc 7.8) |
| S8 | Người chấm độc lập là con người | **THUA** | Người chấm thứ hai là LLM (A9). Việc 1.9 và 7.6 |
| S9 | Tái lập được, có artifact ẩn danh | **THẮNG** (chờ upload) | submission check pass; `make_anonymous_artifact.py`. Người làm: upload |
| S10 | Đúng định dạng và hạn của venue | **THUA** (chưa xác minh) | Bài hiện 14 trang `acmsmall`. Việc 0.3, 5.4 (người làm): tra giới hạn trang FSE 2027 |
| S11 | Thầy và một người đọc độc lập đã duyệt | **THUA** | Việc 1.9, 5.5 (người làm) |

**Kết luận hiện tại:** bài đạt S1–S4 và S9; bài **chưa** chắc thắng vì S7 và S8 (phần phản biện hay tấn công nhất), và S10, S11 là việc của người. Không thể bảo đảm bài được nhận. Việc làm được là đóng từng ô THUA.

## B. Nhật ký từng lần chạy (cập nhật sau MỖI lần chạy)

Mỗi dòng gồm:
- **Thuật toán / mã đổi gì:** đã cập nhật gì trong thuật toán hoặc mã.
- **Đối chiếu bài gốc:** tìm ra lỗi so với bản FSE gốc (AI sinh), hay áp dụng nguyên bài gốc.
- **Kết quả:** THẮNG nếu đạt tiêu chí đặt trước khi chạy, THUA nếu không.
- **Nếu THUA:** debug lý thuyết lại ở đâu. Một dòng THUA chỉ đóng khi có một dòng THẮNG sau nó.

| # | Ngày | Run / commit | Việc | Thuật toán / mã đổi gì | Đối chiếu bài gốc | Kết quả | Nếu THUA: debug tiếp ở đâu |
|---|---|---|---|---|---|---|---|
| R1 | 30/10 | Study Q stream 0–1 | Đo "harm" trên SWE-bench Verified | Không đổi (áp dụng giao thức đã freeze) | Bài gốc dự đoán harm cao (projected); đo thật: HQ1 6/55 | **THẮNG** (chạy đúng giao thức; HQ1 không ủng hộ là kết quả âm hợp lệ) | — |
| R2 | 30/10 | Q-A1 rate, lần 1 (41193552100) | Người chấm thứ hai | — | — | **THUA**: ACCESS_TOKEN_EXPIRED sau khoảng 60 phút | Không phải lỗi lý thuyết: token gcloud cache 1 giờ. Sửa: chia shard + `fresh_gcp_token.py` |
| R3 | 30/10 | Q-A1 rate, chia shard | Người chấm thứ hai | Chia shard, token mới cho mỗi lần gọi | — | **THẮNG**: đồng thuận 87,7%, 8/36 | — |
| R4 | 31/10 | Theory checks | Kiểm lý thuyết | Thêm FastBetting (giống hệt e-process, chạy O(n)) | **Lỗi bài gốc:** Định lý 4 (α theo scope) sai, hằng số TV phải là 2ξ, cận tổ hợp sai, công thức pairing sai, số d̄ sai | **THẮNG**: C1–C6, C8, C9 held; C7 False đúng như dự đoán | — |
| R5 | 31/10 | Library simulation | Kiểm soát tổ hợp | Ô tổ hợp + sổ cái + luật thực thi (`execution.py`, TD7) | **Lỗi bài gốc:** chứng nhận theo từng kỹ năng không bảo vệ tập kỹ năng chạy chung | **THẮNG**: P1 27,9% so với P2 0/1.000 | — |
| R6 | 31/10 | Study R (41218737641) | Footprint 2 họ trên 16 repo | Không đổi | Bài gốc d̄ = 0,34 (bịa); đo thật: 1 hàm chung | **THẮNG** | — |
| R7 | 31/10 | Study R2, push đầu (29e2284) | Thư viện 12 họ | — | — | **THUA**: workflow không có `workflow_dispatch` | Không phải lỗi lý thuyết: tên step có `: `, YAML không parse. Sửa bằng ngoặc kép, có actionlint |
| R8 | 31/10 | Study R2 (41223600552) | Census 12 họ | 10 họ mới (`skill_library.py`) | **Lỗi Giả định 4 trên dữ liệu thật:** `type(x) is not int` → `isinstance` tạo site mới cho guard bool ở hàm khác (pydal, pycubrid) | **THUA về lý thuyết**: luật thực thi tĩnh bỏ sót tương tác | Debug: footprint lấy trên mã gốc là chưa đủ, cần thêm quan hệ "kích hoạt" |
| R9 | 31/10 | Study R2-A1 (re-run, 7da8592) | Cạnh enabling | `components(..., edges)`, census `with_enabling_edges`, mô phỏng đồ thị thật | Sửa Giả định 4: chỉ cần cho cặp giao hoán | **THẮNG**: luật bắt được cặp pydal; mô phỏng P1 7,1% so với P2 0/1.000 | — |
| R10 | 31/10 | Paper build (41224364294) | PDF | — | — | **THUA**: LaTeX lỗi | Không phải lỗi lý thuyết: `_` chưa escape trong `\texttt{yaml.safe_load}`. Đã sửa |
| R11 | 31/10 | Rà lý thuyết ↔ mã (6b44846) | Kiểm mã có đúng lý thuyết | `ledger.py` (TC2), `conformance.py` (TC7), `site_footprint` (TC5), C10, C11 | **Lỗi:** (TC5) mã cấp module bị coi là rời nhau, sai với Hệ quả 2.6; (TC3/TC4) bài không nói luật e-Holm mà D–H dùng | **THUA → sửa**: TC5 là lỗi không chặt thật | Debug: census R2 lần trước cũng bỏ `<module>`, phải chạy lại (R2-A2) |
| R12 | 31/10 | Theory checks (00fe817) | C10, C11 | — | Luật D–H khớp Nhận xét e-Holm | **THẮNG**: FWER 2,4% / 7,3% ≤ 10%; ledger ≤ α | — |
| R13 | 31/10 | Study R2-A2 (193b136; 41226541891 không đổi số) | Census có mã cấp module | Census giữ `file::<module>` | — | **THẮNG**: 467 hàm/vùng (trước 456), các số khác không đổi; kết luận giữ nguyên | — |
| R14 | 31/10 | Paper build (bf6c5e3) | PDF sau R2 + rà lý thuyết | — | — | **THẮNG**: 14 trang, 39/39 con số khớp; bảng 2 (thư viện 12 họ) hiển thị đúng | — |
| R15 | 31/10 | Study S (41227728959) | Hành vi thật của tổ hợp trên 23 đơn vị (21 vùng chung + 2 cặp enabling) | `composition_study.py`: snapshot O/A/B/AB/BA, input G0, harm certificate + e-Holm | Định lý 2.5 lần đầu đo trên mã thật; phát hiện TC12 (gộp method cùng tên, bảo thủ) | **THUA**: chỉ 2/23 đơn vị chạy được, 0 thay đổi hành vi, nên không kết luận được gì | Vòng C bước 1 (hạ tầng): 14 method cần constructor có tham số; 1 method private bị name mangling; hera_pspec và cerberus import lỗi (không lưu log cài, sai phiên bản Python). Không phải lỗi lý thuyết. Sửa: amendment S-A1 |
| R16 | 31/10 | Study S-A1 (6de047c) | Chạy lại với receiver dựng từ constructor | `composition_inner.py`; Python theo manifest; lưu log cài | Giả định 4 trên tổ hợp thật: 12 đơn vị không có thay đổi "nảy sinh" khi ghép, không phụ thuộc thứ tự; 1 input masking chưa lặp lại | **THẮNG một phần**: 12/23 dùng được; cổng loại đúng 3 ô có thay đổi hành vi (pydal IS_STRONG.validate, 23/200 input), admit 45 ô | Còn THUA ở: hera_pspec không cài được (`uvtools>=0.2.0` không có bản cho Python 3.12; 9 đơn vị); G0 không sinh `bool` cho tham số `int`. Việc tiếp: 7.8 |
| R17 | 31/10 | Paper build (cb65df4) + submission check | PDF có Study S | — | — | **THẮNG** | — |
| R18 | 31/10 | Study S-A2 (c2eb155) | Thay một phần `int` bằng `bool`; thử cài hera_pspec bằng Python 3.11 | `subst()` trong `composition_inner.py`, fallback 3.11 | Dự đoán viết trước: các phép viết lại nhạy với bool đổi hành vi nhiều hơn → đúng một phần (IS_STRONG 23 → 29/200). **Lần đầu thấy phụ thuộc thứ tự trên mã thật** (pydal `QueryBuilder.parse`, 1/200 input) | **THUA một phần**: biến thể mới chạy một lần, chưa loại được nhiễu; hera_pspec vẫn không cài được (`uvtools>=0.2.0` không có bản phù hợp cho 3.11 lẫn 3.12) | Vòng C bước 4: viết phép kiểm loại nhiễu, chạy mỗi biến thể hai lần (S-A3). Quy tắc quyết định viết trước: chỉ báo phụ thuộc thứ tự là thật nếu còn sau S-A3 |
| R19 | 31/10 | Study S-A3 (đang chạy) | Lặp lại mọi biến thể | Chỉ tính input ổn định ở O và mọi biến thể | — | *chờ kết quả* | — |

## C. Vòng debug khi THUA (làm theo thứ tự)

1. **Lỗi hạ tầng** (YAML, token, LaTeX, proxy)? Chạy `Gatekeeper failure audit` và sửa. Đây không phải lỗi lý thuyết.
2. **Mã có làm đúng điều bài chứng minh không?** Đối chiếu với [THEORY_CODE_AUDIT](paper/THEORY_CODE_AUDIT.md) và thêm dòng TC nếu thấy chỗ mới.
3. **Giả định có đúng trên dữ liệu thật không?** (i.i.d., TV ≤ ξ, Giả định 4.) Nếu sai trên dữ liệu thì đổi thuật toán, như cạnh enabling ở R8 → R9, không đổi dữ liệu.
4. **Chứng minh có lỗ hổng không?** Viết phản ví dụ bằng số; thêm một phép kiểm C mới vào `tools/theory_checks.py`.
5. **Sửa xong:** viết amendment nếu study đã freeze, chạy lại bằng workflow, rồi thêm một dòng mới vào bảng B.

---

## Quy tắc chung (đọc trước khi bắt đầu)

1. **Không viết con số nào vào bài nếu nó không có trong một tệp kết quả của repo.** Mỗi con số phải trỏ được tới một tệp JSON hoặc MD trong `research_closure/results/` và một run trên GitHub Actions.
2. **Kế hoạch trước, dữ liệu sau.** Mọi phân tích xác nhận phải được commit trước khi chạy. Phân tích làm sau khi thấy dữ liệu phải ghi rõ "sau khi thấy dữ liệu", như Q-A1.
3. **Kết quả âm vẫn báo cáo.** HQ1 không được ủng hộ là một kết quả, không phải thất bại.
4. **Mỗi lần chạy trên GitHub Actions:** ghi run id vào PROCESS_LOG. Nếu thất bại, chạy workflow `Gatekeeper failure audit` để xem nguyên nhân gốc trước khi chạy lại.
5. **Không sửa tệp đã đóng băng** (có trong `study_*/FREEZE.json`). Muốn đổi thì viết amendment.
6. **Sau MỖI lần chạy:** thêm một dòng vào bảng B (mục trên), cập nhật bảng điểm A, và nếu kết quả là THUA thì làm vòng debug C.

---

## Giai đoạn 0: chốt câu chuyện của bài (1 tuần, cần thầy duyệt)

- [ ] **0.1 Đọc lại ba tài liệu theo thứ tự:** [TRACKING_FSE](TRACKING_FSE.md) mục 2 (đối chiếu kỳ vọng), [STUDY_Q_RESULT](../research_closure/results/study_q/STUDY_Q_RESULT.md), [THEORY](paper/THEORY.md) mục 7.
  *Xong khi:* tự viết được, trong 5 câu, bài này khẳng định gì và không khẳng định gì.
- [x] **0.2 Chọn khung bài.** Có hai khung hợp lý theo dữ liệu hiện có:
  - **(A) Bài phương pháp và lý thuyết:** chấp nhận thay đổi mã có kiểm soát rủi ro (Định lý 4′, 6′, 7′ đã sửa) cộng bằng chứng thực nghiệm trung thực, gồm kết quả âm của Study D–H và đồ thị pha các cổng.
  - **(B) Bài thực nghiệm về oracle:** "khoảng 11% patch resolved trên SWE-bench Verified khác hành vi bản fix trên đầu vào hợp lệ" (Study Q, Q-A1), với lý thuyết là phần phụ.
  *Xong khi:* thầy chọn một khung, ghi vào TRACKING_FSE mục 4. **→ Đã chọn khung A (31/10/2026).**
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

> **Trạng thái 31/10/2026:**
> - 2.1 [`paper/NUMBERS_MAP.md`](paper/NUMBERS_MAP.md): mọi số của bản nháp → nguồn thật hoặc BỎ.
> - 2.2 [`paper/latex/sections/evaluation.tex`](paper/latex/sections/evaluation.tex): chỉ số đo được; `tools/check_paper_numbers.py` kiểm ở mỗi lần build.
> - 2.3 nêu trong [`threats.tex`](paper/latex/sections/threats.tex) là chưa kiểm; **thiết kế phép đo vẫn cần thầy quyết**.
> - 2.4 3/31 đơn vị; độ nhạy 11/36 = 30,6%.
> - 2.5 EVIDENCE_LEDGER.
> - Sửa một lỗi diễn giải: "0/2.400" là kiểm tính không trạng thái của harness, không phải đo tác hại.

- [x] **2.1 Lập bảng "số trong bài → tệp nguồn":** mỗi con số của Bảng 1, 2, 3 và Hình 3 trong bản nháp đi kèm (a) tệp kết quả thật, hoặc (b) "BỎ".
  *Xong khi:* không còn con số projected nào trong bài. Mọi số của SkillShift-SE (180 cặp, 22,7% → 5,1%, 41/46, …) đều là projected, nên phải bỏ, trừ khi thật sự xây benchmark đó.
- [x] **2.2 Đưa các kết quả đã có vào bài:**
  - Study D–H: 0/2.400 khác biệt (kết quả âm về kỹ năng);
  - đồ thị pha các cổng (`paper_snippets/P0_AND_PHASE_DIAGRAM.md`);
  - Study P: 16/205 = 7,8%, RQ5;
  - Study Q: Q2 = 43,1%, Q4 = 11,1%, HQ1 không ủng hộ, Q5 = 3,88;
  - Q-A1: 8/36 = 22,2%, đồng thuận 87,7%;
  - RQ3: `D2_cerberus`.
- [ ] **2.3 Quyết định về Giả định D:** hoặc đo trên một mẫu cặp kỹ năng có footprint rời nhau (cần thiết kế study mới, có đăng ký trước), hoặc nêu nó là giả định chưa kiểm trong Threats.
- [x] **2.4 (Nếu chọn khung B)** Giới hạn "bản fix trả giá trị ≠ đầu vào hợp lệ": đếm số đơn vị HQ1 mà mọi mục là đối tượng giả do G2 dựng. Đây là phân tích sau khi thấy dữ liệu, phải ghi nhãn rõ.
- [x] **2.5 Ghi vào EVIDENCE_LEDGER** run id và commit cho mọi kết quả đưa vào bài.

## Giai đoạn 3: dọn nợ kỹ thuật ảnh hưởng tới tính tin cậy (song song với giai đoạn 2)

> **Trạng thái 31/10/2026:** 3.1, 3.2, 3.4, 3.5 xong; 3.3 đã ghi trong Threats, còn bản sửa mã cho study sau. Chi tiết: [TECH_DEBT](TECH_DEBT.md).

- [x] **3.1 Freeze lệch của Study B, C, N, P** (xem PROCESS_LOG): viết amendment hoặc giải thích trong EVIDENCE_LEDGER cho từng study.
  *Xong khi:* `python tools/freeze_study.py verify study_<x>` cho kết quả đã giải thích được với mọi study.
- [x] **3.2 Q5 trong `q_analyze.py`** tính khác định nghĩa của giao thức: ghi chú trong bài là dùng số tính lại (3,88).
- [ ] **3.3 Lỗi `FileNotFoundError`** của 4 instance trong Study Q (patch tạo tệp mới): ghi trong Threats; sửa công cụ cho study sau.
- [x] **3.4 Token Vertex hết hạn sau khoảng 1 giờ:** mọi workflow gọi model chạy lâu nên chia job (như `study-q-review-rate.yml`). Xem API_AND_FAILURES mục 3.
- [x] **3.5 Chạy `Gatekeeper failure audit`** và kiểm rằng mọi lần thất bại đều có nguyên nhân được ghi trong API_AND_FAILURES.

## Giai đoạn 4: viết bài (2 đến 3 tuần)

> **Trạng thái 31/10/2026:** bản bài đầy đủ theo khung A ở [`paper/latex/main.tex`](paper/latex/main.tex), PDF 6 trang ở [`paper/latex/build/paper.pdf`](paper/latex/build/paper.pdf) (workflow `Gatekeeper paper LaTeX build`; mỗi lần build kiểm 16 con số).
> - 4.1, 4.2, 4.3, 4.5, 4.6 xong.
> - 4.4: 7 trích dẫn placeholder đều có thật nhưng sai tên ([`paper/CITATIONS_AUDIT.md`](paper/CITATIONS_AUDIT.md)); đã sửa trong `refs.bib`. Tác giả MemCoder và MemGovern đã bổ sung đủ.
> - **Còn lại của giai đoạn 4:** một người đọc độc lập (1.9); thầy đọc toàn bài; cân số trang theo venue (FSE: 10 trang + tài liệu tham khảo, nên còn chỗ để mở rộng Evaluation nếu thầy muốn).

Thứ tự viết nên đi từ phần chắc nhất tới phần khó nhất:
- [x] **4.1 Phần Method / Theory** (từ THEORY.md, đã có chứng minh).
- [x] **4.2 Phần Evaluation:** mỗi RQ một tiểu mục; mỗi tiểu mục gồm câu hỏi, cách đo, kết quả kèm khoảng tin cậy, và giới hạn.
- [x] **4.3 Threats to validity:** ít nhất các mục sau:
  - người chấm thứ hai cùng họ model;
  - 19/55 đơn vị không tái tạo được;
  - G2 xem diff của bản fix;
  - đối tượng giả do G2 dựng;
  - khung là các bản nộp công khai lấy được;
  - Giả định D chưa kiểm;
  - ξ_s không đo được.
- [x] **4.4 Related work:** đọc lại reading list. **Kiểm từng trích dẫn** qua DBLP, arXiv hoặc DOI; bảy mục có tác giả "Authors" (PAPER_AUDIT, N4) phải được thay bằng tác giả thật hoặc bỏ.
  *Xong khi:* không còn mục nào có tác giả placeholder.
- [x] **4.5 Introduction và Abstract viết sau cùng**, chỉ dùng số đã có ở 4.2.
- [x] **4.6 Bỏ banner "projected"** chỉ khi giai đoạn 2.1 đã xong.

## Giai đoạn 5: kiểm trước khi nộp (1 tuần)

> **Trạng thái 31/10/2026:**
> - 5.1–5.3 tự động hoá, đã pass trên Actions: workflow `Gatekeeper submission check` (tái lập + artifact ẩn danh) và `Gatekeeper paper LaTeX build`.
> - 5.4: đã chuyển sang `acmsmall` một cột, `review,anonymous` (FSE 2027); **giới hạn trang và hạn nộp phải xác minh trên trang chính thức**.
> - 5.5: việc của thầy.
> - Danh sách việc của người: [`paper/SUBMISSION_CHECKLIST.md`](paper/SUBMISSION_CHECKLIST.md).

- [x] **5.1 Kiểm tái lập:** người khác clone repo, chạy `python -m unittest discover -s tests` (343+ test pass) và workflow `theory checks`, rồi được cùng số.
- [x] **5.2 Artifact ẩn danh** (double-blind): repo hiện công khai và có tên người dùng. Tạo bản ẩn danh (ví dụ anonymous.4open.science), bỏ tên và email trong commit.
- [x] **5.3 Kiểm số lần cuối:** mỗi con số trong PDF có trong bảng 2.1.
- [ ] **5.4 Kiểm định dạng:** số trang, template ACM, mục Data availability chỉ mô tả những gì thật sự có trong artifact (bản nháp mô tả nhiều thứ không có, PAPER_AUDIT N5).
- [ ] **5.5 Thầy duyệt bản cuối;** ghi vào PROCESS_LOG ngày nộp và mã bài.

## Giai đoạn 6: sau khi nộp

> **Trạng thái 31/10/2026: bài CHƯA nộp.** Đã chuẩn bị sẵn:
> - 6.1: workflow `Gatekeeper submission snapshot` + `tools/snapshot_submission.py` (có test). Chạy ngay sau khi nộp, với venue và mã bài; nó lưu PDF, SHA-256 của PDF và artifact, commit, rồi gắn tag `submitted-<venue>-<mã>`.
> - 6.2: mẫu [`paper/REVIEW_RESPONSE.md`](paper/REVIEW_RESPONSE.md) và 16 phản biện giả định có câu trả lời soạn sẵn [`paper/ANTICIPATED_REVIEWS.md`](paper/ANTICIPATED_REVIEWS.md).

- [ ] **6.1 Lưu bản nộp** (PDF, commit hash của artifact) vào `docs/paper/submitted/`.
- [ ] **6.2 Khi có phản biện:** mỗi ý kiến một dòng trong `docs/paper/REVIEW_RESPONSE.md`: ý kiến, đồng ý hay không, đã sửa ở đâu.

## Giai đoạn 7: tăng sức cho bài tới chuẩn A* (đang làm)

- [x] **7.1 Thư viện kỹ năng đa dạng:** 12 họ, Study R2 (giao thức trước, amendment R2-A1, R2-A2).
- [x] **7.2 Rà lý thuyết ↔ mã:** [THEORY_CODE_AUDIT](paper/THEORY_CODE_AUDIT.md), TC1–TC11; C10, C11.
- [x] **7.3 Luật thực thi chặt hơn:** cạnh enabling, footprint có tên module.
- [x] **7.4 (S7) Đo tác hại thật của tổ hợp:** Study S + S-A1 (12/23 đơn vị). Mô tả ban đầu: chọn các cặp chồng lấn trong R2 (6 ô tổ hợp) và các cặp enabling; viết oracle hàm (như Study D) cho từng cặp; chạy e-process cho ô đơn và ô tổ hợp. Cần giao thức trước. Chi phí 0 USD, chỉ tốn thời gian CI.
- [ ] **7.5 (S6) Admit thật với 12 họ** trên các target có oracle sẵn (Study D/E/G): dùng `drawharness` với skill R2. Cần giao thức trước.
- [ ] **7.6 (S8) Người chấm thứ hai là con người** cho Q-A1 (154 mục): việc của người.
- [ ] **7.7 (S5) Chạy GSE gốc** nếu có mã công khai (A12).
- [ ] **7.8 (S7, phần còn lại) Study S mở rộng:**
  - cài hera_pspec bằng Python 3.11 hoặc từ nguồn `uvtools`;
  - thêm bộ sinh input dựa trên kiểu thật, ví dụ sinh `bool` cho tham số `int` vì `bool` là lớp con của `int`.

  Cả hai đều cần amendment S-A2 viết trước khi chạy.

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
