# Các API dùng trong dự án, và lý do từng lần chạy thất bại

File này trả lời hai câu hỏi:
1. **Mỗi API:** gọi ở đâu, input là gì, body và context gửi đi là gì, output nhận về là gì, giới hạn và chi phí.
2. **Mỗi lần chạy thất bại trên GitHub Actions:** thất bại ở bước nào, nguyên nhân gốc là gì, đã sửa thế nào.

**Kiểm lại trên GitHub Actions** (0 USD):
- workflow `Gatekeeper failure audit` (`.github/workflows/failure-audit.yml`, công cụ `tools/failure_audit.py`) đọc log của **bước thất bại** trong mọi run lỗi, xếp nhóm nguyên nhân, và commit [`research_closure/results/failure_audit/FAILURE_AUDIT.md`](../research_closure/results/failure_audit/FAILURE_AUDIT.md) (bảng đầy đủ, có link tới từng run) cùng `FAILURE_AUDIT.json` (kèm dòng bằng chứng).
- Muốn xem một run cụ thể: nhập id vào ô `runs`.

---

## 1. Các API

### 1.1 Vertex AI (Gemini), giao diện tương thích OpenAI — **tốn tiền**

| Mục | Giá trị |
|---|---|
| Endpoint | `POST https://aiplatform.googleapis.com/v1/projects/{GCP_PROJECT}/locations/global/endpoints/openapi/chat/completions` |
| Xác thực | Header `Authorization: Bearer $GOOGLE_OAUTH_TOKEN`. Token lấy bằng `gcloud auth print-access-token` sau bước `google-github-actions/auth` với secret `GCP_SA_KEY`. **Token sống khoảng 1 giờ.** |
| Mã client | `gatekeeper_ext/b9_cohort.py: CohortClient.complete`, bọc bởi `tools/cohort_inner.py: RefreshingClient` |
| Cấu hình model | `research_closure/pilot/models.json` |

**Body gửi đi (JSON):**

```json
{
  "model": "google/gemini-3.8-flash",
  "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
  "max_tokens": 4000,
  "temperature": 0.0,
  "seed": 123456789,
  "reasoning_effort": "low"
}
```

**Output nhận về** (client chuẩn hoá): `{"text": <nội dung trả lời>, "usage": {"input", "output", "usage_missing"}, "raw": {"id", "model", "finish_reason", "usage", "request_params"}}`.
- Số token output tính **cả token "thinking"** (`gatekeeper_ext/usage.py`).
- Nếu nhà cung cấp không trả `usage`, client lấy cận trên để không chi vượt.

**Xử lý lỗi:**
- HTTP 429 được thử lại với back-off 10, 30, 90, 180 giây.
- Token được làm mới mỗi 1.500 giây bằng `GK_TOKEN_CMD`. *Lưu ý:* `gcloud` có thể trả lại token còn trong bộ nhớ đệm, nên job chạy quá khoảng 1 giờ vẫn có thể hết hạn; xem lỗi 3.1.
- Mọi lỗi HTTP khác được ném ra thành `RuntimeError("HTTP <mã>: <body>")`.
- Trần chi `b9.SpendGuard`: trước mỗi lần gọi, công cụ kiểm tra (đã chi + chi tối đa của lần gọi này) ≤ trần.

**Các nơi dùng, với input và context cụ thể:**

