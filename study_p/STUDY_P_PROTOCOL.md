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
- **Nhánh A\*:** ứng viên A\* **mới** khi tiếp tục khám phá sau 1.300 ứng viên đó (theo khoá thứ tự), mục tiêu khoảng 1.000 ứng viên mới, tức khoảng 540 ứng viên A\*.
- **Nhánh RR:** nửa RR của 1.300 ứng viên đầu (612, chưa bị chạm) cộng phần RR mới; không chạm tới cho đến khi có IPA.

## 4. Giai đoạn và cổng (nhánh A\*), ngưỡng dự kiến

| Giai đoạn | Nội dung | Cổng dự kiến |
|---|---|---|
| P-S2 | Kiểm định bằng `vet_target2.py` bản 2.1 | **P1:** ≥ 100 ELIGIBLE trong 500 ứng viên đầu (dự kiến khoảng 134) |
| P-S3 | Oracle mức hàm, phân phối trộn | **P2:** ≥ 50 instance dùng được (dự kiến khoảng 70 nếu tỉ lệ như phát triển) |
| P-GEN | Sinh patch (model nhẹ; model mạnh theo quy tắc ở mục 6) | **P3:** ≥ 40 patch plausible |
| P-SCORE | θ̂ và quyết định của từng cổng trên cùng đầu vào | **P4:** ≥ 15 patch có θ̂ trong [max(1%, 2/n), 10%] và ≥ 8 patch mà các cổng quyết định khác nhau |

**Giả thuyết xác nhận (như Study N):** H1, hơn 10% patch plausible có θ̂ trong vùng trên; H2, smoke 20 admit sai hơn 15% patch không chấp nhận được (θ̂ > 5%); H3, kiểm định cỡ mẫu cố định admit ít nhất bằng Gatekeeper trên patch chấp nhận được. n = 400 đầu vào mỗi patch.

## 5. Ngân sách và lịch

Chỉ credit Free Trial (khoảng 288 USD, hết hạn 20/1/2027); trần cứng 200 USD cho toàn bộ P-GEN. Giá Flash tăng gấp đôi từ 1/1/2027, nên P-GEN nên chạy **trong tháng 12**.

## 6. Model

Model nhẹ `gemini-3.8-flash` bắt buộc. Model mạnh `gemini-4-argon` chỉ được mở sau một lượt thử trên **instance phát triển** (59 instance dùng được ở bước 2), theo đúng quy tắc của Study N mục 6, nay dùng oracle mức hàm.

## 7. Còn phải làm trước khi đóng băng

1. Pipeline sinh patch chấm bằng oracle mức hàm (thay phần chấm mức test).
2. Lượt thử trên instance phát triển (tương đương P0 và P1).
3. Kiểm định đồng thuận với bộ sinh viết tay (RQ3) trên 12 target cũ.
4. Chốt ngưỡng P1 đến P4 và kế hoạch phân tích; đưa mọi file vào danh sách băm; chạy kiểm tra trước khi đóng băng.
