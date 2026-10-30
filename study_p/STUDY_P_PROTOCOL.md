# Study P: giao thức (BẢN NHÁP, chưa đóng băng)

> Bản nháp để người nghiên cứu và người hướng dẫn xem. Sẽ được đóng băng (cùng mọi file quyết định trong danh sách băm) **trước** khi kiểm định cohort. Khung mẫu được dựng trước khi đóng băng vì việc đó không nhìn kết quả nào.

## 1. Câu hỏi nghiên cứu

| RQ | Nội dung | Dữ liệu |
|---|---|---|
| RQ0 | Vì sao kiểm tra hồi quy ở mức test thất bại trên PR thật | Study M, Study N (đã có) |
| RQ1 | Phễu khả thi của oracle mức hàm: bao nhiêu PR có hàm bị sửa gọi được và phân biệt được bản gốc với bản fix | Cohort P (đăng ký trước) |
| RQ2 | Phân phối tỉ lệ hồi quy theo đầu vào θ của từng patch LLM plausible so với bản fix, với cận trên hợp lệ mọi lúc | Cohort P |
| RQ3 | Bộ sinh tự động đồng thuận thế nào với bộ sinh viết tay | 12 target của các Study D đến H |
| RQ4 | Sai số và chi phí mẫu của các cổng chấp nhận (census, zero-tolerance, B8+, smoke 20, cỡ mẫu cố định, e-process) | Cohort P |
| RQ5 | Chênh lệch có tương ứng với patch sai không | Mẫu kiểm tra thủ công |

## 2. Đại lượng đo

Với mỗi đầu vào x và hàm bị sửa: **hồi quy** khi bản gốc cho cùng kết quả với bản fix, còn patch cho kết quả khác (giống định nghĩa ở mức test); **chênh lệch** khi patch khác bản fix. θ là xác suất hồi quy dưới phân phối đầu vào D, ước lượng bằng θ̂ trên n đầu vào.

**Phân phối D, trộn đều:** 50% từ bộ sinh theo chữ ký (bước 1), 50% từ chương trình sinh do model viết (bước 2). Lý do: chỉ dùng chương trình sinh "xem bản fix" sẽ dồn đầu vào quanh vùng sửa và bỏ sót hồi quy ở chỗ khác. Chương trình sinh của mỗi hàm được tạo **một lần**, lưu và băm **trước khi sinh bất kỳ patch nào**; patch không bao giờ được cho chương trình sinh xem.

**Thực thi:** mọi snapshot chạy ở cùng một đường dẫn; địa chỉ bộ nhớ và số dòng trong thông báo được che; bản gốc chạy hai lần, đầu vào cho kết quả không ổn định bị loại; tối đa 2 giây mỗi lời gọi.

## 3. Khung mẫu và hai nhánh

- **Thứ tự:** seed drand của Study M giai đoạn S1, cùng truy vấn và bộ lọc.
- **Đã lộ:** 500 ứng viên đầu của Study M và 800 ứng viên của Study N. Nhánh A\* của chúng là dữ liệu phát triển (bao gồm 107 instance dùng cho hai bước khả thi).
- **Phần A (đã dựng, 30/10/2026):** 1.000 ứng viên mới khi tiếp tục khám phá sau 1.300 ứng viên đó trong không gian tìm kiếm gốc: 555 A\*, 445 RR. Không gian gốc chỉ còn khoảng 800 kết quả, đủ cho khoảng 130 ứng viên nữa.
- **Phần B (không gian mở rộng, ghi trước khi kiểm định):** cùng truy vấn, bộ lọc và seed, trên (1) trang 3 đến 5 của 42 tháng gốc và (2) trang 1 đến 5 của 24 tháng mới từ 1/2021 tới 12/2022; loại mọi ứng viên đã lộ và mọi ứng viên của phần A; sắp theo cùng khoá thứ tự; nối sau phần A trong mỗi khung. Lý do: theo mục 4.2, ở mọi π_low hợp lý từ 0,2 đến 0,5, phần A thiếu từ 324 tới 1.735 ứng viên A\* (`tools/p_thresholds.py`). Mở rộng không gian, không hạ hiệu ứng nhỏ nhất đáng quan tâm.
- **Nhánh A\*:** ứng viên A\* của phần A rồi phần B, theo thứ tự.
- **Nhánh RR:** nửa RR của 1.300 ứng viên đầu (612, chưa bị chạm), rồi RR của phần A (445) và phần B; không chạm tới cho đến khi có IPA.
- **Phân tích độ nhạy đăng ký trước:** lặp lại phân tích chính sau khi loại các repo có mặt trong tập phát triển (nhánh A\* đã lộ của Study M và Study N).