| Dùng cho | Model | Context gửi đi (system / user) | Output mong đợi | Tham số | Trần chi |
|---|---|---|---|---|---|
| **G2: model viết chương trình sinh đầu vào** (Study P, Q; `gatekeeper_ext/fn_llm_gen.py`) | `vertex-gemini-flash` | system: "You write Python input generators for differential testing…". user: tên hàm và tệp, mô tả issue (≤ 3.000 ký tự), 40 dòng đầu module, `__init__` của lớp, mã hàm bản gốc (≤ 6.000 ký tự), **diff của bản fix** cho tệp đó (≤ 4.000 ký tự), các quy tắc (chỉ dùng `rng`, không mạng, nửa đầu vào thường, nửa quanh issue) | một khối mã Python định nghĩa `make_inputs(rng, n)` | `max_tokens` 4.000; nhiệt độ 0,0 rồi 0,4 nếu lần đầu hỏng (kèm thông báo lỗi); seed theo instance | 0,15 USD mỗi instance |
| **Sinh patch** (Study P, vòng B9 đã đóng băng) | flash, argon | mô tả issue, mã liên quan (`gatekeeper_lite/b9.py`) | một diff | theo `b9.repair` | theo cấu hình study |
| **Người chấm thứ hai** (RQ5, Q-A1; `tools/rq5_rate_llm.py`) | `vertex-gemini-argon` | system: bộ mã R / B / U. user: tên hàm, tệp, diff của patch (≤ 3.000 ký tự), output của bản fix và của patch. **Không** có đầu vào, loại hay giả thuyết (chấm mù) | JSON `{"code": "R"|"B"|"U", "reason": "..."}` | nhiệt độ 0, `max_tokens` 2.000, seed 1 | 2 USD mỗi lần chạy (mỗi phần) |
| **Smoke endpoint** (`vertex-smoke.yml`) | các model | prompt ngắn | kiểm `finish_reason`, giá | | rất nhỏ |

**Giá** (theo `models.json`, USD cho 1 triệu token, input / output):
- flash: 0,75 / 3,75; từ 1/1/2027: 1,5 / 7,5.
- argon: 2 / 10; từ 1/12/2026: 4 / 20.

### 1.2 drand (nguồn ngẫu nhiên công khai cho seed) — miễn phí

- `GET https://api.drand.sh/52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971/public/{round}` (chuỗi quicknet, 3 giây mỗi vòng).
- **Input:** `seed_time_utc` của study, đổi ra số vòng.
- **Output:** `{"round", "randomness", "signature"}`.
- **Seed** = 15 ký tự hex đầu của `sha256(<hash của FREEZE.json gốc> + randomness)`, đổi ra số nguyên (`tools/run_study_d.py: drand_seed`).
- **Vì sao dùng:** seed được quyết định **sau** khi đóng băng, nên không ai chọn được seed có lợi.
- **Lỗi có thể gặp:** gọi trước `seed_time_utc` thì vòng chưa có, và công cụ dừng với "seed round is in the future" (lỗi 3.3).

### 1.3 Docker Hub (image chính thức của SWE-bench) — miễn phí

- `docker pull swebench/sweb.eval.x86_64.<instance_id, "__" đổi thành "_1776_">:latest` (`tools/q_f0.py: image_name`).
- Output: image có `/testbed` là bản gốc của repo; công cụ áp gold patch hoặc patch của agent lên bản sao.
- Nếu không kéo được, bản ghi có trạng thái `NO_IMAGE`.

### 1.4 Kho bản nộp SWE-bench (Q-F2) — miễn phí

- `metadata.yaml` trong kho `SWE-bench/experiments`.
- Dự đoán lấy từ `https://swe-bench-submissions.s3.amazonaws.com/verified/<bản nộp>/all_preds.jsonl`, hoặc GitHub raw, hoặc `logs/<instance>/patch.diff`.
- Output: `study_q/evidence/POOL.jsonl.gz` (31.205 patch resolved, 469 instance).
- Lỗi có thể gặp: HTTP 502 (lỗi 3.8).

### 1.5 GitHub REST API (trong workflow) — miễn phí

- `gh run download <run> -p 'Q_*'` tải artifact; `gh api repos/{owner}/{repo}/actions/runs/...` lấy danh sách run, job và log.
- Xác thực: `GITHUB_TOKEN` với quyền `actions: read` và `contents: write` (để commit kết quả).
- Lưu ý khi chạy **ngoài** Actions (phiên trợ lý): proxy chặn tải artifact và log trực tiếp, nên mọi bước cần log hoặc artifact được làm trong workflow.

---

## 2. Tổng hợp lý do thất bại

Nguồn: [`FAILURE_AUDIT.md`](../research_closure/results/failure_audit/FAILURE_AUDIT.md), 64 run thất bại trong 400 run gần nhất. Bảng đầy đủ từng run và dòng bằng chứng nằm trong tệp đó. Dưới đây là phân tích nguyên nhân gốc theo nhóm, đã đối chiếu tay với log.

