# Nhật ký quá trình

Ghi mọi việc đã làm, theo thứ tự thời gian (UTC): làm gì, vì sao, bằng chứng ở đâu, kết quả ra sao. Mục mới thêm ở **cuối**. Trạng thái tổng hợp ở [TRACKING_FSE](TRACKING_FSE.md); cấu trúc repo ở [STRUCTURE](STRUCTURE.md).

Mẫu cho mỗi mục:

```
### <ngày giờ UTC> — <việc>
- Vì sao:
- Đã làm:
- Bằng chứng: commit / run / tệp
- Kết quả:
- Còn mở:
```

---

## 31/10/2026

### 06:47 — Đóng băng Study Q
- Bằng chứng: commit `94c87bc` ("Freeze Study Q"); `study_q/FREEZE.json` băm 68 tệp; seed drand lúc 2026-10-31T07:47:53Z.

### 06:50 và 07:59 — Stream run #1 và #2 thất bại
- Đã làm: chạy workflow `Gatekeeper Study Q stream` với `only=3`.
- Kết quả: job `plan` dừng với `AssertionError`, vì `3` không phải id instance (cần dạng `astropy__astropy-12907`). Không tốn chi phí model.

### 08:21 — Đưa patch `study_q_stream_msg` lên main
- Vì sao: ô `only` cần nhận nhiều định dạng hơn và báo lỗi rõ ràng thay cho `AssertionError`.
- Bằng chứng: commit `4898596`; `.github/workflows/study-q-stream.yml` có SHA-256 `a75e602e…`, khớp `research_closure/manifests/study_q_stream_msg.json`.
- Kết quả: `freeze_study.py verify study_q` báo 68 tệp không đổi (workflow không nằm trong freeze).

### 08:29 — Smoke 3 instance (run #3)
- Đã làm: `only = astropy__astropy-12907, astropy__astropy-13033, astropy__astropy-13236`.
- Bằng chứng: [run 41184775725](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41184775725).
- Kết quả: 3/3 thành công, `status: FINISHED, error: null`; seed `460798324973423911`. Mỗi instance khoảng 1 phút, artifact khoảng 1 KB.
- Còn mở: chưa mở artifact để xem có hàm dùng được không (sandbox của trợ lý không tải được artifact).

### 08:33 — Che token Vertex trong log
- Vì sao: log của run #3 in nguyên văn `GOOGLE_OAUTH_TOKEN` (`ya29…`) ở mọi bước sau bước "Vertex access token", do token được ghi vào `GITHUB_ENV` mà không che.
- Đã làm: thêm `echo "::add-mask::$t"` trước khi ghi token, ở cả 13 workflow có cùng mẫu; manifest `research_closure/manifests/workflow_mask_vertex_token.json`.
- Bằng chứng: commit `206da51`; cả 13 tệp YAML vẫn parse được; freeze Study Q không đổi.
- Còn mở: token đã lộ (sống khoảng 1 giờ) vẫn còn trong log của các run trước; nên xoá các log đó nếu cần.

### 08:33 — Bắt đầu stream part 0 (235 instance)
- Bằng chứng: [run 41185100083](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41185100083), chạy trên commit `206da51`; 236 job (1 plan + 235 instance); job `plan` thành công.

### 08:35 — Thêm file tracking
- Bằng chứng: commit `9ea7356`, `TRACKING_FSE.md` (nay ở `docs/`).
- Nội dung: 10 kỳ vọng của bài so với study tương ứng, checklist Study Q, quy tắc chọn khẳng định, nhật ký.

### ~08:50 — Thêm review kiến thức và công thức
- Bằng chứng: commit `635eebc`, `REVIEW_FSE.md` (nay ở `docs/paper/`).
- Đã làm: viết từ ghi chép của repo và mã nguồn (lúc này chưa có PDF); chạy lại mọi phép tính (vùng [0,75%; 10,87%], ngưỡng chịu hại 1,97%, 110 lần rút, alpha ledger, công suất HQ1 với n = 18).

