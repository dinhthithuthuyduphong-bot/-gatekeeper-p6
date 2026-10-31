# Study P: kết quả (cohort xác nhận, phân tích theo kế hoạch đã băm, amendment P-A1 đến P-A4)

## Phễu (RQ1)

| Bước | Số |
|---|---|
| Khung A\* (toàn bộ không gian tìm kiếm) | 3.562 |
| Có bản ghi (1 job bị mất theo quy tắc P-A3: `cs340_s26_repo_pr76`) | 3.561 |
| ELIGIBLE sau kiểm định | 764 (21,5%) |
| Có hàm bị sửa dùng được (oracle mức hàm) | 415 (54,3% của ELIGIBLE) |
| Patch plausible của model nhẹ (1 mỗi instance) | **205** |

Lỗi sinh patch (31) đều là hạ tầng (429 sau khi đã thử lại, quá hạn đọc, mất kết nối). Chi phí model: khoảng 38,8 USD (Flash 12,43; Argon 20,59; chương trình sinh 5,75).

## Kết quả chính (đã đăng ký)

**16/205 = 7,8%** patch plausible có tỉ lệ hồi quy θ̂ trong vùng [3/n; 10,9%].

| Khoảng 95% | Giá trị |
|---|---|
| Wilson | 4,9% đến 12,3% |
| Bootstrap gom cụm theo repo (10.000 lần) | 4,4% đến 11,7% |

**P3 đạt** (nửa độ rộng 0,037 ≤ 0,05). **Cận dưới > 0.** **H1 (phụ) không bác bỏ** (p = 0,88; cần ≥ 29 ca), đúng như cảnh báo sớm sau PP2.

## H3 và các cổng

**P4 không đạt** (chỉ 4 cặp bất đồng giữa kiểm định cỡ mẫu cố định và Gatekeeper: 2 mỗi bên), nên **H3 không được kiểm định**. Ở n = 400, hai cổng thống kê gần như luôn quyết định giống nhau (cùng tỉ lệ admit 0,898).

| Cổng | Tỉ lệ admit | Admit patch θ̂ > 5% | Từ chối patch θ̂ = 0 |
|---|---|---|---|
| Census (qua test) | 1,000 | **16/16** | 0/176 |
| Zero-tolerance | 0,859 | 0/16 | 0/176 |
| B8+ | 0,702 | 0/16 | **32/176** |
| Smoke 20 | 0,907 | **2/16** | 0/176 |
| Cỡ mẫu cố định | 0,898 | 0/16 | 0/176 |
| Gatekeeper | 0,898 | 0/16 | 0/176 |

## Độ nhạy (đã đăng ký)

- Loại repo của tập phát triển: 14/127 = 11,0% (6,7% đến 17,7%).
- Tỉ trọng G2: 0% → 4,0% (1,8% đến 8,4%); 50% → 7,8%; 100% → 4,9% (2,7% đến 8,8%). Kết quả **phụ thuộc phân phối đầu vào**.

## Thăm dò: model mạnh

Argon: 229 patch plausible (Flash 205; ghép cặp: chỉ Flash 18, chỉ Argon 42), 22 trong vùng = 9,6% (6,4% đến 14,1%).

## Kiểm tra sau khi thấy kết quả (KHÔNG đăng ký trước, chỉ để diễn giải)

1. **Bootstrap gom cụm theo tên repo** (các fork của cùng một bài tập trùng tên): 3,9% đến 12,4%. Độ bất định vững.
2. **Loại repo có tên giống bài tập của sinh viên** (13 patch): **8/192 = 4,2%** (2,1% đến 8,0%). **8 trong 16 ca trong vùng đến từ bài tập.** Với dự án thật, tỉ lệ có lẽ gần 4% hơn 8%.
3. **`anomalib_pr2437` (θ̂ = 0,5):** cả 200 đầu vào G0 là "hồi quy", G2 là 0. Đầu vào theo chữ ký thường không hợp lệ với hàm; một khác biệt về loại lỗi trên đầu vào không hợp lệ có thể không phải hồi quy theo nghĩa người dùng quan tâm.

## Việc cần làm trước khi viết bài: RQ5 (kiểm tra thủ công)

Câu hỏi "chênh lệch có tương ứng với patch sai không" đã có trong giao thức (RQ5) nhưng chưa có kế hoạch chi tiết. Đây là mối đe doạ lớn nhất cho tính hợp lệ của phép đo. Kế hoạch phải được viết và commit **trước** khi xem bất kỳ ví dụ chênh lệch nào.
