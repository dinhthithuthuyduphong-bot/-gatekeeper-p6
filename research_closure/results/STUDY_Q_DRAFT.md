# Study Q: bản nháp (chưa đăng ký; chờ kết quả khả thi Q-F0)

## Vì sao có Study Q

RQ5 của Study P cho thấy 97,5% đầu vào "hồi quy" của patch plausible nằm ở chỗ **bản fix cũng ném lỗi**; tỉ lệ hồi quy theo hợp đồng chỉ khoảng 0,5% đến 3%, so với 7,8% khi coi mọi khác biệt là tác hại. Kết luận đó đến từ dữ liệu của chính ta, một phần phân loại là sau khi thấy dữ liệu. Study Q **kiểm định nó trên một bộ dữ liệu độc lập, được cộng đồng dùng rộng rãi**: SWE-bench Verified [Jimenez et al. 2024; OpenAI 2024], nơi các công trình trước báo cáo tỉ lệ chênh lệch hành vi cao ở patch plausible [Wang, Pradel & Liu 2026].

## Câu hỏi (dự kiến)

| RQ | Nội dung |
|---|---|
| Q1 | Phễu khả thi: bao nhiêu instance có hàm bị sửa gọi thẳng được, bên trong Docker image chính thức |
| Q2 | Tỉ lệ patch plausible công khai (bản nộp của các agent) **khác hành vi** so với bản fix, đo bằng oracle mức hàm |
| Q3 (xác nhận) | Trong các patch có ít nhất một đầu vào "hồi quy" theo nghĩa ngây thơ, tỉ lệ **không có** hồi quy theo hợp đồng (loại C1 của RQ5, quy tắc giữ nguyên) |
| Q4 | Tỉ lệ hồi quy theo hợp đồng, ước lượng với độ chính xác định trước |

**Giả thuyết xác nhận dự kiến (HQ1):** tỉ lệ ở Q3 lớn hơn 0,5 (nhị thức chính xác một phía [Clopper & Pearson 1934]). Cơ sở: ở RQ5, 13 đến 15 trong 16 patch "trong vùng" không có hồi quy theo hợp đồng. Cỡ mẫu và các ngưỡng sẽ được **suy ra bằng công thức** sau Q-F0, như Study P (công suất, hiệu ứng thiết kế theo instance [Kish 1965], cận dưới Wilson của các tỉ lệ đo được [Wilson 1927]).

## Thiết kế dự kiến

- **Môi trường:** Docker image chính thức của SWE-bench cho từng instance; không tự cài môi trường (điểm nghẽn của Study M và N).
- **Patch:** các bản nộp công khai trong kho `SWE-bench/experiments`, chỉ patch được ghi là resolved (plausible); quy tắc chọn bản nộp sẽ được ghi trước, theo một tiêu chí khách quan (ví dụ theo ngày nộp).
- **Oracle:** mức hàm, hai nguồn đầu vào (G0, G2), cùng quy tắc ổn định, cùng đường dẫn chung, cùng che địa chỉ và số dòng như Study P; chế độ ghi lại bật từ đầu (lưu patch và mọi đầu ra).
- **Phân loại:** đúng quy tắc C1, C2, C3 đã commit ở RQ5 [Meyer 1992], kèm tách "từ chối có chủ đích" (ValueError, NotImplementedError và ngoại lệ tự định nghĩa) **ghi trước** thay vì sau khi thấy dữ liệu.
- **Ước lượng:** khoảng Wilson và bootstrap gom cụm theo instance và theo repo [Field & Welsh 2007]; ước lượng thay cho kiểm định có hay không ở Q4 [Cumming 2014].

## Q-F0 (đang chạy, 0 USD model)

Mẫu phân tầng 3 instance mỗi repo (khoảng 36 trên 12 repo), chỉ G0, bên trong image chính thức. Đo: kéo được image không, bản fix áp được không, phiên bản Python, tỉ lệ instance có hàm dùng được. Kết quả này dùng để **suy ra** cỡ mẫu và ngưỡng, rồi mới viết giao thức đăng ký.

## Tài liệu tham khảo bổ sung

- Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *ICLR 2024*.
- OpenAI (2024). Introducing SWE-bench Verified. (bài đăng kỹ thuật; cần kiểm tra lại trích dẫn chính xác)
- Meyer, B. (1992). Applying "design by contract". *Computer*, 25(10), 40–51.
- Các tài liệu khác như trong giao thức Study P, mục 8.

## Kết quả Q-F0 (G0, 0 USD)

- Hạ tầng chạy trọn **33/33** instance ngay lần đầu: quy ước tên image đúng, bản fix áp được, mọi môi trường Python (3.6 đến 3.11) chạy được qua `docker exec`. Có **182** bản nộp công khai trên SWE-bench Verified.
- Dùng được: **3/33 = 9%** (Wilson 3% đến 24%). Nguyên nhân thất bại giống hệt bước khả thi 1 của Study P: bản gốc không bao giờ khác bản fix trên đầu vào theo chữ ký (17 instance), và phương thức của lớp không dựng được (17 hàm); Django cần cấu hình settings khi import.

## Yêu cầu cỡ mẫu (suy ra bằng công thức)

HQ1 (nhị thức chính xác, α = 0,05, công suất 0,8, H0: 0,5, thay thế 0,8 theo RQ5) cần **18 patch có khác biệt ngây thơ**. Với cận dưới Wilson của tỉ lệ đó ở Study P (29/205, cận dưới 0,10) và một patch mỗi instance: cần **180 patch plausible**, tức **khoảng 180 instance dùng được** trên khung 500, tỉ lệ dùng được khoảng **36%**.

## Q-F1 (G2, khoảng 1 USD): quy tắc ghi trước

Chạy G2 (model nhẹ viết chương trình sinh, xem mô tả issue và diff) trên **đúng 33 instance** của Q-F0. **Đi tiếp với thiết kế một patch mỗi instance** khi cận dưới Wilson 95% của tỉ lệ dùng được, nhân 500, **≥ 180**. Nếu không đạt, xét thiết kế nhiều patch mỗi instance (các bản nộp khác nhau) với hiệu chỉnh hiệu ứng thiết kế [Kish 1965], dùng hệ số tương quan ước lượng từ dữ liệu, trước khi đăng ký.
