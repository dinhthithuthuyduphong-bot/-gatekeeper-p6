# Study Q: kết quả (phân tích theo giao thức đã đóng băng, mục 6)

**Dữ liệu:** stream part 0 ([run 41185100083](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41185100083)) và part 1 ([run 41187862326](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41187862326)), seed `460798324973423911`. Tổng hợp bằng workflow `Gatekeeper Study Q analyze` (commit `9a8ab44`).

**Tệp:** [`Q_ANALYSIS.json`](Q_ANALYSIS.json) (đầu ra của `tools/q_analyze.py`), [`FRAME_CHECK.json`](FRAME_CHECK.json), [`Q_RECORDS.jsonl.gz`](Q_RECORDS.jsonl.gz) (bản ghi thô của cả 469 instance). Freeze `study_q` verified ở mọi bước. Không có amendment.

## Q1: phễu

| Bước | Số |
|---|---|
| Khung (instance có ít nhất một patch resolved) | 469 |
| Có bản ghi | **469** (đủ khung, không trùng) |
| `FINISHED` (có hàm dùng được, patch đã chấm) | 245 (52,2%) |
| `NOT_USABLE` (không hàm nào đạt ≥ 100 đầu vào ổn định có khác biệt gốc/fix) | 220 |
| `ERROR` | 4: `django__django-12858`, `-13109`, `-16485`, `scikit-learn__scikit-learn-10908`. Cả bốn là `FileNotFoundError` khi dựng bản đã vá, với patch tạo tệp mới trong thư mục chưa có |
| Patch được chấm / không áp được | 694 / 21 |

Tỉ lệ dùng được 52,2% cao hơn cận dưới dự kiến (38%), gần Q-F1 (54,5%).

## Q2, Q4: tỉ lệ ở mức patch (694 patch)

| Đại lượng | k/n | Tỉ lệ | Wilson 95% | Bootstrap theo repo 95% |
|---|---|---|---|---|
| **Q2** khác hành vi so với bản fix (mọi khác biệt) | 299/694 | 43,1% | 39,4% – 46,8% | 38,0% – 55,1% |
| Khác biệt ngây thơ (gốc = fix, patch khác) | 89/694 | 12,8% | 10,5% – 15,5% | 8,3% – 19,6% |
| **Q4** hồi quy theo hợp đồng (C1 hoặc C2-D) | 77/694 | **11,1%** | 9,0% – 13,6% | 6,4% – 18,2% |

## Q3 / HQ1 (xác nhận): KHÔNG được ủng hộ

Cổng Q-G1 **đạt**: 55 instance có ít nhất một patch có khác biệt ngây thơ (≥ 18).

| | Giá trị |
|---|---|
| Instance mà patch có khác biệt ngây thơ **không** có hồi quy theo hợp đồng | **6/55 = 10,9%** (Wilson 5,1% – 21,8%) |
| HQ1: tỉ lệ > 0,5 | **không bác bỏ H0** (p một phía ≈ 1,0) |

Kết quả đi theo **hướng ngược** dự đoán: trên SWE-bench Verified, khoảng 89% khác biệt ngây thơ là hồi quy theo hợp đồng. Dự đoán dựa trên RQ5 của Study P là 80% **không** phải.

## Q5: hệ số phóng đại

| Định nghĩa | Ước lượng | Bootstrap theo instance 95% |
|---|---|---|
| **Theo giao thức (mục 1, 6.4): Q2 / Q4** | **3,88** | 3,08 – 5,14 |
| Theo `q_analyze.py`: khác biệt ngây thơ / Q4 | 1,16 | 1,05 – 1,31 |

**Lệch giữa công cụ và giao thức:** `q_analyze.py` ghi trường `Q5_inflation_naive_over_contract` bằng (khác biệt ngây thơ)/Q4. Giao thức định nghĩa Q5 là Q2/Q4, với Q2 là **mọi** khác biệt. Ở đây báo cáo cả hai; con số theo giao thức (3,88) do trợ lý tính lại từ `Q_RECORDS.jsonl.gz`, ngoài công cụ đã đóng băng.

## Độ nhạy (giao thức mục 6.5)

| Phân tích | Kết quả |
|---|---|
| (a) Chỉ C1 | Q4 = 74/694 = 10,7%; HQ1: 9/55 = 16,4% không có hồi quy, vẫn không ủng hộ |
| (b) Chỉ G0 / chỉ G2 | Hồi quy theo hợp đồng: G0 8/694 = 1,2%; G2 72/694 = 10,4% |
| (c) Chỉ bản nộp trước 2025 | 29/221 = 13,1% |
| (d) Chỉ instance có ≥ 3 patch khác nhau | 74/676 = 10,9% |

