# Status audit — Study M discovery and Vertex smoke
Ngày rà soát: 26/10/2026 (UTC+7).
Commit main đã kiểm tra: fdcb8d5d0d066faecc50801a64d7e8989d61b9ce (14:48:03 UTC+7).
Phạm vi: đọc artifact, kiểm tra số đếm/hash/thứ tự, đọc code và trạng thái workflow. Không chạy test target, không dispatch workflow, không gọi API model.

## 1. Kết luận

S1 đã hoàn tất mục tiêu thu 500 ứng viên. Bước này mở đường cho vetting nhưng chưa chứng minh M1/M2/M3/M4 đạt. Vertex smoke xác nhận các endpoint được cấu hình trả HTTP 200 và có thể trả diff trên một prompt rất nhỏ. Chưa có bằng chứng năng lực sửa lỗi cohort thực tế, hiệu quả Gatekeeper hay đủ điều kiện mở lượt sinh patch chính.

Kết quả tiến bộ nằm ở hạ tầng và nguồn dữ liệu ứng viên. Đánh giá khả năng A* chưa được nâng lên chỉ từ hai artifact này.

## 2. Provenance và workflow

| Workflow | Run | Commit | Kết quả GitHub |
|---|---|---|---|
| Study M discover | 40284015631 | 963fd9d3253c04253e9af96dc67acf04c55951c1 | completed/success |
| Vertex smoke mới nhất | 40288044756 | fdcb8d5d0d066faecc50801a64d7e8989d61b9ce | completed/success |
| Vertex smoke trước đó | 40287010559 | c49e26d90898e1d3af7a6b66a2a9195b6ee7787f | completed/success |

Artifact đính kèm phù hợp cấu trúc và dữ liệu của smoke script hiện tại, nhưng VERTEX_SMOKE.json không chứa run ID, timestamp hoặc commit. Vì vậy không chứng nhận riêng provenance của ZIP chỉ bằng tên file. Lần chạy sau nên đưa các trường provenance vào artifact.

SHA256 STUDY_M_DISCOVERY.zip:
f8ade6a1cd40cb1d9c11d4fc1ef06d67d2d13cdb906bbac0ab58e9aa4ed557dc

SHA256 M_ORDERED.json:
1f7565709d746df47f2b3d1872fa447ad7ab82ad462c3203482134019c01c735

## 3. Study M S1 — kết quả tính lại từ artifact

| Chỉ số | Giá trị |
|---|---:|
| Search hits | 16.800 |
| PR duy nhất trong kết quả tìm kiếm | 16.430 |
| Qua bộ lọc metadata | 14.750 |
| Đã kiểm tra danh sách file | 3.285 |
| Ứng viên giữ lại | 500 |
| Repo khác nhau trong 500 ứng viên | 310 |
| PR trùng cặp repo+PR | 0 |
| Trùng tên instance | 0 |
| Thời gian trong discovery log | 2.367 giây = 39 phút 27 giây |
| API calls được log | 3.453 |
| Lý do dừng | target reached |
| Tỷ lệ qua bộ lọc file trong số đã xét | 15,22% |

Hai bảng attrition cân bằng số học. M_CANDIDATES.json và M_ORDERED.json giống nhau. Seed trong artifact là 722277585642093255. Thứ tự khớp hàm discovery dùng owner/repo. Đợt này chưa xác minh chữ ký drand độc lập hoặc tái chạy tìm kiếm GitHub.

100% ở đây chỉ là 500/500 mục tiêu candidate discovery, không phải 100% Study M.

### Phân chia tính lại bằng quy tắc trong tools/split_candidates.py

| Track | PR | Repo |
|---|---:|---:|
| ASTAR | 269 | 162 |
| RR | 231 | 148 |
| Tổng | 500 | 310 |

Không có repo chung giữa hai track theo chuỗi URL đã chuẩn hóa chữ thường. Đây là tính lại metadata, không phải vetting và không xem kết quả test của nửa RR. Không tạo hoặc commit candidate list chính thức trong đợt này. Repo rời nhau không bảo đảm không có code/maintainer/fork chung.

ASTAR đủ điều kiện sơ bộ “ít nhất 80 candidate”. M1 vẫn yêu cầu ít nhất 40 ELIGIBLE trong 250 candidate đầu; 19 candidate còn lại không được tự động thay thế những candidate thất bại.

