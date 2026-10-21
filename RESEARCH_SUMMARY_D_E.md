# Gatekeeper-Lite — tóm tắt kết quả nghiên cứu (Study D + Study E)

Hai nghiên cứu prospective, protocol đóng băng trước khi chạy, seed từ drand, cùng một skill học từ PySStuBs (loại `bool` khỏi kiểm tra `isinstance(x, int)`), cùng bộ chạy. **26 ô trên 12 repository** (Study D: 16 ô, 7 repo; Study E: 10 ô, 5 repo). Tái lập: Study D chạy lại cho kết quả giống hệt.

## Kết quả gộp (đếm theo ô; mô tả, không phải tỉ lệ quần thể)

| Comparator | Admit | Có lợi được admit | **Có hại được admit** | Thay đổi vô ích được admit |
|---|---|---|---|---|
| B2 (bind được là dùng) | 22 | 3/3 | **3/3** | 16 |
| B6-R (bind + replay + fingerprint) | 22 | 3/3 | **3/3** | 16 |
| B8 (chạy đủ 300 lần rút + census) | 19 | 3/3 | 0/3 | 16 |
| **Gatekeeper-Lite** | **2** | **2/3** | **0/3** | **0** |

*Ô có hại tính cả E3 (cấp 3, minh hoạ); nếu bỏ E3: B2/B6-R admit 2/2 ô có hại chính, Gatekeeper 0/2.*

## Ba điều Gatekeeper làm được mà B6-R không làm được

1. **Chặn tái dùng có hại** (Study E): B6-R admit cả 3; Gatekeeper từ chối cả 3 chỉ sau 2 lần rút mỗi ô. Bộ test gốc của target (tới 51.524 test) không bắt được các tác hại này.
2. **Chỉ chấp nhận khi có lợi ích đo được** (Study D): Gatekeeper không admit ô nào trong 16 thay đổi vô ích mà B2, B6-R và B8 đều admit (ví dụ skill sửa nhầm hàm không có lỗi).
3. **Kiểm soát sai số cho cả họ quyết định:** e-Holm FWER 0,1, kiểm tra bằng mô phỏng (FWER 0,040 ở kịch bản xấu nhất).

## Giới hạn phải nói rõ

- **Bỏ lỡ 1/3 ô có lợi** (pycubrid): lợi ích tập trung ở 11% đầu vào, dưới biên θ = 0,2. Kiểm định dấu (ablation) sẽ admit được.
- **Không tiết kiệm thời gian:** số lần rút ít hơn (Study D −11%, Study E −30%), nhưng wall-clock gần như bằng B8 vì census dùng chung chiếm phần lớn thời gian.
- **B8 an toàn ngang Gatekeeper** về ô có hại; khác biệt nằm ở việc B8 admit thay đổi vô ích và không có điểm dừng sớm.
- **Một họ lỗi, quy mô nhỏ;** ô có hại chính chỉ có 2; một ô tranh cãi (packaging).
- **B9 (sửa lỗi bằng LLM) chưa chạy** (chờ ngân sách sau 31/10, kế hoạch phân tích đã đăng ký trước).
