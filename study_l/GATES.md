# Study L — cổng quyết định bằng 0 đồng (GATES), đóng băng TRƯỚC khi chạy bất kỳ cổng nào

**Mục đích.** Quyết định, bằng bằng chứng không tốn tiền, xem hướng "đo tác hại một phần trên patch LLM thật, kèm oracle không do người viết" có đủ tiềm năng để tiếp tục hay không. Không cổng nào gọi API trả phí. Không cổng nào dùng kết quả của D/E/G/H để chỉnh tham số.

**Quy tắc bất biến.** Các ngưỡng trong file này **không được sửa bằng amendment**. Muốn đổi ngưỡng phải mở study mới. Amendment chỉ được thêm công cụ và đường dẫn vào danh sách hash (ví dụ generator tự động, harness), và phải ghi vào `AMENDMENTS.md` **trước** khi chạy cổng liên quan.

## Định nghĩa dùng chung

- **Patch ứng viên:** patch công khai do hệ thống LLM sinh cho một instance kiểu SWE-bench (nguồn: `all_preds.jsonl` trong kho SWE-bench/experiments), hoặc patch sinh trong pipeline của repo nếu G2 thất bại.
- **Patch plausible:** vượt bộ test fail-to-pass và pass-to-pass của instance (test của upstream, không sửa).
- **Chênh lệch:** với mỗi lần rút x từ generator, gọi ℓ₀ = [mã gốc khác bản fix upstream trên x], ℓ₁ = [patch khác bản fix upstream trên x]; Z = ℓ₁ − ℓ₀; hồi quy R = [ℓ₀ = 0 và ℓ₁ = 1]. (Khớp Definition ở bài báo.)
- **Generator tự động:** thuật toán cố định, không viết tay theo target, đóng băng bằng amendment L-A1 trước G1.
- **Tỉ lệ tác hại thật ĥ:** ước lượng từ 10.000 lần rút held-out; seed lấy từ drand sau thời điểm đóng băng của L-A1. Không dùng 10.000 lần rút này cho bất kỳ quyết định admit nào.
- **Vùng cần cổng thống kê:** ĥ ∈ [0,25%, 10%]. Căn cứ: cổng zero-tolerance 300 lần rút giữ ít hơn một nửa patch chấp nhận được khi h > 0,23%; smoke 20 lần còn admit nhầm hơn 10% patch không được phép đến h ≈ 10,9% (xem `PHASE_DIAGRAM.md`).

## Bốn cổng

| Cổng | Câu hỏi | Điều kiện đạt | Nếu không đạt |
|---|---|---|---|
| **G1** Oracle tự động có tin được không | Trên 6 instance B9 có bản fix upstream (D1–D5, A1): oracle vi sai bản fix + generator tự động có (a) phát hiện lỗi gốc với patch đúng đã biết (có ≥ 1 lần rút có lợi trong 300), (b) 0 hồi quy với patch đúng đó, (c) kết quả giống nhau trong 3 lần chạy lặp, (d) bắt được hồi quy ở ≥ 1 trong ≤ 5 đột biến AST định trước của bản fix? | Đạt cả (a)–(d) trên **≥ 5/6** instance | Bỏ hướng oracle tự động. Không tiêu tiền. Báo cáo kết quả âm |
| **G2** Số instance dùng được | Sàng 300 instance theo thứ tự lấy từ beacon: bao nhiêu cái dựng được môi trường, tất định, chạy được vi sai, và có ≥ 1 patch plausible công khai? | **≥ 40 instance** và **≥ 150 patch plausible** | Chuyển sang pipeline tự dựng của repo (tập nhỏ hơn), báo cáo tỉ lệ loại và lý do |
| **G3** Vùng có tồn tại trong patch thật | Trong patch plausible của tập G2: bao nhiêu patch có ĥ trong vùng cần cổng? | **≥ 15 patch trong vùng**, và **≥ 8 patch** mà quyết định của Gatekeeper-mixture hoặc cỡ mẫu cố định khác quyết định của cổng đơn giản (B8+ hoặc smoke 20) | Không có câu chuyện "cổng thống kê thắng cổng đơn giản". Chuyển sang bài đo đạc hoặc kênh ISSTA/MSR. Không tiêu tiền |
| **G4** Giá trị của dừng sớm | Trên dữ liệu G3, quy tắc tuần tự cần ít hơn bao nhiêu lần rút so với cỡ mẫu cố định ở cùng sai số admit sai? | **≥ 40%** ít hơn | Phần tuần tự chỉ là câu chuyện chi phí; bài ghi thẳng và không tuyên bố ưu thế |

Các ngưỡng là phán đoán của người nghiên cứu, **không** phải chuẩn khoa học hay tính công suất chính thức. Chúng được chọn để (i) đủ lớn cho so sánh ghép cặp trên các patch khác biệt quyết định, (ii) đủ nhỏ để một sinh viên chạy được trên Actions trong hai tuần.

## So sánh được đăng ký (dùng cùng dữ liệu, cùng ngân sách)

census-only; B8+ (300 lần rút, 0 hại, ≥ 1 lần có lợi); smoke 20; cỡ mẫu cố định n = 300 và n = 1000 (cùng θ = 0,2, η = 0,05, α = 0,1, Holm); Gatekeeper c = 0,9; Gatekeeper-mixture. Quy tắc cấp patch F-A2 là quy tắc chính; quyết định ở mức patch.

## Quy tắc dừng

- G1 hoặc G2 thất bại: dừng hướng này, báo cáo cho người hướng dẫn, **chưa chạy G3**.
- G3 thất bại: dừng, **không chi tiền cho thí nghiệm có model**.
- Chỉ khi G1–G3 đạt mới xem xét thí nghiệm model có kiểm soát. Dữ liệu patch công khai khác nhau về scaffold chứ không chỉ về model, nên không đủ để kết luận theo từng model; thí nghiệm trả phí chỉ được mở nếu câu hỏi đó còn cần trả lời.

## Mốc thời gian (không phải hạn nộp bài)

G1: trước 2/11/2026. G2: trước 9/11. G3 và G4: trước 16/11. Hồ sơ Go/No-Go gửi người hướng dẫn: 23/11.