### Hai vấn đề cần chốt trước S2

1. **Thứ tự không nhất quán giữa công cụ.** discover_m_candidates.py băm seed:owner/repo#pr; order_candidates.py băm seed:https://github.com/owner/repo.git#pr. Artifact đúng thứ tự discovery nhưng khác thứ tự script order. Chạy order lại sẽ đổi thứ tự, có thể đổi 250 mục đầu. Giữ nguyên artifact; ghi quy ước canonical và quyết định phương pháp/amendment trước S2, không âm thầm sắp lại.
2. **8 lỗi API bị tính là loại bởi bộ lọc file.** rejected_files chứa api error = 8, còn errors=[] và dòng kết thúc errors:0 chỉ phản ánh nhóm lỗi khác. Không báo “không có lỗi”. Log không có danh tính 8 PR và mã lỗi tương ứng; việc kiểm toán tiền tố gặp giới hạn. Chọn và ghi rõ cách xử lý trước outcome: giữ đây là thất bại thu thập đã khai báo, hoặc khôi phục với quy tắc retry/amendment nhất quán. Không lựa chọn sau khi thấy kết quả test.

## 4. Vertex smoke — HTTP thành công không đồng nghĩa nhiệm vụ thành công

| Chỉ số | Flash | Pro |
|---|---:|---:|
| Tổng request trong ZIP | 8 | 8 |
| HTTP 200 | 8/8 | 8/8 |
| Tiny replies không rỗng | 5/5 | 0/5 |
| Tiny replies kết thúc length | 0/5 | 5/5 |
| Probe kết thúc stop | 3/3 | 3/3 |
| Probe chứa diff | 3/3 | 3/3 |
| Tổng prompt token | 302 | 302 |
| Tổng output gồm reasoning | 143 | 736 |
| Tổng reasoning token được ghi | 0 | 598 |
| Chi phí theo giá cấu hình, USD | 0,000763 | 0,009436 |

Tổng implied cost: 0,010199 USD; tương đương khoảng 275 VND nếu dùng quy ước 27.000 VND/USD của dự án. Đây là tổng của ZIP này, không bao gồm smoke run trước hoặc usage khác. Chưa xác minh bảng giá chính thức trong đợt rà soát; đây không phải hóa đơn.

Pro ở tiny prompt bị cắt và không trả nội dung dù summary ghi OK 5/5. OK của script là HTTP 200. Với probe 1.000 token, cả ba phản hồi hoàn tất; trung vị output gồm reasoning là 241 token, trung vị reasoning 195. Chưa thể suy ra trần 4.000 token đủ cho lỗi thực tế hay toàn bộ cohort.

Không có 429 trong mẫu nhỏ này không chứng minh quota đủ cho chạy song song lớn. Script gọi tuần tự; tham số burst không phải phép đo tải đồng thời.

### Giới hạn probe

Prompt tools/vertex_smoke.py nói is_none(0) trả True vì dùng == None. Với số nguyên Python bình thường, phát biểu này sai: 0 == None là False. Diff đổi sang is None kiểm tra định dạng/phản hồi, nhưng chưa chứng minh sửa một lỗi được tái hiện. Khi mở rộng smoke thành kiểm tra nhiệm vụ, dùng input có overloaded equality hoặc một bug có test fail-before/pass-after thật; giữ các kết quả hiện có đúng nhãn infrastructure-only.

## 5. Billing và credit

Ảnh đính kèm cho thấy Reports hiển thị 0 VND cho 1–26/10/2026, savings 0 và chưa đủ dữ liệu dự báo. Không thấy dòng Vertex AI, credit applied, số dư credit hoặc ngày hết hạn. Do đó chưa xác minh được Free Trial đang trả cho các request.

Google ghi nhận dữ liệu Billing có thể đến chậm so với sử dụng. Cần xem đúng project và Vertex AI service/SKU, đối chiếu gross usage cost, credit áp dụng và net cost sau khi dữ liệu xuất hiện.
Nguồn: https://docs.cloud.google.com/billing/docs/how-to/reports

GATES.md mới gọi Free Trial là “không tính chi tiền”. Trong báo cáo nghiên cứu cần ghi tách:
- chi phí API theo usage;
- credit đã sử dụng;
- tiền mặt phải thanh toán.

