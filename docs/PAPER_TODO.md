# To-do list hoàn thành bài báo, từ đầu tới lúc nộp

Dành cho người **chưa có kinh nghiệm nghiên cứu**. Làm từ trên xuống. Mỗi việc có: **làm gì**, **vì sao**, **xong khi nào** (tiêu chí kiểm được), **ở đâu** (tệp, workflow). Đánh dấu `[x]` khi xong, và ghi một dòng vào [`docs/PROCESS_LOG.md`](PROCESS_LOG.md) mỗi lần hoàn thành một việc.

Trạng thái tổng hợp: [TRACKING_FSE](TRACKING_FSE.md). Lý thuyết: [THEORY](paper/THEORY.md). Lỗi của bản nháp: [PAPER_AUDIT](paper/PAPER_AUDIT.md). API và lỗi khi chạy: [API_AND_FAILURES](API_AND_FAILURES.md).

---

## A. Bảng điểm: bài đã đạt chuẩn A* (ISSTA/FSE/ICSE) hoặc Q1 (TOSEM/TSE/EMSE) chưa?

Cập nhật sau **mỗi** lần chạy. **THẮNG** = đạt, có bằng chứng trong repo. **THUA** = chưa đạt; mỗi ô THUA phải có một việc trong lộ trình D.

| # | Tiêu chí | Trạng thái | Bằng chứng / việc |
|---|---|---|---|
| S1 | Lý thuyết đúng, mọi mệnh đề có chứng minh, kiểm bằng số | **THẮNG** | 5 vòng kiểm chứng minh; C1–C11 |
| S2 | Mã làm đúng lý thuyết đã chứng minh | **THẮNG** | THEORY_CODE_AUDIT TC1–TC24 |
| S3 | Đóng góp mới, nói rõ cái gì không mới | **THẮNG** | Mục 5, Intro |
| S4 | Thực nghiệm thật, đăng ký trước, có kết quả âm | **THẮNG** | D, E, G, H, P, Q, R2, S |
| S5 | **Tiêu chí chính của bài FSE gốc:** thắng B6 ở cùng mức giữ lợi ích | **THẮNG** | Study T với B6-strong (replay trên mọi gói nguồn): B6 2 hại / 1.256 giữ; G 0 / 1.512 |
| S6 | Thắng baseline thống kê, smoke và B8 | **THẮNG một phần** | Tác hại rõ (Study T): smoke ngang G, rẻ hơn 10 lần. **Tác hại hiếm (Study U): G 0 hại, smoke 10, test pass 44** (thắng). Giữ lợi ích: G ≥ FS nhưng < B8 không bảo đảm (thua) |
| S7 | Nguồn đa dạng, đủ lớn | **THẮNG** | Study T: 60 gói phổ biến nhất PyPI, 235 kỹ năng có trên thị trường (Ruff), 1.465 ô có quyết định thật |
| S8 | Người chấm độc lập (model đã hiệu chuẩn) | **THẮNG** | 20/20 mỗi model; Q-A1 5/36 – 8/36 |
| S9 | Tái lập, artifact ẩn danh | **THẮNG** (chờ upload) | submission check |
| S10 | Venue, định dạng | **THẮNG** (sát giới hạn) | ISSTA 2027, 11/1/2027; nội dung 16 trang / giới hạn 18 |
| S11 | Chứng minh được kiểm độc lập | **THẮNG** | 5 vòng; vòng cuối chỉ còn ký hiệu |
| S12 | Câu hỏi B9 của bài gốc: so với để LLM sửa trực tiếp | **THẮNG** | T-A6: B9 gây hại 10/148 ô, đắt gấp 26 lần; G 0 hại |
| S13 | Retirement trên thay đổi môi trường thật | **THUA** (chỉ có demo) | → **D5** |
| S14 | Tổ hợp thật gây hại "nảy sinh" (minh hoạ Định lý 2) | **THUA** (chưa thấy) | → **D6** |
| S15 | Chi phí và điểm hoà vốn (RQ4 của bài gốc) | **THUA** (chưa đo) | → **D2** |

