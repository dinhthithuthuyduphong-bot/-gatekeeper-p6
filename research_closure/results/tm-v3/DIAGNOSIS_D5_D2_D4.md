# Chẩn đoán từ bằng chứng thô của harness test-mutation (phát triển, 26/10/2026)

Nguồn: artifact D5, D2, D4 chạy bằng harness đã thêm lưu bằng chứng. Các instance này đã lộ kết quả, **không dùng làm bằng chứng xác nhận**. Không gộp số liệu harness cũ và harness v3.

## Kết quả đã quan sát

| Target | Biên dịch / đủ cặp | Nguyên nhân thật (từ bằng chứng thô) |
|---|---|---|
| D5 pycubrid | 200 / **25** | pytest in `stopping after 25 failures`: cấu hình riêng của repo dừng lượt chạy, nên 175 mutant không được thực thi. Cả 25 mutant đã chạy đều **thất bại ở cả ba arm** vì giá trị kỳ vọng trong `assert` bị đột biến (ví dụ `'NUMBER' == 'NUMBERx'`) |
| D2 Cerberus | 199 / **3** | pytest in `stopping after 2 failures`: cùng cơ chế. File `cerberus/tests/tests.py` đã được tìm thấy (sửa discovery hoạt động) |
| D4 openfeature | 200 / 200 | Đủ cặp. Draw **59 là draw duy nhất** mà bản gốc khác bản fix, và cũng là draw duy nhất khác nhau giữa hai lần chạy cùng một arm: cả hai đều thất bại giống hệt nhau, chỉ khác `<Mock id='…'>`. **Tỉ lệ kích hoạt thật là 0/200**; con số 0,5% là nhiễu đo lường |

## Ba lỗi đo lường (harness v3 chỉ sửa các lỗi này)

1. `--maxfail=0` được thêm vào lệnh pytest (sau `addopts` của repo); phát hiện và từ chối lượt chạy bị cắt (`stopping after N failures`).
2. Chuẩn hoá thông báo lỗi che `id='<số>'` của `unittest.mock` (id ngắn như `id=7` vẫn được giữ vì có thể là giá trị thật).
3. Ghi thêm `common_failure_fraction`: tỉ lệ draw mà mọi arm đều chỉ thất bại, tức draw không phân biệt được các arm.

## Điều v3 **không** sửa (giới hạn đã biết, ghi trước khi chạy lại)

- Đột biến vẫn có thể rơi vào giá trị kỳ vọng của `assert`; phân phối đột biến giữ nguyên để so sánh được với lần trước. Nếu `common_failure_fraction` cao, thiết kế "chỉ đột biến đầu vào" là một phiên bản khác (v4) và cần được đăng ký riêng.
- D1 timeout chưa được xử lý: tăng timeout không giải quyết bài toán chi phí.
- Đây vẫn là bằng chứng phát triển, không phải đánh giá tiến cứu.
