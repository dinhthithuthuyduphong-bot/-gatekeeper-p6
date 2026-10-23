# Kiểm tra tính không trạng thái của harness (post hoc, 0 đồng)

100 lần rút đã ghi mỗi scope được chạy lại **theo thứ tự xáo trộn**, với **worker mới sau mỗi 25 lần rút**, cùng seed băm như lượt chạy gốc; mọi kết quả ghép cặp (Z, regression) được so với kết quả đã ghi. Công cụ: `tools/statelessness_check.py`; workflow: `statelessness-check.yml`.

| Target | Trạng thái | Sai khác / số lần rút so sánh |
|---|---|---|
| C1_jsonschema | STATELESS | bool: 0/100, int: 0/100 |
| C2_voluptuous | STATELESS | bool: 0/100, int: 0/100 |
| D1_py_ecc | STATELESS | bool: 0/100, int: 0/100 |
| D2_cerberus | STATELESS | bool: 0/100, number: 0/100 |
| D3_speckit | STATELESS | bool: 0/100, int: 0/100 |
| D5_pycubrid | STATELESS | bool: 0/100, int: 0/100 |
| E1_pyyaml | STATELESS | bool: 0/100, int: 0/100 |
| E2_packaging | STATELESS | bool: 0/100, int: 0/100 |
| E3_databricks | STATELESS | bool: 0/100, int: 0/100 |
| G1_pydal | STATELESS | null: 0/100, plain: 0/100 |
| K1_trino | STATELESS | bool: 0/100, int: 0/100 |
| K2_tomlkit | STATELESS | bool: 0/100, int: 0/100 |

**Tổng:** 12 target, 2.400 lần rút, **0 sai khác, 0 lỗi harness**. Không kết quả nào phụ thuộc thứ tự thực thi hay trạng thái giữ lại giữa các lần rút.

**Vì sao quan trọng:** mô phỏng (`study_h/results/DEPENDENCE_SIM.md`) cho thấy quy tắc admit không bền khi lần rút phụ thuộc nhau (lặp mỗi lần rút 2 lần → 7,5% admit sai ở biên, so với 0,2% khi i.i.d.). Tính độc lập là điều kiện bắt buộc; kiểm tra này là bằng chứng thực nghiệm cho điều kiện đó trên toàn bộ target thật.
