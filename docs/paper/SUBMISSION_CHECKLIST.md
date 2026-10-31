# Checklist nộp bài (giai đoạn 5)

## Đã tự động hoá (chạy lại bất cứ lúc nào, 0 USD)

| Kiểm | Workflow | Lần chạy gần nhất |
|---|---|---|
| Tái lập: test, kiểm lý thuyết giống hệt bản commit, 19 con số trong bài (gồm Abstract) tính lại từ tệp kết quả, freeze của mọi study được trích (P tại commit đóng băng) | `Gatekeeper submission check`, job `repro` | ✅ run 41212215560 |
| Artifact ẩn danh: bỏ ghi chú nội bộ, PDF bản nháp, `.git`; thay link repo; quét cả tệp nén; **0 dấu vết danh tính**; chạy lại test, kiểm số và freeze **bên trong** artifact | `Gatekeeper submission check`, job `artifact` (tải `ANONYMOUS_ARTIFACT`) | ✅ run 41212215560 |
| Biên dịch bài, không còn tham chiếu thiếu, kiểm số | `Gatekeeper paper LaTeX build` | ✅ run 41212373969 (acmsmall, 10 trang tính cả tài liệu tham khảo) |
| Kiểm lý thuyết C1–C9 | `Gatekeeper theory checks` | ✅ |

## Việc của người, theo thứ tự

- [x] **Venue (tra 31/10/2026 bằng tìm kiếm):**
  - **FSE 2027 đã hết hạn** (research track 2–3/10/2026; [trang chính thức](https://conf.researchr.org/track/fse-2027/fse-2027-papers)).
  - **Chọn ISSTA 2027:** tóm tắt **8/1/2027**, bài **11/1/2027**, hội nghị 7–10/9/2027 tại Singapore ([ISSTA 2027](https://conf.researchr.org/home/issta-2027)).
  - Quy định của ISSTA 2026: **18 trang** cho nội dung và hình, tài liệu tham khảo không giới hạn; `acmsmall,review,anonymous`; mục Data Availability bắt buộc, không tính trang. Bài hiện 14 trang tính cả tham khảo. **Còn phải xem lại khi call for papers chính thức của ISSTA 2027 đăng.**
- [x] **Bổ sung đủ tác giả** của MemCoder và MemGovern (31/10/2026) trong `docs/paper/latex/refs.bib` (xem `docs/paper/CITATIONS_AUDIT.md`).
- [ ] **Người đọc độc lập** (PAPER_TODO 1.9) kiểm các chứng minh trong mục Theory. *Đã có bản thay bằng model:* workflow `Gatekeeper model stand-ins` (proofs), kết quả ở `research_closure/results/model_reviews/PROOF_REVIEW.md`. Không thay được người, nhưng bắt được lỗi trước khi người đọc.
- [ ] **Thầy đọc và duyệt toàn bài** (PAPER_TODO 5.5). *Đã có 3 phản biện giả lập bằng model* (`MOCK_REVIEWS.md`); mọi yếu điểm được xử lý trong `docs/paper/MODEL_REVIEW_RESPONSE.md`.
- [ ] **Tải artifact ẩn danh:** chạy `Gatekeeper submission check`, tải `ANONYMOUS_ARTIFACT`, mở `gatekeeper-artifact.zip`, xem lướt; rồi đưa lên một dịch vụ ẩn danh (ví dụ anonymous.4open.science, hoặc Zenodo ở chế độ ẩn danh nếu venue cho phép). Mục Data Availability đã có trong bài (link `anonymous.4open.science/r/gatekeeper-artifact` cần kích hoạt khi tải lên).
- [ ] **Không** dẫn link tới repo GitHub hiện tại trong bài nộp: repo công khai và có tên tài khoản.
- [ ] Nộp bản PDF build mới nhất (`docs/paper/latex/build/paper.pdf`); ghi ngày nộp, mã bài và commit hash vào `docs/PROCESS_LOG.md` (PAPER_TODO 5.5, 6.1).