### Sau đó — Kiểm tra toàn bộ bài FSE theo PDF gốc
- Vì sao: người nghiên cứu cung cấp 3 PDF và cho biết bản thảo do AI sinh, chưa chắc đúng.
- Đã làm:
  1. Kiểm SHA-256 của 3 PDF: khớp `research_closure/PRIVATE_SOURCE_DIGESTS.json`.
  2. Đọc toàn văn bằng `pdftotext`; kiểm từng định lý, mệnh đề, con số, trích dẫn; tính lại mọi phép tính tính lại được.
  3. Viết [`docs/paper/PAPER_AUDIT.md`](paper/PAPER_AUDIT.md): 9 lỗi toán (T1 đến T9), 7 lỗi số liệu và thống kê (S1 đến S7), 5 lỗi trình bày (N1 đến N5), mỗi lỗi kèm cách sửa; có phát biểu và chứng minh thay thế cho Định lý 4 và Định lý 7.
  4. Cập nhật `REVIEW_FSE.md` (bỏ ghi chú "[đối chiếu PDF]", thêm R13, R14) và mục 5 của `TRACKING_FSE.md`.
- Kết quả chính:
  - Định lý 4: hằng số 2ξ_s; α phải cấp theo ô; admit lại cần sổ cái.
  - Định lý 7: không thể đạt 1 − ε; cận đúng và chặt là 1 + min(a, b).
  - Mệnh đề 9: tỉ lệ phương sai đúng là 1 + 2σ_T²/σ_S².
  - CI [3,1; 9,8] không vượt biên 5 điểm.
  - Các tỉ lệ 5,1% / 11,5% / 22,7% không ứng với số nguyên trên 63 cặp có hại.
  - d̄ = 0,34 mâu thuẫn với 11,4%.
  - Phép tính số học đơn giản trong bài đều khớp.
- Còn mở: sửa bản LaTeX (repo không có `main.tex`); xác minh 7 trích dẫn placeholder.

### Sau đó — Sắp xếp lại repo
- Vì sao: gốc repo có khoảng 30 tệp lẫn lộn (tài liệu, script của gói cập nhật cũ, manifest, log).
- Nguyên tắc: **không chuyển** tệp nào nằm trong một `FREEZE.json` hoặc được workflow, công cụ hay test gọi tới. Trước khi chuyển, đã kiểm tham chiếu của từng tệp gốc bằng `grep` trên toàn repo và trên mọi `FREEZE.json`.
- Đã làm:
  - `docs/`: `TRACKING_FSE.md`, `PROCESS_LOG.md` (tệp này), `STRUCTURE.md`; `docs/paper/`: `REVIEW_FSE.md`, `PAPER_AUDIT.md`, `source/` (3 PDF); `docs/history/`: `RESEARCH_SUMMARY_D_E.md`, `REVIEW_RESPONSE_PLAN.md`, `START_HERE.md`, `START_HERE_VI.md`, `README_PRE_B9.md`, `RESULTS_AND_SCAN.md`, `WORKFLOW_FIX_RESULT.md`.
  - `archive/root_packages/`: `APPLY_CI_FIX.py`, `APPLY_NEXT_UPDATE.py`, `APPLY_UPDATE.py`, `CI_FIX_MANIFEST.json`, `DELTA_MANIFEST.json`, `FILE_CHANGES.md`, `MANIFEST_SHA256.json`, `MISSING_FILES.txt`, `PACKAGE_MANIFEST.json`, `PACKAGE_VALIDATION.json`, `SHA256.json`, `STATIC_VALIDATION.json`, `UPDATE_MANIFEST.json`, `UPDATE_PATHS.txt`, `hygiene.log`, `PACKAGE_CHECKS/`.
  - Xoá `study_p_feasibility.json` ở gốc: bản trùng y hệt (`cmp`) của `research_closure/manifests/study_p_feasibility.json`.
  - Sửa đường dẫn trong `README.md`, `README_VI.md`, `EVIDENCE_LEDGER.md` và các liên kết tương đối trong hai tệp đã chuyển vào `docs/`.
  - Thêm `.gitignore` (`__pycache__/`, `*.pyc`).
- Giữ ở gốc: `README.md`, `README_VI.md`, `EVIDENCE_LEDGER.md`, `RUN_P6_REMOTE.py` (workflow `p6-remote-smoke.yml` và `tests/test_remote.py` gọi tới).
- Không chuyển `study_*`, `tools/`, `gatekeeper_*`: đường dẫn của chúng nằm trong các `FREEZE.json` và workflow (lý do chi tiết ở [STRUCTURE](STRUCTURE.md)).
- Kiểm tra:
  - 339 unit test pass trước và sau khi sắp xếp; `tools/repo_hygiene.py`: 0 tệp trùng.
  - `freeze_study.py verify` trên 13 study có `FREEZE.json`, chạy ở commit trước (git worktree) và sau khi sắp xếp: **kết quả giống hệt nhau**. D, E, F, G, H, L, M, M-A\*, Q: verified.
  - **Phát hiện (đã có từ trước, không do đợt này):** B, C báo đổi `tools/run_study_d.py`; N báo đổi `tools/repo_hygiene.py`; P báo đổi `research_closure/results/ALIGNMENT_WITH_FSE.md`. Các study này đã xong. Cần ghi nhận như amendment, hoặc giải thích trong EVIDENCE_LEDGER, trước khi dùng làm bằng chứng đóng băng.

