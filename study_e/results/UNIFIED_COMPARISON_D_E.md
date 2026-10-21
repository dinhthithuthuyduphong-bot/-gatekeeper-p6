# So sánh theo chuẩn chung: trạng thái cuối của mã, cùng oracle, cùng hàm kết luận

| Target | Skill + Gatekeeper | Skill + B6-R | Skill + B8 | B9 (DeepSeek / Gemini) |
|---|---|---|---|---|
| A1_speckit_catalog | NO_PATCH | NO_PATCH | NO_PATCH | chưa chạy / không áp dụng |
| C1_jsonschema | NO_PATCH | NO_EFFECT | NO_EFFECT | chưa chạy / không áp dụng |
| C2_voluptuous | NO_PATCH | NO_EFFECT | NO_EFFECT | chưa chạy / không áp dụng |
| D1_py_ecc | SUCCESS | SUCCESS | SUCCESS | chưa chạy / không áp dụng |
| D2_cerberus | NO_PATCH | NO_EFFECT | NO_EFFECT | chưa chạy / không áp dụng |
| D3_speckit | SUCCESS | SUCCESS | SUCCESS | chưa chạy / không áp dụng |
| D4_openfeature | NO_PATCH | NO_PATCH | NO_PATCH | chưa chạy / không áp dụng |
| D5_pycubrid | NO_PATCH | SUCCESS | SUCCESS | chưa chạy / không áp dụng |
| E1_pyyaml | NO_PATCH | HARMFUL | NO_EFFECT | chưa chạy / không áp dụng |
| E2_packaging | NO_PATCH | HARMFUL | NO_EFFECT | chưa chạy / không áp dụng |
| E3_databricks | NO_PATCH | HARMFUL | NO_EFFECT | chưa chạy / không áp dụng |
| K1_trino | NO_PATCH | NO_EFFECT | NO_EFFECT | chưa chạy / không áp dụng |
| K2_tomlkit | NO_PATCH | NO_EFFECT | NO_EFFECT | chưa chạy / không áp dụng |

SUCCESS = có lợi ở scope lỗi, không hại ở đâu; HARMFUL = có hại ở bất kỳ scope nào hoặc census; NO_EFFECT = có thay đổi nhưng không đo được lợi ích; NO_PATCH = không triển khai gì (mã giữ nguyên).
