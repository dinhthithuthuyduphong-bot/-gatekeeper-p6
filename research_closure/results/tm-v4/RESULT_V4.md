# Kết quả harness v4 (tm-dev-v4-reach) trên D5, D2, D4: giai đoạn phát triển

Instance đã lộ kết quả; **không dùng làm bằng chứng xác nhận**. Không gộp số liệu v2, v3, v4. Unit-only: 20 test qua trong cả bốn lần chạy.

## Số đo

| Target | Test chạy tới code bị sửa | Draw (đủ cặp) | Tất định | Kích hoạt (gốc khác fix) | Patch đúng đã biết | Đột biến bản fix bị bắt | Draw mà mọi arm chỉ thất bại | Bốn kiểm tra |
|---|---|---|---|---|---|---|---|---|
| D5 pycubrid | 5/23 | 91 | có | **6,6% (6/91)** | skill: help 6, hurt 0 | 4/5 | 25,3% | **đạt** |
| D4 openfeature | 17/133 | 200 | có | **1,0% (2/200)** | gold: help 2, hurt 0 | 5/5 | 44,0% | **đạt (yếu)** |
| D2 Cerberus | 12/145 | 200 | có | **1,0% (2/200)** | skill: **help 0** | 2/2 | 76,5% | không đạt (a) |

## So với v3 (cùng instance)

| Target | Kích hoạt v3 → v4 | Draw thất bại chung v3 → v4 |
|---|---|---|
| D5 | 2,0% → 6,6% | 70,5% → 25,3% |
| D4 | 0% → 1,0% | 66,5% → 44,0% |
| D2 | 0% → 1,0% | 74,4% → 76,5% |

Bộ lọc theo độ phủ giúp rõ ở D5 và D4; gần như không giúp D2.

## Các draw có ích là gì (đã kiểm tra từng draw)

- **D5 (6 draw):** đều có dạng `STRING op True/False` (`STRING.__eq__("hello")` thành `STRING.__eq__(True)`, `STRING != 8` thành `STRING != True`). Bản gốc coi bool như int; bản fix và patch của skill thì không. Patch giống bản fix ở cả 6.
- **D4 (2 draw):** `FlagResolutionDetails(value=True)` thành `value=-1` hoặc `{}`. Bản gốc trả nguyên giá trị sai kiểu; bản fix trả về mặc định (False). Cả hai test đều thất bại, nhưng giá trị trong thông báo assert khác nhau; chỉ chữ ký thông báo lỗi chuẩn hoá mới phân biệt được.
- **D2 (2 draw):** (i) `assertBadType('a_number', 'number', False)`: bản fix chấp nhận test, bản gốc **và patch của skill** thì thất bại; (ii) `'max': True` trong schema: bản fix ném `SchemaError`, bản gốc và skill thì không.

## Phát hiện về D2

Harness phát hiện đúng lỗi nhưng **patch của skill giống bản gốc, không giống bản fix**, ở cả hai draw. Điều này khớp với Study D, nơi skill ở D2 không cho lợi ích đo được (QUARANTINE; B6-R và B8 đều NO_EFFECT). Kiểm tra (a) thất bại ở D2 vì **patch được dùng làm "patch đúng đã biết" thực ra không sửa lỗi**, không phải vì harness không thấy lỗi. Định nghĩa "patch đúng đã biết = skill nếu skill gắn được" trong L-A1 là một giả định sai cho D2. Không đổi kết quả cho vừa; ghi lại như một giới hạn của định nghĩa.

## Áp dụng quy tắc đã ghi trước

Quy tắc: tiếp tục hướng test-level nếu (a)–(d) cùng tính đủ cặp đạt trên **ít nhất 2 trong 3** target. D5 và D4 đạt, nên điều kiện **thỏa**. Lưu ý D4 đạt yếu: patch là chính bản fix nên (b) vô nghĩa và (a) chỉ dựa trên 2 draw.

## Giới hạn

- Lượng draw nhỏ: D5 chỉ có 91 draw duy nhất vì chỉ 5 test chạy tới code bị sửa; mẫu gần như liệt kê hết không gian đột biến, không còn là mẫu độc lập đồng phân phối.
- Tỉ lệ kích hoạt 1–6,6% ở các instance đã được chọn vì có lỗi đã biết; chưa biết trên instance mới.
- Draw thất bại chung vẫn 25–77%.
- Vẫn là bằng chứng phát triển, trên instance đã lộ.
