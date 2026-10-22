# Study G — skill thứ hai: so sánh với None bằng `is` (BẢN NHÁP)

## 1. Vì sao chọn họ lỗi này

Reviewer coi "chỉ một skill, một họ lỗi" là điểm yếu lớn nhất. Họ lỗi E711 (`x == None` → `x is None`) có **cả ba loại ô một cách tự nhiên**, nên trả lời được nhiều câu hỏi cùng lúc:

| Loại ô | Khi nào xảy ra | Nguồn oracle khả dĩ |
|---|---|---|
| Có lợi | `x` có thể là đối tượng ghi đè `__eq__` (mảng numpy, proxy) khiến `== None` báo lỗi hoặc sai | test upstream của các bản fix "use `is None`" |
| **Có hại** | mã **cố ý** dùng `==` với None để sinh biểu thức: SQLAlchemy (`Model.col == None` → `IS NULL`), pandas, các DSL truy vấn | **test và tài liệu của chính thư viện** (ví dụ SQLAlchemy biên dịch `== None` thành `IS NULL`): có thể đạt **oracle cấp 1** |
| Vô hại | `x` là đối tượng thông thường | vi sai |

## 2. Những gì đã làm (0 đồng)

- Phép biến đổi `gatekeeper_ext/none_identity.py` (chỉ so sánh hai toán hạng, bỏ qua so sánh chuỗi), có test; đăng ký lúc chạy, **không sửa file nào đã đóng băng** của Study D/E/F.
- Công cụ quét áp dụng nhận `--skill` để quét bằng skill mới.

## 3. Những gì phải làm trước khi đóng băng

1. **Chốt nguồn skill trước khi chọn target:** một commit fix thật (PySStuBs hoặc commit công khai) làm ví dụ replay, để B6-R không chạy trên fixture tự dựng như ở Study D/E.
2. **Khung chọn target khai báo trước**, quét chỉ đọc, ghi lại mọi ứng viên bị loại.
3. **Oracle cấp 1 cho ô có hại:** ưu tiên repo dùng SQLAlchemy có bộ test chạy với SQLite trong bộ nhớ.
4. **Baseline mạnh hơn được đăng ký cùng lúc:** B6-R với ví dụ replay thật, fingerprint gồm cả phiên bản gói, và **B6-S(k)** (thêm k lần smoke test bằng đầu vào của scope).
5. **Quy tắc dừng khi vô vọng** được đăng ký như một phần của quy tắc chính (phân tích thứ cấp cho thấy nó không đổi quyết định nào ở D/E nhưng giảm 83–90% số lần rút).

## 4. Rủi ro

- Có thể không tìm được ô có hại với oracle cấp 1 chạy được (test cần cơ sở dữ liệu ngoài). Khi đó ghi `BLOCKED`, không hạ tiêu chuẩn.
- Bộ sinh cho "đối tượng ghi đè `__eq__`" phải được khai báo theo đúng API công khai của target, không tự chế đối tượng.
