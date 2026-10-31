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
