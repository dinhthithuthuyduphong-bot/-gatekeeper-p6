# Study I: hai kết quả mới cho skill `none-identity`

**Ngày báo cáo: 24/10/2026, giờ Việt Nam. B9 giữ HOLD. Không gọi API model.**

Đây là phần bổ sung khám phá/hồi cứu, tách khỏi các study đã đóng băng. Có một
target có hại mới (SQLAlchemy) và một target có lợi mới (NetworkX). Các kết quả
đã chạy local; workflow GitHub bên dưới được chuẩn bị để tái lập sau khi bạn
đưa các file lên `main`, chưa được chạy trên GitHub trong lần bàn giao này.

| Kết quả | Bằng chứng thực thi |
|---|---|
| SQLAlchemy — harmful tier 1 | 1.552 pass + 1 skip trước skill; 1.543 pass + 9 fail + 1 skip sau skill, ổn định 3 lần. Test upstream nguyên trạng. |
| NetworkX — beneficial upstream witness | 54 test gốc pass cả trước/sau; một test hành vi upstream từ bản phát hành sau chuyển từ ValueError sang pass, ổn định 3 lần. Bản skill khớp AST bản fix upstream. |
| Gatekeeper diagnostic | NetworkX `given_positions`: ADMIT sau 80 draw; SQLAlchemy `null_semantics`: báo hại sau 3 draw. Census phủ quyết cả target SQLAlchemy. |
| Kiểm toán dữ liệu | Tính lại từ 1.200 cặp draw thô; 400 cặp kiểm tra đổi thứ tự/worker mới không sai khác. Thiếu draw, sửa nhãn, JSON rỗng đều bị từ chối. |

Đọc [báo cáo tổng hợp và hướng dẫn cập nhật](PROGRESS_AND_UPDATE_VI.md),
[kết quả SQLAlchemy](SQLALCHEMY_RESULT_VI.md),
[kết quả NetworkX](NETWORKX_RESULT_VI.md) và [protocol](PROTOCOL.md).

## Chạy bằng GitHub Actions

1. Copy **nội dung** thư mục `main_update` trong gói bàn giao vào gốc repository:
   thêm `study_i/` và `.github/workflows/study-i-zero-cost.yml`.
2. Commit trực tiếp lên `main`. Không sửa nội dung các study D/E/G hoặc B9.
3. Mở **Actions → Gatekeeper Study I - zero-cost target validation → Run workflow → main**.
4. Chờ hai job `reproduce` và job `audit` hoàn tất. Tải ba artifact
   `study-i-sqlalchemy`, `study-i-networkx`, `study-i-verified`.
5. Kiểm tra `FAMILY_RESULT.md` trong artifact `study-i-verified`. Nếu lưu lượt CI
   vào repo, đặt vào thư mục kết quả mới theo run ID, không ghi đè log local đã có.

Workflow xanh nghĩa là **tái lập đúng kết quả nghiên cứu đã khai báo**, bao gồm
9 regression cố ý quan sát trên nhánh SQLAlchemy có skill. Nó không có nghĩa
bản patch SQLAlchemy an toàn để triển khai. Nếu kiểm tra không khớp, workflow
đỏ và vẫn giữ log; không nới assertion để ép xanh.

Workflow chỉ chạy thủ công, quyền `contents: read`, không dùng secret/GCP/model
và không tự commit. Không chạy workflow `Gatekeeper B9 run` hay freeze lại các
study cũ để thực hiện phần bổ sung này. Chi phí API model bằng 0; runner local/CI
vẫn dùng tài nguyên hoặc quota của tài khoản.

## Chạy local (Linux)

Từ gốc repo, tạo hai virtualenv riêng. Cần Git, Python 3.12.14 và Python 3.8.20.
Không cài hai bộ dependency vào cùng môi trường.

```bash
python3.12 -m venv .venv-study-i-sqlalchemy
.venv-study-i-sqlalchemy/bin/python -m pip install -r study_i/requirements-sqlalchemy.txt
.venv-study-i-sqlalchemy/bin/python -u study_i/run.py sqlalchemy --output out-study-i/sqlalchemy
.venv-study-i-sqlalchemy/bin/python -u study_i/statelessness.py sqlalchemy --results out-study-i/sqlalchemy

python3.8 -m venv .venv-study-i-networkx
.venv-study-i-networkx/bin/python -m pip install -r study_i/requirements-networkx.txt
.venv-study-i-networkx/bin/python -u study_i/run.py networkx --output out-study-i/networkx
.venv-study-i-networkx/bin/python -u study_i/statelessness.py networkx --results out-study-i/networkx

python3.12 study_i/verify.py --results out-study-i --output out-study-i/family
```

`run.py` tự lấy upstream tại commit cố định. Có thể truyền `--checkout` để dùng
checkout sạch đã có. Thư mục output phải mới/rỗng. Không đưa thư mục `work/`
chứa bản sao source hoặc virtualenv lên GitHub; giữ JSON, JSONL, XML, patch và log.

Chỉ kiểm toán lại dữ liệu đã bàn giao, không cần cài dependency target:

```bash
python3.12 study_i/verify.py --results study_i/results/2026-10-24 --output out-study-i-audit
```

Nếu báo hash core/skill thay đổi, đối chiếu commit gốc
`13edea776af145ec897a1a992e9d7e054043ca25`; không tự sửa hash để bỏ qua. README
hoặc tài liệu ngoài các file core được khóa có thể thay đổi mà không ảnh hưởng.

## Cấu trúc bằng chứng

* `targets.json`: pin source, môi trường, 4 cell, hash frozen core và upstream witness.
* `vendor/`: test, gold module và giấy phép NetworkX nguyên trạng.
* `oracles/`: generator/oracle chẩn đoán do nghiên cứu viên viết, phân biệt với test upstream.
* `results/2026-10-24/{sqlalchemy,networkx}/`: manifest, patch, XML, log, raw draw,
  kiểm tra statelessness, `RESULT.md` và `RESULT.json` cho từng target.
* `results/2026-10-24/family/`: quyết định sau census + e-Holm trên đủ 4 cell.
* `results/2026-10-24/clean_networkx_replay/`: lần tái lập độc lập môi trường chỉ
  cài 6 dependency, cùng kết quả; không tính là một target mới.
* `search_evidence/`: các lượt không đủ điều kiện, kể cả lỗi môi trường.

Các file log chứa đường dẫn máy chạy gốc để truy vết. Script tái lập dùng đường
dẫn tương đối và checkout mới; bạn không cần tạo lại đường dẫn `/workspace/...`.

Đây chưa phải bằng chứng khái quát trên nhiều skill/model hoặc tiết kiệm chi phí
LLM. Không gộp kết quả khám phá này vào claim tiến cứu của Study G.
