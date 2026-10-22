# Gatekeeper-Lite — tóm tắt kết quả nghiên cứu (Study D + Study E)

Hai nghiên cứu prospective, protocol đóng băng trước khi chạy, seed từ drand, cùng một skill học từ PySStuBs (loại `bool` khỏi kiểm tra `isinstance(x, int)`), cùng bộ chạy. **26 ô trên 12 repository** (Study D: 16 ô, 7 repo; Study E: 10 ô, 5 repo). Tái lập: Study D chạy lại cho kết quả giống hệt.

## Kết quả gộp (đếm theo ô; mô tả, không phải tỉ lệ quần thể)

| Comparator | Admit | Có lợi được admit | **Có hại được admit** | Thay đổi vô ích được admit |
|---|---|---|---|---|
| B2 (bind được là dùng) | 22 | 3/3 | **3/3** | 16 |
| B6-R (bind + replay + fingerprint) | 22 | 3/3 | **3/3** | 16 |
| B8 (chạy đủ 300 lần rút + census; tính theo ô) | 19 | 3/3 | 0/3 | 16 |
| **Gatekeeper-Lite** | **2** | **2/3** | **0/3** | **0** |

*Ô có hại tính cả E3 (cấp 3, minh hoạ); nếu bỏ E3: B2/B6-R admit 2/2 ô có hại chính, Gatekeeper 0/2.*

## So sánh theo chuẩn chung (trạng thái cuối của mã)

Mỗi cách tiếp cận được đánh giá bằng **mã mà nó để lại** trên target, chấm bằng cùng oracle (300 lần rút mỗi scope) và cùng hàm kết luận mà B9 sẽ dùng (`tools/unified_comparison.py`, `study_e/results/UNIFIED_COMPARISON_D_E.md`). **Không có kết quả nào được mô phỏng:** B2, B6-R và B8 quyết định ở mức target (B8 từ chối cả skill nếu có hại ở bất kỳ scope nào); Gatekeeper triển khai toàn bộ skill khi có ít nhất một scope được admit, và mọi kết quả scope đã đo đều được tính. Ở mọi target, các scope Gatekeeper không admit đều có 0 thay đổi đo được, nên không cần cơ chế giới hạn scope. Trên 13 target:

| Kết luận cuối | Skill + Gatekeeper | Skill + B6-R | Skill + B8 |
|---|---|---|---|
| SUCCESS (có lợi, không hại) | 2 | 3 | 3 |
| **HARMFUL** | **0** | **3** | 0 |
| NO_EFFECT (thay đổi vô ích) | 0 | 5 | 5 |
| NO_PATCH (mã giữ nguyên) | 11 | 2 | 5 |

Cột B9 sẽ được điền vào cùng bảng sau khi chạy, theo đúng chuẩn này.

## Ba điều Gatekeeper làm được mà B6-R không làm được

1. **Chặn tái dùng có hại** (Study E): B6-R admit cả 3; Gatekeeper từ chối cả 3 chỉ sau 2 lần rút mỗi ô. Bộ test gốc của target (tới 51.524 test) không bắt được các tác hại này.
2. **Chỉ chấp nhận khi có lợi ích đo được** (Study D): Gatekeeper không admit ô nào trong 16 thay đổi vô ích mà B2, B6-R và B8 đều admit (ví dụ skill sửa nhầm hàm không có lỗi).
3. **Kiểm soát sai số cho cả họ quyết định:** e-Holm FWER 0,1, kiểm tra bằng mô phỏng (FWER 0,040 ở kịch bản xấu nhất).

## Cách diễn đạt kết luận (đã chốt)

- **Được nói:** trên các ô đã đăng ký trước, Gatekeeper-Lite không admit ô có hại nào trong 3 ô có hại (2 ô chính, 1 ô minh hoạ), trong khi B6-R admit cả 3; và không để lại thay đổi vô ích nào.
- **Không được nói:** "Gatekeeper chặn 100% skill gây hại" như một khẳng định chung. Bằng chứng gồm 2 ô chính với nguồn oracle cấp 2b (ý đồ trong mã) và cấp 2 (maintainer, có tranh cãi); **chưa có ô có hại nào với oracle cấp 1** (test upstream khẳng định hành vi), vì lượt quét 15 thư viện không tìm được.
- **Sai số khi gộp hai study:** mỗi study kiểm soát FWER ở mức 0,1 trên họ ô riêng. Một kết luận đồng thời trên cả hai study có xác suất sai tổng tối đa 0,2 (bất đẳng thức Bonferroni). Kết luận nên được nêu theo từng study.

