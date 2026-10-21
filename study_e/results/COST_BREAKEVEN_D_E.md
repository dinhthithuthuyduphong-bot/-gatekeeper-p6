# Điểm hòa vốn chi phí (từ dữ liệu đã đo, không chạy thêm)

| Target | Chi phí cố định F (s) | Giây / lần rút đo được | Lần rút GK / B8 | Tiết kiệm thời gian hiện tại | Giây/lần rút cần để tiết kiệm 10% | Tiết kiệm tối đa có thể (lần thử rất đắt) |
|---|---|---|---|---|---|---|
| C1_jsonschema | 4.1 | 1.44 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |
| C2_voluptuous | 2.0 | 0.19 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |
| D1_py_ecc | 740.7 | 2.59 ms | 410 / 600 | 0.07% | 0.57 s | 31.7% |
| D2_cerberus | 1.9 | 0.28 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |
| D3_speckit | 14.7 | 55.43 ms | 410 / 600 | 21.97% | 0.01 s | 31.7% |
| D5_pycubrid | 5.0 | 0.36 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |
| E1_pyyaml | 17.1 | 1.17 ms | 302 / 600 | 1.97% | 0.01 s | 49.7% |
| E2_packaging | 176.2 | 0.22 ms | 302 / 600 | 0.04% | 0.07 s | 49.7% |
| E3_databricks | 41.9 | 1.43 ms | 302 / 600 | 1.00% | 0.02 s | 49.7% |
| K1_trino | 4.7 | 0.69 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |
| K2_tomlkit | 2.6 | 0.38 ms | 600 / 600 | 0.00% | không đạt được | 0.0% |

Tổng: F = 1011 s; lần rút Gatekeeper 5326 so với B8 6600 (ít hơn 19.3%). Với chi phí mỗi lần rút đo được (vài ms), tiết kiệm thời gian gần bằng 0 ở hầu hết target; spec-kit (55 ms/lần rút) đã tiết kiệm khoảng 22%. Tiết kiệm không bao giờ vượt tỉ lệ lần rút giảm được (cột cuối), và bằng 0 ở các ô không có quyết định sớm (không có lợi ích, không có hại).