### 09:05 — Kiểm tra part 0 (lần 1)
- Bằng chứng: [run 41185100083](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41185100083), trạng thái `in_progress` sau khoảng 32 phút; `get_job_logs failed_only`: **0 job lỗi**.
- **Xác nhận bản sửa che token:** log job `Q_astropy__astropy-12907` (job 124490360875) in `GOOGLE_OAUTH_TOKEN: ***`.
- Còn mở: chưa chạy part 1 (chờ part 0 xong). Artifact mỗi instance vẫn khoảng 1 KB, cần mở ra kiểm tra trước khi phân tích.

### 09:14 — Part 0 xong; bắt đầu part 1
- Part 0: [run 41185100083](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41185100083) xong lúc 09:11, kết luận `success`, **0 job lỗi** trên 236 job (1 plan + 235 instance).
- Kiểm tra mẫu: artifact nhỏ (100 artifact đầu: 595 đến 1.806 byte, trung vị 734). Log cho thấy trạng thái khác nhau giữa các instance, ví dụ `django__django-13807`: `NOT_USABLE`; `astropy__astropy-13033`: `FINISHED`. Nghĩa là pipeline chạy đúng các nhánh của `tools/q_instance.py`.
- **Phát hiện, lệch giao thức:** giao thức mục 3 ghi "Chế độ ghi lại bật: lưu patch và mọi đầu ra". `q_instance.py` có bật `capture=True`, nhưng chỉ lưu **bản tóm tắt** (`q_classify.summarise`: số đếm theo loại C1/C2/C3) vào `Q_<id>.json`. Danh sách đầu ra từng đầu vào bị xoá cùng thư mục tạm. Patch vẫn truy lại được từ `POOL.jsonl.gz` qua `sha`. **Không sửa** công cụ vì đã đóng băng và đang chạy. Cần người nghiên cứu quyết: ghi một amendment mô tả lệch này, hoặc chạy lại có lưu đầu ra cho các instance cần kiểm tra thủ công.
- Part 1: [run 41187862326](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41187862326), 234 instance, bắt đầu 09:14 trên commit `3d8ff85`. Kiểm tra trước khi chạy: các tệp mà job dùng (`tools/q_instance.py`, `study_q/`, `research_closure/pilot/models.json`) không bị đợt sắp xếp lại đụng tới; `freeze_study.py verify study_q` vẫn verified.

### 09:59 — Part 1 xong
- [Run 41187862326](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41187862326): kết luận `success`, 0 job lỗi trên 235 job (1 plan + 234 instance). Không instance nào cần chạy lại.

### ~10:00 — Viết và chạy workflow tổng hợp
- Vì sao: chưa có workflow nào gọi `tools/q_analyze.py`; artifact sẽ hết hạn sau 90 ngày nên cần lưu bản ghi thô vào repo.
- Đã làm: `.github/workflows/study-q-analyze.yml` (commit `79ba306`). Workflow kiểm freeze; tải `Q_*` của các run được chỉ định (run sau thắng khi trùng); kiểm mỗi instance của khung có đúng một bản ghi; chạy `q_analyze.py`; commit `Q_ANALYSIS.json`, `FRAME_CHECK.json`, `Q_RECORDS.jsonl.gz`. Đã chạy thử `q_analyze.py` cục bộ trên bản ghi giả trước khi push.
- Bằng chứng: commit kết quả `9a8ab44` do bot đẩy lên; `FRAME_CHECK`: 469/469, không thiếu, không thừa.