| Nhóm | Số run | Nguyên nhân gốc | Đã sửa / cách phòng |
|---|---|---|---|
| **Workflow không khởi động** | 13 | Tệp workflow lỗi ở commit đó, nên GitHub không tạo job. Tên run hiện bằng đường dẫn tệp (`.github/workflows/study-d-run.yml`, `p7-2-guarded-repair-scope.yml`, và một bản trùng tên có dấu cách `… 1.yml`) | Sửa YAML; kiểm `yaml.safe_load` cho mọi workflow trước khi push |
| **Thiếu tệp** | 8 | Workflow chạy trước khi tệp nó cần được commit: manifest `study_p_feasibility.json`, `tools/vet_dev.py`, `study_m_astar/candidates.json`, `study_f/FREEZE.json`, thư mục `study_q/evidence/` | Commit tệp trước, chạy sau; bước đầu của workflow kiểm tệp tồn tại |
| **Thiếu thư viện / công cụ** | 6 | `typer` (phụ thuộc của repo đích Study B); `pip install` lỗi (Study D); hàm `_set` bị đổi chỗ khi refactor `amend_study_d`; Python 3.8.20 không có trên Ubuntu 22.04 | Cài phụ thuộc trong workflow; giữ tương thích khi refactor; chọn phiên bản Python có sẵn |
| **Lệnh chặn có chủ đích (guard)** | 10 | Study chưa đóng băng (`DRAFT`, "amendments apply only to a FROZEN study"); amendment đã áp ("P-A2 already applied"); seed chưa tới giờ ("seed round is in the future"); thiếu tiền điều kiện ("REFUSED: missing files", "a part-B candidate is already in the frames"); "FROZEN FILES CHANGED" | **Không phải lỗi**: guard làm đúng việc. Đọc thông báo rồi làm đúng thứ tự |
| **Test đơn vị hỏng** | 5 | Bản sao thừa của tệp test ở gốc repo (`test_fn_probe`, `test_vet_target2`) che bản trong `tests/`; và `PyYAML` thiếu khi chạy test (Q freeze, run 41175551823) | Công cụ `tools/repo_hygiene.py` và workflow `repo hygiene` |
| **Runner bị dừng (mã 143)** | 5 | Mã của một repo được kiểm tra gửi SIGTERM ra cả nhóm tiến trình. Bước tải artifact cũng không chạy, nên mất cả mảnh (Study P cohort run 41036085344: 2/200 job; mảnh 151, 181; provisioning vet) | Amendment P-A2 (chạy tiếp phần còn lại), P-A3 (mỗi ứng viên một job) |
| **Exception của Python** | 8 | Lỗi mã: `AttributeError` của oracle Study H; `PYTHONHASHSEED` sai giá trị (Study D smoke); `git fetch` lỗi; dọn thư mục tạm bị tranh chấp; các audit "next evidence" báo test hoặc inventory hỏng | Sửa từng lỗi; xem bằng chứng trong FAILURE_AUDIT.json |
| **Đầu vào bị từ chối** | 3 | `only=3` không phải id instance (Study Q stream run #2); RQ3 kỳ vọng 14 target nhưng thấy 16 (assertion của kế hoạch) | Patch `study_q_stream_msg` (thông báo rõ); amendment P-A1 cho RQ3 |
| **Mạng / dịch vụ ngoài** | 2 (5xx 1, ngắt kết nối 1) | HTTP 502 khi tải kho bản nộp; GitHub API ngắt kết nối (Study P phần B) | Chạy lại; công cụ nên thử lại khi gặp 5xx |
| **Hết giờ** | 1 | `pytest` của test-mutation quá hạn | Tăng giới hạn hoặc chia nhỏ |
| **Token hết hạn** | 1 | Người chấm thứ hai Q-A1 (run 41193552100) chạy khoảng 60 phút > tuổi thọ token; `gcloud` trả token cũ trong bộ nhớ đệm | Chia thành 6 job (`study-q-review-rate.yml`); thành công ở run 41197881665 |
| **Hạ tầng runner** | 1 | Container lỗi `chdir` (OCI runtime) trong Gatekeeper-Lite demo | Chạy lại |
| **Khác** | 1 | P6.3 OCR replay: chính công cụ báo `SETUP_OR_REPLAY_FAILURE` (container phát lại không khớp) | Xem log của P6.3 |

Số trong bảng khớp với lần audit thứ ba (run 41207250040), và đã được đối chiếu tay với dòng bằng chứng của từng run. Lần audit thứ nhất và thứ hai xếp sai phần lớn: chúng đọc cả log và bắt nhầm một dòng tiêu đề bảng có chữ "HTTP 429"; đã sửa để chỉ đọc bước thất bại.

## 3. Ghi chú nguyên nhân gốc cho các lỗi trong phiên ngày 31/10/2026

### 3.1 Token Vertex hết hạn (run 41193552100)
- **Triệu chứng:** sau khoảng 60 phút, Vertex trả `401 UNAUTHENTICATED, reason ACCESS_TOKEN_EXPIRED`; `rq5_rate_llm.py` chỉ ghi tệp ở cuối nên mất hết.
- **Chuỗi nguyên nhân:**
  1. 154 lần gọi tuần tự, mỗi lần khoảng 20 giây;
  2. token cấp lúc bắt đầu job sống khoảng 60 phút;
  3. `RefreshingClient` gọi lại `gcloud auth print-access-token` mỗi 25 phút, nhưng `gcloud` trả **token còn hạn trong bộ nhớ đệm**, chính là token cũ;
  4. tới phút 60 token hết hạn.
- **Sửa:** mỗi job xử lý một phần (6 phần, khoảng 10 phút mỗi phần), mỗi job có token mới.
- **Sửa tận gốc (31/10/2026):** `tools/fresh_gcp_token.py` luôn tạo token mới bằng google-auth; 13 workflow dùng nó làm `GK_TOKEN_CMD`. Kiểm: workflow `Gatekeeper Vertex token check`. Vẫn nên giữ job dưới 45 phút và ghi kết quả dần dần.

### 3.2 `only=3` (run 41182723003)
- Ô `only` nhận id instance; "3" không phải id, nên `assert set(sel) <= set(ids)` hỏng mà không có thông báo.
- **Sửa:** patch `study_q_stream_msg` báo id sai kèm vài id ví dụ.

### 3.3 Seed chưa tới giờ (run 41178191261)
- Stream chạy lúc 06:50, trong khi `seed_time_utc` là 07:47:53. Vòng drand đó chưa tồn tại, nên `drand_seed` dừng.
- **Đây là thiết kế đúng:** seed phải lấy sau khi đóng băng.

### 3.4 Lệch giao thức Study Q: không lưu đầu ra
- Không phải run thất bại, nhưng là lỗi thiết kế công cụ: `q_instance.py` chỉ lưu số đếm. Đã xử lý bằng amendment Q-A1.

### 3.5 Kiểm tra từ phiên trợ lý (không phải lỗi của repo)
- Proxy của phiên chặn: tải artifact (`*.blob.core.windows.net`), tải log trực tiếp, GraphQL (`gh workflow run`), và push tag.
- Cách làm: kích hoạt workflow qua REST/MCP; đọc log qua MCP hoặc trong workflow; mốc amendment ghi bằng commit thay cho tag.


## Lỗi cài đặt: `SETUPTOOLS_SCM_PRETEND_VERSION` toàn cục (tìm ra 31/10/2026, Study S-A4)
- **Triệu chứng:** `ERROR: No matching distribution found for uvtools>=0.2.0`, dù PyPI có `uvtools 0.2.0`.
- **Nguyên nhân gốc:** harness đặt `SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0` trong môi trường của lệnh `pip install` để build gói đang kiểm (repo clone không có tag). Biến này áp cho **mọi** gói build từ mã nguồn bằng setuptools-scm, nên `uvtools` được build thành 0.0.0 ("Requested uvtools>=0.2.0 ... but installing version 0.0.0").
- **Sửa:** chỉ đặt phiên bản giả cho gói đang kiểm, `SETUPTOOLS_SCM_PRETEND_VERSION_FOR_<TÊN_GÓI>` (Study S-A5).
- **Ảnh hưởng tới study cũ:** `tools/rq3_target.py`, `statelessness_check.py`, `run_study_d.py` và một số tool khác dùng cùng mẫu. Các target của chúng đã cài được, nên kết quả không bị ảnh hưởng; khi dùng lại các tool này cho target mới thì phải sửa giống S-A5.
