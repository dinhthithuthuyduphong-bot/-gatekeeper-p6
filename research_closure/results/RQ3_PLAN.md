# RQ3: kế hoạch (ghi và commit TRƯỚC khi chạy)

**Câu hỏi:** bộ sinh đầu vào tự động có phát hiện **cùng một thay đổi hành vi** của một kỹ năng học được như bộ sinh viết tay của nghiên cứu gốc không? Đây là cầu nối giữa Study P và bài FSE gốc: cùng target, cùng kỹ năng, cùng cặp phiên bản.

## Đối tượng

**Quy tắc:** mọi target đánh giá (`study_d`, `study_e`, `study_g`, thư mục `eval_targets`) **trừ target smoke** (manifest ghi "SMOKE" trong `role`, hoặc dùng fixture cục bộ). Study H không có target đánh giá. Danh sách thật được workflow in ra và lưu ở mỗi lượt chạy.

**Sửa trước khi có dữ liệu (2/11/2026):** bản đầu của kế hoạch ghi "14 target", đếm trên bản repo cục bộ của người soạn; repo thật có 16 thư mục target. Lượt chạy đầu dừng ở bước lập kế hoạch, **trước** khi đo bất kỳ target nào, nên con số được thay bằng quy tắc trên. Với mỗi target: mã ở commit đã ghi, và cùng mã sau khi áp kỹ năng (`bind_modules`, như nghiên cứu gốc). Target mà kỹ năng không áp được (OUT_OF_SCOPE) được báo cáo và loại khỏi phép so.

## Bộ sinh

| Mã | Bộ sinh | Đầu vào |
|---|---|---|
| hand | `scopes()` của oracle viết tay, qua `execute()` | 200 mỗi phạm vi |
| G0 | theo chữ ký hàm, trên các hàm kỹ năng sửa (tối đa 3) | 200 mỗi hàm |
| G2 | chương trình `make_inputs` do `gemini-3.8-flash` viết, xem mã hàm gốc, mô tả kỹ năng và diff (tối đa 2 lời gọi mỗi hàm) | 200 mỗi hàm |

Bản gốc chạy hai lần, đầu vào không ổn định bị loại; mọi phiên bản chạy ở cùng một đường dẫn; tối đa 5 giây (hand) hoặc 2 giây (G0, G2) mỗi lời gọi.

## Phân tích

- **Chính:** với mỗi target, "phát hiện" = có ít nhất một đầu vào ổn định cho kết quả khác giữa hai phiên bản. Đồng thuận giữa hand và (G0 hoặc G2): **tỉ lệ đồng thuận** với khoảng Clopper–Pearson 95% [Clopper & Pearson 1934] và **kappa** [Cohen 1960].
- **Phụ:** đồng thuận riêng của G0 và G2; số target mà hand phát hiện nhưng bộ sinh tự động bỏ sót, và ngược lại; tỉ lệ chênh lệch theo phạm vi và theo hàm, đặt cạnh nhau.

**Vì sao thước đo chính là nhị phân:** oracle viết tay gọi qua API cấp cao, còn bộ sinh tự động gọi thẳng hàm bị sửa, nên không gian đầu vào khác nhau và tỉ lệ không so trực tiếp được.

## Giới hạn đã biết

14 target, gần như cùng một họ kỹ năng (`bool-excluded-from-int`; G1 dùng `none-identity`), nên khả năng khái quát hẹp. G2 xem diff của kỹ năng, nên đầu vào dồn quanh vùng thay đổi, như ở Study P.