### ~10:05 — Kết quả Study Q
- Chi tiết: [`research_closure/results/study_q/STUDY_Q_RESULT.md`](../research_closure/results/study_q/STUDY_Q_RESULT.md).
- Phễu: 245 `FINISHED`, 220 `NOT_USABLE`, 4 `ERROR` (`FileNotFoundError` khi patch tạo tệp mới); 694 patch được chấm.
- Q2 = 43,1%; Q4 = 11,1% (Wilson 9,0% – 13,6%).
- **HQ1 không được ủng hộ:** 6/55 = 10,9% (p ≈ 1), ngược hướng dự đoán từ RQ5. Mọi phân tích độ nhạy cho cùng kết luận.
- **Phát hiện thêm:** `q_analyze.py` tính Q5 bằng (khác biệt ngây thơ)/Q4 = 1,16, trong khi giao thức định nghĩa Q5 = Q2/Q4. Trợ lý tính lại theo giao thức từ bản ghi thô: 3,88 (bootstrap theo instance 3,08 – 5,14). Cả hai được báo cáo.
- Còn mở (cần người nghiên cứu và người hướng dẫn quyết):
  1. Có chạy lại 55 instance của HQ1 với đầu ra được lưu để chấm tay C1 không. Việc này cần amendment, vì là bổ sung sau khi thấy kết quả.
  2. Hướng viết bài theo nhánh "không bác bỏ" (TRACKING_FSE mục 4).
  3. ALIGNMENT_WITH_FSE.md (thuộc freeze Study P) không được sửa; kết luận mới nằm ở STUDY_Q_RESULT.md và TRACKING_FSE.md.

### ~10:10 — Người nghiên cứu chọn hướng 1: chấm tay các đơn vị HQ1
- Đã làm:
  - **Amendment Q-A1** (`study_q/AMENDMENTS.md`, commit `f275126`), ghi rõ là bổ sung sau khi thấy kết quả. Quy tắc tái tạo, cách chọn mục, bộ mã và người chấm được ghi trước khi xem ví dụ. Áp bằng `tools/amend_study.py`: seed vẫn gắn hash đóng băng gốc, freeze làm lại, `verify` OK.
  - Công cụ mới, kèm test:
    - `tools/q_review_capture.py`: bọc `q_instance.run`, không sửa nó; lưu đầu ra, đầu vào và patch;
    - `tools/q_review_items.py`: kiểm tái tạo, dựng mục chấm mù;
    - `tools/q_review_agreement.py`: tính đồng thuận và kết quả.
  - Workflow mới: `study-q-review-capture.yml`, `study-q-review-items.yml`, `study-q-review-rate.yml`.
  - Push tag `study_q-q-a1` bị proxy chặn (403); mốc của amendment là commit `f275126`.
- Smoke 2 instance (run 41192194052): cả hai tái tạo đúng hệt.
- Chạy đủ 55 instance (run 41192489807): 55/55 thành công. Dựng mục (run 41193394796): 36/55 tái tạo, 154 mục từ 31 đơn vị.
- Trợ lý chấm 154 mục (R 135, B 19) và commit `827b404` trước người chấm thứ hai, không mở `KEY.json`. Các output sympy được kiểm tương đương bằng sympy.
- **Người chấm thứ hai, lần 1** (run 41193552100): thất bại sau khoảng 60 phút với `ACCESS_TOKEN_EXPIRED`, không lưu gì. Nguyên nhân: `gcloud auth print-access-token` trả token còn trong bộ nhớ đệm, nên lần làm mới mỗi 25 phút của client không lấy được token mới.
  - Sửa: chia mục thành nhiều job (commit `5871c3f`); `tools/rq5_rate_llm.py` không đổi.
  - Lần 2 (run 41197881665, 6 job): thành công, 0,38 USD.
- Kết quả: đồng thuận 87,7%, kappa 0 (người chấm thứ hai mã R mọi mục); 28/31 đơn vị có hồi quy đã xác nhận; **8/36 = 22,2%** đơn vị tái tạo được không có hồi quy đã xác nhận (Wilson 11,7% – 38,1%). Kết luận HQ1 giữ nguyên. Chi tiết trong `STUDY_Q_RESULT.md`, mục Q-A1.
- Còn mở: viết lại khẳng định trong bài theo nhánh "không bác bỏ"; nêu giới hạn "bản fix trả giá trị ≠ đầu vào hợp lệ" (đối tượng giả do G2 dựng).

