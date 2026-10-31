# Rà soát toàn bài trước khi nộp (đọc như phản biện FSE), 31/10/2026

Đọc lại toàn bộ `build/paper.pdf` và tìm những chỗ một phản biện khó tính có thể dùng để đánh trượt. Mỗi điểm có mức độ, cách sửa và bằng chứng. Tất cả đã sửa trong commit kèm theo; bộ kiểm số kiểm 26 con số.

| # | Mức | Điểm yếu | Sửa | Bằng chứng |
|---|---|---|---|---|
| W1 | 🔴 | **Abstract tự mâu thuẫn.** Abstract nói các cổng thống kê "chặn" 16 patch "có tác hại một phần cao", trong khi mục 7.3 cho thấy 97,5% đầu vào "hồi quy" là đầu vào mà bản fix cũng từ chối. Phản biện sẽ nói bài tự bác bỏ khẳng định của mình. | Viết lại: census admit cả 16 patch có **khác biệt hành vi một phần**, các cổng thống kê không admit patch nào, **nhưng** kiểm tay cho thấy phần lớn khác biệt nằm ở đầu vào mà bản fix cũng từ chối. Điều này nối thẳng sang RQ4 (định nghĩa tác hại). | `main.tex`; `research_closure/results/rq5/RQ5_RESULT.md` |
| W2 | 🔴 | **Không thí nghiệm nào chạm phần mới nhất của bài** (tổ hợp, luật thực thi, sổ cái α). Lý thuyết về cả thư viện không có bằng chứng thực nghiệm. | Thêm **mục 7.2 "Library-level control (simulation)"**, dùng đúng e-process, sổ cái và luật thực thi của hệ thống. Chỉ admit từng kỹ năng: **27,9%** thư viện chạy một thành phần có hại (9,9% ở q = 0,1; 42,4% ở q = 0,5). Có tổ hợp + sổ cái + luật thực thi: **0/1.000** ở mọi q. Cái giá: 3,59 thay vì 4,48 kỹ năng có lợi được chạy, và thêm 8% lần thử. Đo trên toàn tập thì chỉ thấy 5,4% vì lợi ích ở chỗ khác che phần hại, nên bảo đảm phải phát biểu theo thành phần. Ghi rõ là mô phỏng trong Threats. | `tools/library_simulation.py`; `research_closure/results/library_sim/LIBRARY_SIMULATION.json`; test |
| W3 | 🟠 | **Thiếu công trình gần nhất của RQ4: PatchDiff** (Wang, Pradel, Liu, ICSE 2026), đo đúng khác biệt hành vi của patch plausible trên SWE-bench Verified (29,6%). | Trích và so sánh: cùng bậc độ lớn; đầu vào mức hàm của bài tìm thấy nhiều khác biệt hơn (43,1%); phân loại theo hợp đồng là cách thay tự động, rẻ hơn cho việc chấm tay của họ. | `evaluation.tex` (7.5), `related.tex` |
| W4 | 🟠 | **Thiếu always-valid A/B testing** (Johari và cộng sự, Operations Research 2022): kiểm định tuần tự khi triển khai, gần với cơ chế của bài. | Thêm tiểu mục Related work, nêu ba điểm khác: phạm vi có thể dịch chuyển, thư viện tăng thêm và admit lại, tổ hợp là quyết định riêng. | `related.tex` |
| W5 | 🟡 | Thiếu tài liệu kinh điển về **patch quá khớp** (Smith và cộng sự, ESEC/FSE 2015). | Thêm vào Related work. | `related.tex` |
| W6 | 🟡 | Study D dùng thủ tục Holm trên e-value, còn lý thuyết dùng hợp cận; câu chữ chưa có trích dẫn. | Trích Vovk & Wang 2021 cho kiểm định nhiều giả thuyết với e-value. | `evaluation.tex` (7.3) |
| W7 | 🟡 | Số test trong mục Implementation đã cũ (359). | Đổi thành "hơn 350"; số chính xác thay đổi theo mã. | `implementation.tex` |

## Vòng 2 ("fix cho tới khi thắng")

| # | Mức | Điểm yếu | Sửa | Bằng chứng |
|---|---|---|---|---|
| W8 | 🟠 | Django chiếm 215/469 instance của Study Q: kết quả có bị một repo chi phối không? | Kiểm bỏ từng repo (post hoc): tỉ lệ HQ1 trong khoảng 8,2% – 16,7%, cận trên Wilson lớn nhất 31,9% (khi bỏ sympy); Q4 trong khoảng 8,2% – 14,0%. Kết luận không đổi. Đã thêm vào mục 7.5 | `tools/q_robustness.py`; `research_closure/results/study_q/Q_ROBUSTNESS.json` |
| W9 | 🟡 | Bài không có hình; các quyết định trên target thật chỉ nằm trong văn bản | Thêm **Hình 1** (sơ đồ pipeline, TikZ) và **Bảng 2** (số ô được admit theo từng baseline, tách theo study) | `approach.tex`, `evaluation.tex` |
| W10 | 🟡 | Giả định 4: chưa có dữ liệu thật về mức giao footprint | Không đo được từ dữ liệu sẵn có (mỗi study chỉ bind một họ kỹ năng); ghi rõ trong Threats, không đoán số | `threats.tex` |

**Sự cố trong vòng này:** một lần sửa bằng script làm hỏng `evaluation.tex` (tệp phình lên 119 nghìn dòng, vì lệnh thay nhận một chuỗi rỗng). `tools/check_paper_numbers.py` báo 21 con số không còn trong bài; tệp được khôi phục từ git **trước khi commit**, và sửa đổi được áp lại có kiểm vị trí.

**Trích dẫn mới đã tra** (tìm kiếm web, 31/10/2026):
- PatchDiff: ICSE 2026, DOI 10.1145/3744916.3764576.
- Johari và cộng sự: Operations Research 70(3):1806–1821, DOI 10.1287/opre.2021.2135.
- Vovk & Wang: Annals of Statistics 49(3):1736–1754, DOI 10.1214/20-AOS2020.
- Smith và cộng sự, ESEC/FSE 2015: theo hiểu biết của trợ lý, tên và hội nghị là chắc; **số trang 532–543 nên kiểm lại** trên DOI trước khi nộp.

**Điểm yếu còn lại, không sửa được bằng văn bản:**
- Chưa có thư viện kỹ năng thật có các kỹ năng giao nhau; mô phỏng thay cho nó và được ghi rõ.
- B9 còn HOLD.
- Giả định 4 chưa được đo trên dữ liệu thật.
