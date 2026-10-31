# Gatekeeper-Lite — kiểm soát rủi ro khi tái sử dụng kỹ năng sửa code

**31/10/2026 — bắt đầu từ [`docs/`](docs/STRUCTURE.md):** [tracking so với bài FSE](docs/TRACKING_FSE.md) · [các lỗi của bài và cách sửa](docs/paper/PAPER_AUDIT.md) · [ôn kiến thức, công thức](docs/paper/REVIEW_FSE.md) · [nhật ký quá trình](docs/PROCESS_LOG.md) · [cấu trúc repo](docs/STRUCTURE.md). Study Q (SWE-bench Verified) đang chạy.

**26/10/2026 — checkpoint mới:** [audit main và hướng A*](research_closure/results/audit-20261026/RESULT.md), [cách chạy development có raw evidence](research_closure/results/audit-20261026/UPDATE_MAIN.md). Study L G1 **FAIL 2/6**; test-mutation mới vẫn DEVELOPMENT, không phải bằng chứng tiến cứu. B9 **HOLD**.

**25/10/2026 — zero-cost follow-up:** [python-control result](study_k/RESULT_VI.md), [reproduce / raw audit](study_k/README.md). A retrospective beneficial transfer was reproduced; B9 remains HOLD. See [cumulative update instructions](research_closure/UPDATE_MAIN.md).


Repo nghiên cứu cho luận văn tái hiện thu gọn (Lite) bài *Scope before Reuse: Risk-Controlled Admission of Learned Coding Skills* (FSE-2027-13). Repo **công khai**; không chứa mã của tổ chức, khoá API hay dữ liệu benchmark riêng. Ba PDF của bản thảo FSE-2027-13 (do AI sinh, mọi số là projected) nằm ở `docs/paper/source/` từ 31/10/2026.

**Cập nhật 24/10/2026:** [kết quả kiểm toán và giới hạn còn mở](research_closure/RESULT.md),
[hướng dẫn chạy audit 0 API](research_closure/UPDATE_MAIN.md). Study I có raw CI đã lưu;
phần closure mới kiểm tra local (125 tests), có benchmark dừng thật và baseline IUT
công bằng hơn. Đây không phải bằng chứng Gatekeeper thắng mọi baseline. Study F có
F-A3 trước paid B9; **B9 HOLD, Study J BLOCKED**. Log và cả kết quả âm được giữ.

## Nội dung

| Thư mục / file | Vai trò |
|---|---|
| `gatekeeper_lite/` | Pipeline: scope screen → binder AST → paired trials → e-process → ADMIT/QUARANTINE; comparator B2, B6-R, B8; composition; retirement |
| `demo/` | 7 target dựng sẵn (bằng chứng loại `CONSTRUCTED_DEMO_FIXTURES`) |
| `real/`, `tools/` | Cùng pipeline trên mã Click thật, chấm bằng test gốc của Click |
| `tests/` | Unit test (`python -m unittest discover -s tests -v`) |
| `.github/workflows/` | Các workflow chạy thủ công: P6.x, P7.x và `gk-lite-demo.yml` |
| `p7/` | Mã P7.x ở dạng đọc được, giải nén từ payload nhúng trong workflow (`tools/extract_embedded_payload.py`) |
| `RUN_P6_REMOTE.py` | Smoke test container của giai đoạn P6 (giữ lại để truy vết) |
| `EVIDENCE_LEDGER.md` | Sổ bằng chứng: run ID, commit, digest artifact, phạm vi kết luận |
| `study_*/` | Protocol, `FREEZE.json` và kết quả của từng study |
| `docs/` | Tracking, review bài, nhật ký, sơ đồ repo; `docs/history/` là tài liệu cũ |
| `archive/` | Script và manifest của các gói cập nhật cũ (chỉ để truy vết) |

Hướng dẫn chạy, ánh xạ với paper và giới hạn: xem [`README_VI.md`](README_VI.md).

## Quy ước về bằng chứng

- **Paper expectation:** số liệu trong bài là *projected*, không phải kết quả của repo này.
- **Implemented:** có mã chạy được.
- **Verified:** có run trên GitHub Actions, artifact và digest ghi trong `EVIDENCE_LEDGER.md`.

Workflow audit 0 API chạy thủ công (`workflow_dispatch`) và không gọi model.
Các workflow B9 trả phí là luồng riêng, hiện bị khóa bởi `pre_b9/RELEASE_GATE.json`.