## 4. Giai đoạn, cổng và cơ sở của các ngưỡng

Mọi ngưỡng được **tính** bằng `tools/p_thresholds.py --pilot-dir` từ dữ liệu đã đo, theo công thức có trích dẫn ở mục 8. Không có ngưỡng nào do phán đoán.

### 4.1 Vùng tác hại một phần

Vùng = [3/n, 1 − 0,1^(1/20)], tức [0,75%; 10,9%] khi n = 400.
- **Cận dưới 3/n:** quy tắc ba [Hanley & Lippman-Hand 1983]. Với 0 sự kiện trong n đầu vào, cận trên 95% của tỉ lệ xấp xỉ 3/n, nên tỉ lệ thấp hơn không phân biệt được với 0.
- **Cận trên 1 − 0,1^(1/20):** smoke 20 admit một patch có tỉ lệ θ với xác suất (1 − θ)^20; phía trên cận này xác suất đó dưới 10%, nên cổng đơn giản đã đủ. (Study M và N dùng [1%, 10%] do phán đoán; Study P thay bằng hai cận suy ra.)

### 4.2 Từ công suất tới số patch

| Giả thuyết | Phép kiểm định | Giả định | Cỡ mẫu |
|---|---|---|---|
| **H1:** hơn 10% patch plausible có θ̂ trong vùng | Nhị thức chính xác một phía [Clopper & Pearson 1934], α = 0,05, công suất 0,80 [Cohen 1988] | Thay thế p = 0,20 là **hiệu ứng nhỏ nhất đáng quan tâm** [Lakens et al. 2018]: gấp đôi giả thuyết không | **P3 = 89** patch plausible |
| **H3:** cỡ mẫu cố định admit ít nhất bằng Gatekeeper trên patch chấp nhận được | McNemar chính xác [McNemar 1947] | q = 0,90 **mô phỏng** bằng chính các cổng ở n = 400 | **P4 = 11** cặp bất đồng |
| H2 (smoke 20 admit sai) | Không kiểm định | (1 − θ)^20 là hàm đã biết; điều cần đo là số patch ở vùng đó, H1 đã đo | Ước lượng thứ cấp |

### 4.3 Một patch mỗi instance: kết quả của PP0, không phải lựa chọn tuỳ ý

Ở PP0 (20 instance × 3 lần), hệ số tương quan trong cụm của biến "plausible" là **0,87** (ước lượng ANOVA [Donner & Klar 2000]); cận trên 95% bằng bootstrap theo cụm [Field & Welsh 2007] là **1,0**; 18/20 instance cho cùng kết quả ở cả 3 lần. Theo thiết kế cụm tối ưu [Raudenbush 1997], m\* = √((c₁/c₂)·(1 − ρ)/ρ) → 0 khi ρ → 1: lặp lại không thêm thông tin, nên **mỗi instance sinh đúng 1 patch** cho mỗi model. Khi đó hiệu ứng thiết kế [Kish 1965] bằng 1 và các instance độc lập.

### 4.4 Từ số patch tới số instance

U = ⌈P3/π_low⌉ (**P2**), E = ⌈U/u_low⌉ (**P1**), C = ⌈E/e_low⌉ ứng viên. Mọi tỉ lệ là cận dưới Wilson 95% [Wilson 1927] **trên đơn vị độc lập**:
- π_low = 0,299 (PP0: 10/20 instance có patch plausible ở lần đầu);
- u_low = 0,448 (bước khả thi 2: 58/107);
- e_low = 0,226 (Study N: 107/400).

| Cổng | Giai đoạn | Ngưỡng |
|---|---|---|
| **P1** | P-S2 kiểm định | ≥ **666** ELIGIBLE (cần kiểm định khoảng **2.941** ứng viên A\*) |
| **P2** | P-S3 oracle mức hàm | ≥ **298** instance dùng được |
| **P3** | P-GEN | ≥ **89** patch plausible |
| **P4** | P-SCORE | ≥ **11** cặp bất đồng giữa cỡ mẫu cố định và Gatekeeper |

Khung A\* sau phần B có 1.940 ứng viên, nên phần B được **chạy tiếp** theo cùng quy tắc tới khi đủ 2.941, trước khi đóng băng.

### 4.5 Phân phối đầu vào: lựa chọn được thay bằng báo cáo phân tầng