Mọi phân tích độ nhạy cho cùng kết luận.

## Diễn giải

1. **Kết luận của RQ5 (Study P) không lặp lại được trên dữ liệu độc lập.** Ở Study P, 97,5% đầu vào "hồi quy" là C2 (bản fix cũng ném lỗi). Ở đây, trên các instance của HQ1, C1 chiếm đa số (1.185 C1, 609 C2-O, 94 C2-D đầu vào). Câu "oracle ngây thơ phóng đại tỉ lệ hồi quy 3 đến 15 lần" **không** được ủng hộ: tách theo hợp đồng chỉ giảm 13% (1,16 lần).
2. **Khả năng giải thích (sau khi thấy dữ liệu, KHÔNG đăng ký trước):** đầu vào theo chữ ký (G0) thường không hợp lệ nên rơi vào C2; đầu vào do model viết (G2) thường hợp lệ nên khác biệt là C1. Study P có tỉ trọng G0 lớn và nhiều repo bài tập; ở đây gần như mọi hồi quy theo hợp đồng đến từ G2 (72 so với 8).
3. **"Mọi khác biệt" vẫn phóng đại khoảng 3,9 lần** so với hồi quy theo hợp đồng (Q2/Q4). Phần phóng đại nằm ở các đầu vào mà bản gốc đã khác bản fix (vùng sửa lỗi), không nằm ở cách phân loại.
4. **11,1% patch resolved công khai** (Wilson 9,0% – 13,6%) có ít nhất một đầu vào hợp lệ mà patch cho kết quả khác bản fix. Con số này cùng bậc với các báo cáo trước về chênh lệch hành vi ở patch plausible.

## Đe doạ tính hợp lệ (quan trọng)

1. **C1 chưa phải "sai".** C1 nghĩa là bản fix trả giá trị và patch trả giá trị khác (hoặc ném lỗi). Một giá trị khác có thể vẫn đúng: định dạng khác, thứ tự khác, một cách hiểu khác của issue. RQ5 của Study P có bước chấm tay để xác nhận C1. **Ở đây không làm được**, vì `q_instance.py` chỉ lưu số đếm theo loại, không lưu đầu ra từng đầu vào. Đây là lệch so với giao thức mục 3 ("lưu patch và mọi đầu ra"), đã ghi trong `docs/PROCESS_LOG.md`.
2. **Đề xuất trước khi viết khẳng định vào bài:** chạy lại, có lưu đầu ra, cho 55 instance của HQ1 (hoặc một mẫu ngẫu nhiên có seed), rồi chấm tay C1 theo đúng quy trình RQ5. Việc này cần một amendment ghi rõ là bổ sung sau khi thấy kết quả.
3. Bản fix (gold patch) được coi là tham chiếu đúng; khác biệt với gold có thể là gold quá hẹp.
4. G2 xem diff của bản fix, nên đầu vào dồn quanh vùng sửa.
5. 4 instance `ERROR` (lỗi công cụ khi patch tạo tệp mới) được tính là không dùng được, không chạy lại.

## Hệ quả cho bài (đối chiếu với quy tắc trong TRACKING_FSE mục 4)

HQ1 không được ủng hộ, nên theo bảng đã ghi trước, kết luận của RQ5 chỉ là **thăm dò, giới hạn ở dữ liệu của Study P**. Khẳng định "oracle so sai khác ngây thơ phóng đại nhiều lần; phải đánh giá theo hợp đồng" **không** được đưa vào bài như một kết quả xác nhận. Điều dữ liệu ủng hộ là:

- khoảng 11% patch resolved trên SWE-bench Verified có khác biệt hành vi trên đầu vào hợp lệ so với bản fix, **cần chấm tay để biết bao nhiêu là sai thật**;
- kết quả phụ thuộc mạnh vào nguồn đầu vào (G0 so với G2).

Chọn hướng viết bài là quyết định của người hướng dẫn.

---

## Amendment Q-A1: chấm tay các hồi quy theo hợp đồng của HQ1 (BỔ SUNG, SAU KHI THẤY KẾT QUẢ)

Kế hoạch: `study_q/AMENDMENTS.md` (Q-A1), commit `f275126`, viết trước khi xem bất kỳ ví dụ nào. Dữ liệu: `qa1/` (`REPRO.json`, `ITEMS.json`, `KEY.json`, `RATINGS_ASSISTANT.json`, `RATINGS_SECOND.json`, `QA1_RESULT.json`, `CAPTURE.tar.gz`).