Credit tài trợ không biến chi phí tính toán thành 0. Đợt này không xác minh số dư/ngày hết hạn đã được ghi trong repo. Không cần chạy thêm model chỉ để kích hoạt hiển thị Billing.

## 6. Code mới và phần vẫn chưa hoàn tất

So với commit S1, main có gatekeeper_ext/b9_cohort.py, usage.py, tests tương ứng, vertex smoke workflow và COHORT_PIPELINE_DESIGN.md. Phân tách client mở rộng khỏi B9 frozen là tiến bộ về quản lý phiên bản. Tuy nhiên tồn tại file test không chứng minh test đã pass; đợt này không chạy unit test.

COHORT_PIPELINE_DESIGN.md vẫn ghi chưa hoàn tất:
- chạy sinh patch trên Actions cho từng instance, môi trường/cassette/spend limits;
- scoring vi sai test-level và quyết định từng gate trên cùng draw.

study_m_astar/config_study_m_astar.json vẫn DRAFT. Chưa có bằng chứng vetting S2, đủ điều kiện S3 hoặc patch cohort từ hai ZIP này.

| Hạng mục | Trạng thái xác minh |
|---|---|
| S1 thu 500 candidate | Hoàn tất mục tiêu, có điểm audit cần xử lý |
| Phân chia track | Tính lại được 269/231; chưa áp dụng lên repo trong đợt này |
| Freeze nhánh ASTAR | Chưa, config DRAFT |
| M1/S2 >=40 instance ELIGIBLE | Chưa có kết quả |
| M2/S3 >=40 instance đủ điều kiện | Chưa có kết quả |
| Vertex connectivity | Đạt trong mẫu nhỏ |
| Chất lượng repair trên cohort/model robustness | Chưa đo |
| Credit đủ điều kiện chi trả | Chưa xác minh |
| M3/M4 | Chưa có kết quả |

## 7. Bước tiếp theo

1. Chốt order contract và cách khai báo 8 lỗi thu thập; giữ ZIP gốc và hash.
2. Tạo split chính thức bằng đúng seed và thuật toán hiện hành; lưu SPLIT_SUMMARY và ASTAR candidates đúng đường dẫn study_m_astar/candidates.json. Không chạy nửa RR.
3. Sau khi protocol được rà soát, chạy “Gatekeeper Study M (A*) freeze”; workflow hiện tại chạy unit tests và verify hashes. Chỉ tiếp tục khi thành công.
4. Chạy “Gatekeeper Study M A-star vet”, limit=250. Shards chỉ điều khiển cách chia công việc, không thay limit/thứ tự. Thu đủ M_VET_* và bảng attrition; không coi job success là tất cả target ELIGIBLE.
5. Song song làm audit oracle/harness và thống kê trên dữ liệu phát triển cũ.
6. Giữ lượt sinh patch chính ở HOLD. Credit có thể dùng sớm theo kế hoạch mới trong repo, nhưng chỉ sau các gate khoa học và xác minh billing tương ứng.

Bước 2–4 là hướng dẫn sau khi xử lý điều kiện bước 1, không phải lệnh đã được thực thi.

## 8. Output của đợt rà soát

File mới: STATUS_M_DISCOVERY_VERTEX_20261026.md.
Đề xuất đường dẫn khi cập nhật main:
research_closure/results/STATUS_M_DISCOVERY_VERTEX_20261026.md

Không sửa code/config, không push, không chạy workflow. Các kiểm tra hoàn tất là phân tích tĩnh và tính lại dữ liệu JSON; không phải chạy compiler hoặc thử nghiệm target.

Input hữu ích tiếp theo:
- Artifact vetting S2 khi chạy xong.
- Chi tiết Billing có project/service, usage cost và credit applied khi xuất hiện; không cần thông tin tài khoản hoặc phương thức thanh toán.

## Nguồn repository

- https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/commit/fdcb8d5d0d066faecc50801a64d7e8989d61b9ce
- https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40284015631
- https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40288044756
- tools/discover_m_candidates.py; tools/order_candidates.py; tools/split_candidates.py; tools/check_track.py
- tools/vertex_smoke.py; gatekeeper_ext/usage.py
- study_m_astar/config_study_m_astar.json; GATES.md; DECISION_RULE.md
- research_closure/results/COHORT_PIPELINE_DESIGN.md
Các path trên được đọc tại commit main đã nêu.