**Kết luận hiện tại:**
- **Phần lý thuyết và tính trung thực đã đạt.**
- **Phần "thắng baseline" chưa đạt**, vì tiêu chí chính của bài gốc (S5) đang thua.
- Bài **chưa** đủ mạnh cho A*. Lộ trình D bên dưới nhắm đúng vào các ô thua.

## A2. Điểm yếu chính hiện tại (rà ngày 1/11, sắp theo mức độ)

| # | Điểm yếu | Mức | Loại | Đang làm / hướng sửa |
|---|---|---|---|---|
| Y1 | ~~B9 chưa có số~~ | — | Đã đóng | **T-A6:** G 0 hại, B9 10/148, rẻ hơn 26 lần |
| Y2 | Ít ô có hại: Study T có 11 ô, nên "0/11 admit" chỉ cho cận trên khoảng 26% (Wilson); Study U có 44 ô, cận khoảng 8% | Cao | Thống kê | Báo CI trong bài; thêm nguồn có nhiều ô có hại hơn (Study U mở rộng: nhiều input/patch hơn, thêm benchmark) |
| Y3 | Giữ lợi ích kém B8 khi kiểm soát FWER trên nhiều ô (U2: 303 so với 621) | Trung bình | Thua thật, đã có lời giải post hoc | U-A1: e-BH giữ 626 (B8 621), 0 hại. Còn cần một study xác nhận viết trước |
| Y4 | Tác hại rõ thì smoke 20 draw ngang G và rẻ hơn 10 lần (Study T) | Trung bình | Thua thật | Bài đã nói rõ; Study U cho thấy G hơn khi tác hại hiếm |
| Y5 | Ground truth là "đổi hành vi trên input sinh ra", không phải test suite hay chuyên gia | Trung bình | Độ tin cậy oracle | T-A4: chạy test suite của gói làm oracle độc lập |
| Y6 | 40% ô Study T không thử được (hàm không gọi được, input không ổn định) | Trung bình | Môi trường | Báo cáo; harness gọi method tốt hơn |
| Y7 | Kỹ năng là luật viết sẵn, chưa có kỹ năng do agent tự học | Trung bình | Phạm vi | Threats; study riêng nếu còn thời gian |
| Y8 | Một môi trường duy nhất, nên retirement và fingerprint chưa có thay đổi môi trường thật | Thấp | Phạm vi | D5 |
| Y9 | Model chấm, judge và generator đều họ Gemini | Thấp | Độ độc lập | Đã hiệu chuẩn (20/20); thêm họ model khác nếu có quyền truy cập |

## D. Lộ trình research (đọc kỹ nếu chưa có kinh nghiệm)

### D0. Nguyên tắc (không được vi phạm)
1. **Viết tiêu chí thắng trước khi chạy.** Mỗi study có `PROTOCOL.md` commit trước; ghi rõ "thắng" là gì và "thua" là gì.
2. **Thua thì báo thua.** Không đổi tiêu chí sau khi thấy dữ liệu. Phân tích làm sau khi thấy dữ liệu phải gắn nhãn *post hoc*.
3. **Mọi kết quả lên `main`.** Workflow chạy trên `main`; tệp kết quả nằm ở `research_closure/results/<study>/`; thêm một dòng vào bảng B.
4. **Đa dạng và minh bạch:** nhiều repo, nhiều loại thay đổi, dữ liệu công khai, ghi rõ license và cách chọn mẫu (không chọn tay).
5. **Hữu ích:** công bố bộ dữ liệu, công cụ và quy trình để người khác chạy lại.

