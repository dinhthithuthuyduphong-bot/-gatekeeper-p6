# Study P: giao thức (BẢN NHÁP, chưa đóng băng)

> Bản nháp để người nghiên cứu và người hướng dẫn xem. Sẽ được đóng băng (cùng mọi file quyết định trong danh sách băm) **trước** khi kiểm định cohort. Khung mẫu được dựng trước khi đóng băng vì việc đó không nhìn kết quả nào.

## 1. Câu hỏi nghiên cứu

| RQ | Nội dung | Dữ liệu |
|---|---|---|
| RQ0 | Vì sao kiểm tra hồi quy ở mức test thất bại trên PR thật | Study M, Study N (đã có) |
| RQ1 | Phễu khả thi của oracle mức hàm: bao nhiêu PR có hàm bị sửa gọi được và phân biệt được bản gốc với bản fix | Cohort P (đăng ký trước) |
| RQ2 | Phân phối tỉ lệ hồi quy theo đầu vào θ của từng patch LLM plausible so với bản fix, với cận trên hợp lệ mọi lúc | Cohort P |
| RQ3 | Bộ sinh tự động đồng thuận thế nào với bộ sinh viết tay | 12 target của các Study D đến H |
| RQ4 | Sai số và chi phí mẫu của các cổng chấp nhận (census, zero-tolerance, B8+, smoke 20, cỡ mẫu cố định, e-process) | Cohort P |
| RQ5 | Chênh lệch có tương ứng với patch sai không | Mẫu kiểm tra thủ công |

## 2. Đại lượng đo

Với mỗi đầu vào x và hàm bị sửa: **hồi quy** khi bản gốc cho cùng kết quả với bản fix, còn patch cho kết quả khác (giống định nghĩa ở mức test); **chênh lệch** khi patch khác bản fix. θ là xác suất hồi quy dưới phân phối đầu vào D, ước lượng bằng θ̂ trên n đầu vào.

**Phân phối D, trộn đều:** 50% từ bộ sinh theo chữ ký (bước 1), 50% từ chương trình sinh do model viết (bước 2). Lý do: chỉ dùng chương trình sinh "xem bản fix" sẽ dồn đầu vào quanh vùng sửa và bỏ sót hồi quy ở chỗ khác. Chương trình sinh của mỗi hàm được tạo **một lần**, lưu và băm **trước khi sinh bất kỳ patch nào**; patch không bao giờ được cho chương trình sinh xem.

**Thực thi:** mọi snapshot chạy ở cùng một đường dẫn; địa chỉ bộ nhớ và số dòng trong thông báo được che; bản gốc chạy hai lần, đầu vào cho kết quả không ổn định bị loại; tối đa 2 giây mỗi lời gọi.

## 3. Khung mẫu và hai nhánh

- **Thứ tự:** seed drand của Study M giai đoạn S1, cùng truy vấn và bộ lọc.
- **Đã lộ:** 500 ứng viên đầu của Study M và 800 ứng viên của Study N. Nhánh A\* của chúng là dữ liệu phát triển (bao gồm 107 instance dùng cho hai bước khả thi).
- **Phần A (đã dựng, 30/10/2026):** 1.000 ứng viên mới khi tiếp tục khám phá sau 1.300 ứng viên đó trong không gian tìm kiếm gốc: 555 A\*, 445 RR. Không gian gốc chỉ còn khoảng 800 kết quả, đủ cho khoảng 130 ứng viên nữa.
- **Phần B (không gian mở rộng, ghi trước khi kiểm định):** cùng truy vấn, bộ lọc và seed, trên (1) trang 3 đến 5 của 42 tháng gốc và (2) trang 1 đến 5 của 24 tháng mới từ 1/2021 tới 12/2022; loại mọi ứng viên đã lộ và mọi ứng viên của phần A; sắp theo cùng khoá thứ tự; nối sau phần A trong mỗi khung. Lý do: theo mục 4.2, ở mọi π_low hợp lý từ 0,2 đến 0,5, phần A thiếu từ 324 tới 1.735 ứng viên A\* (`tools/p_thresholds.py`). Mở rộng không gian, không hạ hiệu ứng nhỏ nhất đáng quan tâm.
- **Nhánh A\*:** ứng viên A\* của phần A rồi phần B, theo thứ tự.
- **Nhánh RR:** nửa RR của 1.300 ứng viên đầu (612, chưa bị chạm), rồi RR của phần A (445) và phần B; không chạm tới cho đến khi có IPA.
- **Phân tích độ nhạy đăng ký trước:** lặp lại phân tích chính sau khi loại các repo có mặt trong tập phát triển (nhánh A\* đã lộ của Study M và Study N).

## 4. Giai đoạn, cổng và cơ sở của các ngưỡng

Ngưỡng **không** do phán đoán: chúng được **suy ra** bằng `tools/p_thresholds.py` (tái tạo được) theo một chuỗi cố định.

### 4.1 Từ công suất của giả thuyết tới số patch (P3, P4)

