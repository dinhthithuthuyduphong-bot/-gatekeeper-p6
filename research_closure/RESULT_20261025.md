# Kết quả hoàn chỉnh và trạng thái khảo sát — 25/10/2026

Gói ZIP tích lũy trên main `fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293`.
Chưa push main hoặc chạy workflow mới trên GitHub. Không gọi model; phí API 0 USD;
B9 vẫn HOLD. Gói gồm toàn bộ sửa đổi closure 24/10 và phần bổ sung Study K.

## Kết quả mới đã đo

| Hạng mục | Kết quả | Giới hạn |
|---|---|---|
| Target có lợi mới cho skill 2: python-control | Baseline 15 pass/1 fail → skill 16 pass/0 fail; upstream gold cũng 16 pass. Ba lần lặp mỗi nhánh | Hồi cứu, một module, một phiên bản; test upstream là smoke test |
| Scope array frequencies | 300 help/0 tie/0 hurt; ADMIT_DIAGNOSTIC ở draw 65 | Generator do nhóm nghiên cứu khai báo; không phải workload thực tế |
| Scope default frequencies | 0 help/300 tie/0 hurt; QUARANTINE | Skill không tạo lợi ích trong scope này |
| State/order check | 200 cặp kiểm tra lại, không sai khác | Chẩn đoán trên mẫu hữu hạn, không phải chứng minh độc lập |
| Coverage | Mỗi draw qua một vị trí sửa; tổng 2/3 vị trí được bao phủ | `gangof4_plot` chưa được kiểm chứng |
| Quét thêm ORM/DSL | 11 repo, 14 snapshot; không có production match mới của none-identity | Không được tính là target gây hại/có lợi |
| Airflow | Xác minh PR sửa `== None` thành `is None` rồi bị upstream revert vì hỏng query | Chưa tái lập bằng assertion upstream; chưa phải target có hại tier-1 mới |

Nguồn đo đầy đủ và `.md` riêng: `study_k/RESULT_VI.md`,
`study_k/results/local-20261025-clean/`. Raw gồm 9 lượt test/144 test executions,
600 paired draws, 200 state rechecks, source/test hashes và gold comparison.
Log lỗi môi trường, pilot và lượt đầu trước khi dựng môi trường sạch đều giữ lại.

Kiểm tra cuối: **129 unit tests PASS**, 12 nhóm kiểm tra/audit hoàn tất, freeze D/E/F/G/H hợp lệ và paid B9 vẫn bị chặn bằng HOLD. Workflow mới chưa chạy trên GitHub.

Khảo sát `pydantic/pydantic-settings` cũng đã hoàn tất ở mức tĩnh: 3 vị trí bool-guard, 0 vị trí none-identity, 0 test/treatment runs. Trạng thái `STATIC_ONLY_NOT_ELIGIBLE`; không có kết quả thực nghiệm bị bỏ dở được tính là thành công. Chi tiết nằm trong `research_closure/results/candidate_screen/pydantic__pydantic-settings.json`.

## Những phần đã có và được giữ trong gói

- Study I: SQLAlchemy là target gây hại bổ sung có test upstream; NetworkX là
  target có lợi hồi cứu. Không đổi dữ liệu cũ hoặc gọi đó là kết quả mới hôm nay.
- Closure: sửa chấm điểm Study F, kiểm toán 72 raw/candidate pairs, F-A3 có archive,
  fixed-size IUT comparator, sensitivity và số đo chi phí tuần tự thật.
- Số đo cũ trên máy local: SQLAlchemy tiết kiệm 14,53%, NetworkX 9,43% so với
  census + chạy đủ draws; không chứng minh lợi thế so với census-only hay LLM.
- Workflow audit tính lại raw Study I/Study K, statistics/cost và xác nhận B9 HOLD.
- Workflow Study K phục hồi Python 3.8.20 qua uv, tránh phụ thuộc setup-python
  cho bản lịch sử; log setup được tạo trước khi chạy tái lập.

Chi tiết và kết quả âm của đợt closure: `research_closure/RESULT.md`.
Biên bản kiểm tra cuối của gói nằm trong `PACKAGE_CHECKS/` ở gốc ZIP.

## Còn mở, không được báo 100%

1. Target gây hại tier-1 tiếp theo ngoài các case đã xác minh; Airflow mới là lead.
2. Cohort độc lập có public freeze trước treatment: Study J vẫn BLOCKED; hai repo
   đã biết outcome là python-control và Airflow đã được ghi vào exposure ledger.
3. Kiểm chứng ngoài scope và toàn patch; các kết quả hiện tại không phủ toàn repo.
4. Lợi thế trước baseline mạnh trên target mới, phụ thuộc model và chi phí LLM;
   chưa có model outcomes mới. B9 trả phí chưa được mở.

## Cách dùng

Mở `START_HERE.md` ở gốc ZIP. Chỉ áp gói tích lũy mới này một lần; giữ nguyên
đường dẫn trong `main_update/`, bao gồm `.github/workflows/`. Helper kiểm tra
base commit và thay đổi local trước khi chép file, không push hay chạy paid job.
Sau khi cập nhật main, chạy **Gatekeeper zero-cost closure audit**, rồi
**Gatekeeper Study K zero-cost reproduction** để tái lập target mới trên CI.
