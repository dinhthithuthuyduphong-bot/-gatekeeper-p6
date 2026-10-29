# Study N: amendments

## N-T1 (sau cổng N1, trước khi chạy giai đoạn N-S3): thêm công cụ N-S3 và băm danh sách đầu vào

**Thay đổi:** chỉ thêm công cụ và một danh sách đầu vào vào danh sách băm. **Không ngưỡng nào thay đổi**; `GATES.md`, `DECISION_RULE.md` và giao thức giữ nguyên.

| File | Vai trò |
|---|---|
| `tools/n_s3_check.py` | dựng lại hai snapshot từ SHA đã ghi ở N-S2, cài một venv theo quy tắc bản 2.1 (module thiếu ở bất kỳ cánh tay nào được cài cho cả hai), chạy harness |
| `tools/n_s3_analyze.py` | chạy harness đã đóng băng `gatekeeper_ext/testmut.py` (tm-dev-v4-reach) bên trong venv đó, với bản fix làm patch tham chiếu |
| `tools/n_s3_shard.py` | chạy theo mảnh, giết cả nhóm tiến trình khi quá giờ; quá giờ là một kết quả, không chạy lại |
| `tools/n_s3_summary.py` | áp cổng N2 đúng như `GATES.md` (≥ 40 instance; ≥ 100 draw đủ cặp, tất định, bản gốc khác bản fix ở ít nhất 1 draw) |
| `tools/repo_hygiene.py` | được `tools/freeze_doctor.py` (đã băm) sử dụng |
| `research_closure/results/study_n_s2/ELIGIBLE.json` | 107 instance ELIGIBLE của N-S2, theo thứ tự khung mẫu, kèm hash bản ghi kiểm định gốc |

**Diễn giải cụ thể hoá (không đổi ngưỡng):** census của mỗi instance là thư mục chung của các file test của PR (nếu đó là gốc repo thì dùng chính các file đó); module được sửa là các file `.py` không phải test mà bản fix thay đổi; seed của harness suy từ tên instance. Đây đúng là các quy tắc của `gatekeeper_ext/b9_cohort.py`, đã băm.

**Kết quả N-S2 đã biết khi viết amendment này:** N1 đạt (107/400). Amendment không phụ thuộc vào kết quả đó ngoài việc liệt kê các instance ELIGIBLE.

## N-A1 (dự kiến)

Đóng băng cấu hình sinh patch theo mục 6 của giao thức, trước khi sinh bất kỳ patch nào cho cohort.
