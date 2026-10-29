# Lượt thử P0 và P1 của Study N (trên instance phát triển)

**Mục đích:** biết chuỗi đo có chạy trọn được không, và model mạnh có đáng dùng không, **trước khi** đóng băng cấu hình sinh patch của cohort (amendment N-A1). Chạy trên **57 instance phát triển** (nửa A\* đã lộ của Study M), **không bao giờ** trên cohort. Quy tắc nằm trong `study_n/STUDY_N_PROTOCOL.md` mục 6 (đã băm).

| | P0 | P1 |
|---|---|---|
| Model | `vertex-gemini-flash` | `vertex-gemini-argon` |
| Instance, lần lặp | 10 instance (mỗi repo tối đa một, theo vị trí), 2 lần | 6 instance đầu của P0, 1 lần |
| Chi tối đa | 2 USD | 3 USD |
| Điều kiện chạy | không | file `research_closure/pilot/P0_RESULT.json` đã commit với `pilot_pass: true` |
| Trần đầu ra | 8.000 token | 32.768 token |
| Đạt khi | (a) ít nhất 8 instance chạy trọn chuỗi, (b) có ít nhất 1 patch plausible | báo cáo: tỉ lệ plausible, token suy luận, tỉ lệ bị cắt |

**Chuỗi đo cho mỗi instance:** lấy văn bản issue (issue được PR liên kết, nếu không thì chỉ tiêu đề PR) → dựng hai snapshot từ SHA → cài một venv → đo draw một lần (đọc nền, lọc độ phủ, bản gốc và bản fix) → sinh patch → gán nhãn bằng test ẩn → chấm trên cùng draw → áp các cổng.

## Điều cần biết khi đọc kết quả

- **Cách tính chi theo trường hợp xấu nhất.** Trước mỗi lời gọi, giới hạn chi cộng trần đầu ra và đầu vào tính bằng số byte của lời nhắc. Với lời nhắc lớn, giới hạn 0,20 USD mỗi instance có thể dừng sớm (`BUDGET_CAP`). Cột "Stopped by the spend guard" cho thấy điều này, và nó **không phải** lỗi của model.
- **So sánh công bằng giữa P0 và P1:** model mạnh có thể bị dừng sau ít lời gọi hơn. Vì vậy báo cáo cả "lời gọi đầu đã qua kiểm tra hiển thị", không chỉ tỉ lệ plausible chung.
- **Giá Flash tăng gấp đôi từ 1/1/2027** (lên 1,5 và 7,5 USD mỗi triệu token); giá Argon khuyến mãi (2 và 10) tới 30/11/2026, rồi 4 và 20.
- Các số này thuộc instance **đã lộ**; chúng quyết định cấu hình, không phải bằng chứng của bất kỳ cổng nào.

## Sau P0

1. Tổng hợp: `python tools/pilot_summary.py DIR OUT --stage P0 --planned 10`.
2. Nếu đạt, commit `P0_RESULT.json` vào `research_closure/pilot/` (đó là điều kiện mở P1).
3. Quyết định về Argon theo quy tắc ở mục 6 của giao thức, sau P1.