**Chạy lại và tái tạo** ([run 41192489807](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41192489807), 55/55 job thành công):

| | Số |
|---|---|
| Đơn vị HQ1 | 55 |
| Tái tạo đúng hệt (cùng patch, cùng hàm, cùng tóm tắt phân loại) | **36** (65%; RQ5 của Study P: 66%) |
| Không tái tạo | 19, gần như đều do chương trình sinh G2 được model viết lại khác lần cohort |
| Đơn vị tái tạo được có hồi quy theo hợp đồng → mục chấm | 31 đơn vị, 154 mục |

**Hai người chấm**, cùng bộ mã R / B / U của RQ5:

| | Trợ lý (chấm trước, commit `827b404`) | `gemini-4-argon` (mù, 0,38 USD) |
|---|---|---|
| R | 135 | 154 |
| B | 19 | 0 |

- **Đồng thuận:** 135/154 = 87,7%.
- **Kappa = 0,0.** Người chấm thứ hai mã R cho mọi mục, nên không có biến thiên. Kappa không mang thông tin; chỉ báo cáo kèm cho đủ.
- **Toàn bộ 19 mục bất đồng** là trợ lý mã B, người chấm thứ hai mã R, ở bốn hàm của sympy:
  - `MatrixDeterminant._eval_det_bareiss`: biểu thức khai triển ra đúng 0 (trợ lý đã kiểm bằng sympy), so với `0`;
  - `tensor_product_simp` và `IdentityOperator.__mul__`: cùng giá trị, khác dạng rút gọn;
  - `StrPrinter._print_Mul`: chỉ thừa dấu ngoặc.
- Bộ mã của RQ5 không liệt kê "biểu thức tương đương về toán" trong nhóm B. Mã B của trợ lý là một cách hiểu rộng hơn bộ mã, và người chấm thứ hai không được thấy phép kiểm bằng sympy.

**Kết quả** (`tools/q_review_agreement.py`):

| | Giá trị |
|---|---|
| Đơn vị có hồi quy đã xác nhận (≥ 1 mục được cả hai mã R) | 28/31 |
| Đơn vị tái tạo được **không** có hồi quy đã xác nhận | **8/36 = 22,2%** (Wilson 11,7% – 38,1%) |
| Hai cận trên cả 55 đơn vị (19 không tái tạo tính là có / không có hồi quy) | 14,5% – 49,1% |
| Nếu coi biểu thức tương đương là R (theo người chấm thứ hai) | 5/36 = 13,9% |
| Tham chiếu: HQ1 đã đăng ký | 6/55 = 10,9% |

**Diễn giải:**
1. Sau khi chấm tay, phần lớn khác biệt ngây thơ trên SWE-bench Verified vẫn là **khác biệt hành vi quan sát được** so với bản fix. Kết luận "HQ1 không được ủng hộ" **đứng vững**: mọi ước lượng ở bảng trên đều dưới 0,5, kể cả cận trên của Wilson (38,1%).
2. Kết luận ngược của RQ5 (Study P) không lặp lại được.
3. **"R" không có nghĩa là patch sai.** R là khác biệt mà người gọi hàm thấy được. Nhiều ca, patch có thể đúng hơn hoặc ngang bản fix, ví dụ `'1/(1/x)'` so với `'1/1/x'`, hay patch từ chối `exp` của một đại lượng có thứ nguyên. Bộ mã không phân xử ai đúng.
4. **Nhận xét định tính, sau khi thấy dữ liệu:** ở ít nhất ba hàm (`modify_field_list`, `apply_limit_choices_to_to_formfield`, `Field.__eq__`), đầu vào là đối tượng giả do G2 dựng (danh sách thay cho node docutils, model giả không có `_meta`, field chưa gắn model). Bản fix tình cờ trả giá trị, còn patch ném lỗi. Quy tắc "bản fix trả giá trị = đầu vào hợp lệ" xếp các ca này vào C1, dù đầu vào có thể nằm ngoài hợp đồng thật của hàm. Đây là giới hạn của cách phân loại, nên ghi trong bài.

**Giới hạn:**
- Người chấm thứ hai cùng họ model với model sinh G2 và không thấy đầu vào (giống RQ5).
- Trợ lý chấm theo từng hàm, vì các mục của cùng một hàm giống nhau.
- 19/55 đơn vị không tái tạo được.
- Lần chạy đầu của người chấm thứ hai ([run 41193552100](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41193552100)) thất bại vì token hết hạn và không lưu gì. Lần chạy được dùng là [run 41197881665](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41197881665), chia 6 job, công cụ chấm không đổi.