### D1. Giữ lợi ích ngang B6-R mà vẫn chặn tác hại (đóng S5, quan trọng nhất)
- **Vấn đề của bài gốc:** tiêu chí chính "thắng B6-R ở cùng mức giữ lợi ích".
- **Chẩn đoán từ dữ liệu:**
  - Ô bị bỏ sót có lợi ích −0,11, nhỏ hơn biên θ = 0,2. Gate đòi "có lợi rõ" trong khi B6-R chỉ đòi "không lỗi khi replay".
  - Vậy hai bên so khác câu hỏi. So công bằng là: **"admit khi không có hại"** (chỉ dùng harm certificate) so với B6-R, rồi tách riêng câu hỏi "có lợi".
- **Việc:**
  - **D1.1** Viết giao thức `study_d2/PROTOCOL.md`. Luật hai tầng: *admit an toàn* = harm certificate (tác hại < η); *chứng nhận có lợi* = e-process lợi ích (như cũ).
  - **D1.2** Phân tích lại trace đã ghi của D, E, G, H (có sẵn, 0 USD). Gắn nhãn *post hoc*, vì dữ liệu đã thấy.
  - **D1.3** Kiểm xác nhận trên **dữ liệu mới** (D3), không dùng lại D–G.
- **Tiêu chí thắng (viết trước):** ở cùng số ô có lợi hoặc vô hại được giữ (≥ mức của B6-R), số ô có hại được admit **nhỏ hơn hẳn** B6-R; tỉ lệ admit sai ≤ α.
- **Nếu thua:** báo cáo, rồi chạy vòng debug C. Câu hỏi đầu tiên: η, c có hợp lý không? Ngân sách draw có đủ không?

### D2. Chi phí: thắng B8 và fixed-sample về số lần chạy (đóng S6, S15)
- **Vấn đề của bài gốc:** RQ4, chi phí và điểm hoà vốn (bài gốc dùng số chưa đo).
- **Chẩn đoán:**
  - Ở trường hợp không có tác hại, gate tuần tự cần 110 draw, fixed-sample cần 99. Giới hạn khi c → 1 cũng là 99, nên **không thể thắng fixed-sample** ở trường hợp này.
  - Lợi thế thật nằm ở **ô có hại: dừng sau khoảng 2 draw**, trong khi fixed-sample luôn chạy đủ n.
- **Việc:**
  - **D2.1** Định nghĩa chi phí = số lượt chạy tới quyết định (ASN), tính trên **tập ô thực tế**, gồm cả ô hại lẫn ô không hại.
  - **D2.2** So gate tuần tự, fixed-sample (n = 99), B8 (300 draw + suite) và smoke test trên cùng ô của D3. Tính điểm hoà vốn: sau bao nhiêu lần tái sử dụng thì chi phí chứng nhận được bù lại.
  - **D2.3 (tối ưu):** gate lai. Chạy tuần tự, nhưng tới n = 99 thì dùng thêm kiểm định cố định, với α chia đôi (hợp lệ theo phép hợp cận; viết chứng minh trước).
- **Tiêu chí thắng:** ASN của gate (hoặc gate lai) < ASN của fixed-sample **trên tập ô thực tế** ở cùng mức lỗi; chi phí < B8 ít nhất 30%.
- **Nếu thua:** báo cáo và giữ lập luận "hợp lệ khi dừng tuỳ ý", không khẳng định về chi phí.

### D3. Bộ dữ liệu đa dạng, đủ lớn: Study T (giao thức `study_t/PROTOCOL.md`, đã commit; kỹ năng = rule autofix của Ruff + R2) (đóng S7; là dữ liệu xác nhận cho D1, D2)
- **Nguồn:**
  - 12 họ kỹ năng (R2) trên **mọi** site của 16 repo hiện có (467 hàm);
  - thêm khoảng 50 gói PyPI phổ biến, chọn theo thứ hạng tải về công khai (không chọn tay), cố định danh sách trước khi chạy.
- **Oracle không cần người:**
  - **Tác hại:** hành vi khác bản gốc trên input sinh từ chữ ký hàm, có thay `bool` cho `int` (đã kiểm ở S), mỗi phiên bản chạy hai lần.
  - **Bộ test của repo:** dùng làm ground truth phụ.
