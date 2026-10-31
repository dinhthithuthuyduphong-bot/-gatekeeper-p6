# Rà soát giai đoạn 1: kiểm lại từng chứng minh, tìm lỗ hổng, sửa

**Đối tượng:** các mục LaTeX của giai đoạn 1 (`latex/sections/problem.tex`, `theory.tex`, `related_stats.tex`) và bản chi tiết [THEORY.md](THEORY.md).

**Cách làm:** đọc như một người phản biện. Với mỗi bước của mỗi chứng minh, hỏi ba câu:
1. bước này dùng giả định nào;
2. giả định đó đã được nêu chưa;
3. bước này có đúng trong mọi trường hợp mà phát biểu bao trùm không.

Lỗ hổng nào kiểm bằng số được thì thêm phép kiểm vào `tools/theory_checks.py`.

> Đây là rà soát của trợ lý. Nó **không thay** cho mục 1.9 của PAPER_TODO (một người đọc độc lập): người đọc thứ hai vẫn cần thiết.

## Kết quả kiểm từng bước

| Kết quả | Bước | Đúng? | Ghi chú |
|---|---|---|---|
| Lemma (e-process) | thừa số > 0 | ✅ | dùng Y ≥ −1 và λ < 1/(1+θ); bản cài đặt dùng λ ≤ 0,5/(1+θ), nằm trong miền |
| | siêu martingale | ✅ | chỉ cần E[Y_i \| quá khứ] ≤ θ; **không** đúng khi rút không hoàn lại (G7) |
| | Ville | ✅ | K₀ = 1, không âm |
| Theorem (admission) | admit ⇒ A_{c,k} | ✅ | A_{c,k} định nghĩa trên cả dãy vô hạn, nên dừng thích nghi chỉ bỏ bớt cơ hội admit |
| | tập ô có H₀ đúng là tất định | ✅ | H₀ là tính chất của P, không phụ thuộc dữ liệu |
| | hợp cận | ✅ với sổ cái cố định | **lỗ hổng G3** khi thư viện tăng thêm kỹ năng hoặc ngân sách phụ thuộc dữ liệu |
| | P → Q | ✅ | Lemma (shift); điều kiện chỉ cần 2ξ ≤ θ (G4) |
| | epoch sau retirement | ⚠️ | môi trường đổi nên P, Q đổi theo; **G2** |
| | bảo đảm cho thứ thực sự chạy | ❌ | **G1**: định lý chỉ nói về ô được admit |
| Lemma (shift) | căn giữa f, \|g\| ≤ b/2 | ✅ | trường hợp liên tục: thay tổng bằng tích phân |
| | hằng số 2 đạt được | ✅ | C3 |
| Proposition (a) | dữ liệu không đổi | ⚠️ | thủ tục còn đọc đặc trưng **của chính đích** (screen); **G6** |
| Proposition (b) | dựng Q | ✅ | P(d) ≥ 1/2 ≥ ξ nên chuyển được khối lượng ξ |
| Theorem (composition) | cận trên | ✅ | |
| | đạt được | ⚠️ | cần các loss tuỳ ý thực hiện được; **G5** |
| Corollary (footprint) | | ❌ | chỉ cho cặp; với ba kỹ năng trở lên cần giả định cho tập; **G1** |
| Proposition (pairing) | hai phương sai | ✅ | nhiễu chạy lại nằm trong V, không nằm trong C (G8) |

## Các lỗ hổng tìm thấy và cách sửa

