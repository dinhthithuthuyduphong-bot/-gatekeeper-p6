# Study G v1 — họ skill thứ hai (`== None` → `is None`): kết quả

**Loại bằng chứng:** prospective, protocol đóng băng trước khi chạy (tag `study-g-freeze`), seed drand vòng 33289163. Một target (pydal, commit `bd5eb6d7`), hai ô. Không có lỗi kỹ thuật, không có amendment.

## 1. Kết quả

| Ô | Skill áp dụng | Nhãn thật (300 lần rút + census) | B2 | B6-R | B8 | Gatekeeper |
|---|---|---|---|---|---|---|
| G1/null | 7 vị trí (`id_query` ×2, `where` ×2, `belongs`, `parse` ×2) | **Có hại**: 81/300 lần rút; **21 test pydal fail mới** | ADMIT | **ADMIT** | REJECT | **REJECT_HARM** |
| G1/plain | như trên | Không đổi ở lần rút; census có regression | ADMIT | ADMIT | REJECT | REJECT_HARM (do census) |

**Cả bốn giả thuyết đã đăng ký được xác nhận:**
- **H-G1:** Gatekeeper REJECT_HARM ở ô `null`.
- **H-G2:** B6-R ADMIT, dù replay chạy trên **bản fix thật** (hera_pspec PR #485).
- **H-G3:** **census bắt được** tác hại (21 test fail mới trên 115 test ổn định), khác với Study E.
- **H-G4:** ô `plain` không có lợi ích và không được admit.

## 2. Cơ chế tác hại

Tái tạo các lần rút bằng seed cho thấy tác hại **chỉ** nằm ở truy vấn `db(db.t).count()` (81/81). Skill đổi `table._id != None` trong `id_query` thành `table._id is not None`, tức một biểu thức truy vấn "mọi dòng có id" thành hằng `True`. Các truy vấn `== None` / `!= None` mà người dùng viết (0/62, 0/82) và tra cứu `db.t(1, a=None)` (0/75) không bị ảnh hưởng.

## 3. Hai lớp chặn độc lập

- **Census** (bộ test của chính pydal): phát hiện ngay, chặn mọi scope của target.
- **E-process báo động** trên scope `null`: tự nó kích hoạt ở **lần rút 103** (tác hại 27% đầu vào; lần rút có hại đầu tiên là lần thứ 7).
- **Baseline B6-S không có census** (phân tích thứ cấp đã đăng ký): với k = 1 và k = 5 lần smoke test, **không thấy tác hại** và sẽ admit; với k = 10 mới thấy. Có census thì B6-S cũng từ chối.

Khác với Study E (tác hại ở 87–100% đầu vào, smoke test 1 lần là đủ), ở đây tác hại chỉ chiếm 27% và tập trung ở một loại truy vấn. Smoke test ít lần không còn đủ; census hoặc e-process theo scope mới bắt được.

## 4. Chi phí

Lần rút: Gatekeeper 403, B8 600.

## 5. Giới hạn

Một target, hai ô; không có ô có lợi (phía có lợi BLOCKED sau khi kiểm định 29/29 ứng viên); đối chứng chỉ nằm trong cùng target.
