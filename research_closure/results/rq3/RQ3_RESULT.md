# RQ3: kết quả cuối cùng (theo `research_closure/results/RQ3_PLAN.md`)

16 target đánh giá của Study D, E, G; **14 đo được**; 2 target mà kỹ năng không áp được (A1_speckit_catalog, D4_openfeature), **giống hệt** kết luận "OUT_OF_SCOPE" của Study D. Ba target của Study G được chạy lại sau amendment P-A1 (lỗi công cụ, trước khi đo).

| Bộ sinh | Đồng thuận phát hiện với bộ sinh viết tay | Khoảng Clopper–Pearson 95% | Kappa (Cohen 1960) | Viết tay thấy, bộ sinh bỏ sót | Bộ sinh thấy, viết tay bỏ sót |
|---|---|---|---|---|---|
| G0 (theo chữ ký) | 8/14 = 0,57 | 0,29 đến 0,82 | 0,19 | 5 | 1 |
| **G2 (model viết)** | **11/14 = 0,79** | 0,49 đến 0,95 | **0,57** | 2 | 1 |
| G0 hoặc G2 | 11/14 = 0,79 | 0,49 đến 0,95 | 0,57 | 2 | 1 |

| Target | Viết tay | G0 | G2 |
|---|---|---|---|
| C1, C2, K1_trino, K2_tomlkit, K1_hera_pspec | Không | Không | Không |
| E1, E2, E3 | Có | Có | Có |
| D1_py_ecc, D5_pycubrid, G1_pydal | Có | Không | **Có** |
| **D2_cerberus** | **Không** | Có | Có |
| D3_speckit, G2_emmett | **Có** | Không | Không |

## Diễn giải

1. **Bộ sinh do model viết đồng thuận tốt hơn hẳn bộ sinh theo chữ ký** (kappa 0,57 so với 0,19): cách sinh theo chữ ký bỏ sót 5 trong 8 target có thay đổi. Điều này ủng hộ việc Study P dùng cả hai nguồn và báo cáo phân tầng.
2. **D2_cerberus: kỹ năng bị áp ra ngoài phạm vi dự định.** Kỹ năng sửa `_validate_allowed` và `_validate_forbidden`, không phải hàm có lỗi gốc (`_validate_type_number`); oracle viết tay chỉ kiểm tra vùng mà tác giả nhắm tới nên không thấy gì, còn bộ sinh tự động thấy hành vi đổi trên 24 đến 56/200 đầu vào. Đây là bằng chứng trực tiếp cho vấn đề "phạm vi trước khi tái sử dụng" của bài gốc: **một oracle viết theo ý đồ tác giả không thấy được tác dụng phụ ngoài ý đồ.**
3. **Điểm mù của cách gọi thẳng hàm:** D3_speckit (lệnh CLI cần dựng dự án tạm) và G2_emmett, nơi oracle viết tay dựng đủ ngữ cảnh mà lời gọi thẳng không có.
4. **Giới hạn:** 14 target, hai họ kỹ năng; khoảng tin cậy rộng; thước đo nhị phân vì hai loại bộ sinh có không gian đầu vào khác nhau.
