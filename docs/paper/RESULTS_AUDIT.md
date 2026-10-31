# Rà thắng / thua của từng kết quả (31/10/2026)

**Thắng** = kết quả ủng hộ đúng điều bài khẳng định, kiểm được từ tệp kết quả.

**Thua thật** = dữ liệu đi ngược điều kỳ vọng. Bài báo cáo trung thực như một kết quả âm.

**Thua do môi trường** = không đo được, hoặc đo sai, vì hạ tầng (cài đặt, harness, token…). Trường hợp này đã debug tới nguyên nhân gốc.

Mọi con số đều được `tools/check_paper_numbers.py` tính lại (51/51).

## Lý thuyết

| Mệnh đề | Chứng minh | Kiểm bằng số | Kết quả |
|---|---|---|---|
| Bổ đề 1 (e-process cược) | có | C1: tỉ lệ admit sai ≤ α | **Thắng** |
| Mệnh đề harm certificate | có (mới) | C9: 0,39η, 110 draw | **Thắng** |
| Định lý 1 (sổ cái, epoch) | có; điều kiện epoch viết lại (TC18) | C2: theo scope 0,45 so với theo ô 0,05; C8: admit lại | **Thắng** |
| Bổ đề sổ cái thư viện | có (mới) | C11 ≤ α | **Thắng** |
| Mệnh đề e-Holm | có (mới) | C10: FWER 2,4% / 7,3% ≤ 10% | **Thắng** |
| Bổ đề shift 2ξ, Mệnh đề 1(a)(b) | có | C3: hằng số 2 đạt được | **Thắng** |
| Định lý 2 (tổ hợp 1 + min(a, b)) | có (+ Giả định 3) | C4: 0 vi phạm / 20.000, đạt cận | **Thắng** |
| Hệ quả 2.6 (cái gì thật sự chạy) | có, theo đồ thị có cạnh enabling | mô phỏng: P2 0/1.000 | **Thắng** |
| Mệnh đề pairing | có | C5 | **Thắng** |
| Số của bản nháp gốc (d̄ = 0,34) | — | C7 = False | **Thua thật của bản gốc**, đã bỏ khỏi bài |

## Thực nghiệm

| Kết quả | Số | Phân loại | Ghi chú |
|---|---|---|---|
| Đồ thị pha các gate (RQ1) | bảng 1 | **Thắng** | Gate tuần tự kiểm soát lỗi ở h ≥ η; smoke test thì không |
| Fixed-sample mạnh hơn sequential ở cùng số draw | 0,92 so với 0,65 tại h = 2% | **Thua thật** (đã báo) | Sequential không nhằm hơn về power; bài nói rõ |
| Mô phỏng thư viện | P1 27,9% so với P2 0/1.000; chi phí 3,59 so với 4,48 | **Thắng** (rủi ro là tổng hợp) | — |
| R2: footprint 12 họ | 59 ô, 18/136 cặp, 6 ô tổ hợp | **Thắng** | — |
| R2: footprint tĩnh bỏ sót tương tác | 1 cặp (pydal) | **Thua thật của thiết kế cũ** | Đã sửa bằng cạnh enabling, mô phỏng lại: 7,1% so với 0/1.000 |
| S: tổ hợp thật | 16/23 hàm; tổ hợp cộng tính; cổng 61/64 | **Thắng** | Lần chạy đăng ký chỉ 2/23: **thua do môi trường** (receiver, mangling, cài đặt), sửa qua S-A1..S-A5. Một dấu hiệu phụ thuộc thứ tự ở S-A2 là **nhiễu** theo quy tắc viết trước (S-A3) |
| S: chưa thấy tổ hợp thật nào gây hại "nảy sinh" | 0 | **Thua một phần** | Định lý 2 vẫn chỉ được minh hoạ bằng cấu trúc và mô phỏng; bài nói rõ |
| D: certificate so với baseline | 2/3 lợi ích, 0 có hại; 3.220 so với 3.600 lượt chạy | **Thắng một phần** | Bỏ sót 1 ô vì lợi ích −0,11 nhỏ hơn biên θ = 0,2: **đúng thiết kế**, không phải lỗi |
| E, G: 4 ô có hại | B2, B6-R admit 4/4; certificate loại 4/4 | **Thắng** | Bộ test của target không thấy hồi quy ở E |
| Tác hại trên target thật gần như tất định | smoke test là đủ | **Thua thật về động cơ** (đã báo) | Study H là trường hợp tác hại hiếm cần cơ chế thống kê |
| P (RQ3) | 16/205 trong dải; census admit 16; gate thống kê admit 0 | **Thắng** | RQ5: phần lớn khác biệt nằm trên input bản fix cũng từ chối, và bài báo cáo điều này |
| Q: HQ1 (đăng ký) | 6/55 | **Thua thật** (giả thuyết không được ủng hộ, báo cáo như kết quả âm) | Ổn định khi bỏ từng repo (8,2–16,7%) |
| Q-A1 (kiểm thủ công) | 8/36 (2 người chấm), 5/36 (đa số 3) | **Thắng** (khẳng định kết quả âm) | 19/55 không tái tạo: **môi trường** (17 vì generator do model viết không được lưu) |
| Người chấm model | hiệu chuẩn 20/20 mỗi model | **Thắng** | κ không định nghĩa được vì model chấm toàn R; đã giải thích |
| Giả định 4 trên dữ liệu | 21 cặp chung hàm và 80 cặp rời nhau giao hoán; 1 cặp không giao hoán đã được luật bắt | **Thắng** | Chỉ kiểm về cú pháp; tương tác ngữ nghĩa vẫn là giả định |

## Các lần THUA do môi trường và nguyên nhân gốc (đã sửa)

| Lần chạy | Nguyên nhân gốc | Sửa |
|---|---|---|
| Q-A1 rate, lần 1 | Token gcloud cache hết hạn sau khoảng 1 giờ | Chia shard, `fresh_gcp_token.py` |
| R2 dispatch | YAML: tên step có `: ` | Đặt trong ngoặc kép; actionlint |
| Build LaTeX | `_` chưa escape | Escape |
| S (đăng ký) | Harness frozen không dựng được receiver; name mangling | `composition_inner.py` (S-A1) |
| S-A2 dấu hiệu phụ thuộc thứ tự | Hash ngẫu nhiên giữa các tiến trình (giả thuyết) | Lặp lại (S-A3), cố định `PYTHONHASHSEED` (S-A4) |
| S hera_pspec | `SETUPTOOLS_SCM_PRETEND_VERSION` áp cho mọi gói, nên `uvtools` thành 0.0.0 | Áp riêng cho gói đang kiểm (S-A5) |
| Mock review "lỗi bố cục LaTeX" | Tool review ghép `related_stats` sai thứ tự | `inline_inputs` |
