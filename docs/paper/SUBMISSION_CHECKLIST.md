# Checklist nộp bài (giai đoạn 5)

## Đã tự động hoá (chạy lại bất cứ lúc nào, 0 USD)

| Kiểm | Workflow | Lần chạy gần nhất |
|---|---|---|
| Tái lập: test, kiểm lý thuyết giống hệt bản commit, 19 con số trong bài (gồm Abstract) tính lại từ tệp kết quả, freeze của mọi study được trích (P tại commit đóng băng) | `Gatekeeper submission check`, job `repro` | ✅ run 41212215560 |
| Artifact ẩn danh: bỏ ghi chú nội bộ, PDF bản nháp, `.git`; thay link repo; quét cả tệp nén; **0 dấu vết danh tính**; chạy lại test, kiểm số và freeze **bên trong** artifact | `Gatekeeper submission check`, job `artifact` (tải `ANONYMOUS_ARTIFACT`) | ✅ run 41212215560 |
| Biên dịch bài, không còn tham chiếu thiếu, kiểm số | `Gatekeeper paper LaTeX build` | ✅ run 41212373969 (acmsmall, 10 trang tính cả tài liệu tham khảo) |
| Kiểm lý thuyết C1–C9 | `Gatekeeper theory checks` | ✅ |

## Việc của người, theo thứ tự

- [ ] **Xác minh quy định của FSE 2027** trên trang chính thức (<https://conf.researchr.org/track/fse-2027/fse-2027-papers>): hạn nộp, **giới hạn số trang**, quy định ẩn danh và artifact. Tìm kiếm cho thấy template là `acmsmall` + `review,anonymous` (bài đã chuyển sang), nhưng giới hạn trang và hạn nộp **chưa xác minh được** từ phiên của trợ lý (trang bị chặn).
- [ ] **Bổ sung đủ tác giả** của MemCoder và MemGovern trong `docs/paper/latex/refs.bib` (xem `docs/paper/CITATIONS_AUDIT.md`).
- [ ] **Người đọc độc lập** (PAPER_TODO 1.9) kiểm các chứng minh trong mục Theory.
- [ ] **Thầy đọc và duyệt toàn bài** (PAPER_TODO 5.5).
- [ ] **Tải artifact ẩn danh:** chạy `Gatekeeper submission check`, tải `ANONYMOUS_ARTIFACT`, mở `gatekeeper-artifact.zip`, xem lướt; rồi đưa lên một dịch vụ ẩn danh (ví dụ anonymous.4open.science, hoặc Zenodo ở chế độ ẩn danh nếu venue cho phép). Đưa link vào mục Data Availability của bài.
- [ ] **Không** dẫn link tới repo GitHub hiện tại trong bài nộp: repo công khai và có tên tài khoản.
- [ ] Nộp bản PDF build mới nhất (`docs/paper/latex/build/paper.pdf`); ghi ngày nộp, mã bài và commit hash vào `docs/PROCESS_LOG.md` (PAPER_TODO 5.5, 6.1).