### ~12:30 — Rà lại lý thuyết, kế hoạch hoàn thành bài, API và lỗi khi chạy
- Vì sao: người nghiên cứu yêu cầu chứng minh lại các ý trong bản nháp (do AI sinh), sửa cho đứng vững, có to-do list chi tiết, và tài liệu API cùng nguyên nhân gốc của các lần chạy thất bại, kiểm lại được trên GitHub Actions.
- **Lý thuyết:** [`docs/paper/THEORY.md`](paper/THEORY.md). Với mỗi ý: bài viết gì, sai ở đâu, phát biểu đúng, chứng minh đầy đủ.
  - Định lý 4′: sổ cái α theo ô, gồm admit lại và tổ hợp; hằng số 2ξ.
  - Mệnh đề 6′(a), 6′(b): 2ξ là cần thiết và chặt, mới so với bản nháp.
  - Định lý 7′: cận chặt 1 + min(a, b).
  - Hệ quả 8′: cần Giả định D.
  - Mệnh đề 9′: công thức tổng quát.
- **Kiểm bằng số:** `tools/theory_checks.py` (dùng đúng e-process của repo; bản tính dồn được test là trùng với bản gốc), workflow `Gatekeeper theory checks`, run 41206524576. Kết quả trong `research_closure/results/theory/`. Ngân sách theo phạm vi cho tỉ lệ admit sai cả họ 45,4% (α = 10%), theo ô 5,1%.
- **To-do:** [`docs/PAPER_TODO.md`](PAPER_TODO.md), 6 giai đoạn, mỗi việc có tiêu chí "xong khi".
- **API và lỗi:** [`docs/API_AND_FAILURES.md`](API_AND_FAILURES.md).
  - Công cụ `tools/failure_audit.py` và workflow `Gatekeeper failure audit` đọc log của bước thất bại, phân nhóm, và commit `research_closure/results/failure_audit/`.
  - Lần 1 và 2 (run 41206526780, 41206699066) xếp sai: đọc cả log, bắt nhầm một tiêu đề bảng "HTTP 429", và chưa đọc đủ job của run có hơn 100 job. Lần 3 (run 41207250040) sửa cả hai và khớp với đối chiếu tay: 64 run thất bại, 14 nhóm.
- Còn mở: đưa các phát biểu đã sửa vào bài (PAPER_TODO giai đoạn 1); thiết kế phép đo cho Giả định D (giai đoạn 2.3).

### ~14:05 — Giai đoạn 1 của PAPER_TODO: đưa lý thuyết đã sửa vào bài
- Vì sao: repo không có bản LaTeX của bài, nên câu chữ sửa được viết thành các mục độc lập, dán thẳng vào bài được.
- Đã làm:
  - `docs/paper/latex/sections/problem.tex` (1.1), `theory.tex` (1.2–1.6), `related_stats.tex` (1.7), `refs.bib` (chỉ các tài liệu thống kê đã kiểm thông tin xuất bản), `main.tex` (chỉ để biên dịch thử).
  - `docs/paper/latex/CHANGES.md`: bảng "đoạn nào của bản nháp thay bằng đoạn nào", kèm các câu ở chỗ khác trong bài phải sửa theo (Abstract, §5.4, §7, §10.3, Threats, Keywords).
  - Workflow `Gatekeeper paper LaTeX build` (`paper-latex.yml`): biên dịch bằng TeX Live, dừng nếu còn tham chiếu hoặc trích dẫn không xác định, commit `build/theory_sections.pdf`. Run 41208218636 thành công.
  - PAPER_TODO: 1.1–1.8 đánh dấu xong.
- Còn mở: 1.9 (một người đọc độc lập kiểm từng chứng minh); dán vào bản bài chính khi có.

### ~14:30 — Rà soát giai đoạn 1 (yêu cầu "review kĩ và chứng minh")
- Kiểm từng bước của từng chứng minh (`docs/paper/PHASE1_REVIEW.md`). Tìm thấy 9 lỗ hổng, G1–G9.
- Lỗ hổng lớn nhất, **G1**: định lý chỉ bảo đảm cho ô được admit, không cho tập kỹ năng thực sự chạy chung. Sửa bằng luật thực thi, Giả định 4 cho tập, và Corollary "What actually runs".
- Thêm C8 (admit lại không có sổ cái: 0,45; có sổ cái: 0,04) và C9 (chứng chỉ tác hại của thí nghiệm ở biên h = η: tỉ lệ ≈ α; 0,394η; 110 lần rút).
- Tổng quát Lemma cho Y bị chặn bất kỳ, để bao cả chứng chỉ tác hại mà Study D–P dùng.
- Workflow: theory checks 41208862692, LaTeX build 41208865501, đều thành công.

