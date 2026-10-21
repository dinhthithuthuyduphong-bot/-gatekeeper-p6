# Truy vết nguồn của skill và giới hạn của B6-R (ghi sau khi đóng băng D/E)

## Chuỗi truy vết

| Mắt xích | Nội dung | Mức xác minh |
|---|---|---|
| Mẫu nguồn | Họ lỗi PySStuBs "More Specific If", skill `add-negative-type-guard` (tuần 3): thêm `and not isinstance(x, bool)` vào kiểm tra `isinstance(x, int)` | Ghi trong báo cáo tuần 3–4; **commit PySStuBs cụ thể không được lưu lại** |
| Cách sửa (π) | `gatekeeper_lite/transforms.py::NegativeTypeGuard(base="int", excluded="bool")`, đóng băng trong FREEZE của Study D và E | Đã băm |
| Ví dụ replay (P) | `demo/sources/status_before.py` → `status_after.py`: **fixture 4 dòng tự dựng**, mô phỏng đúng mẫu trên | Hash trong `SUPPLEMENTARY_MANIFEST.json` (không nằm trong FREEZE gốc) |
| Hợp đồng môi trường (D) | `python >= 3.8` | Đã băm |

## Hệ quả cho B6-R

- B6-R của nghiên cứu là **bản tái dựng yếu hơn B6 của paper** ở phía nguồn: replay chạy trên fixture tự dựng, không trên commit và bộ test của dự án nguồn; fingerprint chỉ so phiên bản Python.
- **Quyết định của B6-R không phụ thuộc vào việc ví dụ replay là fixture hay commit thật.** Skill tái tạo đúng cách sửa trên mọi ví dụ thuộc mẫu này, nên replay pass trong cả hai trường hợp; quyết định do bước bind và fingerprint quyết định. Vì vậy các kết quả "B6-R admit 3/3 ô có hại" ở Study E không phải là hệ quả của replay yếu.
- **Không được** trình bày B6-R như một bản tái hiện đầy đủ B6 của paper. Trình bày đúng: "replay trên ví dụ nguồn của skill + so khớp fingerprint môi trường".
- Cải thiện khả dĩ (0 đồng, chưa làm): replay trên một fix thật **không thuộc** tập đánh giá cùng mẫu (ví dụ pygeoapi PR #2419). Đây chỉ là phân tích bổ sung, không thay kết quả đã đóng băng.
