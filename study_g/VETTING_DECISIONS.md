# Study G — quyết định sau kiểm định (trước khi áp skill lên bất kỳ target nào)

## Phía có lợi: BLOCKED

Đã kiểm định **toàn bộ 29 ứng viên** theo thứ tự tìm kiếm (12 ở vòng 1, 17 ở vòng 2; 6 commit trùng ở các fork bị bỏ). Không ứng viên nào có test **hành vi** gắn với phép viết lại `== None` → `is None`:

| Ứng viên | Kết quả công cụ | Lý do không dùng |
|---|---|---|
| 26 ứng viên | NOT_ELIGIBLE | không có test fail trước / pass sau (dọn lint) |
| proov-km-waechter-fix (2 fork, cùng test) | ELIGIBLE (2 F→P) | F→P kiểm tra KeyError khi thiếu khoá, được sửa bằng thay đổi khác trong cùng commit; chỗ `path == None` dùng giá trị thông thường |
| quantammsim | ELIGIBLE (25 F→P) | test liên quan duy nhất (`TestE711NoneComparison`) kiểm tra **mã nguồn**, không kiểm tra hành vi; các F→P khác thuộc lỗi lint khác |

**Diễn giải:** `== None` và `is None` chỉ khác nhau khi `__eq__` bị ghi đè; các bản fix E711 công khai gần như luôn là dọn phong cách. Đây là kết quả của nghiên cứu, không phải lý do để hạ tiêu chuẩn.

## Phía có hại

| Target | Trạng thái | Bằng chứng |
|---|---|---|
| **G1 pydal** | **Sẵn sàng** | 31 dòng test upstream dùng `== None` (cấp 1); census VALID (115 test ổn định / 142); oracle đúng 10/10 trên mã gốc ở cả hai scope |
| emmett | Đang viết oracle | chạy được (146 test); 1 dòng test upstream; cần mã test ORM để viết oracle |
| promnesia | **Loại** | lỗi thu thập test cả hai lần (một lần thử lại đã dùng) |
| emfcamp | **Loại** | không cài được |
| flex, meerkat, các ứng dụng cần PostgreSQL/MongoDB | **Loại** | xem `harm_candidates.json` |

## Đối chứng

Commit **trước** các bản dọn lint đã chạy được test (hera_pspec, pyelftools, atomic_notes, ndsolver): skill làm lại đúng việc dọn lint trên đối tượng thông thường; kỳ vọng không đổi hành vi. Chọn sau lượt quét áp dụng (`candidates_control_scan.json`).
