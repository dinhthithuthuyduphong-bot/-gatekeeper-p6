# Bàn giao mở rộng skill 2 — 24/10/2026

**Có hai kết quả khả thi đã được chạy và lưu log: một target có hại mới
(SQLAlchemy) và một target có lợi mới (NetworkX).** Không tiêu ngân sách API,
không chạy B9, không sửa kết quả của study đã đóng băng.

Repository được đối chiếu:
[Gatekeeper main tại 13edea77](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/tree/13edea776af145ec897a1a992e9d7e054043ca25).
Main hiện vẫn chứa kết quả cũ; **gói này chưa được đẩy lên GitHub**.

## Tiến độ đối với hai yêu cầu

| Yêu cầu | Trước phần bổ sung | Bằng chứng mới | Mức hoàn thành thực chất |
|---|---|---|---|
| Thêm harmful target có oracle cấp 1 | pydal là target đạt yêu cầu đã biết | SQLAlchemy: 9 test upstream P→F, cùng kết quả ở 3 lần chạy | Đã có thêm một repo đủ điều kiện về bằng chứng thực thi; chờ cập nhật main và tái lập CI |
| Thêm beneficial cell cho skill 2 | Phía positive của Study G ghi BLOCKED | NetworkX: upstream behavioral witness F→P, 54 test census giữ xanh; skill khớp AST gold; một cell diagnostic admit | Đã có case có lợi chạy thật; còn giới hạn hồi cứu và scope được chọn sau tìm kiếm |

Không sửa dòng BLOCKED trong tài liệu lịch sử của Study G để làm như case này
đã có ngay từ đầu. Kết quả mới được đặt trong `study_i/`, với nhãn hồi cứu/khám
phá. Đây là cách thêm vào `main` mà vẫn bảo toàn dấu vết nghiên cứu.

## Kết quả chính

| Target | Không skill | Có skill | Lặp |
|---|---|---|---:|
| SQLAlchemy, 3 module upstream | 1.552 pass, 1 skip | 1.543 pass, 9 fail, 1 skip | 3 |
| NetworkX, 2 module upstream | 54 pass | 54 pass | 3 |
| NetworkX, upstream witness từ release sau | 1 functional ValueError | 1 pass | 3 |

NetworkX còn có nhánh gold upstream: 54 census + 1 witness đều pass, ba lần.
Một môi trường sạch chỉ cài sáu package cũng tái lập toàn bộ kết quả NetworkX.

| Cell | Help / tie / hurt trên 300 draw | Dừng tuần tự | Sau census + e-Holm |
|---|---|---|---|
| SQLAlchemy / null_semantics | 0 / 69 / 231 | Báo hại tại draw 3 | REJECT_CENSUS |
| SQLAlchemy / plain_queries | 0 / 300 / 0 | Chưa đủ bằng chứng, 300 | REJECT_CENSUS |
| NetworkX / given_positions | 300 / 0 / 0 | Admit tại draw 80 | ADMIT_DIAGNOSTIC |
| NetworkX / default_positions | 0 / 300 / 0 | Chưa đủ bằng chứng, 300 | QUARANTINE |

Kiểm toán độc lập từ XML/JSONL: **24 lượt test chính, 1.200 cặp draw gốc**.
Đổi thứ tự và worker mới: **0 sai khác/400 cặp kiểm tra**, 0 lỗi harness.
Ba kiểm tra dữ liệu hỏng — thiếu một draw, sửa Z, JSON kết quả rỗng — đều bị
từ chối, không sinh kết luận admission. Đây là kiểm tra của phần bổ sung;
không hàm ý toàn bộ các tool khác trong repository đã được kiểm toán/sửa.

## Điều cần hiểu đúng về mức cải thiện research

1. **Đã có thêm bằng chứng cho skill 2 theo cả hai chiều.** Không còn phải chỉ
   trình bày harmful pydal mà không có một case beneficial hành vi nào được tái lập.
2. **SQLAlchemy không chứng minh hơn full retest.** Chín regression đã bị chính
   bộ test upstream phát hiện. Giá trị là target harmful có oracle mạnh và
   cơ chế semantic rõ ràng, không phải ưu thế so với mọi baseline.
3. **NetworkX là hồi cứu, không phải prospective.** Code trước fix 2015 được
   chạy dưới Python 3.8.20/NumPy 1.17.5; witness từ release NetworkX 1.11 sau đó.
   Không nói test này được thêm trong commit fix. Scope có explicit positions
   tập trung vào vùng có lợi; không khái quát 300/300 ra mọi lệnh gọi thư viện.
