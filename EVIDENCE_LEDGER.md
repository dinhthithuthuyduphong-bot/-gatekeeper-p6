# Sổ bằng chứng (evidence ledger)

Mỗi dòng là một lần chạy trên GitHub Actions. "Phạm vi" ghi rõ điều được và **không** được kết luận. Digest có dấu `…` là bản rút gọn (12 ký tự đầu, tính từ file artifact đã tải về); cần bổ sung đầy đủ từ trang Actions.

| Mốc | Run ID | Commit | Artifact (sha256) | Phạm vi |
|---|---|---|---|---|
| P6.6 runner closure | 38847724560 | 243e3a3 | OCR `d5300dac7b37…`, pandas `9fd43227a4ba…` | Runner phát triển: 24 container, seed cố định, timeout, cleanup. Không phải trial độc lập |
| P7.0 source skill expansion | 38876972775 | 2a27674 | click `08778db1b871…`, requests `36ffab807725…`, werkzeug `cf6abdc1801c…` | Ba nguồn sửa lỗi chạy lại được; test nguồn đã lộ; không phải transfer |
| P7.1 independent oracle pilot | 38916044021 | cf3b4da | skill `eb071b9152f3…`, oracle `1c25072a70ad…` | Skill đóng băng sửa ca đã biết nhưng hỏng một đầu vào mới; 1 cụm issue |
| P7.2 repaired source / independent scope | (bổ sung) | (bổ sung) | `bbc13f77dbd2…`, `8af2995ccefe…` | v2 sửa có thông tin về target (không độc lập); v2 từ chối ở cụm đối chứng âm |
| P7.3 anchored binder | 38996416312 | e5e4422 | exposed `66bdbae17445fc737b0a5eac34c6a3c2bab13314ea1c484f0fc2de03af6463a5`, source `16c2d4a7337111685abb8ee44e24dfde4c666c7ef70459117cc48b3234188045` | Binder v3 trên target đã dùng để phát triển (#3298): bằng chứng phát triển |
| Gatekeeper-Lite demo #2 | 39139075701 | 6908381 | `b58c2391c3e194ce5eeb8d490a5872ef5a834fe2d1095affe0101bab00564b64` | Toàn chuỗi trên target dựng sẵn; không phải repository độc lập |
| Gatekeeper-Lite real-click | (chưa chạy) | | | Click thật, test gốc của Click; R1 đã thấy, R2–R3 chưa xem |

## Việc còn thiếu để tái lập

- Mã P7.x đang được **nhúng trong file workflow** dưới dạng base64 nén xz (ví dụ `p7-3-anchored-binder.yml`, bước "Unpack frozen binder revision and exposed target"). Mã chạy được và đóng băng, nhưng người đọc không xem hay diff được. Cần giải nén ra dạng đọc được bằng `python tools/extract_embedded_payload.py .github/workflows/p7-3-anchored-binder.yml p7/p7_3` và commit thư mục `p7/` kèm `MANIFEST.json` (sha256 của payload và từng file).
- Gắn tag cho các commit bằng chứng, ví dụ `p7.3-evidence` → `e5e4422`, `gk-lite-demo-v1` → `6908381`.
- Prospective pairs (trên target độc lập, protocol đóng băng trước): **0**.
