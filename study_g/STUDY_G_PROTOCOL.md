# Study G — họ skill thứ hai: so sánh với None bằng `is` (protocol)

**Trạng thái và thời điểm đóng băng:** ghi trong `config_study_g.json`, do workflow `study-g-freeze.yml` đặt; hash trong `FREEZE.json` (gồm cả skill mở rộng `gatekeeper_ext/`, bộ chạy `tools/run_study_g.py`, ví dụ replay và oracle).

## 1. Câu hỏi

Hai điểm yếu reviewer nêu: (1) chỉ một skill, một họ lỗi; (2) chưa có ô có hại với oracle **cấp 1** (test upstream khẳng định hành vi). Study G dùng skill thứ hai `none-identity` (`x == None` → `x is None`, `x != None` → `x is not None`) và hỏi: **Gatekeeper có từ chối một lần tái dùng có hại, được xác định bằng test upstream, mà B6-R (replay + fingerprint) chấp nhận không?**

## 2. Skill

- Phép biến đổi: `gatekeeper_ext/none_identity.py` (chỉ so sánh hai toán hạng; bọc ngoặc toán hạng không nguyên tử; test ngữ nghĩa trên 12 dạng biểu thức).
- **Ví dụ replay là một bản fix thật**: hera_pspec PR #485 (merge `f1235c7`) đổi `n_dlys == None` thành `n_dlys is None` trong `get_delays`. hera_pspec **không** thuộc tập đánh giá. B6-R của Study G vì vậy mạnh hơn B6-R của Study D/E (vốn dùng fixture tự dựng).

## 3. Chọn target (đã thực hiện trước khi áp skill)

Theo `SELECTION_RULES.md`; chi tiết trong `VETTING_DECISIONS.md`.

| Phía | Kết quả |
|---|---|
| Có lợi | **BLOCKED**: kiểm định đủ 29/29 ứng viên; không có test hành vi gắn với phép viết lại (dọn lint; `==` và `is` chỉ khác nhau khi `__eq__` bị ghi đè) |
| Có hại | **G1 pydal** (commit `bd5eb6d7`): `field == None` dựng truy vấn IS NULL; 31 dòng test upstream khẳng định ngữ nghĩa này (**cấp 1**). Loại: emmett (census không chạy được trong snapshot), promnesia, emfcamp, flex, các ứng dụng cần máy chủ CSDL |
| Đối chứng | hera_pspec bị loại (không cài được trên runner); các ứng viên khác không gọi được qua API công khai. Đối chứng còn lại: **scope `plain` của pydal** (truy vấn không có None, oracle vi sai) |

## 4. Ô và oracle

| Ô | Bộ sinh | Kỳ vọng |
|---|---|---|
| G1_pydal/null | 1–8 dòng, mỗi dòng NULL với xác suất 1/2; truy vấn `== None` count, `!= None` count, `db.t(1, a=None)`, `db(db.t).count()` | tính từ chính các dòng đã chèn (ngữ nghĩa IS NULL của test upstream) |
| G1_pydal/plain | 1–8 giá trị nguyên; truy vấn `== v`, `> v`, danh sách id | vi sai: không được đổi |

Kiểm tra chạy được (chỉ mã gốc, 3 lần): census VALID (115 test ổn định / 142; 27 test lỗi sẵn do mã Python 2 bị loại theo quy tắc), oracle 10/10 ở cả hai scope, 0 lỗi thực thi.

## 5. Thống kê và quy tắc

Giữ nguyên Study D/E: θ = 0,2, η = 0,05, báo động α = 0,05, n_max = 300, e-Holm FWER 0,1 trên **họ 2 ô** (cả hai ô đều binding được; quyết định trước mọi lần rút), seed từ drand sau thời điểm đóng băng.

**Phân tích thứ cấp đăng ký trước** (trên trace đã ghi): B6-S(k) với k ∈ {1, 5}; quy tắc futility (dừng khi cận trên CS 95% của lợi ích < θ).

## 6. Giả thuyết

- **H-G1:** G1/null: Gatekeeper REJECT_HARM.
- **H-G2:** G1/null: B6-R ADMIT (replay trên bản fix thật pass, fingerprint khớp).
- **H-G3:** census của pydal (115 test) có hay không phát hiện regression; **cả hai kết quả đều được báo cáo** (khác Study E, skill ở đây sửa cả `id_query`, nên census có thể bắt được).
- **H-G4:** G1/plain: không có lợi ích; Gatekeeper không admit.

## 7. Giới hạn đã biết trước

Một target, hai ô; không có ô có lợi; đối chứng chỉ ở trong cùng target. Đây là bằng chứng hẹp về một câu hỏi cụ thể (ô có hại với oracle cấp 1 trên họ skill thứ hai), không phải đánh giá toàn diện họ skill này.
