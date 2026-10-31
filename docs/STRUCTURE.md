# Cấu trúc repo

Repo được chia theo **lớp**, mỗi lớp chỉ phụ thuộc vào lớp ở dưới nó:

```
 tài liệu          docs/  README*.md  EVIDENCE_LEDGER.md  paper_snippets/  research_closure/*.md
     │
 bằng chứng        study_*/  results/  evidence/  harness_checks/  research_closure/results/  next_evidence/
     │             (protocol + FREEZE.json + kết quả của từng study)
 điều phối         .github/workflows/  (91 workflow, chạy thủ công)
     │
 công cụ           tools/  (104 script: chạy, đóng băng, phân tích từng study)
     │
 lõi               gatekeeper_lite/  (pipeline: screen → binder → paired trials → e-process → ADMIT/QUARANTINE)
                   gatekeeper_ext/   (oracle mức hàm, các cổng, phân loại theo hợp đồng, usage)
     │
 kiểm thử          tests/  (339 test; `python -m unittest discover -s tests`)
```

## Thư mục

| Thư mục | Lớp | Vai trò |
|---|---|---|
| `gatekeeper_lite/` | lõi | Cài đặt bài FSE: gói kỹ năng, screen, binder AST, paired trials, e-process, alpha ledger, comparator, composition, retirement |
| `gatekeeper_ext/` | lõi | Phần mở rộng cho Study D đến Q: draw, oracle mức hàm (`fn_*`), cổng (`gates.py`), phân loại (`q_classify.py`) |
| `tools/` | công cụ | Một script cho mỗi bước của mỗi study (`run_study_*`, `freeze_study.py`, `p_analyze.py`, `q_instance.py`, `q_analyze.py`, …) |
| `tests/` | kiểm thử | Unit test cho lõi và công cụ |
| `.github/workflows/` | điều phối | Mỗi workflow là một bước có thể tái lập; bước trả phí bị khoá bởi `pre_b9/RELEASE_GATE.json` |
| `study_b/` … `study_q/` | bằng chứng | Mỗi study: protocol, `AMENDMENTS.md`, `config_*.json`, `FREEZE.json` (băm các tệp đã đóng băng), kết quả |
| `research_closure/` | bằng chứng + tài liệu | Kết quả tổng hợp (`results/`), manifest của từng gói cập nhật (`manifests/`), audit |
| `results/`, `evidence/`, `harness_checks/`, `next_evidence/` | bằng chứng | Log và kết quả của các đợt chạy cũ |
| `demo/`, `real/`, `p7/` | bằng chứng | Target dựng sẵn (demo), target Click thật, mã giai đoạn P7 |
| `pre_b9/` | điều phối | Cổng khoá các workflow B9 trả phí |
| `paper_snippets/` | tài liệu | Đoạn văn soạn sẵn để dán vào bài |
| `docs/` | tài liệu | **Điểm vào cho người đọc**: tracking, review bài, nhật ký, sơ đồ này |
| `docs/paper/source/` | tài liệu | Ba PDF gốc của FSE-2027-13 |
| `docs/history/` | tài liệu | Tài liệu cũ từng nằm ở gốc (START_HERE, tổng hợp D+E, kế hoạch trả lời phản biện, …) |
| `archive/root_packages/` | lưu trữ | Script và manifest của các gói cập nhật cũ từng bị giải nén vào gốc; chỉ để truy vết |

## Điểm vào

| Muốn | Đọc |
|---|---|
| Biết dự án đang ở đâu so với bài FSE | [`docs/TRACKING_FSE.md`](TRACKING_FSE.md) |
| Biết bài FSE sai ở đâu và sửa thế nào | [`docs/paper/PAPER_AUDIT.md`](paper/PAPER_AUDIT.md) |
| Ôn kiến thức, công thức | [`docs/paper/REVIEW_FSE.md`](paper/REVIEW_FSE.md) |
| Xem đã làm gì, khi nào, vì sao | [`docs/PROCESS_LOG.md`](PROCESS_LOG.md) |
| Run ID, commit, digest của từng bằng chứng | [`EVIDENCE_LEDGER.md`](../EVIDENCE_LEDGER.md) |

## Vì sao không chuyển các thư mục `study_*` vào `studies/`

Mỗi `FREEZE.json` lưu **đường dẫn tương đối từ gốc repo** của các tệp đã đóng băng (ví dụ `study_q/config_study_q.json`, `tools/q_instance.py`). Workflow và công cụ cũng gọi thẳng các đường dẫn này. Chuyển thư mục sẽ làm `freeze_study.py verify` thất bại và phá tính truy vết của các study đã đóng băng, trong đó có Study Q đang chạy. Vì vậy ở đây **chỉ sắp xếp lại các tệp không bị tham chiếu**, còn các lớp được ghi bằng tài liệu này.

**Quy tắc cho tệp mới:**

1. Tài liệu đặt ở `docs/`.
2. Mã dùng lại đặt ở `gatekeeper_ext/`; script đặt ở `tools/`; mỗi study một thư mục `study_<x>/`.
3. Manifest của gói cập nhật đặt ở `research_closure/manifests/`, **không** để ở gốc.
4. Không để tệp ở gốc trừ `README*.md`, `EVIDENCE_LEDGER.md`, `RUN_P6_REMOTE.py` (workflow `p6-remote-smoke.yml` và `tests/test_remote.py` gọi tới) và `.gitignore`.
