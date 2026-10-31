# Study Q: giao thức (đóng băng bằng workflow `Gatekeeper Study Q freeze`; dựa trên Q-F0, Q-F1, Q-F2)

## 1. Câu hỏi

| RQ | Nội dung |
|---|---|
| Q1 | Phễu: instance của SWE-bench Verified có hàm bị sửa gọi thẳng được bên trong Docker image chính thức |
| Q2 | Tỉ lệ patch plausible công khai **khác hành vi** so với bản fix (mọi khác biệt) |
| **Q3 (xác nhận, HQ1)** | Trong các instance có ít nhất một patch có khác biệt ngây thơ (bản gốc trùng bản fix, patch khác), tỉ lệ mà patch được chọn **không có** hồi quy theo hợp đồng (không có đầu vào loại C1 và không có từ chối có chủ đích bị bỏ qua) |
| Q4 | Tỉ lệ patch plausible có hồi quy theo hợp đồng, ước lượng với độ chính xác |
| Q5 | Hệ số phóng đại: Q2 so với Q4 |

## 2. Khung và chọn patch

- **Instance:** 469/500 instance của SWE-bench Verified [Jimenez et al. 2024; OpenAI 2024] có ít nhất một patch resolved lấy được trong kiểm kê Q-F2 (125/182 bản nộp; tệp kho patch được băm lúc đóng băng).
- **Patch:** với mỗi instance, các patch resolved được gom theo nội dung (chuẩn hoá); thứ tự là `sha256(seed : instance : sha của patch)`, seed lấy từ drand **sau** khi đóng băng (như Study M, N, P); lấy **m = 3** patch đầu (ít hơn nếu instance có ít hơn).
- **Cơ sở của m = 3** (mục 4): với m = 1, số patch có khác biệt kỳ vọng theo cận dưới là 17,9 < 18 cần thiết; với m = 3, trường hợp xấu nhất (tương quan hoàn toàn giữa các patch của cùng instance) bằng m = 1, mọi trường hợp khác lớn hơn (tới 48,4 khi độc lập).

## 3. Đo

- **Môi trường:** Docker image chính thức của từng instance; bản gốc = `/testbed`, bản fix = bản gốc + patch vàng, patch = bản gốc + patch của agent; mọi snapshot chạy ở cùng một đường dẫn.
- **Oracle mức hàm:** hai nguồn đầu vào, G0 (theo chữ ký) và G2 (model nhẹ viết `make_inputs`, xem mô tả issue và diff của bản fix), 200 đầu vào mỗi nguồn. Chương trình G2 của mỗi instance được **tạo một lần, lưu và băm trước khi chấm bất kỳ patch nào**. Bản gốc chạy hai lần; đầu vào không ổn định bị loại. **Chế độ ghi lại bật**: lưu patch và mọi đầu ra.
- **Dùng được:** có ít nhất một hàm bị sửa với ≥ 100 đầu vào ổn định mà bản gốc khác bản fix trên ít nhất một đầu vào (như Study P).

## 4. Phân loại (ghi trước, rút kinh nghiệm từ RQ5)

Mỗi đầu vào có khác biệt ngây thơ (bản gốc trùng bản fix, patch khác) được xếp theo phản ứng của **bản fix** [Meyer 1992]. "Có chủ đích" được xác định theo **nguồn gốc** của ngoại lệ, không theo loại: một ngoại lệ là **chủ động** khi khung lệnh cuối cùng của traceback nằm trong mã của chính repo (không trong thư viện) và dòng đó là một câu lệnh `raise`, cách lập trình viên chủ động phát ngoại lệ [Python Language Reference, "The raise statement"]; ngược lại là **ngẫu nhiên** (phát sinh trong lúc thực thi, ví dụ `IndexError` khi truy cập danh sách rỗng). Lý do không dùng danh sách loại ngoại lệ: tài liệu Python cho thấy cùng một loại (ví dụ `TypeError`, `ValueError`) vừa có thể được ném chủ động để kiểm tra đầu vào, vừa có thể phát sinh ngẫu nhiên [Python Library Reference, "Built-in Exceptions"]. Cờ này được ghi bởi `tools/q_probe_inner.py`, lớp bọc của trình chạy của Study P (không sửa tệp nào của Study P).

