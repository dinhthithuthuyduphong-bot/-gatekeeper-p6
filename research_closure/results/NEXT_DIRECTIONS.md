# Bốn hướng tiếp theo, đánh giá theo bằng chứng của Study N (đề xuất của người nghiên cứu)

Study N dừng ở N2 (8/107). Mỗi hướng dưới đây được đánh giá theo việc nó có giải quyết **đúng các nguyên nhân thất bại đã đo** hay không.

| Nguyên nhân ở N-S3 | Số | Hướng 1 (test của gói phụ thuộc) | Hướng 2 (draw sinh tự động, gọi thẳng hàm bị sửa) |
|---|---|---|---|
| Bản gốc không bao giờ khác bản fix | 22 | Có lẽ tệ hơn: test của client ít khi chạm đúng một bản fix nhỏ | **Giải quyết trực tiếp**: đầu vào được sinh cho chính hàm bị sửa |
| Không có test chạy tới code bị sửa | 17 | Không giải quyết | **Giải quyết**: không cần test nào chạy tới hàm |
| Lượt chạy nền không cho kết quả | 35 | Tệ hơn: phải cài thêm các gói client | **Có thể giải quyết**: chỉ cần import được module, không cần chạy bộ test |
| Không tất định | 17 | Không giải quyết | Một phần: so sánh giá trị trả về thay vì thông báo lỗi |
| Draw là tập hữu hạn, không hoàn lại | (giới hạn đã biết) | Không giải quyết, còn gom cụm theo gói | **Giải quyết**: generator cho draw độc lập cùng phân phối, đúng giả định của e-process |

## Đánh giá

**Hướng 2 (đề xuất làm hướng chính cho A\*).** Nó đánh vào đúng bốn trong năm nhóm nguyên nhân, và khôi phục giả định draw độc lập cùng phân phối mà kiểm định tuần tự cần. Có sẵn cách kiểm chứng: 12 target của các Study D đến H có generator viết tay, nên đo được độ đồng thuận giữa generator tự sinh và generator viết tay. **Rủi ro:** sinh khác biệt so với bản vá chuẩn đã có tiền lệ (theo hiểu biết của tôi, chưa kiểm chứng trong phiên này: sinh test ngẫu nhiên trên bản vá chuẩn để phát hiện patch quá khớp ở Java, và PatchDiff ở ICSE 2026 dùng LLM sinh test phân biệt). Phần mới phải nằm ở **ước lượng tỉ lệ chênh lệch theo đầu vào và so sánh các cổng có hiệu lực mọi lúc**, không phải ở việc sinh test. Ngoài ra, nhiều hàm cần đối tượng phức tạp, nên tỉ lệ gọi được có thể thấp. **Phải đo trước**, chi phí bằng 0.

**Hướng 1 (không làm hướng chính).** Trả lời đúng phê bình về oracle độc lập, nhưng làm **trầm trọng thêm** cả hai điểm nghẽn đã đo: cài đặt (phải cài thêm gói) và kích hoạt (test của client hiếm khi chạm một bản fix nhỏ). Có thể dùng làm kiểm tra độ vững trên vài instance đã qua.

**Hướng 3 (không đủ đứng riêng).** Mô phỏng của chính ta cho thấy kiểm định cỡ mẫu cố định an toàn như và mạnh hơn Gatekeeper ở cùng số draw; lợi thế của quy tắc tuần tự chỉ là dừng sớm. Hợp làm một mục của bài chính.

**Hướng 4 (lưới an toàn, làm song song ngay).** Dữ liệu đã đầy đủ và trung thực: Study M (khâu cài đặt từ 10% lên 27%), Study N (oracle mức test dùng được ở 1/13 instance, kèm phân loại nguyên nhân), các Study D đến H. Phù hợp tạp chí (EMSE, TOSEM) hoặc MSR; khó đạt A\*.

## Đề xuất thứ tự

1. **Đo khả thi Hướng 2 trước, không tốn tiền:** trên 107 instance A\* của Study N (đã lộ ở S2, S3 nhưng **chưa** lộ với oracle mức hàm), đo tỉ lệ instance mà hàm bị sửa gọi được với đầu vào sinh tự động **và** bản gốc khác bản fix trên ít nhất một đầu vào, có tất định.
2. Nếu tỉ lệ đủ cao: đăng ký **Study P** trên ứng viên **mới** (tiếp tục khám phá theo cùng thứ tự seed) cho nhánh A\*, và nửa RR (612 ứng viên, chưa chạm) cho nhánh RR.
3. Song song: viết bản thảo Hướng 4, làm lưới an toàn bất kể Hướng 2 ra sao.

Việc mở Study P là một **quyết định mới** của người nghiên cứu và người hướng dẫn, phải được ghi rõ trong bài, giống cách Study M dẫn tới Study N.