| Giả thuyết | Phép kiểm định | Giả định thay thế và lý do | Cỡ mẫu (công suất 0,8, α = 0,05) |
|---|---|---|---|
| **H1:** hơn 10% patch plausible có θ̂ trong [max(1%, 2/n), 10%] | Nhị thức chính xác một phía, H0: p ≤ 0,10 | p = 0,20: **hiệu ứng nhỏ nhất đáng quan tâm**, gấp đôi giả thuyết không | 89 patch độc lập |
| **H3:** cỡ mẫu cố định admit ít nhất bằng Gatekeeper trên patch chấp nhận được | McNemar chính xác một phía trên cặp bất đồng | q = 0,90 = tỉ lệ cặp bất đồng mà cỡ mẫu cố định là bên admit, **mô phỏng** bằng chính các cổng ở n = 400, θ từ 1% đến 4% | 11 cặp bất đồng |

**Hiệu chỉnh gom cụm:** mỗi instance cho m patch (m = số model × số lần lặp), không độc lập. Theo **hiệu ứng thiết kế Kish**, DE = 1 + (m − 1)ρ. Với m = 3 và ρ = 0,3, DE = 1,6, nên H1 cần **P3 = 143 patch plausible**. Mô phỏng cho thấy một patch trong vùng thấp làm hai cổng thống kê bất đồng với xác suất 0,27; **P4 = 11 cặp bất đồng**.

**H2 được hạ thành ước lượng thứ cấp, có lý do lý thuyết:** xác suất smoke 20 admit một patch có tỉ lệ hồi quy θ là (1 − θ)^20, một hàm đã biết. Điều duy nhất cần đo là số patch thật có θ trong vùng đó, và H1 đã đo điều này. Ngoài ra, kiểm định H2 cần khoảng 88 patch không chấp nhận được, không khả thi.

### 4.2 Từ số patch tới số instance (P2, P1)

U = ⌈P3 / (m · π_low)⌉ instance dùng được (**P2**); E = ⌈U / u_low⌉ instance ELIGIBLE (**P1**); C = ⌈E / e_low⌉ ứng viên cần kiểm định. Mọi tỉ lệ là **cận dưới Wilson 95%** của giá trị đã đo:
- e_low = 0,226 (107/400 ELIGIBLE ở Study N);
- u_low = 0,448 (58/107 dùng được ở bước khả thi 2, sau kiểm tra đường dẫn);
- π_low = cận dưới của tỉ lệ patch plausible mỗi lần sinh, **đo ở lượt thử PP0**;
- ρ = max(ICC ước lượng ở PP0, 0,3).

| π_low | P2 (dùng được) | P1 (ELIGIBLE) | Ứng viên cần kiểm định |
|---|---|---|---|
| 0,20 | 239 | 534 | 2.358 |
| 0,30 | 159 | 356 | 1.572 |
| 0,40 | 120 | 268 | 1.184 |
| 0,50 | 96 | 215 | 950 |

**P1 và P2 sẽ được cố định bằng công thức trên với π_low và ρ đo ở PP0, trước khi đóng băng.** Nếu số ứng viên cần vượt khung hiện có, khung được mở rộng bằng cùng quy tắc khám phá (theo khoá thứ tự), trước khi đóng băng.

### 4.3 Lượt thử trên instance phát triển (không phải giai đoạn đăng ký)

| | PP0 | PP1 |
|---|---|---|
| Instance | 20 trong 58 instance phát triển dùng được (mỗi repo một, theo vị trí) | 10 đầu của PP0 |
| Model, số lần | `gemini-3.8-flash`, 3 lần | `gemini-4-argon`, 1 lần |
| Chi tối đa | 6 USD | 6 USD |
| Đạt khi | ≥ 16 instance chạy trọn chuỗi **và** ≥ 1 patch plausible | Chỉ báo cáo; mở nhánh Argon theo quy tắc ở mục 6 |
| Đầu ra cho ngưỡng | π_low, ICC | |

## 5. Ngân sách và lịch

Chỉ credit Free Trial (khoảng 288 USD, hết hạn 20/1/2027); trần cứng 200 USD cho toàn bộ P-GEN. Giá Flash tăng gấp đôi từ 1/1/2027, nên P-GEN nên chạy **trong tháng 12**.

## 6. Model

Model nhẹ `gemini-3.8-flash` bắt buộc. Model mạnh `gemini-4-argon` chỉ được mở sau một lượt thử trên **instance phát triển** (59 instance dùng được ở bước 2), theo đúng quy tắc của Study N mục 6, nay dùng oracle mức hàm.

## 7. Còn phải làm trước khi đóng băng

1. ~~Pipeline sinh patch chấm bằng oracle mức hàm~~ (xong: `gatekeeper_ext/fn_draws.py`, oracle `function` trong `tools/cohort_inner.py`).
2. Lượt thử PP0 (và PP1 nếu PP0 đạt); tính P1, P2 bằng `tools/p_thresholds.py --from-pilot`.
3. Kiểm định đồng thuận với bộ sinh viết tay (RQ3) trên 12 target cũ.
4. Mở rộng khung nếu cần; giai đoạn P-S3 tạo và băm chương trình sinh cho từng instance trước khi sinh patch.
5. Đưa mọi file vào danh sách băm; chạy kiểm tra trước khi đóng băng.
