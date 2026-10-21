# Chi phí: thời gian đo thật và ước tính theo mô hình (từ dữ liệu đã ghi, không chạy thêm)

Thời gian đo thật = census (3 baseline + treatment + chạy lại nếu có) + khởi động worker + thời gian rút mẫu đã ghi (`gatekeeper_seconds` cho Gatekeeper; `seconds` cho B8, tức đủ 300 lần rút mỗi scope). Không gồm tải repo và cài dependency. Hai cột cuối là **ước tính theo mô hình** T = F + n·c.

| Target | F đo được (s) | Lần rút GK / B8 | GK đo được (s) | B8 đo được (s) | Tiết kiệm đo được | c cần để tiết kiệm 10% (mô hình) | Tiết kiệm tối đa (mô hình, c rất lớn) |
|---|---|---|---|---|---|---|---|
| C1_jsonschema | 4.14 | 600 / 600 | 5.01 | 5.01 | 0.00% | không đạt được | 0.0% |
| C2_voluptuous | 2.01 | 600 / 600 | 2.12 | 2.12 | 0.00% | không đạt được | 0.0% |
| D1_py_ecc | 740.74 | 410 / 600 | 742.26 | 742.30 | 0.00% | 0.57 s | 31.7% |
| D2_cerberus | 1.86 | 600 / 600 | 2.03 | 2.03 | 0.00% | không đạt được | 0.0% |
| D3_speckit | 14.68 | 410 / 600 | 37.67 | 47.94 | 21.42% | 0.01 s | 31.7% |
| D5_pycubrid | 5.00 | 600 / 600 | 5.21 | 5.21 | 0.00% | không đạt được | 0.0% |
| E1_pyyaml | 17.08 | 302 / 600 | 17.50 | 17.79 | 1.61% | 0.01 s | 49.7% |
| E2_packaging | 176.20 | 302 / 600 | 176.28 | 176.33 | 0.03% | 0.07 s | 49.7% |
| E3_databricks | 41.92 | 302 / 600 | 42.75 | 42.78 | 0.07% | 0.02 s | 49.7% |
| K1_trino | 4.74 | 600 / 600 | 5.15 | 5.15 | 0.00% | không đạt được | 0.0% |
| K2_tomlkit | 2.60 | 600 / 600 | 2.83 | 2.83 | 0.00% | không đạt được | 0.0% |

**Tổng (đo thật):** lần rút Gatekeeper 5326 so với B8 6600 (ít hơn 19.3%); thời gian Gatekeeper 1038.82 s so với B8 1049.49 s (ít hơn 1.02%). Chi phí cố định chiếm gần toàn bộ thời gian; tiết kiệm thời gian chỉ đáng kể ở target có lần rút đắt (spec-kit). Tiết kiệm không bao giờ vượt tỉ lệ lần rút giảm được, và bằng 0 ở các ô không có quyết định sớm.
