# Study D — kết quả (study-e-v1)

Trạng thái protocol: FROZEN · đóng băng: xem config trên repo (tag study-e-freeze) · θ=0.2, η=0.05, α=0.1 (e-Holm, FWER), n_max=300, K=10

## 1. Bộ dữ liệu

| Target | Vai trò | Commit | Skill áp dụng ở | Skill từ chối ở |
| --- | --- | --- | --- | --- |
| E1_pyyaml | HARM (tier 2b: bool listed explicitly in ignore_aliases) | f5e4504a92 | lib/yaml/representer.py | — |
| E2_packaging | MIXED/contested (tier 2: maintainer closed PR #1425) | 1a62a26afe | src/packaging/version.py | — |
| E3_databricks | illustrative (tier 3 characterization; not primary evidence) | a737ef3107 | src/databricks/sql/utils.py | — |
| K1_trino | CONTROL (bool handled before the int branch) | 74c6156ee6 | trino/dbapi.py | — |
| K2_tomlkit | CONTROL (bool handled before the int branch) | eddd27e43a | tomlkit/items.py | — |

## 2. Quyết định theo ô

| Ô | Giúp/hòa/hại (đến lúc dừng) | Census | B2 | B6-R | B8 (đủ ngân sách) | Gatekeeper (e-Holm) | e-BH (phụ) | Số lần rút GK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1_pyyaml/bool | 0/0/2 | 0 regression mới | ADMIT | ADMIT | REJECT | REJECT_HARM | — | 2 |
| E1_pyyaml/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| E2_packaging/bool | 0/0/2 | 0 regression mới | ADMIT | ADMIT | REJECT | REJECT_HARM | — | 2 |
| E2_packaging/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| E3_databricks/bool | 0/0/2 | 0 regression mới | ADMIT | ADMIT | REJECT | REJECT_HARM | — | 2 |
| E3_databricks/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| K1_trino/bool | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| K1_trino/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| K2_tomlkit/bool | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| K2_tomlkit/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |

## 3. Chi phí đo được (wall-clock thật trên runner)

| Target | GK: lần rút | B8: lần rút | Census (giây) | Khởi động worker (giây) | GK tổng (giây) | B8 tổng (giây) |
| --- | --- | --- | --- | --- | --- | --- |
| E1_pyyaml | 302 | 600 | 17.03 | 0.052 | 17.5 | 17.79 |
| E2_packaging | 302 | 600 | 176.15 | 0.051 | 176.28 | 176.33 |
| E3_databricks | 302 | 600 | 41.88 | 0.041 | 42.75 | 42.78 |
| K1_trino | 600 | 600 | 4.69 | 0.05 | 5.15 | 5.15 |
| K2_tomlkit | 600 | 600 | 2.55 | 0.05 | 2.83 | 2.83 |

Tổng wall-clock: Gatekeeper 244.51 s, B8 244.88 s (Gatekeeper / B8 = 1.00). Chi phí cố định (census, khởi động) tính cho cả hai; chỉ phần rút mẫu khác nhau.

## 5. Ablation đăng ký trước (chạy lại trên dữ liệu đã ghi)

| Biến thể | E1_pyyaml/bool | E1_pyyaml/int | E2_packaging/bool | E2_packaging/int | E3_databricks/bool | E3_databricks/int | K1_trino/bool | K1_trino/int | K2_tomlkit/bool | K2_tomlkit/int |
|---|---|---|---|---|---|---|---|---|---|---|
| full | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| no_harm_cert | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| no_census | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| bonferroni | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| sign_test | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| eta_0.10 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | REJECT_HARM@2 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |

## 6. Giới hạn

- Kết luận chỉ áp dụng cho các bộ sinh đã khai báo trên target ở commit đã ghim.
- Đối chứng ngữ nghĩa (voluptuous) dùng hợp đồng của chính target; kết luận 'có hại' phụ thuộc hợp đồng đó.
- Composition và retirement chỉ được minh hoạ trên dữ liệu phát triển.
