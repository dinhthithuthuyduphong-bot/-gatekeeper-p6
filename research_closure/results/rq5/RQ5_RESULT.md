# RQ5: chênh lệch có phải hồi quy thật không (kết quả)

## Tái tạo

29 patch được sinh lại với đúng điều kiện của cohort; **19/29 (66%) tái tạo đúng hệt** mọi số đếm gốc. 10 patch không tái tạo được (model không hoàn toàn tất định dù cùng seed và nhiệt độ 0) được đưa vào dưới dạng hai cận, đúng như kế hoạch.

## Theo quy tắc đã commit trước (phân loại theo phản ứng của bản fix)

Trên 19 patch tái tạo được có **767 đầu vào hồi quy**:

| Loại | Số | Tỉ lệ |
|---|---|---|
| C1 (bản fix trả giá trị, patch khác): hồi quy trên đầu vào hợp lệ | 19 | 2,5% |
| C2 (bản fix ném lỗi): đầu vào ngoài hợp đồng | 748 | **97,5%** |
| C3 (quá hạn) | 0 | |

**Kết quả chính hiệu chỉnh:** patch plausible có θ̂ chỉ tính C1 trong vùng: **1 đến 4 trên 205 = 0,5% đến 2,0%** (Wilson: cận dưới 0,09% đến 2,7%; cận trên 0,8% đến 4,9%). Con số đã đăng ký là 16/205 = 7,8%.

Ca C1 duy nhất trong vùng trong số patch tái tạo được: `litellm_pr13466` (17 đầu vào, patch ném `RuntimeError` nơi bản fix trả danh sách). Ba cận trên đến từ patch không tái tạo được (`cadquery_pr1477`, `chembench_pr484`, `litellm_pr12108`).

## Phân tích sau khi thấy dữ liệu (KHÔNG có trong kế hoạch)

Quy tắc đã commit coi **mọi** C2 là ngoài hợp đồng. Điều đó đúng khi bản fix ném lỗi **ngẫu nhiên** do dùng sai, nhưng có thể sai khi bản fix ném lỗi **có chủ đích** để kiểm tra đầu vào. Phân theo loại ngoại lệ:

| Bản fix ném | Patch | Số | Diễn giải |
|---|---|---|---|
| cùng loại, khác thông báo | ném cùng loại | 370 | khác chữ trong thông báo lỗi |
| `IndexError` | trả giá trị | 231 | patch chịu đầu vào rỗng tốt hơn bản fix; gần như toàn bộ ở repo bài tập |
| `TypeError` | ném `ValueError` hoặc trả giá trị | 101 | khác cách phản ứng khi bị dùng sai |
| **`ValueError`, `NotImplementedError`** | **trả giá trị** | **46** | patch bỏ qua một kiểm tra **có chủ đích**: có thể là hồi quy thật |

Nếu tính thêm hai patch thuộc nhóm cuối (`swmmanywhere_pr177`, 8,1%; `ceci_pr85`, 3,5%): **3 đến 6 trên 205 = 1,5% đến 2,9%** (Wilson: 0,5% đến 6,2%).

## Kết luận

1. **Hồi quy thật trên đầu vào hợp lệ là hiếm**: khoảng **0,5% đến 3%** patch plausible, cận trên 95% khoảng 5 đến 6%.
2. **Con số đã đăng ký (7,8%) bị chi phối bởi khác biệt không phải hồi quy**: 97,5% đầu vào "hồi quy" nằm ở chỗ bản fix cũng ném lỗi, chủ yếu khác thông báo lỗi và đầu vào rỗng ở repo bài tập.
3. **Hệ quả phương pháp:** một oracle so sai khác hành vi "ngây thơ" (mọi khác biệt là tác hại) **phóng đại tỉ lệ hồi quy khoảng 3 đến 15 lần**; phải phân biệt theo hợp đồng của hàm. Điều này cũng đặt câu hỏi cho các con số chênh lệch hành vi đã công bố về patch plausible.

## Còn phải làm (bước 3 của kế hoạch)

Hai người chấm độc lập (trợ lý và `gemini-4-argon`) xem các ví dụ C1, và **mở rộng sau khi thấy dữ liệu** (ghi rõ) sang các ví dụ "từ chối có chủ đích" của `swmmanywhere_pr177` và `ceci_pr85`.

## Bước 3: hai người chấm (hoàn tất)

17 mục (7 ví dụ C1 theo kế hoạch; 10 ví dụ "từ chối có chủ đích" theo phần mở rộng sau khi thấy dữ liệu). Trợ lý chấm và commit trước; `gemini-4-argon` chấm mù (không thấy loại, nguồn gốc, giả thuyết), tốn 0,03 USD.

**Đồng thuận 17/17, cả hai chấm R cho mọi mục; kappa không xác định** (không có biến thiên). Bốn patch có khác biệt hành vi thật được xác nhận: `litellm_pr13466`, `splunk_ansible_pr896`, `swmmanywhere_pr177`, `ceci_pr85`.

**Kết quả RQ5 cuối cùng:**
- theo kế hoạch (C1, tái tạo được, trong vùng, được hai người xác nhận): **1/205 = 0,5%** (Wilson 0,09% đến 2,7%), `litellm_pr13466`, mà đầu vào là một đối tượng giả do model dựng;
- thêm các ca "từ chối có chủ đích" (sau khi thấy dữ liệu): **3/205 = 1,5%** (0,5% đến 4,2%);
- cận trên khi tính cả 3 patch không tái tạo được: 6/205 = 2,9% (1,3% đến 6,2%).

**Giới hạn của bước chấm:** các mục đã được lọc sẵn (chỉ C1 và từ chối có chủ đích), nên bước chấm không có ca nào để phân biệt R với B và không đo được độ tin cậy giữa người chấm; người chấm thứ hai cùng họ model với model sinh patch; người chấm chỉ thấy đầu ra, không thấy đầu vào.
