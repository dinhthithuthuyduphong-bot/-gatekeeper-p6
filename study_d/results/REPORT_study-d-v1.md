# Study D — kết quả (study-d-v1)

Trạng thái protocol: FROZEN (A1) · đóng băng: xem config trên repo (tag study-d-freeze, study-d-freeze-a1) · θ=0.2, η=0.05, α=0.1 (e-Holm, FWER), n_max=300, K=16

## 1. Bộ dữ liệu

| Target | Vai trò | Commit | Skill áp dụng ở | Skill từ chối ở |
| --- | --- | --- | --- | --- |
| A1_speckit_catalog | applicability control (bug behind int(...) without isinstance; skill not expected to fix it) | 7fda89decb | — | src/specify_cli/presets.py: NO_MATCH |
| C1_jsonschema | no-op control (bool already excluded) | cfe8a40716 | jsonschema/_types.py | — |
| C2_voluptuous | semantic control (bool accepted by design; skill expected harmful) | dcaaf3dd68 | voluptuous/validators.py | voluptuous/schema_builder.py: NO_MATCH |
| D1_py_ecc | positive (independent rediscovery of PR #161) | 5cb90f3387 | py_ecc/bls/ciphersuites.py, py_ecc/fields/field_elements.py, py_ecc/fields/optimized_field_elements.py | — |
| D2_cerberus | positive (independent rediscovery of d25ae8f); the int check uses an alias (_int_types) | 2b63c1b9cc | cerberus/cerberus.py | — |
| D3_speckit | positive (independent rediscovery of PR #3268; fix has the skill's exact shape) | f6f3540409 | src/specify_cli/extensions/_commands.py | — |
| D4_openfeature | positive (independent rediscovery of PR #621); type checked via a variable (py_type) | 93296c6e77 | — | openfeature/client.py: NO_MATCH |
| D5_pycubrid | positive (independent rediscovery of PR #479) | 068325e75a | pycubrid/types.py | — |

## 2. Quyết định theo ô

| Ô | Giúp/hòa/hại (đến lúc dừng) | Census | B2 | B6-R | B8 (đủ ngân sách) | Gatekeeper (e-Holm) | e-BH (phụ) | Số lần rút GK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1_py_ecc/bool | 85/25/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | ADMIT | ADMIT | 110 |
| D1_py_ecc/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| D2_cerberus/bool | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| D2_cerberus/number | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| D3_speckit/bool | 56/54/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | ADMIT | ADMIT | 110 |
| D3_speckit/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| D4_openfeature/bool | — | — | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | — | 0 |
| D4_openfeature/int | — | — | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | — | 0 |
| D5_pycubrid/bool | 33/267/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| D5_pycubrid/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| A1_speckit_catalog/bool | — | — | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | — | 0 |
| A1_speckit_catalog/int | — | — | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | OUT_OF_SCOPE | — | 0 |
| C1_jsonschema/bool | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| C1_jsonschema/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| C2_voluptuous/bool | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |
| C2_voluptuous/int | 0/300/0 | 0 regression mới | ADMIT | ADMIT | ADMIT | QUARANTINE | — | 300 |

## 3. Chi phí đo được (wall-clock thật trên runner)

| Target | GK: lần rút | B8: lần rút | Census (giây) | Khởi động worker (giây) | GK tổng (giây) | B8 tổng (giây) |
| --- | --- | --- | --- | --- | --- | --- |
| C1_jsonschema | 600 | 600 | 4.09 | 0.055 | 5.01 | 5.01 |
| C2_voluptuous | 600 | 600 | 1.97 | 0.043 | 2.12 | 2.12 |
| D1_py_ecc | 410 | 600 | 740.69 | 0.05 | 742.26 | 742.3 |
| D2_cerberus | 600 | 600 | 1.82 | 0.042 | 2.03 | 2.03 |
| D3_speckit | 410 | 600 | 14.61 | 0.069 | 37.67 | 47.94 |
| D5_pycubrid | 600 | 600 | 4.95 | 0.048 | 5.21 | 5.21 |

Tổng wall-clock: Gatekeeper 794.31 s, B8 804.61 s (Gatekeeper / B8 = 0.99). Chi phí cố định (census, khởi động) tính cho cả hai; chỉ phần rút mẫu khác nhau.

## 5. Ablation đăng ký trước (chạy lại trên dữ liệu đã ghi)

| Biến thể | D1_py_ecc/bool | D1_py_ecc/int | D2_cerberus/bool | D2_cerberus/number | D3_speckit/bool | D3_speckit/int | D4_openfeature/bool | D4_openfeature/int | D5_pycubrid/bool | D5_pycubrid/int | A1_speckit_catalog/bool | A1_speckit_catalog/int | C1_jsonschema/bool | C1_jsonschema/int | C2_voluptuous/bool | C2_voluptuous/int |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | ADMIT@110 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@110 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| no_harm_cert | ADMIT@26 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@44 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| no_census | ADMIT@110 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@110 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| bonferroni | ADMIT@110 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@110 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| sign_test | ADMIT@110 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@110 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | ADMIT@158 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |
| eta_0.10 | ADMIT@54 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | ADMIT@54 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | OUT_OF_SCOPE | OUT_OF_SCOPE | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 | QUARANTINE@300 |

## 6. Giới hạn

- Kết luận chỉ áp dụng cho các bộ sinh đã khai báo trên target ở commit đã ghim.
- Đối chứng ngữ nghĩa (voluptuous) dùng hợp đồng của chính target; kết luận 'có hại' phụ thuộc hợp đồng đó.
- Composition và retirement chỉ được minh hoạ trên dữ liệu phát triển.