| # | Mức | Lỗ hổng | Sửa (đã đưa vào LaTeX và THEORY.md) |
|---|---|---|---|
| **G1** | 🔴 | Định lý bảo đảm cho từng **ô được admit**, nhưng thứ thực sự chạy là một **tập kỹ năng**. Nếu S và S′ cùng được admit, footprint giao nhau, mà tổ hợp chưa được quyết định lại vẫn chạy chung, thì định lý không nói gì. Bản nháp tự thừa nhận đây là 15% ca hại (§10.3). | Thêm **luật thực thi** (`problem.tex`): chỉ chạy một tập khi mọi thành phần liên thông (theo đồ thị giao footprint) có từ hai kỹ năng là một ô **đã được admit**. Mở rộng định nghĩa ô cho tổ hợp nhiều kỹ năng. Tổng quát Giả định 4 cho **tập** kỹ năng. Thay Corollary cũ bằng **Corollary "What actually runs"**: ngoài biến cố của định lý, STR_Q(E) ≤ m(−θ + 2ξ). |
| **G2** | 🟠 | Sau retirement, môi trường đổi (nâng phụ thuộc), nên P, Q của epoch mới khác. | Ký hiệu P^{(k)}, Q^{(k)} theo epoch; định lý phát biểu theo epoch. |
| **G3** | 🟠 | Sổ cái "cấp trước" không rõ khi thư viện **tăng thêm** kỹ năng, hoặc khi α được cấp theo tần suất dùng ước lượng từ dữ liệu. | Sổ cái là **hàm của danh tính ô** trên tập đếm được mọi ô có thể có, nên thư viện tăng thêm vẫn được bao. Thêm **Remark** về ngân sách phụ thuộc dữ liệu: vẫn đúng nếu tổng ≤ α hầu chắc chắn **và** dãy thử của ô độc lập với thông tin dùng để cấp α (có chứng minh một dòng); nếu hai ô dùng chung task thì có thể sai. |
| **G4** | 🟡 | Điều kiện "2ξ < θ" chặt hơn mức cần. | Đổi thành 2ξ ≤ θ, kèm một dòng chứng minh. |
| **G5** | 🟡 | Construction của định lý tổ hợp cần loss tuỳ ý thực hiện được. | Trỏ tới Giả định 3 (rich target class). |
| **G6** | 🟡 | Mệnh đề (a): thủ tục còn đọc fingerprint và vị từ của **đích**. | R† có cùng mọi đặc trưng mà thủ tục đọc, gồm cả đặc trưng của đích. |
| **G7** | 🟡 | Rút **không hoàn lại** từ tập task hữu hạn làm trung bình có điều kiện trôi, nên K_n không còn là siêu martingale. | Nêu rõ trong Assumption 1: phải rút có hoàn lại, hoặc dùng e-process cho quần thể hữu hạn. |
| **G8** | 🟡 | Mệnh đề ghép cặp chưa nói về nhiễu khi chạy lại. | Nhiễu nằm trong V_π, V_∅; chỉ phần chung của task nằm trong C. Công thức không đổi. |
| **G9** | 🟡 | Lỗi "admit lại mà không có sổ cái" (bản nháp, §5.4) chưa được kiểm bằng số. | Thêm **C8**: kiểm lại một ô ở biên H₀ qua 10 epoch, mỗi epoch dùng đủ α, cho tỉ lệ admit sai **0,45**; dùng sổ cái chỉ **0,05** (α = 0,1). |

## Kiểm bằng số sau khi sửa

Workflow `Gatekeeper theory checks` ([kết quả](../../research_closure/results/theory/THEORY_CHECKS.md)):

| Kiểm | Kết quả |
|---|---|
| C1 e-process một ô | tỉ lệ admit sai 0,066 ≤ 0,1 |
| C2 ngân sách theo phạm vi / theo ô | 0,45 / 0,05 |
| C3 hằng số dịch chuyển | đúng bằng 2; ≤ 2 trên mẫu ngẫu nhiên |
| C4 định lý tổ hợp | 0 vi phạm; construction đạt 1 − θ |
| C5 ghép cặp | 5,20 so với công thức 5,2 |
| C6 sổ cái | tổng ≤ 1 |
| C7 số của bản nháp | không khớp, đúng như dự đoán |
| **C8 admit lại** | không có sổ cái 0,45; có sổ cái 0,05 |

## Những gì vẫn là giả định (phải nêu trong bài, không chứng minh được)

1. **Assumption 1:** task i.i.d., rút có hoàn lại.
2. **Assumption 2:** ξ_s khai báo, không đo được trực tiếp.
3. **Assumption 3:** lớp repo đủ giàu. Chỉ dùng cho các kết quả *không thể* (Proposition, construction).
4. **Assumption 4:** không tương tác khi footprint rời nhau. **Mạnh**; phải đo (PAPER_TODO 2.3).
5. **Luật thực thi:** đây là một **ràng buộc thiết kế** của hệ thống, không phải giả định toán. Hệ thống phải cài đặt nó; bản nháp chưa có.

## Kết luận

Sau các sửa đổi, mọi kết quả của giai đoạn 1 có chứng minh đầy đủ, dưới các giả định đã nêu rõ. Mọi phát biểu kiểm được bằng số đều đã kiểm. Lỗ hổng lớn nhất (G1) **đổi cả thiết kế**: hệ thống phải chặn việc chạy chung các kỹ năng có footprint giao nhau cho tới khi tổ hợp được admit. Điều này cũng loại bỏ đúng nguồn 15% ca hại mà bản nháp mô tả.
