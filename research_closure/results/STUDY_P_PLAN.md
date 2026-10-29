# Study P: kế hoạch và ngưỡng đi tiếp (ghi TRƯỚC khi chạy đo khả thi, 29/10/2026)

## Câu hỏi và định vị

Study P kết hợp hướng 2 và hướng 3: gọi **thẳng** hàm bị sửa với đầu vào sinh tự động, ước lượng **tỉ lệ chênh lệch theo đầu vào** của mỗi patch so với bản fix upstream kèm cận trên hợp lệ mọi lúc, và so sánh các cổng chấp nhận trên patch thật. Hướng 4 (vì sao kiểm tra ở mức test thất bại) trở thành RQ0 với dữ liệu của Study N. Hướng 1 nhiều nhất là oracle phụ. Lý do và các công trình liên quan: báo cáo nghiên cứu tiền lệ đi kèm.

## Bước 1: đo khả thi (không phải giai đoạn đăng ký, chi phí 0)

Trên **107 instance A\* của Study N** (`research_closure/results/study_n_s2/ELIGIBLE.json`): đã lộ ở N-S2 và N-S3 (oracle mức test), **chưa** lộ với oracle mức hàm. Không sinh patch nào.

Mỗi instance: tối đa 3 hàm bị sửa (có ở cả hai phiên bản), 200 đầu vào sinh theo chữ ký (`gatekeeper_ext/fn_inputs.py`), bản gốc chạy hai lần và bản fix một lần, mỗi lần trong một tiến trình riêng, tối đa 2 giây mỗi lời gọi. Một instance **dùng được** nếu có ít nhất một hàm với ≥ 100 đầu vào cho kết quả ổn định và bản gốc khác bản fix trên ít nhất một đầu vào.

## Ngưỡng đi tiếp, cố định từ bây giờ

| Kết quả của bước 1 | Hành động |
|---|---|
| **≥ 27 trên 107** instance dùng được (≥ 25%) | **Đi tiếp:** đăng ký Study P trên ứng viên mới (tiếp tục khám phá theo cùng thứ tự seed cho nhánh A\*; nửa RR 612 ứng viên chưa chạm cho nhánh RR). Với tỉ lệ ELIGIBLE 26,8%, khoảng 600 ứng viên mới cho khoảng 160 instance ELIGIBLE, nên khoảng 40 instance dùng được |
| **Từ 11 đến 26** | Đi tiếp có điều kiện: thử một bộ sinh mạnh hơn (đầu vào do model nhẹ viết, chi phí nhỏ) trên chính 107 instance này, với ngưỡng 27 không đổi |
| **≤ 10** (không hơn oracle mức test, 8/107) | Không mở Study P. Hướng 4 trở thành bài chính (tạp chí hoặc MSR), dùng dữ liệu Study M, N và các Study D đến H |

Ngưỡng 25% được chọn để một cohort mới có kích thước thực tế (khoảng 600 ứng viên kiểm định) đủ cho ≥ 40 instance dùng được. Nó là phán đoán, không phải phân tích công suất.

## Ghi chú về giới hạn của bộ sinh bước 1

Bộ sinh chỉ dùng kiểu khai báo, giá trị mặc định và một tập giá trị vô hướng; phương thức của lớp chỉ được gọi khi lớp dựng được không cần tham số. Vì vậy bước 1 là **cận dưới** của khả năng gọi được. Hàm cần đối tượng phức tạp, tệp hay mạng sẽ không gọi được ở bước này.

## Kết quả bước 1 (bộ sinh theo chữ ký, 29/10/2026)

**14 trên 107 instance dùng được (13,1%)**, nằm trong vùng 11 đến 26: chưa đủ ngưỡng 27, nên áp hành động "thử bộ sinh mạnh hơn" đã ghi ở trên.

| Phễu | Số |
|---|---|
| Không có hàm bị sửa ở cả hai phiên bản | 7 |
| Không hàm nào import hay gọi được | 28 |
| Kết quả không ổn định | 1 |
| Bản gốc không bao giờ khác bản fix trên đầu vào sinh ra | 57 |
| **Dùng được** | **14** |

Theo hàm: 74 hàm có bản gốc trùng bản fix trên mọi đầu vào; 45 là phương thức của lớp không dựng được nếu thiếu tham số; 10 không import được. Ở các hàm dùng được, tỉ lệ bản gốc khác bản fix có trung vị 72% (0,5% đến 100%).

**Quan sát sau khi xem kết quả (không dùng để vượt ngưỡng):** oracle mức hàm và mức test gần như không trùng nhau: cả hai dùng được ở 1 instance, chỉ mức hàm ở 13, chỉ mức test ở 7, không oracle nào ở 86.

## Bước 2: bộ sinh do model nhẹ viết (thiết kế cố định TRƯỚC khi chạy)

Cùng 107 instance, cùng tối đa 3 hàm mỗi instance, cùng định nghĩa "dùng được", **ngưỡng 27 không đổi**.

- **Model:** `google/gemini-3.8-flash`, `reasoning_effort` low, trần đầu ra 4.000 token. Tối đa **2 lời gọi** mỗi hàm: lời gọi đầu nhiệt độ 0; nếu bộ sinh lỗi khi chạy trên bản gốc, lời gọi thứ hai nhận thông báo lỗi.
- **Model được xem:** mã nguồn của hàm trong **bản gốc** (và `__init__` của lớp nếu là phương thức), đầu module, văn bản issue (issue liên kết hoặc tiêu đề PR), và **diff của bản fix cho file đó**. Model viết một hàm `make_inputs(rng, n)` trả về `n` bộ (đối tượng nhận, tham số vị trí, tham số tên). Bộ sinh chạy **trong từng snapshot** với cùng seed, nên mọi phiên bản nhận cùng một chương trình sinh.
- **Lời dặn model:** khoảng một nửa đầu vào là cách dùng thông thường, một nửa nhắm vào vùng mà issue và bản fix liên quan.
- **Lý do được xem bản fix:** bản fix là oracle, giống cách RGT sinh test trên bản vá chuẩn. **Giới hạn đã biết:** đầu vào tập trung quanh vùng sửa có thể bỏ sót chênh lệch ở chỗ khác; Study P (nếu mở) sẽ phải dùng phân phối trộn với bộ sinh theo chữ ký.
- **Ngân sách:** trần cứng 16 USD (0,15 USD mỗi instance, tính theo trường hợp xấu nhất), dự kiến khoảng 3 USD; chỉ credit Free Trial.
- **Kết luận:** ≥ 27 dùng được với bộ sinh bước 2 thì đăng ký Study P; nếu không, hướng 4 thành bài chính. Không có bước 3.
