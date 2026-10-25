# Sửa run 40173786064 — khôi phục file thiếu, không bỏ test

Run dừng ở audit: **135 tests, 132 pass, 3 ERROR** vì thiếu
`study_k/results/local-20261025-clean/RESULT.json`. Quét source, baseline
Pydantic và cost đều SKIPPED; chưa có kết quả nghiên cứu mới.

Main `a8026c9ffce247f2d253b4188a50156f506cb3af` có 442 file khớp gói đã gửi
và thiếu 23 file Study K. Danh sách đầy đủ: `MISSING_FILES.txt`. Bản chẩn đoán:
`main_update/next_evidence/CI_FIX_40173786064.md`.

## Trong ZIP này có gì?

- Chỉ **4 file repository mới/sửa** trong `main_update/`: inventory, checker,
  một lệnh preflight thêm vào closure audit, và báo cáo lỗi.
- Helper và hướng dẫn khôi phục 23 file **từ ZIP FINAL của bạn**. Không nén lại
  các raw log/kết quả cũ theo yêu cầu. Không tự tạo RESULT hoặc sửa expected test.
- `CI_FIX_MANIFEST.json` có checksum nguồn và đích; `PACKAGE_CHECKS/` chỉ là
  kiểm tra việc đọc/hash/sao chép file, không phải kết quả chạy lại CI.

**Chỉ upload 4 file mới là chưa đủ:** phải khôi phục 23 file cũ cùng lúc.

## Cách khuyến nghị: dùng bản clone main

Giải nén gói sửa ra ngoài thư mục repo. Giữ file
`Gatekeeper_Final_ZeroCost_20261025.zip` gốc làm nguồn; không chạy lại helper
APPLY_UPDATE của FINAL và không ghi đè toàn bộ FINAL lên NEXT.

Thay đường dẫn bên dưới bằng đường dẫn thật:

```bash
git switch main
git pull --ff-only
python /duong-dan/goi-sua/APPLY_CI_FIX.py --repo . --final-zip /duong-dan/Gatekeeper_Final_ZeroCost_20261025.zip --check-only
python /duong-dan/goi-sua/APPLY_CI_FIX.py --repo . --final-zip /duong-dan/Gatekeeper_Final_ZeroCost_20261025.zip
git diff --stat
git status --short
git add --pathspec-from-file=/duong-dan/goi-sua/UPDATE_PATHS.txt
git commit -m "Restore missing Study K evidence and check inventory before tests"
git push origin main
```

Bọc đường dẫn trong dấu ngoặc kép nếu có dấu cách. Nếu đã giải nén FINAL,
thay `--final-zip ...` bằng `--final-dir /duong-dan/thu-muc-FINAL`; thư mục này
phải chứa `main_update/`.

Helper chỉ sao chép file đúng hash, yêu cầu main sạch, từ chối ghi đè nội dung
khác, không compile/test, không commit/push hoặc gọi API. Trên đúng snapshot
đã kiểm tra sẽ có **27 đường dẫn cập nhật: 23 khôi phục + 4 mới/sửa**.
`RESTORATION_RECEIPT.json` được lưu cạnh helper sau khi chép.

## Nếu cập nhật bằng giao diện GitHub

1. Giải nén FINAL. Lấy đúng 23 file trong `MISSING_FILES.txt` từ `main_update/`
   của FINAL, giữ nguyên đường dẫn khi upload vào root repo.
2. Thêm/thay 4 file trong `main_update/` của gói sửa này, cũng giữ nguyên đường dẫn.
3. Commit vào main. Đừng upload ZIP thành một file thay cho các file thành phần.

23 file chia thành 11 file ở `study_k/results/local-20261025-clean/` và 12 file
ở `study_k/results/pilot_attempts/`. Có thể đối chiếu trực tiếp checksum trong
manifest. Không sửa nội dung log/JSON hoặc đổi tên RESULT thành chữ thường.

## Chạy lại đúng commit mới

GitHub → Actions → **Gatekeeper next evidence - zero-cost** → **Run workflow**
→ branch **main** → bật **run_cost = true**.

**Không dùng Re-run jobs của run 40173786064:** thao tác đó dùng commit cũ.
Preflight mới sẽ tạo `EVIDENCE_INVENTORY.json`; khi đủ nguyên vẹn phải có
`EVIDENCE_INVENTORY_OK`, 38/38 file khớp. Unit suite và các raw audit vẫn chạy
đầy đủ sau đó. Chỉ khi audit thành công mới đến scout, Pydantic và cost.

Gửi lại URL run mới và artifact **next-evidence-return-a1** (hoặc attempt mới
nhất), kể cả khi lỗi. Gói này không có kết quả CI mới để khẳng định toàn bộ
workflow đã xanh. B9 tiếp tục HOLD; không cần API key/GCP secret.
