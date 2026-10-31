# Rà soát mã và GitHub Actions (31/10/2026)

Mục tiêu: những gì một phản biện artifact (hoặc người dùng lại repo) sẽ thấy khi mở repo, và những gì có thể làm sai bằng chứng.

## GitHub Actions

| # | Vấn đề | Mức | Đã sửa | Bằng chứng |
|---|---|---|---|---|
| CA1 | **Không có CI tự chạy**: 0/101 workflow chạy khi push hoặc có PR; test, kiểm số và freeze chỉ chạy khi có người bấm | 🔴 | `ci.yml` chạy khi push lên main và khi có PR: unit test, actionlint, 30 con số của bài, freeze của mọi study được trích (P tại commit đóng băng) | run 41218161428, 41218445716 |
| CA2 | **346 lần dùng action ghim theo tag** (`@v6`), tag có thể bị dời; bằng chứng "đóng băng" phụ thuộc mã bên ngoài có thể đổi | 🟠 | Mọi action được ghim theo SHA commit (`tools/pin_actions.py`). SHA được tra **bên trong** Actions (phiên không đọc được repo khác; `GITHUB_TOKEN` không được sửa workflow), rồi áp bằng `--mapping`. Bảng ánh xạ: `.github/actions-pins.json`. Dependabot giữ các bản ghim cập nhật | run 41217291272; `pin_actions --check`: 0 |
| CA3 | `google-github-actions/auth@v2` chạy Node 20 đã bị khai tử (cảnh báo ở mọi run) | 🟠 | Nâng lên v3 (Node 24) ở cả 16 workflow; kiểm bằng `Gatekeeper Vertex token check` | run 41218337136 |
| CA4 | `results-check.yaml` trùng hệt `results-check.yml` | 🟡 | Xoá bản `.yaml` | — |
| CA5 | Workflow gọi model `rq5-rate.yml` không có `timeout-minutes` (mặc định 6 giờ) | 🟡 | 50 phút | — |
| CA6 | Bước lint của CI mất hơn 9 phút, vì shellcheck chạy trên các workflow nhúng payload lớn | 🟡 | actionlint với `-shellcheck=`; vẫn kiểm cấu trúc workflow | run 41218445716 |
| CA7 | 38 workflow khác (chạy miễn phí) không có `timeout-minutes` | 🟡 | Chưa sửa: không tốn tiền model; mặc định của GitHub vẫn chặn ở 6 giờ | — |

## Mã Python (ruff: F, E9, B006, B008, B023)

| # | Kết quả | Xử lý |
|---|---|---|
| PY1 | Không có lỗi tên chưa định nghĩa (F821) hay lỗi cú pháp (E9) | — |
| PY2 | 16 cảnh báo B023 (closure bắt biến vòng lặp) | Đã xem từng chỗ: **đều là báo động giả**, vì hàm được gọi ngay trong lượt lặp đó (`visit`, `need`, `ex.map` trong khối `with`) |
| PY3 | F632 trong `tests/test_ext.py` | Cố ý (test hành vi của `5 is None`); đã đánh dấu `noqa` |
| PY4 | 45 import thừa (F401) | Đã xoá 21 trong `tools/`, `tests/` không đóng băng. Phần còn lại nằm trong tệp đã đóng băng (sửa sẽ làm freeze lệch), trong mã vendor hoặc trong fixture của demo, nên giữ nguyên |
| PY5 | 12 biến không dùng (F841) | Trong mã vendor, hoặc trong tệp đã đóng băng; giữ nguyên |

Freeze của D, E, G, H, Q vẫn verified sau mọi sửa đổi; toàn bộ test pass.
