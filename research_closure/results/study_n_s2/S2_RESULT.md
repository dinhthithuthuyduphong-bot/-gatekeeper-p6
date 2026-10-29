# Study N, giai đoạn N-S2: kết quả và cổng N1 (27/10/2026)

**Cổng N1: ĐẠT.** 107 ELIGIBLE trong 400 ứng viên đầu của `study_n/candidates_astar.json` (ngưỡng đã đăng ký: ≥ 60; tối thiểu 200 ứng viên). Kiểm định bằng `tools/vet_target2.py` bản 2.1; cả 400 ứng viên đều có kết quả.

| | Số |
|---|---|
| Ứng viên đã kiểm định | 400 |
| Có test chạy được | 162 |
| **ELIGIBLE** (có test fail trước, pass sau) | **107** (26,8%; Wilson 95%: 22,6% đến 31,3%), trên 61 repo |
| Test chạy, không có fail-to-pass | 55 |
| Không chạy được: thiếu module Python | 119 |
| Không chạy được: lỗi conftest hoặc fixture | 50 |
| Không chạy được: lý do khác | 67 |
| Lỗi của công cụ kiểm định | 2 |

Tỉ lệ ELIGIBLE (26,8%) nhỉnh hơn lượt phát triển trên nửa A\* đã lộ của Study M (23,8%; khoảng tin cậy chồng nhau), nên lượt phát triển không làm thổi phồng kết quả.

**Đầu vào cho N-S3:** `ELIGIBLE.json` liệt kê 107 instance theo thứ tự trong khung mẫu, kèm SHA của commit gốc và commit bản fix, các file thay đổi, và hash của từng bản ghi kiểm định gốc. Danh sách này được băm bởi amendment N-T1 trước khi chạy N-S3.
