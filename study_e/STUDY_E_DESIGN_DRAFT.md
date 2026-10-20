# Study E — đối chứng có hại (BẢN NHÁP, chưa đóng băng)

## 1. Vì sao cần

Study D không có ô nào có hại, nên câu hỏi an toàn chính — **Gatekeeper có từ chối một lần tái dùng có hại mà B6-R (replay + fingerprint) chấp nhận không** — chưa được kiểm tra trên dữ liệu thật. Study E chỉ nhắm vào câu hỏi này, dùng **đúng skill đã đóng băng** của Study D, không sửa skill.

## 2. Ba lớp ô

| Lớp | Định nghĩa | Ứng viên ban đầu (từ khảo sát) |
|---|---|---|
| HARM | Skill khớp ở đường xử lý mà target **cố ý** nhận bool qua kiểm tra int | PyHive `ParamEscaper.escape_item`; databricks-sql ≤ 2.9.3; cantools (thăm dò) |
| MIXED | Cùng hàm vừa có lỗi bool-as-int, vừa có hành vi bool-as-int được chủ đích | packaging `Version.from_parts` (#1425); python-memcached (#75, bản trước khi chuyển sang `type()`) |
| CONTROL | Skill không khớp, hoặc khớp nhưng không đổi hành vi | trino-python-client, redis-py, pymemcache, abseil-py, python-memcached (master) |

Danh sách được chốt **sau** lượt quét áp dụng (`study-e-scan.yml`, chỉ đọc mã) và **trước** khi chạy skill trên bất kỳ target nào.

## 3. Nguồn oracle theo cấp (báo cáo riêng từng cấp, không gộp)

| Cấp | Nguồn kỳ vọng "bool được chấp nhận" |
|---|---|
| 1 | Test upstream khẳng định bool đi qua đường đó (công cụ quét tìm test có `True/False` tham chiếu đúng hàm) |
| 2 | Lời maintainer trong issue/PR (ví dụ voluptuous #443, packaging #1425, python-memcached #75) |
| 3 | Hành vi hiện hữu được ghi nhận (characterization), không có tài liệu khẳng định |

Ô cấp 3 chỉ được dùng để minh hoạ, không dùng làm bằng chứng chính.

## 4. Quy tắc chọn target (khai báo trước)

Một ứng viên vào Study E khi: (a) lượt quét cho thấy skill khớp trong một hàm gọi được qua API công khai; (b) có ít nhất một nguồn oracle cấp 1 hoặc cấp 2; (c) bộ test chạy được và pin được commit. Mọi ứng viên bị loại được ghi lại cùng lý do (chống chọn lọc).

## 5. Giả thuyết

- **H-E1:** ở ô HARM, Gatekeeper dừng với REJECT_HARM.
- **H-E2:** ở cùng các ô đó, B6-R ADMIT (replay ở nguồn pass, fingerprint khớp).
- **H-E3:** ở ô MIXED, báo động tác hại vẫn kích hoạt dù có lợi ích ở một phần đầu vào.

## 6. Thiết kế thống kê

Giữ nguyên Study D: bộ sinh i.i.d. theo scope, census 3 baseline, θ = 0,2, η = 0,05, e-Holm FWER 0,1 trên các ô của Study E (họ ô riêng), seed từ drand sau thời điểm đóng băng Study E.

## 7. Rủi ro đã biết

- Có thể không đủ ứng viên cấp 1–2. Khi đó Study E được báo cáo là "không đủ điều kiện", **không** hạ tiêu chuẩn để có kết quả.
- PyHive ít được bảo trì; môi trường có thể cần pin `future` và phiên bản Python cũ.