### ~15:00 — Giai đoạn 2
- 2.1: `docs/paper/NUMBERS_MAP.md`. Mọi số của bản nháp được đánh dấu BỎ, hoặc thay bằng số đo gần nghĩa nhất (kèm tệp nguồn).
  - **Phát hiện:** "0/2.400" trong TRACKING là kiểm tính không trạng thái của harness, không phải đo tác hại. Đã sửa TRACKING. ALIGNMENT_WITH_FSE thuộc freeze nên không sửa; ghi chú trong NUMBERS_MAP.
- 2.2: `sections/evaluation.tex`, chỉ số đo được, mỗi số có chú thích nguồn. `tools/check_paper_numbers.py` tính lại 16 con số từ JSON và kiểm chúng có trong LaTeX; được gắn vào workflow build.
- 2.3: `sections/threats.tex` nêu Assumption 4 là **chưa kiểm**. Thiết kế phép đo cần thầy quyết.
- 2.4: 3/31 đơn vị chỉ có đầu vào là đối tượng giả; độ nhạy 11/36 = 30,6% (18,0% – 46,9%); kết luận HQ1 giữ nguyên.
- 2.5: thêm bảng nguồn vào `EVIDENCE_LEDGER.md`.

### ~15:30 — Chọn khung A; giai đoạn 3
- Người nghiên cứu chọn **khung A** (phương pháp và lý thuyết). Đã ghi ở TRACKING mục 4 và PAPER_TODO 0.2.
- **3.1 Freeze lệch:**
  - Study P: commit `c214516` thêm 8 dòng văn bản vào `ALIGNMENT_WITH_FSE.md` sau lần đóng băng cuối; kiểm tại commit đóng băng `6437ecf`: 91 tệp không đổi.
  - B, C, N: mã dùng chung, đóng băng trong phần lịch sử đã mất khi repo được tạo lại (gốc `656ab92`); bài không trích các study này.
  - Giải thích và quy tắc mới ghi trong `EVIDENCE_LEDGER.md`.
- **3.2** Q5: đã ghi trong Threats. **3.3** `FileNotFoundError`: tệp đã đóng băng nên chưa sửa mã; cách sửa cho study sau ghi ở `docs/TECH_DEBT.md`.
- **3.4 Token Vertex, sửa tận gốc:** `tools/fresh_gcp_token.py` tạo token mới bằng google-auth thay cho token cũ trong bộ nhớ đệm của `gcloud`; 13 workflow gọi model dùng nó làm `GK_TOKEN_CMD`. Workflow `Gatekeeper Vertex token check` (run 41210471245): hai token cách nhau một phút **khác nhau**, mỗi token còn hạn 60,0 phút. Có test.
- **3.5** Failure audit chạy lại (run 41210473427): vẫn 64 run thất bại, đều đã có nguyên nhân trong API_AND_FAILURES.

### ~16:00 — TD7: cài luật thực thi
- `gatekeeper_ext/execution.py`: tách tập kỹ năng sắp chạy thành các thành phần liên thông của đồ thị giao footprint; chỉ cho chạy khi mọi thành phần là một ô đã admit; có chọn tập con tham lam và danh sách tổ hợp còn phải kiểm.
- Đặt ở `gatekeeper_ext`, vì `freeze_study.py` so **cả tập** tệp của `gatekeeper_lite` (thêm một tệp ở đó sẽ làm mọi freeze báo lệch). Freeze của D, E, G, H, Q vẫn verified.
- 8 test, gồm test thuộc tính trên 300 thư viện ngẫu nhiên.

### ~16:30 — Giai đoạn 4: viết bài theo khung A
- **4.4 Kiểm trích dẫn** (`docs/paper/CITATIONS_AUDIT.md`): 7 mục placeholder đều là bài có thật ở đúng mã arXiv, nhưng **mọi tên bài trong bản nháp đều sai**. Ví dụ, GSE thật là "Learning Globally Reusable Skills for Coding Agents" (Yang và cộng sự); "Formal Skill Verification" là bài của Alfredo Metere. Phiên không vào được arxiv.org; đã tra qua tìm kiếm web.
- **Bản bài đầy đủ**, `docs/paper/latex/main.tex`: intro, motivation, approach, implementation, related, conclusion (mới); evaluation có RQ1–RQ4; abstract chỉ dùng số đo được.
- Build (run 41211396873): thành công, 6 trang, không còn tham chiếu thiếu; 16/16 con số khớp.
- Còn mở: chép đủ tác giả MemCoder và MemGovern; mục 1.9 (người đọc độc lập); thầy đọc toàn bài; số trang theo venue.

