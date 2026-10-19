# Study C — admission theo scope (ĐÃ ĐÓNG BĂNG 20/10/2026)

**Trạng thái:** FROZEN. Hash trong `study_c/FREEZE.json`; workflow `study-c-run.yml` kiểm tra lại trước khi chạy.

**Quyết định chốt:** quét vòng 3 (9 repository trong hệ sinh thái Click) không có site nào trên giá trị default; sau 3 vòng (15 repository) chỉ có rich-click và asyncclick đủ điều kiện, cả hai đã dùng ở Study B. Vì vậy Study C dùng **regime A**: 6 bản phát hành Click **chưa từng chạy** có nhánh `== ""` chưa guard (8.1.8, 8.2.0, 8.2.2, 8.3.0, 8.3.1, 8.3.2; nhánh có từ 8.1.8 và được sửa ở 8.3.3). Các revision đã dùng (commit cha #3298, 8.1.7, 8.2.1) bị loại. Kết quả được gắn nhãn `PROSPECTIVE_REGIME_A_UNSEEN_REVISIONS` và báo riêng với Study B (regime B).

## 1. Câu hỏi (đúng tinh thần *Scope before Reuse*)

Cùng một skill (guard `isinstance(x, str)` trước `x == ""` ở mã hiển thị default), trên **repository mới chưa từng xem**:

- **H1 (lợi ích):** trong scope *đối tượng* (đối tượng so sánh chặt, array-like), Gatekeeper-Lite có **admit** không?
- **H2 (an toàn):** trong scope *chuỗi lazy*, Gatekeeper-Lite có **từ chối vì tác hại** không?
- **H3 (so sánh):** B2/B6-R, vốn không nhìn vào lớp hành vi, có cho **cùng một quyết định ở mọi scope** không?

Study B v1 chỉ trả lời được H2 (tác hại) theo kiểu gộp. Study C tách scope ngay từ đầu, nên trả lời được cả lợi ích (kỳ vọng E3 của paper) lẫn an toàn trên cùng một lần chạy.

## 2. Thiết kế (dự kiến đóng băng)

- **Skill/binder:** như Study B (`empty-default-guard-family`, `click-guard-v3`), dùng lại file đã đóng băng.
- **Oracle:** `study_c/oracle_templates/test_gk_metamorphic.py` (v2): cùng tính chất thay thế như Study B, tăng ca đối tượng so sánh chặt từ 8 lên 12 để có lực kiểm định (xem mục 4); cộng bộ test gốc của target (phiên pytest riêng).
- **Scope khai báo trước** theo tên task: `objects` = `[strict-`, `[array-`; `lazy` = `[lazy-`. Task không thuộc lớp nào (bộ test gốc) thuộc **mọi** scope, nên một regression ở đó chặn admission ở mọi scope.
- **Bằng chứng:** kiểm định dấu (q0 = 0,6, q1 = 0,9), e-BH FDR 0,1 trên mọi ô (cặp × scope), dừng sớm khi E ≥ K/0,1, dừng vì tác hại khi e ≥ 20. Ngân sách 24 task mỗi ô, lọc theo khả năng chạm, ưu tiên task metamorphic.
- **Target (đã chốt):** 6 bản phát hành Click ở trên × 2 binder × 2 scope = 24 ô. Ban đầu dự định chọn từ quét vòng 3 (công cụ hiển thị default trong hệ sinh thái Click). Điều kiện: site `== ""` chưa guard trên giá trị default, bộ test chạy được, giấy phép mở, **chưa từng chạy**. Ghim theo commit. Loại mọi revision đã dùng ở P7.x, real-click và Study B.

## 3. Báo cáo

Theo từng scope: số cặp có lợi được admit, có hại bị admit, có lợi bị bỏ lỡ, chi phí; cho B2, B6-R, B8, Gatekeeper. Kết quả Study B v1 được trích lại nguyên văn, không gộp.

## 4. Lực kiểm định (tính trước)

Với 12 ca so sánh chặt đều có lợi: E = 1,5^12 ≈ 130 ≥ K/0,1 khi K ≤ 13 ô, nên ô *objects* có thể được admit ngay cả khi chỉ có một ô đạt. Với 8 ca như Study B: E ≈ 25,6, chỉ đạt khi e-BH cho R ≥ K/2,56 ô đạt; vì vậy oracle v2 tăng lên 12 ca.

## 5. Phương án dự phòng (giữ nguyên để truy vết)

- Danh sách target (sau quét vòng 3).
- Nếu quét vòng 3 không có target nào: dùng phương án dự phòng là báo cáo Study C như **phân tích theo scope trên dữ liệu Study B** (gắn nhãn hậu kiểm), không claim prospective.
