# Study E — đối chứng có hại (protocol)

**Trạng thái và thời điểm đóng băng:** ghi trong `config_study_e.json`, do workflow `study-e-freeze.yml` đặt; hash trong `FREEZE.json`.

## 1. Câu hỏi

Study D không có ô nào có hại, nên câu hỏi an toàn chính chưa được kiểm tra: **Gatekeeper có từ chối một lần tái dùng có hại mà B6-R (bind + replay + fingerprint) chấp nhận không?** Study E dùng **đúng skill đã đóng băng của Study D**, không sửa.

## 2. Khung chọn target và kết quả chọn

Nguồn: lượt quét áp dụng chỉ đọc trên 15 ứng viên (`study-e-scan.yml`, vòng 1 và vòng 2 có mã nguồn hàm). Quy tắc khai báo trước: skill khớp ở hàm gọi được qua API công khai; có nguồn oracle; bộ test chạy được; pin được commit.

| Mã | Target (commit) | Lớp | Nguồn oracle | Vai trò trong phân tích |
|---|---|---|---|---|
| E1 | pyyaml `f5e4504a` — `SafeRepresenter.ignore_aliases` | HARM | **Cấp 2b:** ý đồ tường minh trong mã (bool được liệt kê trong tuple các kiểu không tạo alias) | Chính |
| E2 | packaging `1a62a26a` — `_validate_epoch/_release/_post/_dev` qua `Version.from_parts` | MIXED (tranh cãi) | **Cấp 2:** maintainer đóng PR #1425 ("overly defensive"); CHANGELOG lại chặn bool ở pylock | Chính |
| E3 | databricks-sql v2.9.3 `a737ef31` — `ParamEscaper.escape_item` | HARM | **Cấp 3:** chỉ là hành vi hiện hữu | Chỉ minh hoạ |
| K1 | trino-python-client `74c6156e` — `_format_prepared_param` | CONTROL | bool xử lý trước nhánh int | Đối chứng |
| K2 | tomlkit `eddd27e4` — `item` | CONTROL | bool xử lý trước nhánh int | Đối chứng |

**Ứng viên bị loại và lý do:** PyHive (test cần máy chủ Hive/Presto, census không chạy được); redis-py (loại sau lượt kiểm tra chạy được, chưa áp skill: bộ test cần máy chủ Redis); cantools (không có nguồn oracle cho bool); python-memcached, cbor2, bencode.py (skill không khớp); pymemcache, abseil-py, msgpack, PyMySQL, pyyaml `add_path_resolver` (không có đường bool có chủ đích hoặc không có nguồn oracle).

**Ghi chú minh bạch:** cấp 2b được **thêm sau khi xem mã nguồn ứng viên và trước khi đóng băng**. Bản nháp ban đầu chỉ có cấp 1 (test upstream), cấp 2 (lời maintainer trong issue/PR), cấp 3 (hành vi hiện hữu). Kết quả được báo cáo riêng theo từng cấp.

**Kiểm tra chạy được trước đóng băng** (workflow `study-e-baseline.yml`, chỉ mã gốc, không áp skill): oracle chạy đúng ở cả 6 target; census VALID ở pyyaml (1.287 test), databricks (130), tomlkit (106); packaging và trino chỉ thiếu thư viện test (`pretend`, `httpretty`) và được bổ sung; redis-py bị loại.

## 3. Oracle

- **E1:** `yaml.dump` dữ liệu lặp lại cùng một giá trị bool không được chứa `&` hoặc `*`, và phải load lại bằng dữ liệu gốc. Scope int: vi sai.
- **E2:** theo lập trường maintainer ở #1425, đầu vào nào `Version.from_parts` đang chấp nhận thì vẫn được chấp nhận. Scope int: vi sai.
- **E3:** `escape_item(True/False)` vẫn trả giá trị, không ném lỗi. Scope int: vi sai.
- **K1–K2:** vi sai ở cả hai scope; mọi thay đổi khi có skill đều là regression.

## 4. Giả thuyết

- **H-E1:** E1/bool: Gatekeeper REJECT_HARM.
- **H-E2:** E1/bool: B6-R ADMIT (replay ở ví dụ nguồn pass, fingerprint MATCH).
- **H-E3:** E2/bool: báo động tác hại kích hoạt.
- **H-E4:** K1–K2: không có thay đổi hành vi; Gatekeeper không admit (không có lợi ích).

## 5. Thống kê

Giữ nguyên Study D: bộ sinh i.i.d. theo scope, census 3 baseline (INVALID nếu < 5 test ổn định), θ = 0,2, η = 0,05, báo động tác hại α = 0,05, e-Holm FWER 0,1 trên **10 ô của Study E** (họ ô riêng, không gộp với Study D), n_max = 300, seed từ drand sau thời điểm đóng băng Study E. Bộ chạy và module quyết định là đúng các file đã đóng băng của Study D, không sửa.

## 6. Báo cáo

Theo từng ô và từng cấp oracle; không gộp cấp 3 với cấp 2/2b. Nếu E1 và E2 cùng bị census INVALID, Study E được báo cáo là "không đủ điều kiện", không thay target.
