# Đối chiếu với ba tài liệu FSE-2027-13

Đọc trực tiếp ba PDF người dùng cung cấp ngày 24/10/2026. Không sửa các PDF.
Không biến giá trị dự kiến trong proposal thành kết quả đã đo.

## Kỳ vọng thực sự

Trang 1 bản paper và cuối bản summary ghi rõ mọi số liệu headline là projected;
chưa có full study được chạy. Vì vậy các số 180 cặp/25 repo, 6,4 điểm giảm hại,
84,3% clean reuse, 41/46 composition và 1,9x chi phí không phải thành tích của repo.
Reading list cũng đánh dấu một số nguồn năm 2026 là VERIFY, tác giả placeholder.
Chưa xác minh các mục đó thì không dùng làm trích dẫn đã xác thực.

Tiêu chí quan trọng nhất của proposal là lợi thế trước replay + fingerprint mạnh
tại mức giữ lại beneficial reuse tương đương; B9 là co-primary; composition và
retirement là các câu hỏi riêng. Một ví dụ có hại mới không tự chứng minh được
các câu hỏi này. Gatekeeper-Lite hiện phù hợp với validation có phạm vi rõ ràng,
không phải đã tái hiện toàn bộ hệ thống/proposal SkillShift-SE.

## Hai điểm toán cần sửa/làm rõ trước khi kế thừa tuyên bố

1. **Theorem 4, bounded shift (paper trang 4).** Với quy ước chuẩn
   TV(P,Q)=sup_A |P(A)-Q(A)| và excess loss Z trong [-1,1], ta có
   |E_Q Z-E_P Z| <= 2 TV(P,Q), không mặc nhiên là TV. Ví dụ Z nhận -1/+1,
   P(Z=+1)=0,1 và Q(Z=+1)=0,2: TV=0,1 nhưng chênh trung bình=0,2.
   Nếu tác giả dùng TV theo chuẩn L1 không chia hai, cần ghi rõ quy ước.
   Lite chỉ chứng nhận generator đã khai báo; đợt sửa này không thêm một bảo đảm
   deployment shift không được đo. Counterexample có kiểm tra thực thi.
2. **Theorem 7, composition (paper trang 4-5).** Với loss trong [0,1] và mỗi skill
   có STR <= -theta, E[loss baseline] >= theta. Do đó STR của composition <=
   1-theta. Không thể đồng thời tuyên bố STR composition >= 1-epsilon cho *mọi*
   epsilon>0 khi epsilon<theta. Câu "no bound ... for any g" cũng cần loại các
   cận hiển nhiên. Phát biểu đủ để tạo động lực vẫn đúng: lợi ích riêng không
   bảo đảm composition an toàn. Construction hợp lệ: loss baseline=theta,
   loss mỗi skill=0, loss composition=1; STR riêng=-theta, STR chung=1-theta>0.

Đây là phản ví dụ/đối chiếu giả định, không phải một tuyên bố novelty mới hay
phản bác toàn bộ ý tưởng. Cần trao đổi với tác giả draft trước khi dùng nguyên
hai phát biểu trong bài của mình.

## Câu hỏi về model

Skill AST đã đóng băng và admission rule không cần gọi model để hoạt động. Điều
đó không đồng nghĩa hiệu quả triển khai không phụ thuộc model. Model thay đổi
phân phối patch, nên thay đổi tỷ lệ patch hữu ích, patch gây hại và power.

Trong Study F, raw và gated dùng **cùng patch**. Gated chỉ giữ hoặc loại patch,
không sửa patch thêm. Vì vậy SUCCESS_gated <= SUCCESS_raw theo thiết kế. Đo đúng:
harm bị chặn, successful patches được giữ, success bị loại, chi phí admission
bổ sung; báo cáo từng model và từng target. Khi không có harmful raw patch,
khả năng chặn harm của model đó là **chưa đánh giá được**, không phải 100%.
So sánh learned skill + admission với direct repair B9 vẫn là câu hỏi khác.

## Trạng thái khoảng trống

| Khoảng trống | Điều đã xử lý 0đ | Phần chưa thể tuyên bố đã đạt |
|---|---|---|
| Generalization | Study I giữ nhãn hồi cứu; Study J có tiêu chí, exposure ledger và preflight chặn thiếu dữ liệu | Chưa có cohort mới đã freeze trước outcome |
| Baseline mạnh | Bổ sung fixed IUT/ Holm đúng alpha, báo cáo kết quả bất lợi cho GK | Chưa có ưu thế prospective trước full replay/fingerprint/smoke |
| Power | Đo adaptive và mixture; tính cỡ mẫu harm-only | Không có cải thiện đồng đều; chưa đổi primary |
| Cost | Công cụ đo dừng thật, census và overhead có log | Hai target không chứng minh chi phí LLM hoặc mọi workload |
| Model | Sửa scorer, inventory, replay, thống kê trong từng model | Không có provider outcomes mới; B9 HOLD |
| Composition/retirement | Làm rõ giới hạn proposal | Không thêm bằng chứng thực nghiệm mới cho hai hướng này |
