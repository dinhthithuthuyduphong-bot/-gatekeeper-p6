# Kết quả harness v3 (D5, D2, D4) và kế hoạch v4 (phát triển, 26/10/2026)

Instance đã lộ kết quả; **không dùng làm bằng chứng xác nhận**. Không gộp số liệu v2, v3 và v4.

## Kết quả v3 (đã sửa maxfail, nhiễu id Mock)

| Target | Đủ cặp | Tất định | Tỉ lệ kích hoạt lỗi (bản gốc khác bản fix) | Patch đúng đã biết | Đột biến của bản fix bị bắt | Draw mà mọi arm đều chỉ thất bại |
|---|---|---|---|---|---|---|
| D5 pycubrid | 200/200 | có | **2,0% (4/200)** | skill: help 4, hurt 0 | 4/5 | 70,5% |
| D2 Cerberus | 199/199 | có | **0/199** | skill: help 0 | 1/2 | 74,4% |
| D4 openfeature | 200/200 | có | **0/200** | gold: help 0 | 4/5 | 66,5% |

Unit-only: 17 test qua trong cả bốn lần chạy.

- Kiểm soát dương hoạt động ở cả ba target: đột biến của bản fix bị bắt.
- Lỗi thật chỉ được thấy ở D5, qua 4 draw. Ở D2 và D4 không draw nào phân biệt bản gốc với bản fix.
- Gần hai phần ba draw ở cả ba target là draw mà mọi arm đều thất bại, nên không phân biệt được arm nào.
- Với D5, call replay của gate G1 cho tỉ lệ kích hoạt 8,7%; test-level cho 2,0%. Test-level thấp hơn.

## Một dự kiến bị bác bỏ bởi bằng chứng

Trước đó dự kiến v4 là "chỉ đột biến đầu vào" (loại literal nằm trong `assert`). Dữ liệu D5 bác bỏ điều này: cả 4 draw có ích đều là literal **trong dòng `assert`**, ở vế toán tử đang được kiểm tra (`STRING.__eq__("hello")` thành `STRING.__eq__(True)`; `STRING != "not an int"` thành `STRING != True`). 130 trong 200 dòng bị đột biến là dòng assert. Một bộ lọc cú pháp sẽ xoá đúng các draw có ích. **Không triển khai bộ lọc đó.**

## v4 (tm-dev-v4-reach)

Chỉ lấy mẫu từ những test **thực sự chạy tới hàm bị sửa** khi chạy nguyên trạng ở commit gốc (theo dõi bằng `sys.setprofile`, nhận diện theo file và dòng đầu của code object). Phân phối đột biến giữ nguyên. Lưu ý: ở giai đoạn phát triển, hàm bị sửa lấy từ bản fix upstream; khi dùng cho patch cần đánh giá, phạm vi là các test chạy tới code mà chính patch đó sửa.

Chưa thử trên repo thật: đường pytest (plugin) chỉ được kiểm thử gián tiếp; đường unittest được kiểm thử đầu cuối.

## Quy tắc đọc kết quả v4 (ghi TRƯỚC khi có dữ liệu v4; là phán đoán, không phải chuẩn khoa học)

1. Báo cáo cho từng target: số test chạy tới code bị sửa, tỉ lệ kích hoạt, help/hurt của patch đúng đã biết, tỉ lệ draw thất bại chung, đột biến bị bắt, đủ cặp, tất định.
2. Hướng test-level **tiếp tục** chỉ khi cả bốn kiểm tra (a)–(d) cùng tính đủ cặp đạt trên **ít nhất 2 trong 3** target (D5, D2, D4) dưới v4.
3. Ngược lại, **dừng hướng này vào 9/11/2026** và báo cáo kết quả âm, kèm tỉ lệ kích hoạt đo được.
4. Dù v4 đạt, đây vẫn chỉ là kết quả phát triển trên instance đã lộ; còn cần cohort mới được đóng băng trước khi xem kết quả.