### ~17:00 — Giai đoạn 5: kiểm trước khi nộp
- **5.2 Artifact ẩn danh:** `tools/make_anonymous_artifact.py`.
  - Lấy các tệp được git theo dõi, bỏ ghi chú nội bộ (PROCESS_LOG, TRACKING, PAPER_TODO, các audit), PDF bản nháp, `archive/`, `docs/history/` và `.git`.
  - Thay link repo bằng `ANONYMOUS/gatekeeper-artifact`; quét văn bản và tệp `.gz` / `.tar.gz` theo tên tài khoản và tác giả trong `git log`.
  - Cục bộ: 1.708 tệp, 223 chỗ thay, **0 dấu vết**.
  - Bên trong artifact (không có `.git`): test pass, freeze D/E/G/H/Q verified, 16/16 rồi 19/19 con số khớp, kết quả kiểm lý thuyết **giống hệt từng byte** bản commit.
  - Có `README_ARTIFACT.md` và test.
- **5.1, 5.3:** workflow `Gatekeeper submission check` gồm job `repro` và `artifact`; run 41212215560 pass cả hai. Bộ kiểm số mở rộng sang Abstract (19 con số).
- **5.4:** tìm kiếm cho thấy FSE 2027 dùng `acmsmall` một cột với `review,anonymous`; bài đã chuyển (run build 41212373969: 10 trang tính cả tài liệu tham khảo). Trang conf.researchr.org bị chặn trong phiên, nên giới hạn trang và hạn nộp chưa xác minh.
- Việc của người: `docs/paper/SUBMISSION_CHECKLIST.md`.

### ~17:45 — Giai đoạn 6 (chuẩn bị; bài chưa nộp)
- **6.1:** `tools/snapshot_submission.py` (có test) và workflow `Gatekeeper submission snapshot` (đầu vào: venue, mã bài, link artifact). Workflow kiểm lại số, dựng lại artifact ẩn danh, lưu `docs/paper/submitted/<venue>-<mã>/` gồm PDF, `SUBMISSION.json` (commit, SHA-256 của PDF, zip và manifest của artifact), commit, rồi gắn tag `submitted-<venue>-<mã>`. Tag được đẩy từ GitHub Actions; phiên của trợ lý bị proxy chặn đẩy tag.
- **6.2:** `docs/paper/REVIEW_RESPONSE.md`: quy tắc trả lời cho người mới, bảng ý kiến, khung bản trả lời. `docs/paper/ANTICIPATED_REVIEWS.md`: 16 ý kiến có thể gặp (A1–A16), mỗi ý có câu trả lời tiếng Anh soạn sẵn, bằng chứng trong repo, và việc có thể làm thêm.
- **Ghi nhận trung thực (A14):** bài chưa chạy phân tích độ nhạy cho hệ số phạt regression. Con số "sweep [0,2; 2,0]" của bản nháp là projected và đã bị bỏ.

### ~18:15 — A14: độ nhạy của hệ số phạt regression (0,5)
- **Phát hiện khi đọc mã:** hệ số 0,5 chỉ có trong `PairedRun.suite_loss`. Quyết định dùng z theo từng test (`PairedRun.z`, ∈ {−1, 0, 1}); nhãn đúng sai dùng tập test fail mới; `suite_loss` chỉ được ghi vào báo cáo (`Z_suite`).
- **Chứng minh:** với bộ một test (mỗi lần rút của Study D–H), loss chặn tại 1 không phụ thuộc λ ≥ 0. Nếu nhánh có kỹ năng fail thì loss đã bằng 1; nếu pass thì không có regression.
- **Kiểm** (`tools/loss_weight_sensitivity.py`, có test):
  - (A) 7.200 lần rút đã ghi (12 tệp, 24 phạm vi) với λ ∈ {0; 0,2; 0,5; 1; 2; 5}: 0 lần rút đổi z;
  - (B) chạy lại demo nhiều test (9 ô): không quyết định hay nhãn nào đổi; `Z_suite` chỉ đổi ở 3 ô khi λ = 0.
  - Kết quả: `research_closure/results/sensitivity/LOSS_WEIGHT_SENSITIVITY.json`.
- **Bài:** thêm một câu vào mục Implementation; bộ kiểm số lên 20 con số; bước kiểm thêm vào workflow `Gatekeeper submission check`; A14 trong ANTICIPATED_REVIEWS chuyển thành "đã làm".