## Chi phí: khi nào lợi ích thời gian xuất hiện

`tools/cost_breakeven.py`, `study_e/results/COST_BREAKEVEN_D_E.md`. Tách rõ **thời gian đo thật** (census + khởi động worker + thời gian rút mẫu đã ghi; không gồm tải repo và cài đặt) với **ước tính theo mô hình**. Tổng 13 target, đo thật: lần rút Gatekeeper 5.326 so với B8 6.600 (ít hơn 19,3%); thời gian 1.038,82 s so với 1.049,49 s (**ít hơn 1,02%**); riêng Study E ít hơn 0,15%. Ngoại lệ: **spec-kit** đo thật tiết kiệm 21,4%, vì mỗi lần rút tốn khoảng 55 ms. Tiết kiệm không bao giờ vượt tỉ lệ lần rút giảm được (tối đa 31,7% ở ô có lợi, 49,7% ở ô có hại) và bằng 0 ở các ô không có lợi cũng không có hại, vì quy tắc không có điểm dừng sớm cho trường hợp "vô ích".

## Độ nhạy theo cấp nguồn oracle (Study E)

| Tập ô có hại được tính | B6-R admit ô có hại | Gatekeeper admit ô có hại |
|---|---|---|
| Chỉ E1 (cấp 2b) | 1/1 | 0/1 |
| E1 + E2 (cấp 2b + cấp 2, tranh cãi) | 2/2 | 0/2 |
| E1 + E2 + E3 (thêm cấp 3, minh hoạ) | 3/3 | 0/3 |

Kết luận về chiều so sánh không đổi ở mọi mức; điều thay đổi là **độ mạnh của bằng chứng**. Ở mức chặt nhất (chỉ E1), bằng chứng là **một ô**.

## Truy vết B6-R

Ví dụ replay của skill là một fixture tự dựng mô phỏng mẫu PySStuBs; commit PySStuBs cụ thể không được lưu. Quyết định của B6-R không phụ thuộc vào điều này (skill tái tạo đúng cách sửa trên mọi ví dụ thuộc mẫu), nhưng B6-R phải được mô tả là **bản tái dựng yếu hơn B6 của paper** ở phía nguồn. Chi tiết: `study_d/PROVENANCE_B6R.md`, `study_d/SUPPLEMENTARY_MANIFEST.json`.

## Study G: họ skill thứ hai (`== None` → `is None`)

Một target (pydal), oracle **cấp 1** (31 dòng test upstream khẳng định `== None` sinh IS NULL), ví dụ replay là **bản fix thật**. B6-R **ADMIT**; Gatekeeper **REJECT_HARM**; B8 REJECT. Tác hại 81/300 lần rút, chỉ ở truy vấn đếm mọi dòng (skill đổi `table._id != None` trong `id_query`). **Census bắt được** (21 test fail mới), khác Study E; e-process báo động cũng tự kích hoạt ở lần rút 103. B6-S không có census với k ≤ 5 sẽ admit. Phía có lợi BLOCKED (29/29 ứng viên là dọn lint, không có test hành vi). Chi tiết: `study_g/results/`.

## Giới hạn phải nói rõ

- **Bỏ lỡ 1/3 ô có lợi** (pycubrid): lợi ích tập trung ở 11% đầu vào, dưới biên θ = 0,2. Kiểm định dấu (ablation) sẽ admit được.
- **Gần như không tiết kiệm thời gian** khi mỗi lần thử rẻ (xem mục chi phí); quy tắc không có điểm dừng sớm khi skill vô ích.
- **B8 an toàn ngang Gatekeeper** về ô có hại; khác biệt nằm ở việc B8 admit thay đổi vô ích và không có điểm dừng sớm.
- **Một họ lỗi, quy mô nhỏ;** ô có hại chính chỉ có 2; một ô tranh cãi (packaging).
- **B9 (sửa lỗi bằng LLM) chưa chạy** (chờ ngân sách sau 31/10, kế hoạch phân tích đã đăng ký trước).
- **Composition và retirement** chỉ được minh hoạ trên dữ liệu phát triển; không có claim.
- **Tái lập:** Study D chạy lại cho kết quả giống hệt; bảng quyết định của 26 ô được tái tạo đúng từ dữ liệu gốc (`tools/results_check.py`).
