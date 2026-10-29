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