### ~18:40 — Bổ sung đủ tác giả MemCoder và MemGovern
- Phiên không vào được arxiv.org và huggingface.co; tra bằng tìm kiếm web, đối chiếu nhiều nguồn.
- **MemCoder** (arXiv:2603.13258): Yi-Xuan Deng, Xiaoqin Liu, Yi Zhang, Guo-Wei Yang, Shuojin Yang. Listing arXiv khớp với ResearchGate và Papers with Code.
- **MemGovern** (arXiv:2601.06789): 15 tác giả (listing arXiv khớp với papers.cool); bài đã được nhận ở Findings of EMNLP 2026, nên `refs.bib` trích bản hội nghị.
- `refs.bib` không còn mục "and others"; PAPER_TODO 4.4 xong.

### ~19:30 — "Fix potential issues sao cho thắng": rà soát toàn bài như phản biện FSE
- Chi tiết: `docs/paper/PHASE4_REVIEW.md`, W1–W7.
- **W1, sửa Abstract tự mâu thuẫn** về 16 patch của Study P: câu cũ ngầm nói chúng có hại thật, trong khi RQ5 cho thấy phần lớn không phải hồi quy.
- **W2, mô phỏng thư viện** (`tools/library_simulation.py`, có test; kết quả trong `research_closure/results/library_sim/`), dùng đúng e-process, sổ cái và luật thực thi của hệ thống:
  - chỉ admit từng kỹ năng: 27,9% thư viện chạy thành phần có hại (q = 0,1 / 0,3 / 0,5 cho 9,9% / 27,9% / 42,4%);
  - cách của bài: 0/1.000 ở mọi q;
  - cái giá: chạy ít hơn khoảng 20% kỹ năng có lợi, thêm 8% lần thử;
  - đo trên toàn tập thì phần hại bị che (5,4%).
- **W3–W6, trích dẫn mới** (đã tra): PatchDiff (ICSE 2026), Johari và cộng sự (OR 2022), Vovk & Wang (AoS 2021), Smith và cộng sự (ESEC/FSE 2015; số trang cần kiểm).
- Bộ kiểm số: 26 con số. Workflow submission check thêm bước tái lập mô phỏng thư viện (phải giống hệt bản commit).

### ~20:00 — "Fix cho tới khi thắng", vòng 2
- **Nói thẳng với người nghiên cứu:** không thể bảo đảm bài được nhận. Việc làm được là bịt mọi chỗ phản biện có thể tấn công mà sửa được ngay, không tốn tiền.
- **W8:** độ vững của Study Q theo từng repo (`tools/q_robustness.py`): bỏ từng repo thì HQ1 nằm trong 8,2% – 16,7% (cận trên lớn nhất 31,9%) và Q4 trong 8,2% – 14,0%. Đã đưa vào bài, có trong bộ kiểm số.
- **W9:** thêm Hình 1 (pipeline, TikZ) và Bảng 2 (quyết định theo ô trên target thật).
- **W10:** mức giao footprint thật không đo được từ dữ liệu sẵn có; ghi trong Threats.
- **Sự cố:** script sửa làm hỏng `evaluation.tex`. Bộ kiểm số bắt được (21 con số biến mất); tệp được khôi phục từ git trước khi commit.

### ~21:30 — Vòng 3: mã, GitHub Actions, dữ liệu thật về tổ hợp
- **Mã và Actions** (`docs/CODE_AUDIT.md`):
  - CI mới (`ci.yml`) chạy khi push và khi có PR; trước đó 0/101 workflow tự chạy.
  - Ghim SHA cho 346 lần dùng action (`tools/pin_actions.py`, tra SHA trong Actions run 41217291272); `auth` nâng v2 → v3, đã kiểm (run 41218337136); Dependabot.
  - Xoá workflow trùng; thêm timeout cho workflow gọi model.
  - ruff: không lỗi thật; 21 import thừa đã dọn; 16 cảnh báo B023 đều là báo động giả.
  - Sự cố nhỏ: lệnh `pkill` khớp nhầm cả shell của chính mình, chạy lại không dùng `pkill`. CI lint ban đầu mất hơn 9 phút vì shellcheck, đã tắt shellcheck trong CI.
- **Study R:** giao thức commit trước (`d655dfd`), chạy run 41218737641: 16/16 repo, 655 tệp, 104 + 16 hàm, **1 hàm chung**. Đưa vào bài (mục 7.2, Intro, Threats); bộ kiểm số lên 30.