| Loại | Bản fix | Patch | Tính là hồi quy theo hợp đồng |
|---|---|---|---|
| C1 | trả giá trị | ném lỗi, hoặc giá trị khác | **Có** |
| C2-D | ném lỗi **chủ động** | trả giá trị | **Có** (bỏ qua một kiểm tra có chủ đích) |
| C2-O | ném lỗi ngẫu nhiên; hoặc cả hai cùng ném | bất kỳ | Không (ngoài hợp đồng) |
| C3 | quá hạn | | Không xác định |

## 5. Giả thuyết và cỡ mẫu

**HQ1:** tỉ lệ ở Q3 > 0,5. Nhị thức chính xác một phía, α = 0,05 [Clopper & Pearson 1934]; thay thế 0,8 (RQ5 của Study P: 13 đến 15 trên 16 patch không có hồi quy theo hợp đồng); công suất 0,8 [Cohen 1988] cần **18 instance**. Đơn vị là instance (một patch có khác biệt mỗi instance, chọn theo thứ tự seed) để các đơn vị độc lập.

**Ước tính đạt được (cận dưới):** 469 × 0,380 (Wilson dưới của Q-F1, 18/33) = 178 instance dùng được; với m = 3 và cận dưới 0,10 của tỉ lệ có khác biệt (Study P, 29/205), từ 17,9 đến 48,4 instance có patch có khác biệt.

**Cổng Q-G1:** nếu số instance có patch có khác biệt **< 18**, HQ1 không được kiểm định (báo cáo mô tả).

## 6. Phân tích

1. Q1: phễu.
2. Q2, Q4: tỉ lệ ở mức patch, khoảng Wilson [Wilson 1927] và bootstrap gom cụm theo instance và theo repo [Field & Welsh 2007]; Q4 với độ chính xác báo cáo kèm [Cumming 2014].
3. **HQ1** như mục 5.
4. Q5: tỉ lệ Q2/Q4 kèm khoảng bootstrap.
5. **Độ nhạy:** (a) chỉ C1 (như kế hoạch RQ5 của Study P, không có C2-D); (b) chỉ G0, chỉ G2; (c) chỉ bản nộp trước 2025; (d) loại instance có ít hơn 3 patch khác nhau.

## 6b. Công cụ

`tools/q_instance.py` (mỗi instance), `tools/q_probe_inner.py`, `gatekeeper_ext/q_classify.py`, `tools/q_analyze.py`; kho patch `study_q/evidence/POOL.jsonl.gz` và dữ liệu `study_q/evidence/VERIFIED.json` được commit bởi workflow `Gatekeeper Study Q pool` trước khi đóng băng; seed lấy từ drand sau đóng băng.

## 7. Ngân sách và thời gian

Model: chỉ chương trình sinh G2, khoảng 0,01 USD mỗi instance, dưới 10 USD; credit Free Trial. Máy: khoảng 469 job (mỗi instance một job, như P-A3), tối đa 20 song song.

## 8. Giới hạn đã biết

- Patch resolved theo bộ test của SWE-bench; mục tiêu là patch plausible, không phải mọi patch.
- Chương trình sinh G2 xem diff của bản fix: đầu vào dồn quanh vùng sửa (như Study P).
- Tiêu chí "chủ động" dựa vào dòng cuối của traceback; một kiểm tra được viết qua hàm trợ giúp (raise nằm trong hàm khác của repo) vẫn được tính là chủ động, còn một ngoại lệ do thư viện ném thay cho repo thì không. Phân tích độ nhạy (a) cho thấy kết quả khi bỏ hẳn C2-D.
- 57 bản nộp không lấy được (47 không có thư mục kết quả); khung là "bản nộp công khai lấy được", không phải mọi bản nộp.

## 9. Tài liệu tham khảo bổ sung

- Python Software Foundation. *The Python Language Reference*, "Simple statements: the raise statement".
- Python Software Foundation. *The Python Standard Library*, "Built-in Exceptions".
- Meyer, B. (1992). Applying "design by contract". *Computer*, 25(10), 40–51.
- Jimenez, C. E., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *ICLR 2024*.
- Các tài liệu thống kê như trong giao thức Study P, mục 8.