Tỉ trọng trộn giữa bộ sinh theo chữ ký (G0) và bộ sinh do model viết (G2) là một lựa chọn, nên **không** được để quyết định kết quả: θ được ước lượng **riêng cho từng tầng** và cho phân phối trộn [ước lượng phân tầng, Cochran 1977], và H1 được báo cáo với ba tỉ trọng (0, 50, 100% G2) như phân tích độ nhạy; kết luận chính dựa vào tỉ trọng 50% đã đăng ký.

### 4.6 Mục tiêu suy luận chính sau PP2 (thay đổi trước khi đóng băng)

**Dữ liệu thử nghiệm dẫn tới thay đổi:** gộp PP0 (lần sinh đầu) và PP2 trên 58 instance phát triển, 4/34 patch plausible có θ̂ trong vùng: **11,8%** (Wilson 95%: 4,7% đến 26,6%). Nếu tỉ lệ thật quanh 12%, phép kiểm định H1 (H0: p ≤ 0,10) có công suất chỉ 0,11 với 89 patch, 0,17 với 170 và 0,28 với 310: **không có cỡ mẫu khả thi nào đủ công suất**. Hạ hiệu ứng nhỏ nhất đáng quan tâm cho vừa dữ liệu là không chấp nhận được, nên mục tiêu suy luận được đổi.

**Phân tích chính: ước lượng với độ chính xác định trước** [Cumming 2014; Kelley & Rausch 2006]. Đại lượng: tỉ lệ patch plausible của model nhẹ có θ̂ trong vùng (mục 4.1), kèm khoảng Wilson 95% [Wilson 1927; Newcombe 1998] và khoảng bootstrap theo cụm **repo** [Field & Welsh 2007], vì các ca trong vùng gom theo repo (2/3 ca của PP2 cùng từ `litellm`).

**Độ chính xác mục tiêu:** nửa độ rộng w = (p₁ − p₀)/2 = **0,05**, suy ra từ hai giá trị của H1, để khoảng tin cậy không thể chứa đồng thời 0,10 và 0,20.

**Khung là toàn bộ không gian tìm kiếm** (khảo sát toàn bộ một khung hữu hạn), không dừng theo số lượng: mọi ứng viên A\* của không gian mở rộng đều được kiểm định (ước tính khoảng 3.578). Ước tính độ chính xác đạt được: 0,036 (theo ước lượng điểm của các tỉ lệ) đến 0,049 (theo cận dưới 95%) ở p = 0,12.

**Thay cho P1 đến P3:** không còn ngưỡng đếm ở từng giai đoạn (khung đã cố định, phễu được báo cáo mô tả). **P3 mới = độ chính xác đạt được**: nửa độ rộng khoảng Wilson của đại lượng chính ≤ 0,05; nếu không đạt, kết quả vẫn báo cáo nhưng ghi rõ là không đủ chính xác. **P4** giữ nguyên (≥ 11 cặp bất đồng để kiểm định H3). **H1 giữ làm phân tích phụ đã đăng ký**, báo cáo cùng công suất thực tế.

## 5. Ngân sách và lịch

Chỉ credit Free Trial (khoảng 288 USD, hết hạn 20/1/2027); trần cứng 200 USD cho toàn bộ P-GEN. Giá Flash tăng gấp đôi từ 1/1/2027, nên P-GEN nên chạy **trong tháng 12**.

## 6. Model

Model nhẹ `gemini-3.8-flash` bắt buộc: giả thuyết xác nhận dùng patch của model này. Model mạnh `gemini-4-argon` chỉ là nhánh thăm dò (RQ4), mở sau PP1 theo quy tắc của Study N mục 6; với hai model trên cùng instance, các phân tích giữa model dùng cặp ghép theo instance.

## 7. Còn phải làm trước khi đóng băng

1. ~~Pipeline sinh patch chấm bằng oracle mức hàm~~ (xong: `gatekeeper_ext/fn_draws.py`, oracle `function` trong `tools/cohort_inner.py`).
2. Lượt thử PP0 (và PP1 nếu PP0 đạt); tính P1, P2 bằng `tools/p_thresholds.py --from-pilot`.
3. Kiểm định đồng thuận với bộ sinh viết tay (RQ3) trên 12 target cũ.
4. Mở rộng khung nếu cần; giai đoạn P-S3 tạo và băm chương trình sinh cho từng instance trước khi sinh patch.
5. Đưa mọi file vào danh sách băm; chạy kiểm tra trước khi đóng băng.

## 7b. Thay đổi rút ra từ PP1 (1/11/2026, trước khi đóng băng)