4. **Oracle draw do nghiên cứu viên viết vẫn tách riêng.** Tier-1 evidence đến
   từ test upstream nguyên trạng; không tự nâng toàn generator lên tier 1.
5. **Các weakness khác còn nguyên phạm vi riêng:** đa dạng nhiều skill, quy mô
   transfer, model dependence, B9 thật và hiệu quả kinh tế khi trial đắt chưa
   được chứng minh bằng hai case này.

Với phần bổ sung này, hợp lý nhất là viết một mục “retrospective extension and
diagnostic validation” trong artifact/paper. Muốn thêm claim tiến cứu cần
target/đầu vào đánh giá mới chưa quan sát và protocol đăng ký trước, không chỉ
đổi seed rồi chạy lại hai case đã được chọn.

## Bạn cần cập nhật gì lên main

Gói ZIP có thư mục `main_update/`. Copy **nội dung bên trong** vào root repo:

* `study_i/`: script, config, source provenance, raw log và các báo cáo `.md`.
* `.github/workflows/study-i-zero-cost.yml`: workflow thủ công để tái lập và kiểm toán.

Gói chỉ thêm file mới; không ghi đè source core, skill, freeze manifest, Study F
hay log cũ. Không cần mở nhánh hoặc PR mới theo cách cập nhật bạn đã chọn.

Nếu dùng Git từ một clone đã có, chuyển về main và đồng bộ **trước khi copy**:

```bash
git switch main
git pull --ff-only origin main
```

Sau khi copy hai đường dẫn trên vào đúng root repo:

```bash
git add study_i .github/workflows/study-i-zero-cost.yml
git diff --cached --stat
git commit -m "Add exploratory skill-2 SQLAlchemy and NetworkX validation"
git push origin main
```

Nếu chưa clone, dùng:

```bash
git clone https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6.git gatekeeper-p6
cd gatekeeper-p6
```

Rồi copy và thực hiện bước commit trên. Nếu dùng GitHub Desktop, chọn branch
`main`, copy nội dung `main_update`, kiểm tra danh sách thay đổi chỉ gồm hai
đường dẫn đã nêu, commit rồi Push origin. Không đưa cả thư mục `main_update`
thành một thư mục con của repo.

## Workflow cần chạy sau khi cập nhật

1. Mở **Actions → Gatekeeper Study I - zero-cost target validation**.
2. Bấm **Run workflow**, chọn **main**, chạy một lần.
3. Hai job `reproduce` dùng môi trường riêng cho SQLAlchemy và NetworkX; job
   `audit` kiểm tra raw evidence và gộp đúng đủ bốn cell.
4. Tải `study-i-sqlalchemy`, `study-i-networkx`, `study-i-verified`. Mở
   `family/FAMILY_RESULT.md` trong artifact verified để xem kết luận.
5. Lưu lượt GitHub thành thư mục mới theo run ID nếu muốn commit evidence.
   Giữ bộ log local ngày 24/10 để so sánh, không thay file báo cáo bằng kết quả
   chưa được chạy hoặc sửa kỳ vọng để ép workflow xanh.

Workflow đã kiểm tra cú pháp YAML, trigger, quyền và pipeline local; **chưa
được dispatch trên GitHub** trong lần này. Nếu fail, log vẫn được upload; gửi
run URL để xác định lỗi môi trường hay khác biệt kết quả. Workflow không tự
ghi kết quả về repo và không gọi B9/GCP/API model.

## File nên đọc trước

* `SQLALCHEMY_RESULT_VI.md`: harmful target, test identities, provenance, timing và giới hạn.
* `NETWORKX_RESULT_VI.md`: positive witness, gold comparison, môi trường lịch sử và diagnostic admission.
* `results/2026-10-24/family/FAMILY_RESULT.md`: bảng quyết định tính lại từ dữ liệu thô.
* `PROTOCOL.md`: quy tắc lấy mẫu, lỗi, census, e-Holm và ranh giới của claim.
* `search_evidence/SEARCH_LEDGER.md`: các ứng viên bị loại/BLOCKED và các lỗi môi trường đã gặp.

**Chi phí:** 0 lượt gọi model, 0 USD API; không dùng credit $300, không mở B9.
Local và GitHub Actions vẫn tiêu tài nguyên/quota runner. Tiền API chưa phải
nút thắt cho hai kết quả này; bước tiếp theo là tái lập CI và giữ claim đúng
với chất lượng bằng chứng đã có.
