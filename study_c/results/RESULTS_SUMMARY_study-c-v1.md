# Study C v1 — admission theo scope (run `39250346083`, 19/10/2026)

**Loại bằng chứng:** PROSPECTIVE_REGIME_A_UNSEEN_REVISIONS — 6 bản phát hành Click chưa từng chạy (8.1.8, 8.2.0, 8.2.2, 8.3.0, 8.3.1, 8.3.2), protocol đóng băng trước (tag `study-c-freeze`, 32 file trong `FREEZE.json`), không có lỗi kỹ thuật.
**Artifact:** `STUDY_C_OUTPUT` (sha256 `0c60525862de328fe68dadca0bc9ba4ffd194921d7bed4b3993ff2137a35a27a`).

## 1. Ba giả thuyết khai báo trước: cả ba được xác nhận

| Giả thuyết | Kết quả |
|---|---|
| **H1** — Gatekeeper admit ở scope *đối tượng* | **12/12 ô** admit (E = 292 ở 8.1.8–8.2.2; E = 130 ở 8.3.x); không ô nào có regression ở bộ test gốc |
| **H2** — Gatekeeper từ chối vì tác hại ở scope *chuỗi lazy* | **12/12 ô** REJECT_HARM, mỗi ô chỉ sau 3 task |
| **H3** — B2/B6-R cho cùng quyết định ở mọi scope | Đúng: B2 và B6-R **ADMIT cả 24 ô**, gồm 12 ô có hại |

| Comparator | Ô có hại bị admit | Ô có lợi được admit | Chi phí (lượt chạy task, tính một lần mỗi cặp) |
|---|---|---|---|
| B2 | 12/12 | 12/12 | 0 |
| B6-R (replay + fingerprint) | **12/12** | 12/12 | 0 |
| B8 (luôn retest) | 0/12 | 12/12 | 9.200 |
| **Gatekeeper-Lite** | **0/12** | **12/12** | 5.128 (528 lượt thử + 4.600 lượt lọc) |

Ở 8.1.8–8.2.2, skill sửa 16 ca (12 so sánh chặt + 4 array-like); ở 8.3.x sửa 12 ca (array-like hỏng ở một phép so sánh khác, có từ 8.3.0, ngoài phạm vi skill). Ở mọi bản, 6 ca chuỗi lazy rỗng bị hỏng.

**Ý nghĩa:** đây là minh hoạ prospective trực tiếp cho luận điểm *Scope before Reuse*: cùng một skill, cùng một fingerprint, nhưng an toàn và có lợi trong một scope và có hại trong scope khác. Gatekeeper-Lite admit đúng chỗ an toàn, chặn đúng chỗ có hại, khớp B8 về chất lượng quyết định với khoảng 56% chi phí. B6-R không thể tách hai scope.

## 2. Ablation hậu kiểm (chạy lại quy tắc trên cùng dữ liệu, không chạy thêm)

| Biến thể | Có hại bị admit | Có lợi được admit | Từ chối vì tác hại | Lượt thử |
|---|---|---|---|---|
| Đầy đủ | 0 | 12 | 12 | 528 |
| Bỏ chia scope | 0 | **0** | 12 (gộp) | 96 |
| E-process trung bình thay kiểm định dấu | 0 | 12 | **0** (chỉ QUARANTINE) | 1.056 |
| Bỏ lọc theo khả năng chạm | 0 | 12 | 12 | 528 |
| Bỏ ưu tiên oracle | 0 | **0** | 6 | 948 |
| Bonferroni thay e-BH | 0 | **6** | 12 | 540 |

- **Chia scope** là thành phần quyết định: bỏ đi thì mất toàn bộ 12 lần tái sử dụng có lợi.
- **Ưu tiên task của oracle** cần thiết: thứ tự ngẫu nhiên tiêu hết ngân sách vào task không phân biệt.
- **e-BH** gấp đôi độ phủ so với Bonferroni ở cùng mức kiểm soát.
- **Kiểm định dấu** cho lý do từ chối rõ ràng (tác hại) và rẻ hơn một nửa so với e-process trung bình.
- **Lọc theo khả năng chạm không đổi quyết định nào** trong Study C (kiểm định dấu đã bỏ qua task không đổi), nhưng tốn 4.600 lượt chạy. Phát hiện trung thực: với kiểm định dấu và thứ tự ưu tiên, có thể bỏ bước lọc để giảm chi phí Gatekeeper xuống còn 528 lượt.

## 3. Hạn chế

- **Regime A:** 6 bản phát hành rất giống nhau của cùng một repository đã dùng khi phát triển, nên các ô tương quan mạnh. e-BH vẫn hợp lệ dưới mọi kiểu phụ thuộc, nhưng độ rộng bằng chứng hẹp. Study B (regime B) là phần bổ sung ngoài Click.
- **Lớp chuỗi lazy** vẫn là kỳ vọng do nhóm khai báo (trước Study B và Study C), chưa có xác nhận độc lập.
- **Bộ test gốc dùng chung** chỉ là `tests/test_options.py`, không phải toàn bộ suite.
- Ablation là hậu kiểm, không đăng ký trước.
