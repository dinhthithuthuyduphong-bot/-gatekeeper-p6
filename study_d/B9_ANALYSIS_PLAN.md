# Kế hoạch phân tích B9 (đăng ký trước, trước mọi lượt gọi trả phí)

Tài liệu này được commit và gắn tag `b9-analysis-plan` **trước** lượt B9 `record` đầu tiên; thời điểm commit là bằng chứng đăng ký trước. Nó không sửa protocol Study D đã đóng băng.

## 1. Đơn vị và dữ liệu

- 6 target có lỗi (D1–D5, A1) × 2 model × 3 lần lặp = 36 lần sửa. C1, C2 không áp dụng (đã khai báo).
- Mỗi lần lặp có một **kết luận cuối** (`b9_verdict`): SUCCESS, HARMFUL, NO_EFFECT, NO_PATCH, CENSUS_INVALID.
- Oracle chấm điểm: đúng oracle rút mẫu đã đóng băng của Study D (300 lần rút mỗi scope, cùng seed) cộng cổng census.

## 2. Chỉ số chính (đã chốt)

| Chỉ số | Định nghĩa |
|---|---|
| Tỉ lệ thành công B9 | Số lần lặp SUCCESS / số lần lặp hợp lệ (không tính CENSUS_INVALID), theo target và tổng |
| Tỉ lệ có hại B9 | Số lần lặp HARMFUL / số lần lặp hợp lệ |
| Chi phí B9 | USD thực tế (từ `usage`), số lần gọi, số lần chạy kiểm tra công khai; tính trên mỗi lần SUCCESS |
| Kết quả "skill + Gatekeeper" | Theo Study D: ADMIT trên scope có lợi = thành công; chi phí = lần rút + census; 0 USD |

## 3. So sánh được khai báo trước

1. **Ở target Gatekeeper đã admit (D1, D3):** so tỉ lệ thành công và tỉ lệ có hại của B9 với tái dùng skill đã được admit.
2. **Ở target skill không áp dụng hoặc chưa đạt lợi ích (D2, D4, A1, D5):** B9 thành công ở đây được báo cáo là **bổ sung** cho skill, không phải "B9 thắng Gatekeeper". Hai cách giải quyết các tình huống khác nhau.
3. **Không công bố "người thắng" duy nhất.** Báo cáo bảng theo target. Chỉ được nói "B9 tốt hơn ở target X" khi B9 có tỉ lệ thành công cao hơn **và** tỉ lệ có hại bằng 0 ở target đó.
4. **Chi phí:** báo cáo hai đơn vị riêng (USD/lần gọi cho B9; lần rút/giây cho Gatekeeper). Không quy đổi về một tỉ giá chung.

## 4. Tính hợp lệ

- Chạy lại cùng cassette ở chế độ `replay` phải cho đúng các kết luận đã ghi. Nếu không, lần chạy đó được báo cáo là không tái lập được.
- Lần lặp bị dừng vì `BUDGET_CAP` được báo cáo riêng, không tính là NO_PATCH.
- Kết quả âm (B9 thành công nhiều hơn skill) được báo cáo nguyên trạng.
