# Gatekeeper-Lite — kiểm soát rủi ro khi tái sử dụng kỹ năng sửa code

Repo nghiên cứu cho luận văn tái hiện thu gọn (Lite) bài *Scope before Reuse: Risk-Controlled Admission of Learned Coding Skills* (FSE-2027-13). Repo **công khai**; không chứa mã của tổ chức, PDF bản thảo, khoá API hay dữ liệu benchmark riêng.

## Nội dung

| Thư mục / file | Vai trò |
|---|---|
| `gatekeeper_lite/` | Pipeline: scope screen → binder AST → paired trials → e-process → ADMIT/QUARANTINE; comparator B2, B6-R, B8; composition; retirement |
| `demo/` | 7 target dựng sẵn (bằng chứng loại `CONSTRUCTED_DEMO_FIXTURES`) |
| `real/`, `tools/` | Cùng pipeline trên mã Click thật, chấm bằng test gốc của Click |
| `tests/` | Unit test (`python -m unittest discover -s tests -v`) |
| `.github/workflows/` | Các workflow chạy thủ công: P6.x, P7.x và `gk-lite-demo.yml` |
| `RUN_P6_REMOTE.py` | Smoke test container của giai đoạn P6 (giữ lại để truy vết) |
| `EVIDENCE_LEDGER.md` | Sổ bằng chứng: run ID, commit, digest artifact, phạm vi kết luận |

Hướng dẫn chạy, ánh xạ với paper và giới hạn: xem [`README_VI.md`](README_VI.md).

## Quy ước về bằng chứng

- **Paper expectation:** số liệu trong bài là *projected*, không phải kết quả của repo này.
- **Implemented:** có mã chạy được.
- **Verified:** có run trên GitHub Actions, artifact và digest ghi trong `EVIDENCE_LEDGER.md`.

Mọi lần chạy đều thủ công (`workflow_dispatch`) và không gọi model trả phí.