- **Ô:** (họ kỹ năng, repo); dự kiến hàng trăm ô.
- **Việc chuẩn bị:** các manifest R2 hiện có `"P": []` (chưa có ví dụ nguồn để replay). Trước khi chạy, mỗi họ cần **một ví dụ before/after thật** lấy từ một commit sửa lỗi công khai (như hera_pspec PR #485 của `none_identity`), từ repo **không** nằm trong danh sách target, ghi nguồn rõ ràng.
- **Baseline trên cùng ô:**
  - B2 (bind);
  - B6-R (replay trên ví dụ nguồn + fingerprint);
  - B8 (mọi input + suite);
  - smoke 20 draw;
  - fixed-sample;
  - gate của mình.
- **Tiêu chí thắng (viết trước):** như D1 và D2, cộng với tỉ lệ admit sai thực tế ≤ α.
- **Chi phí:** 0 USD (GitHub Actions).
- **Kết quả:** `research_closure/results/study_t/`, cộng một *datasheet* (nguồn, license, cách chọn, giới hạn).

### D4. B9: so với để LLM sửa trực tiếp (đóng S12)
- **Vấn đề của bài gốc:** B9 là mục tiêu đồng-chính; hiện đang HOLD.
- **Việc:**
  - Chọn ngẫu nhiên khoảng 30 ô của D3.
  - Cho model sửa trực tiếp với cùng ngân sách lượt chạy.
  - So tỉ lệ tác hại và chi phí.
- **Chi phí ước tính:** 2–5 USD (Gemini). Có giới hạn tiền cứng (`SpendGuard`).
- **Tiêu chí thắng:** gate có tỉ lệ tác hại thấp hơn ở chi phí không cao hơn.

### D5. Retirement trên thay đổi môi trường thật (đóng S13)
- **Việc:**
  - Chạy lại các ô của D3 trên phiên bản phụ thuộc hoặc Python khác (ví dụ 3.11 → 3.12, bản phụ thuộc mới hơn).
  - Đo: fingerprint đổi có trùng với hành vi đổi không, và chứng nhận cũ còn đúng không.
- **Tiêu chí thắng:** retirement theo fingerprint bắt được mọi ô mà hành vi đổi, kèm chi phí kiểm lại (sổ cái epoch).

### D6. Tìm tổ hợp thật gây hại "nảy sinh" (đóng S14)
- **Việc:** chạy Study S trên mọi cặp kề nhau của D3 (gồm khoảng 50 gói mới).
- **Tiêu chí:** ghi nhận mọi trường hợp nảy sinh, masking hoặc phụ thuộc thứ tự, kèm ví dụ cụ thể.
- **Nếu không thấy:** báo cáo là trên mã thật các tổ hợp này cộng tính. Đó là kết quả hữu ích: thiết kế "chỉ kiểm thành phần liên thông" là đủ và rẻ.

### D7. Viết lại và nộp
- Cập nhật mục Evaluation theo D1–D6 (bảng mới: thắng hay thua với từng baseline).
- Kiểm chứng minh mọi mệnh đề mới (gate lai D2.3) bằng `Gatekeeper model stand-ins`.
- Submission check, rồi nộp ISSTA 2027: tóm tắt **8/1/2027**, bài **11/1/2027**.

### Thứ tự làm và thời gian dự kiến
1. **D1.2** (vài giờ, dùng dữ liệu cũ, chỉ để định hướng).
2. **D3** (giao thức trước; 1–2 tuần CI).
3. **D1.3 và D2** (phân tích trên D3).
4. **D6, D5** (dùng lại hạ tầng của D3).
5. **D4** (cần tiền).
6. **D7.**

Chậm nhất ngày **20/12/2026** phải xong D1–D3, để còn 3 tuần viết.

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
| R19 | 31/10 | Study S-A3 (ef8e41a) | Lặp lại mọi biến thể | Chỉ tính input ổn định ở O và mọi biến thể | Quy tắc viết trước: phụ thuộc thứ tự ở R18 không còn sau khi lặp → là **nhiễu**, không báo là phát hiện. Giả thuyết nguyên nhân: `PYTHONHASHSEED` ngẫu nhiên giữa các tiến trình | **THẮNG**: kết quả cuối sạch. 12 hàm, tổ hợp cộng tính (0 nảy sinh, 0 masking, 0 phụ thuộc thứ tự); cổng loại đúng 3/48 ô có thay đổi hành vi | Còn: hera_pspec (9 đơn vị) không cài được; nên cố định `PYTHONHASHSEED` ở các lần chạy sau |
| R20 | 31/10 | Paper build (10cccea) | PDF có kết quả cuối của Study S | — | — | **THẮNG**: 14 trang, 47/47 con số khớp | — |
| R21 | 31/10 | Tra venue (WebSearch) | Giới hạn trang, hạn nộp | — | — | **THUA → đổi hướng**: FSE 2027 đã hết hạn (2–3/10). Chọn ISSTA 2027 (11/1/2027, 18 trang): **THẮNG** | — |
| R22 | 31/10 | Rà yếu điểm bằng máy | Kiểm yêu cầu bắt buộc của venue | Thêm mục Data Availability; DOI Smith 2015; sửa câu "a single command" thành "four commands" cho đúng README | — | **THẮNG** | — |
| R23 | 31/10 | Study S-A4 (3e8a99e) | Cài các gói HERA từ GitHub | `--s-a4`, cố định `PYTHONHASHSEED` | — | **THUA** với hera_pspec; kết quả 12 đơn vị lặp lại y hệt S-A3 (ổn định với hash seed cố định) | Vòng C bước 1, **tìm ra nguyên nhân gốc** từ log: harness đặt `SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0` cho mọi gói, nên `uvtools` build từ mã nguồn thành 0.0.0. Sửa: S-A5 |
| R24 | 31/10 | Study S-A5 (684b956) | Phiên bản giả chỉ áp cho gói đang kiểm | `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_<NAME>` | — | **THẮNG**: hera_pspec cài được; 16/23 đơn vị dùng được; tổ hợp cộng tính; cổng loại đúng 3/64 ô | Còn 7 đơn vị gọi không được (6 crash, 1 property) |
| R25 | 31/10 | Model stand-ins (41229462629, a2a004c) | Người chấm thứ 3; model kiểm chứng minh; 3 phản biện giả lập | `qa1_three_raters.py`, `llm_review.py` | **Model tìm 5 điểm chứng minh** (sổ cái theo scope, thời điểm dừng của e-Holm, Giả định 3 trong Định lý 2, luật thực thi cho thành phần đơn, tính hiện thực ở Mệnh đề 1b), đều đúng, đều đã sửa. Phản biện: accept / strong accept / weak accept; 13 điểm, xử lý trong MODEL_REVIEW_RESPONSE.md | **THẮNG một phần**: cả hai model chấm R cho toàn bộ 154 mục, nên κ vô nghĩa; theo đa số 3 người chấm, Q-A1 thành 5/36 | Vòng C bước 2: model chấm có phân biệt R/B không? → phép kiểm hiệu chuẩn (R26) |
| R26 | 31/10 | Hiệu chuẩn người chấm (41230256324) | 20 mục biết trước đáp án | `rater_calibration.py` | — | **THẮNG**: argon 20/20, flash 20/20, nên hai model phân biệt được R/B; việc chấm R cho cả 154 mục là đánh giá thật, không phải thiên lệch | — |
| R27 | 31/10 | Paper round 5 (0d6eff1) | Sửa theo model review | Xem MODEL_REVIEW_RESPONSE.md; thêm bảng tổng quan các study; sửa câu sai "mọi study dùng seed drand" | — | **THẮNG**: 49/49 con số khớp | — |
| R28 | 31/10 | Chứng minh mọi mệnh đề (2ce2676) | Đi từ lý thuyết đã chứng minh tới mã | Harm certificate và e-Holm thành Mệnh đề có chứng minh; Bổ đề sổ cái; Giả định 4 / Hệ quả theo đồ thị kề (gồm cạnh enabling); điều kiện epoch; đo cộng tính chính xác trong Study S | Phát hiện: Giả định 4 với loss {0,1} ngầm đòi không task nào bị cả A và B đổi; công cụ S đo lỏng hơn (TC17), không đổi số báo cáo | **THẮNG**: 51/51 con số khớp; baseline B2, B6-R, B8 và gate của P khớp lý thuyết (TC19–TC22) | — |
| R29 | 31/10 | Sự cố push | — | — | — | **THUA do môi trường**: `git pull --rebase origin main` báo "Cannot rebase onto multiple branches", nên push không chạy và 3 workflow chạy trên commit cũ | Hủy 3 run, push lại, chạy lại trên 2ce2676 |
| R30 | 31/10 | Model kiểm chứng minh vòng 2, 3 (a2a82df, 92d049c) | Kiểm lại sau khi sửa | Vòng 2: 5 điểm nhỏ; vòng 3: 6 điểm nhỏ, 0 lỗi lớn | Vòng 3 chỉ ra **thứ tự chuẩn của ô tổ hợp** (TC24): một tập kỹ năng phải có một thứ tự áp dụng cố định; trước đó lý thuyết đếm theo tập còn thực thi phụ thuộc thứ tự | **THẮNG**: đã sửa cả 11 điểm, kèm `canonical_order` trong mã; cách đạt cận của Định lý 2 với loss nhị phân kiểm bằng số | — |
| R31 | 31/10 | Paper build (88f54c0) | PDF | — | — | **THẮNG**: 16 trang (giới hạn 18 + tham khảo), 51/51 con số khớp | — |
| R32 | 31/10 | Model kiểm chứng minh vòng 4 (ddfe12f) | Kiểm sau vòng 3 | — | 10/11 mệnh đề "correct"; còn 1: chứng minh Hệ quả 1 ngầm dùng tính giao hoán khi gom các thành phần bị xen kẽ trong thứ tự chuẩn | **THẮNG**: thêm phần (i) giao hoán vào Giả định 4 (phiên bản ngữ nghĩa của cạnh enabling) và bước hoán vị vào chứng minh | — |
| R33 | 31/10 | Model kiểm chứng minh vòng 5 (101db84); PDF (6fb8605) | Kiểm sau vòng 4 | — | 10/11 "correct"; điểm còn lại chỉ là ký hiệu ở Mệnh đề 3(a) | **THẮNG**: đã sửa ký hiệu. Phần lý thuyết hội tụ (lỗi lớn qua 5 vòng: 0; điểm nhỏ: 5 → 5 → 6 → 1 → 1 về ký hiệu); PDF 16 trang | — |
| R34 | 31/10 | Study T census (a42c8df) | Ba yếu tố thắng | — | — | **THẮNG**: 60 gói phổ biến nhất, 235 kỹ năng (225 rule Ruff thuộc 40 nhóm, 10 họ R2), 2.578 ô (1.171 Ruff gắn safe, 1.163 unsafe) | — |
| R35 | 31/10 | Study T-A1 (trước trial) | Sửa baseline không công bằng | Fixed-sample 99 → 199 draw (tính cho K = 2.578; ở 99 draw FS không thể admit gì) | — | **THẮNG** (công bằng trước khi chạy) | — |
| R36 | 31/10 | Study T trials (41237317062, 0ae6608) | 1.465 ô dùng được (1.439 Ruff) / 2.578 | — | Ground truth trên mẫu input độc lập; 12 ô có hại, đều được Ruff gắn "unsafe" hoặc "mixed" | **W2 THẮNG lớn:** G giữ 1.420 ô an toàn, nhãn Ruff giữ 633 (×2,2), cả hai 0 ô có hại; G admit an toàn 727/744 ô "unsafe". **W4 THẮNG** theo định nghĩa. **W1 THUA** theo định nghĩa chặt: G 0 ô có hại, thắng U (11) và B6-R (9), nhưng nhãn Ruff cũng 0. **W3 THUA:** G 198 draw so với B8 200. **Smoke 20 ngang G** về tác hại, giữ nhiều hơn 6 ô, rẻ hơn 10 lần | Vòng C: (1) **môi trường:** 961 ô không dùng được (467 không gọi được hàm, 494 thiếu input ổn định); shard 7 bị tắt runner nên thiếu 3 gói (đang chạy lại); phân tích im lặng bỏ qua gói thiếu, đã sửa. (2) **thua thật:** trên lint fix, tác hại khi có thì rõ (≥ 5%, smoke bắt hết) và rất hiếm (12/1.465), nên lợi thế "tác hại hiếm" và "dừng sớm" của G không phát huy. Hướng tiếp: (a) LLM judge (đang chạy); (b) test suite (T-A3), vì B8 thật gồm cả suite, đắt hơn nhiều; (c) báo cáo trung thực: G là luật tốt nhất trong các luật có bảo đảm (FS 1.400, B8 1.414) |
| R37 | 1/11 | Study T LLM judge (df0564b) | Baseline hiện đại: model đọc diff | gemini-flash chấm 2.578/2.578 ô, 2,20 USD | — | **THẮNG** cho G: LJ admit **6/11** ô có hại và giữ 1.064 ô an toàn; G 0/11 và 1.420. G hơn LJ ở cả hai chiều | — |
| R38 | 1/11 | Shard 7 chạy lại lần 1 (41237317062, attempt 2) | Thiếu 3 gói | — | — | **THUA do môi trường**, lặp lại: runner bị tắt sau khoảng 9 phút, cả hai lần | Vòng C bước 1: lỗi tất định, nhiều khả năng một input sinh ra cấp phát vài GB làm runner hết bộ nhớ. Sửa: T-A3, giới hạn 2 GB cho mỗi tiến trình con (`RLIMIT_AS`), chỉ áp cho shard 7; đang chạy lại |
| R39 | 1/11 | Shard 7 với T-A3 (00ffb43) + đưa Study T vào bài | Đủ 60/60 gói | Mục 7.4 mới, Bảng `tab:market`, Abstract, Intro, Threats; 4 phản biện giả định mới (A12, A22–A24) | Tiêu chí chính của bài gốc: thắng B6-R cả hai chiều | **THẮNG**: 1.559 ô dùng được (1.531 Ruff), 12 ô có hại. G 0 hại / 1.512 giữ; nhãn Ruff 0 / 677; B6-R 9 / 996; LJ 6 / 1.128; FS 0 / 1.492; B8 0 / 1.506; **smoke 0 / 1.518 (thua)**. 60/60 con số khớp | Còn THUA: W1 (hoà nhãn Ruff), W3 (chi phí), smoke test. Hướng: T-A4 test suite (oracle độc lập); nhóm kỹ năng có tác hại hiếm, nơi G có lợi thế |
| R40 | 1/11 | Paper build (ce3f5ab) | PDF có Study T | — | — | **THẮNG**: 18 trang tổng; nội dung tới trang 16 (Conclusion), trang 17 là Data Availability (không tính trang), sau đó là tham khảo. Giới hạn ISSTA: 18 trang nội dung, nên **chỉ còn khoảng 1–2 trang**; thêm nội dung mới phải rút gọn chỗ khác | — |
| R41 | 1/11 | T-A5 B6-strong (1c79be0) | B6 trung thành với bài gốc: replay trên mọi gói nguồn khác | `market_analyze.b6_strong` (post hoc, viết trước khi tính) | B6-R cũ yếu hơn B6 thật: replay fixture hoặc ví dụ tài liệu, thay vì repo nguồn | **THẮNG**: B6-strong 2 hại / 1.256 giữ, mạnh hơn B6-R (9 / 996); G 0 / 1.512 vẫn hơn ở cả hai chiều. B6-majority 10 / 1.503 | — |
| R42 | 1/11 | Study U (1c79be0) | Tác hại hiếm trên kỹ năng thị trường: 693 patch agent đã resolved trên SWE-bench | `rare_harm_study.py`, chia input gate/tham chiếu theo seed | Đóng điểm yếu "smoke ngang G" | **U1 THẮNG** (G 0, smoke 10, test pass 44 patch có hại). **U3 THẮNG** (dải 5–20%: smoke 10/33, G 0). **U2 THUA**: G giữ 303/649, FS 299, B8 621 | Vòng C: thua thật, không phải môi trường. Bảo đảm FWER trên 693 ô cần khoảng 190 draw sạch, trong khi trung bình chỉ có khoảng 149 input. Hướng: nhiều input hơn mỗi patch, hoặc e-BH (FDR) cho mục đích sàng lọc (amendment trước) |
| R43 | 1/11 | Báo cáo kết quả tự sinh (bcf2635) | Số liệu thống kê trước, đánh giá sau | `results_report.py`: số đếm, tỉ lệ, Wilson 95%, draw/ô, rồi cột đánh giá | — | **THẮNG** | Lộ ra Y2: 0/11 chỉ cho cận trên khoảng 26% |
| R44 | 1/11 | Study T-A6 B9 + U-A1 (8048fb7) | Câu hỏi đồng-chính của bài gốc: để model tự sửa | gemini-flash tự áp rule lên 150 ô; e-BH cho Study U | — | **B9-W THẮNG:** B9 gây hại ở 10/148 ô (2 ô vốn an toàn, nghĩa là model tự gây hại), 6 trả lời không parse được; G 0. Chi phí 0,0080 so với 0,0003 USD/ô (×26), 16,9 so với 2,3 giây. **U-A1 (post hoc):** e-BH giữ 626/649 (B8 621), 0 hại | — |

## C. Vòng debug khi THUA (làm theo thứ tự)

1. **Lỗi hạ tầng** (YAML, token, LaTeX, proxy)? Chạy `Gatekeeper failure audit` và sửa. Đây không phải lỗi lý thuyết.
2. **Mã có làm đúng điều bài chứng minh không?** Đối chiếu với [THEORY_CODE_AUDIT](paper/THEORY_CODE_AUDIT.md) và thêm dòng TC nếu thấy chỗ mới.
3. **Giả định có đúng trên dữ liệu thật không?** (i.i.d., TV ≤ ξ, Giả định 4.) Nếu sai trên dữ liệu thì đổi thuật toán, như cạnh enabling ở R8 → R9, không đổi dữ liệu.
4. **Chứng minh có lỗ hổng không?** Viết phản ví dụ bằng số; thêm một phép kiểm C mới vào `tools/theory_checks.py`.
5. **Sửa xong:** viết amendment nếu study đã freeze, chạy lại bằng workflow, rồi thêm một dòng mới vào bảng B.

---

## E. Lịch sử: các giai đoạn 0–7 đã làm (giữ để tra cứu; việc mới nằm ở D)

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
- [x] **0.3 Chọn hội nghị hoặc tạp chí và hạn nộp** → ISSTA 2027 (11/1/2027), xem SUBMISSION_CHECKLIST. (FSE, ICSE, ISSTA, ASE, EMSE, TOSEM). Ghi hạn, giới hạn số trang, double-blind hay không.
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
- [x] **7.8 (S7, phần còn lại) Study S mở rộng:** đã làm S-A2, S-A3. hera_pspec không cài được (đã báo). Mô tả ban đầu:
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
