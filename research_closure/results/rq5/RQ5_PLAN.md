# RQ5: chênh lệch có phải hồi quy thật không (kế hoạch, commit TRƯỚC khi xem bất kỳ ví dụ nào)

## Đối tượng

29 patch plausible của model nhẹ có θ̂ > 0 trong cohort Study P (`RQ5_TARGETS.json`; 16 trong vùng, 13 trên vùng). Hash của chương trình sinh đã được đối chiếu với bản ghi của cohort.

## Bước 1: sinh lại và kiểm tra tái tạo

Bản ghi cohort **không lưu nội dung patch** (thiếu sót thiết kế; đã sửa bằng chế độ ghi lại của amendment P-A5). Mỗi patch được **sinh lại** bằng đúng pipeline: cùng seed (`study-p-cohort:` + tên, lần lặp 0), cùng nhiệt độ, cùng giới hạn chi, cùng chương trình sinh đã lưu, chỉ với model nhẹ (seed không phụ thuộc danh sách model), với chế độ ghi lại bật.

**Quy tắc tái tạo:** patch sinh lại được dùng **chỉ khi** nó cho đúng hệt các số đếm gốc: số đầu vào chấm được, số hồi quy, số giúp ích, số khác biệt, và số hồi quy theo từng nguồn. Patch không tái tạo được được báo cáo riêng và đưa vào kết quả dưới dạng **hai cận** (tính như cũ, hoặc loại khỏi vùng).

## Bước 2: phân loại theo quy tắc (tự động, không phán đoán)

Mỗi đầu vào hồi quy (bản gốc trùng bản fix, patch khác) được xếp loại theo kết quả của **bản fix** (tham chiếu), theo nguyên lý hợp đồng [Meyer 1992]: một đầu vào mà phiên bản tham chiếu từ chối bằng ngoại lệ là đầu vào **ngoài hợp đồng** của hàm.

| Loại | Bản fix | Patch | Ý nghĩa |
|---|---|---|---|
| **C1a** | trả về giá trị | ném ngoại lệ | hồi quy trên đầu vào hợp lệ |
| **C1b** | trả về giá trị | trả về giá trị khác | hồi quy trên đầu vào hợp lệ |
| C2a | ném ngoại lệ | trả về giá trị | patch chấp nhận đầu vào mà tham chiếu từ chối |
| C2b | ném ngoại lệ | ném loại ngoại lệ khác | khác cách từ chối |
| C2c | ném ngoại lệ | cùng loại, khác thông báo | khác thông báo lỗi |
| C3 | quá hạn ở một trong hai | | không xác định |

**Đại lượng hiệu chỉnh:** θ̂_C1 = (C1a + C1b) / số đầu vào chấm được. **Kết quả chính hiệu chỉnh:** tỉ lệ patch plausible (trên 205) có θ̂_C1 trong vùng [3/n; 10,9%], kèm khoảng Wilson 95%. Patch có θ̂ = 0 không đổi. Cả 29 patch được xét lại (một patch trên vùng có thể rơi vào vùng khi chỉ tính C1).

## Bước 3: xem xét thủ công các ví dụ C1 (sau bước 2)

Tối đa 5 ví dụ C1 mỗi patch, gồm đầu vào, đầu ra của bản fix và của patch, được hai người chấm **độc lập**: (1) trợ lý, (2) `gemini-4-argon` không được biết loại hay giả thuyết. Bộ mã: **R** = khác biệt người dùng thấy được trong hành vi của hàm; **B** = khác biệt về biểu diễn không mang nghĩa (thứ tự của tập hợp không có thứ tự, sai số dấu phẩy động dưới 1e-9, khoảng trắng); **U** = không xác định. Báo cáo kappa [Cohen 1960]. Một patch được coi là **hồi quy đã xác nhận** khi có ít nhất một ví dụ được cả hai người chấm mã R.

## Báo cáo

Bảng phân loại theo patch; kết quả chính hiệu chỉnh (bước 2); tỉ lệ đã xác nhận (bước 3); số patch không tái tạo được và hai cận. Mọi kết quả này **bổ sung** cho kết quả đã đăng ký (7,8%), không thay thế nó.
