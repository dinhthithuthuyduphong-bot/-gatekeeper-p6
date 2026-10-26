# Kết quả xử lý lỗi Study M A-star vet #1
Ngày: 26/10/2026 (UTC+7).
Commit nguồn: 036f9eeff76523d4034e04aa6c1e251914251601.
Run lỗi: https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/40296709754
Job đã đọc: 121484429311.

## Nguyên nhân đã xác nhận

Job plan xác minh thành công 40 file frozen, sau đó check_track.py không đọc được study_m_astar/candidates.json vì file chưa tồn tại. Job vet phụ thuộc plan nên chưa chạy. Không có kết quả S2 hay bằng chứng M1 thất bại từ run này.

Freeze ban đầu còn thiếu việc ràng buộc candidates.json, GATES.md và DECISION_RULE.md. Vì vậy “freeze verified” không có nghĩa mọi đầu vào cần cho S2 đã sẵn sàng.

## Thay đổi trong gói sửa

| File | Thay đổi |
|---|---|
| study_m_astar/candidates.json | Mới: 269 ứng viên ASTAR, giữ nguyên thứ tự S1 |
| study_m_astar/SPLIT_SUMMARY.json | Mới: seed, counts, hash nguồn và danh sách |
| study_m_astar/evidence/s1/M_ORDERED.json | Mới: bản gốc 500 metadata candidate, giữ nguyên bytes |
| study_m_astar/evidence/s1/SEED.json | Mới: seed receipt S1 gốc |
| study_m_astar/evidence/s1/M_DISCOVERY_LOG.json | Mới: discovery log gốc |
| study_m_astar/AMENDMENTS.md | Cập nhật: MASTAR-A1 mô tả nguyên nhân, phục hồi và giới hạn |
| study_m_astar/MASTAR_A1_EDITS.txt | Mới: mở rộng extra_tracked, không đổi ngưỡng hay seed |
| research_closure/results/STUDY_M_ASTAR_VET1_RECOVERY.md | Mới: báo cáo và hướng dẫn này |

Không sửa file config frozen hoặc FREEZE.json bằng tay. Hai file đó sẽ được workflow amendment cập nhật có ghi thời điểm và lịch sử.
Không sửa các script dùng chung, workflow hiện có, nội dung GATES.md/DECISION_RULE.md, danh sách RR hay B9.
Việc đưa metadata RR vào snapshot nguồn chỉ phục vụ provenance; không chạy/vet hoặc đọc kết quả của RR.

## Kết quả kiểm tra đã thực hiện

- SHA256 ZIP nguồn khớp bản đã kiểm tra:
  f8ade6a1cd40cb1d9c11d4fc1ef06d67d2d13cdb906bbac0ab58e9aa4ed557dc
- SHA256 M_ORDERED.json:
  1f7565709d746df47f2b3d1872fa447ad7ab82ad462c3203482134019c01c735
- 500 cặp repo/PR duy nhất.
- Thứ tự khớp discovery dùng owner/repo; không gọi order_candidates.py.
- Seed 722277585642093255.
- ASTAR 269 PR / 162 repo; RR 231 PR / 148 repo.
- Giao tập repo bằng 0.
- Chỉ chuẩn bị dữ liệu và kiểm tra JSON/hash; không chạy compiler, unit tests dự án hoặc target tests.
- CI sau sửa: CHƯA CHẠY. S2: CHƯA CÓ KẾT QUẢ. M1/M2: CHƯA ĐƯỢC CHỨNG NHẬN.

## Hướng dẫn cập nhật main

1. Giải nén Gatekeeper_M_ASTAR_Vet1_Recovery.zip.
2. Copy hai thư mục study_m_astar và research_closure vào đúng gốc repo. Commit trực tiếp main theo cách bạn đang dùng.
3. Không bấm lại “Gatekeeper Study M (A*) freeze”: nhánh đã FROZEN và công cụ từ chối freeze lần hai.
4. Vào Actions → Gatekeeper study amend → Run workflow, chọn main, nhập:
   - study: study_m_astar
   - amendment: MASTAR-A1
   - edits_file: MASTAR_A1_EDITS.txt
5. Chờ amendment success. Workflow chạy unit tests hiện có, thêm ràng buộc hash, ghi lịch sử amendment, commit và tag. Nếu nó thất bại, gửi log; chưa chạy vet.
6. Vào Actions → Gatekeeper Study M A-star vet → Run workflow mới trên main:
   - shards: 25
   - limit: 250
7. Không dùng Re-run jobs của lượt cũ vì lượt cũ vẫn tham chiếu commit thiếu file.
8. Khi hoàn tất, gửi toàn bộ artifact M_VET_* để tổng hợp ELIGIBLE và attrition.

Ngay sau khi upload gói nhưng trước amendment, verify freeze có thể báo thay đổi AMENDMENTS.md. Đó là trạng thái chuyển tiếp dự kiến; phải chạy amendment trước vet.
Nếu main đã có sửa đổi khác ở file frozen hoặc S2 đã chạy sau snapshot này, không áp dụng amendment một cách mù quáng; cần đối chiếu các thay đổi/kết quả mới trước.

## Kỳ vọng ở lần chạy tiếp theo

- plan xác minh freeze mới và track ASTAR thành công.
- 25 shard xử lý tổng cộng 250 candidate đầu, mỗi shard 10 candidate.
- Có M_VET_* artifacts, trừ sự cố hạ tầng riêng.
- Job success không đồng nghĩa mọi target ELIGIBLE. Chỉ kết quả fail-before/pass-after mới xác nhận M1.

## Giới hạn được giữ nguyên, không che giấu

Discovery có 8 API file-fetch failures không lưu danh tính PR; errors=[] thuộc nhóm khác. Recovery dùng cohort đã thu, giữ các trường hợp này là collection exclusions, không truy vấn lại để chọn case thuận lợi.
Order helper và discovery dùng dạng repo khác nhau; gói này ghi rõ sử dụng thứ tự discovery đã có, không sắp lại.
GATES.md và DECISION_RULE.md chỉ được hash-bound từ amendment này; không tuyên bố chúng đã được hash-bound ở freeze gốc.
Bản sửa không khắc phục các câu hỏi phương pháp rộng hơn về oracle/statistical validity; đó là các việc độc lập vẫn cần làm.

## Chi phí và quyền thay đổi

Agent không push GitHub, không chạy workflow, không gọi model. Recovery không cần API LLM. Thời gian Actions còn phụ thuộc quota của tài khoản.