1. **Lỗi HTTP 429 (RESOURCE_EXHAUSTED) được thử lại** theo giãn cách hàm mũ có chặn (10, 30, 90, 180 giây; tối đa 4 lần), đúng chiến lược Google khuyến nghị cho lỗi này trên Vertex (tài liệu "Error code 429"). Lý do: 2 trong 3 thất bại ở PP1 là 429; đó là tín hiệu về hạn mức, không phải câu trả lời của model, nên không được tính là thất bại của model. Mọi lỗi HTTP khác vẫn được ghi nhận ngay.
2. **Chương trình sinh được tạo đúng một lần** ở P-S3, lưu cùng hash, và **không bao giờ tạo lại**. Lý do: ở PP1, chương trình sinh của `skeletoken_pr74` hỏng ở cả hai lần dù ở PP0 tạo được: việc tạo không ổn định, nên tạo lại sẽ làm phễu khả thi phụ thuộc vào lần chạy. Tỉ lệ tạo thất bại được báo cáo trong RQ1.
3. **Nhánh model mạnh (thăm dò, RQ4) được mở theo quy tắc ở mục 6.** Trên các instance mà cả hai model đều sinh được patch không vướng lỗi hạ tầng (7 instance), Argon cho 6 patch plausible, Flash 5: điều kiện "không thấp hơn" thoả. Chi phí PP1 khoảng 0,015 USD mỗi lần sinh ở giá khuyến mãi; ở giá đầy đủ (4 và 20 USD mỗi triệu token) khoảng 0,03 USD, tức khoảng 9 USD cho 298 instance, trong ngân sách. Cỡ mẫu so sánh nhỏ (7), nên nhánh này chỉ là thăm dò; giả thuyết xác nhận chỉ dùng patch của model nhẹ.

## 8. Tài liệu tham khảo cho các công thức và quyết định

- Cumming, G. (2014). The new statistics: Why and how. *Psychological Science*, 25(1), 7–29.
- Kelley, K., & Rausch, J. R. (2006). Sample size planning for the standardized mean difference: Accuracy in parameter estimation via narrow confidence intervals. *Psychological Methods*, 11(4), 363–385.
- Newcombe, R. G. (1998). Two-sided confidence intervals for the single proportion: Comparison of seven methods. *Statistics in Medicine*, 17(8), 857–872.
- Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26(4), 404–413.
- Cochran, W. G. (1977). *Sampling Techniques* (3rd ed.). Wiley.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Erlbaum.
- Donner, A., & Klar, N. (2000). *Design and Analysis of Cluster Randomization Trials in Health Research*. Arnold.
- Field, C. A., & Welsh, A. H. (2007). Bootstrapping clustered data. *Journal of the Royal Statistical Society: Series B*, 69(3), 369–390.
- Hanley, J. A., & Lippman-Hand, A. (1983). If nothing goes wrong, is everything all right? Interpreting zero numerators. *JAMA*, 249(13), 1743–1745.
- Howard, S. R., Ramdas, A., McAuliffe, J., & Sekhon, J. (2021). Time-uniform, nonparametric, nonasymptotic confidence sequences. *Annals of Statistics*, 49(2), 1055–1080.
- Kelly, J. L. (1956). A new interpretation of information rate. *Bell System Technical Journal*, 35(4), 917–926.
- Kish, L. (1965). *Survey Sampling*. Wiley.
- Lakens, D., Scheel, A. M., & Isager, P. M. (2018). Equivalence testing for psychological research: A tutorial. *Advances in Methods and Practices in Psychological Science*, 1(2), 259–269.
- McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2), 153–157.
- Ramdas, A., Grünwald, P., Vovk, V., & Shafer, G. (2023). Game-theoretic statistics and safe anytime-valid inference. *Statistical Science*, 38(4), 576–601.
- Raudenbush, S. W. (1997). Statistical analysis and optimal design for cluster randomized trials. *Psychological Methods*, 2(2), 173–185.
- Vovk, V., & Wang, R. (2021). E-values: Calibration, combination and applications. *Annals of Statistics*, 49(3), 1736–1754.
- Wang, Y., Pradel, M., & Liu, Z. (2026). Are "solved issues" in SWE-bench really solved correctly? An empirical study. *ICSE 2026*.
- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, 22(158), 209–212.
- Ye, H., Martinez, M., & Monperrus, M. (2021). Automated patch assessment for program repair at scale. *Empirical Software Engineering*, 26, Article 20.

Các mục trên được trích từ hiểu biết của người soạn; **số trang, tập và số bài phải được kiểm tra lại với bản gốc** trước khi đưa vào bài. Wang et al. và Ye et al. đã được kiểm chứng trong báo cáo nghiên cứu tiền lệ.
