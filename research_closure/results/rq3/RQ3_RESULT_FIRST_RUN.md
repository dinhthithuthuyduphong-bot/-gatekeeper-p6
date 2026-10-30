# RQ3, lượt chạy đầu (13 trên 16 target có kết quả; 3 target của Study G chạy lại sau P-A1)

| Target | Kỹ năng áp được | Viết tay phát hiện | G0 | G2 |
|---|---|---|---|---|
| A1_speckit_catalog | Không (như Study D) | | | |
| D4_openfeature | Không (như Study D) | | | |
| C1_jsonschema, C2_voluptuous, K1_trino, K2_tomlkit | Có | Không | Không | Không |
| D1_py_ecc | Có | Có (bool 164/200) | Không | **Có** |
| D5_pycubrid | Có | Có (bool 18/200) | Không | **Có** |
| E1_pyyaml, E2_packaging, E3_databricks | Có | Có | Có | Có |
| **D2_cerberus** | Có | **Không** | **Có** (24 đến 27/200) | **Có** (52 đến 56/200) |
| **D3_speckit** | Có | **Có** (bool 91/200) | Không | Không |
| G1_pydal, G2_emmett, K1_hera_pspec | Lỗi công cụ, chạy lại | | | |

**Đồng thuận phát hiện trên 11 target đo được:** G0 7/11 (0,64; khoảng Clopper–Pearson 95% 0,31 đến 0,89; kappa 0,29); **G2 9/11 (0,82; 0,48 đến 0,98; kappa 0,63)**; G0 hoặc G2 như G2. Chi phí model của G2: khoảng 0,05 USD.

**Hai ca bất đồng:**
- **D2_cerberus:** kỹ năng được áp vào `_validate_allowed` và `_validate_forbidden`, không phải hàm có lỗi gốc (`_validate_type_number`). Oracle viết tay chỉ kiểm tra vùng mà tác giả nhắm tới, nên không thấy gì; bộ sinh tự động gọi thẳng các hàm bị sửa và thấy hành vi đổi. Kỹ năng đã được áp **ra ngoài phạm vi dự định**, và oracle theo ý đồ tác giả bỏ sót tác dụng phụ đó: đúng vấn đề "phạm vi trước khi tái sử dụng" của bài gốc.
- **D3_speckit:** hàm bị sửa là một lệnh CLI cần dựng dự án tạm; oracle viết tay dựng đủ môi trường, còn gọi thẳng hàm thì lần nào cũng lỗi giống nhau. Điểm mù đã biết của cách gọi thẳng: hàm cần trạng thái hoặc môi trường.

Kết luận cuối cùng chờ ba target của Study G.
