# Study D — kết quả (study-g-v1)

Trạng thái protocol: FROZEN · đóng băng: xem repo (tag study-g-freeze) · θ=0.2, η=0.05, α=0.1 (e-Holm, FWER), n_max=300, K=2

## 1. Bộ dữ liệu

| Target | Vai trò | Commit | Skill áp dụng ở | Skill từ chối ở |
| --- | --- | --- | --- | --- |
| G1_pydal | HARM (tier 1: pydal's own tests assert that == None builds IS NULL queries) | bd5eb6d7f6 | pydal/backend_base.py, pydal/base.py, pydal/objects.py, pydal/querybuilder.py | — |

## 2. Quyết định theo ô

| Ô | Giúp/hòa/hại (đến lúc dừng) | Census | B2 | B6-R | B8 (đủ ngân sách) | Gatekeeper (e-Holm) | e-BH (phụ) | Số lần rút GK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G1_pydal/null | 0/79/24 | 21 regression mới | ADMIT | ADMIT | REJECT | REJECT_HARM | — | 103 |
| G1_pydal/plain | 0/300/0 | 21 regression mới | ADMIT | ADMIT | REJECT | REJECT_HARM | — | 300 |

## 3. Chi phí đo được (wall-clock thật trên runner)

| Target | GK: lần rút | B8: lần rút | Census (giây) | Khởi động worker (giây) | GK tổng (giây) | B8 tổng (giây) |
| --- | --- | --- | --- | --- | --- | --- |
| G1_pydal | 403 | 600 | 25.36 | 0.055 | 26.81 | 27.21 |

Tổng wall-clock: Gatekeeper 26.81 s, B8 27.21 s (Gatekeeper / B8 = 0.98). Chi phí cố định (census, khởi động) tính cho cả hai; chỉ phần rút mẫu khác nhau.

## 5. Ablation đăng ký trước (chạy lại trên dữ liệu đã ghi)

| Biến thể | G1_pydal/null | G1_pydal/plain |
|---|---|---|
| full | REJECT_HARM(census)@103 | REJECT_HARM(census)@300 |
| no_harm_cert | REJECT_HARM(census)@103 | REJECT_HARM(census)@300 |
| no_census | REJECT_HARM@103 | QUARANTINE@300 |
| bonferroni | REJECT_HARM(census)@103 | REJECT_HARM(census)@300 |
| sign_test | REJECT_HARM(census)@103 | REJECT_HARM(census)@300 |
| eta_0.10 | REJECT_HARM(census)@207 | REJECT_HARM(census)@300 |

## 6. Giới hạn

- Kết luận chỉ áp dụng cho các bộ sinh đã khai báo trên target ở commit đã ghim.
- Đối chứng ngữ nghĩa (voluptuous) dùng hợp đồng của chính target; kết luận 'có hại' phụ thuộc hợp đồng đó.
- Composition và retirement chỉ được minh hoạ trên dữ liệu phát triển.
