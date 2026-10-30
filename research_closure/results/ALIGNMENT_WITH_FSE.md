# Đối chiếu hướng hiện tại với bài FSE gốc (31/10/2026)

**Bài gốc:** "Scope before Reuse: Risk-Controlled Admission of Learned Coding Skills" (FSE-2027-13). Đối tượng: **kỹ năng lập trình học được** (phép biến đổi mã tái sử dụng, cùng họ với Getafix, Genesis, Refazer, LASE). Câu hỏi: khi một kỹ năng học ở một phạm vi được **tái sử dụng** ở phạm vi khác, một chứng chỉ tác hại tuần tự có quyết định việc chấp nhận với rủi ro được kiểm soát tốt hơn các cổng đơn giản không.

## Bằng chứng đến nay so với kỳ vọng

| Kỳ vọng của bài gốc | Bằng chứng của chính dự án | Đánh giá |
|---|---|---|
| Tác hại một phần phổ biến khi tái sử dụng kỹ năng | Study D đến H: 12 target thật đều không có trạng thái (0/2.400 sai khác); cổng đơn giản là đủ | **Không ủng hộ**, trên các target đó |
| Gatekeeper tốt hơn cổng đơn giản | Đồ thị pha: ở cùng số draw, kiểm định cỡ mẫu cố định an toàn như và **mạnh hơn** Gatekeeper; PP0: ở patch có θ̂ = 2,5%, cỡ mẫu cố định admit còn Gatekeeper từ chối | **Không ủng hộ** về công suất. Lợi thế thật: dừng sớm và hiệu lực khi dừng tuỳ ý [Ramdas et al. 2023] |
| Oracle hành vi đo được tác hại | Oracle mức test: dùng được 8/107; oracle mức hàm: 59/107 (58 sau kiểm tra), chuỗi đo chạy ở 18/20 instance của PP0 | **Ủng hộ** với oracle mức hàm |
| Tác hại một phần tồn tại trong thay đổi mã thật | PP0 (instance đã lộ, thăm dò): patch qua mọi test ẩn nhưng hồi quy trên 2,5% và 4,75% đầu vào (`client_py_pr505`), 1,3% (`pyaptamer_pr542`) | **Có tín hiệu**, cần xác nhận trên cohort |

## Chỗ đang theo đúng và chỗ đang lệch

**Theo đúng:** cơ chế cốt lõi (chấp nhận có kiểm soát rủi ro bằng chứng chỉ tác hại, so với cổng đơn giản); oracle là sai khác hành vi so với một bản tham chiếu; đăng ký trước và báo cáo kết quả âm.

**Lệch:**
1. **Đối tượng** đổi từ kỹ năng học được (một phép biến đổi áp dụng ở nhiều chỗ) sang **patch LLM** (một thay đổi cho một PR).
2. **Chiều "phạm vi"** (tái sử dụng ở nơi khác) không còn trong Study P.
3. **Khẳng định Gatekeeper mạnh hơn** không được bằng chứng của chính dự án ủng hộ.

**Kết luận:** chưa lạc đường, nhưng đã **chuyển trọng tâm**. Study P trả lời câu hỏi về cổng bằng bằng chứng tốt hơn, nhưng không còn kiểm định việc tái sử dụng kỹ năng giữa các phạm vi.

## Đề xuất (cần người hướng dẫn quyết)

**(A) Đóng khung lại, không cố kéo về kỹ năng.** Khái niệm chung là **chấp nhận một thay đổi mã vào một phạm vi**: một patch LLM là thay đổi cho một phạm vi; một kỹ năng là thay đổi cho nhiều phạm vi; cả hai được đánh giá bằng cùng tỉ lệ hồi quy θ dưới phân phối đầu vào của phạm vi đó.
- Luận văn giữ tựa "Scope before Reuse", với hai phần: kỹ năng (Study D đến H, kết quả âm) và thay đổi mã (Study M đến P).
- Bài A\* đổi trọng tâm sang **đo tác hại một phần của patch LLM và chọn cổng chấp nhận**, với RQ3 (bộ sinh tự động so với bộ sinh viết tay trên 12 target của Study D đến H) làm **cầu nối** về đúng các target của bài gốc.

**Khẳng định cần bỏ hoặc thu hẹp:** "Gatekeeper mạnh hơn kiểm định cỡ mẫu cố định" (bỏ); "kỹ năng học được" thành "thay đổi mã" (thu hẹp); giữ "kiểm định hợp lệ mọi lúc" như một **tính chất** (hiệu lực khi dừng tuỳ ý, dừng sớm), không như lợi thế công suất.

**(B) Thêm chiều tái sử dụng vào Study P** (áp một patch sang các chỗ gọi khác): không tự nhiên với patch LLM, và cần một oracle mới; không đề xuất.
