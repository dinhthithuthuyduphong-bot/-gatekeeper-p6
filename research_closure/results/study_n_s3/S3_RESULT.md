# Study N, giai đoạn N-S3: kết quả và cổng N2

**Cổng N2: KHÔNG ĐẠT.** 8 trong 107 instance đủ điều kiện harness (ngưỡng đã đăng ký: ≥ 40). Cả 107 instance đều chạy xong; không có quá giờ.

| Nguyên nhân | Số | Diễn giải |
|---|---|---|
| Lượt chạy nền của bộ test không cho kết quả | 35 | **Không rõ nguyên nhân**: công cụ không ghi lại đuôi log ở bước này (thiếu sót chẩn đoán) |
| Bản gốc không bao giờ khác bản fix trên draw | 22 | Trung vị 10 hàm test và 200 draw: đột biến hằng số trong test không chạm tới hành vi mà bản fix thay đổi |
| Không tất định | 17 | Trung vị 72% draw thất bại ở mọi cánh tay; thông báo lỗi thay đổi giữa các lần chạy |
| Không có test nhanh nào chạy tới code bị sửa | 17 | Bộ test của PR không đi qua hàm được sửa |
| Không có hàm bị sửa tồn tại ở cả hai phiên bản | 4 | Bản fix thêm hàm mới |
| Lỗi khi chạy một cánh tay, hoặc không có đầu ra | 3 | |
| Chỉ 50 draw đủ cặp | 1 | |
| **Đạt** | **8** | trên 8 repo; trung vị 200 draw; tỉ lệ kích hoạt lỗi trung vị 2,5% (0,5% đến 10,5%); 7/8 có đối chứng dương (đột biến AST bị bắt) |

**Hệ quả theo `study_n/DECISION_RULE.md`:** F1 không đạt, nên nhánh A\* của Study N dừng. Nhánh RR dự phòng của Study N dùng **cùng** harness, nên với tỉ lệ 7,5% đã đo, nó cũng không khả thi như thiết kế. Không có patch nào được sinh cho cohort; không có kết quả patch nào được xem.

**Kết luận thực nghiệm (có giá trị tự thân):** trên PR sửa lỗi Python thật, chỉ khoảng **1 trên 13** instance có kiểm thử hồi quy ở mức test (đột biến test của upstream, so với bản fix) dùng được. Điểm nghẽn gồm cả hạ tầng chạy test (35 + 17) và bản chất của oracle (22 + 17).
