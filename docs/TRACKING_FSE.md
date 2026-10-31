# Theo dõi tiến độ, đối chiếu với bài FSE-2027-13

**Bài gốc:** *Scope before Reuse: Risk-Controlled Admission of Learned Coding Skills* (FSE-2027-13). Mọi số headline trong bài là **projected** ([PAPER_EXPECTATION_AUDIT](../research_closure/PAPER_EXPECTATION_AUDIT.md)). File này chỉ ghi những gì đã **đo** trong repo, kèm đường dẫn tới bằng chứng.

Cập nhật lần cuối: **31/10/2026** (sau khi đối chiếu PDF và sắp xếp lại repo). Nhật ký đầy đủ: [PROCESS_LOG](PROCESS_LOG.md). Quy ước trạng thái: ✅ xong · 🔄 đang chạy · ⏳ chưa làm · ❌ kết quả âm (đã báo cáo) · ⛔ bị khoá.

---

## 1. Khung hiện tại (đã chốt)

Đối tượng nghiên cứu đã chuyển từ "kỹ năng học được" sang **chấp nhận một thay đổi mã vào một phạm vi**. Luận văn giữ tựa "Scope before Reuse" ([ALIGNMENT_WITH_FSE](../research_closure/results/ALIGNMENT_WITH_FSE.md)).

- **Phần 1, kỹ năng** (Study D đến H): kết quả âm.
- **Phần 2, thay đổi mã** (Study M đến Q): Study P đo trên patch LLM; RQ5 cho thấy oracle so khác biệt "ngây thơ" phóng đại tỉ lệ hồi quy; **Study Q** kiểm định lại kết luận này trên SWE-bench Verified.
- **Cầu nối:** RQ3 (bộ sinh tự động so với bộ sinh viết tay, chạy trên các target của bài gốc).

## 2. Đối chiếu từng kỳ vọng của bài FSE

| # | Kỳ vọng / khẳng định của bài FSE | Study | Trạng thái | Bằng chứng hiện có |
|---|---|---|---|---|
| E1 | Tác hại một phần phổ biến khi tái sử dụng kỹ năng | D đến H | ❌ | 12 target thật, 0/2.400 khác biệt; cổng đơn giản là đủ |
| E2 | Gatekeeper mạnh hơn cổng đơn giản | Đồ thị pha, PP0, Study P (H3) | ❌ về công suất | Kiểm định cỡ mẫu cố định an toàn như Gatekeeper và mạnh hơn; ở Study P hai cổng có cùng tỉ lệ admit (0,898); H3 không kiểm định được vì P4 không đạt ([P_RESULT](../research_closure/results/study_p/P_RESULT.md)). Giữ lại như một **tính chất**: hợp lệ khi dừng tuỳ ý, dừng sớm |
| E3 | Cổng có kiểm soát rủi ro hơn census / smoke test | Study P | ✅ | Census admit 16/16 patch có θ̂ > 5%, smoke 20 admit 2/16; cổng thống kê admit 0/16 |
| E4 | Oracle hành vi đo được tác hại | N, P | ✅ (mức hàm) | Oracle mức test dùng được 8/107; oracle mức hàm dùng được 54,3% số ELIGIBLE (Study P) |
| E5 | Tác hại một phần tồn tại trong thay đổi mã thật | P, RQ5 | ⚠️ thu hẹp | Kết quả đăng ký 16/205 = 7,8%; sau RQ5, hồi quy theo hợp đồng chỉ 0,5% đến 2,9% ([RQ5_RESULT](../research_closure/results/rq5/RQ5_RESULT.md)) |
| E6 | "Phạm vi trước khi tái sử dụng": oracle phải nhìn ra ngoài ý đồ của tác giả | RQ3 | ✅ | `D2_cerberus`: oracle viết tay không thấy gì, G2 thấy 24 đến 56/200 đầu vào đổi hành vi ([RQ3_RESULT](../research_closure/results/rq3/RQ3_RESULT.md)) |
| E7 | Tác hại phải định nghĩa theo hợp đồng, không theo mọi khác biệt (đóng góp mới, không có trong bài gốc) | **Q** | ❌ không xác nhận | HQ1 không được ủng hộ: chỉ 6/55 = 10,9% khác biệt ngây thơ không phải hồi quy theo hợp đồng. Q4 = 11,1% patch có hồi quy theo hợp đồng (C1 chưa chấm tay) ([STUDY_Q_RESULT](../research_closure/results/study_q/STUDY_Q_RESULT.md)) |
| E8 | So sánh với B9 (sửa trực tiếp) | F / B9 | ⛔ HOLD | `pre_b9/RELEASE_GATE.json` |
| E9 | Composition, retirement | (không có study) | ⏳ | Chưa có bằng chứng thực nghiệm mới; có hai lưu ý toán (Định lý 4 và 7) trong [PAPER_EXPECTATION_AUDIT](../research_closure/PAPER_EXPECTATION_AUDIT.md) |
| E10 | Tổng quát hoá trên cohort mới đã đóng băng trước khi có kết quả | J, P, Q | ✅ | P và Q đã xong; Q cho kết quả trái với P (RQ5) |

## 3. Study Q: tiến độ chi tiết

Giao thức: [STUDY_Q_PROTOCOL](../study_q/STUDY_Q_PROTOCOL.md). Amendment: chưa có ([AMENDMENTS](../study_q/AMENDMENTS.md)).

| Bước | Trạng thái | Ghi chú |
|---|---|---|
| Q-F0 khả thi, chỉ G0 | ✅ | 33/33 instance chạy được; dùng được 3/33 |
| Q-F1, G2 | ✅ đạt quy tắc | 18/33 = 54,5%; cận dưới Wilson × 500 = 190 ≥ 180 |
| Q-F2 kiểm kê kho patch | ✅ | 125/182 bản nộp; 31.205 patch resolved; 469 instance |
| Đóng băng (`Freeze Study Q`, commit `94c87bc`) | ✅ | `freeze_study.py verify study_q`: 68 tệp không đổi |
| Seed drand sau đóng băng | ✅ | `460798324973423911` (thời điểm seed 2026-10-31T07:47:53Z) |
| Sửa workflow stream (patch `study_q_stream_msg`) | ✅ | Ô `only` nhận nhiều định dạng hơn, báo lỗi rõ ràng; run #1 và #2 lỗi vì `only=3` không phải id |
| Che token Vertex trong log (commit `206da51`) | ✅ | Thêm `::add-mask::` cho 13 workflow; đã xác nhận trong log của part 0 (`GOOGLE_OAUTH_TOKEN: ***`) |
| Smoke 3 instance ([run #3](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41184775725)) | ✅ | 3/3 thành công, `FINISHED`. Lưu ý: mỗi instance khoảng 1 phút, artifact khoảng 1 KB, cần mở ra kiểm tra |
| Stream part 0, 235 instance ([run #4](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41185100083)) | ✅ | 08:33 đến 09:11 UTC; 235/235 job thành công, 0 lỗi |
| Stream part 1, 234 instance ([run #5](https://github.com/dinhthithuthuyduphong-bot/-gatekeeper-p6/actions/runs/41187862326)) | ✅ | 09:14 đến 09:59 UTC; 234/234 job thành công |
| ⚠️ Lệch giao thức: không lưu đầu ra từng đầu vào | ✅ xử lý bằng Q-A1 | `q_instance.py` chỉ lưu tóm tắt C1/C2/C3, trong khi giao thức mục 3 nói lưu mọi đầu ra. Cần amendment hoặc chạy lại có lưu (xem PROCESS_LOG) |
| Chạy lại instance lỗi hạ tầng (`only=...`) | ✅ không cần | 0 job lỗi; 4 bản ghi `ERROR` là lỗi công cụ (patch tạo tệp mới), tính là không dùng được |
| Workflow tổng hợp `Gatekeeper Study Q analyze` | ✅ | Commit `79ba306`; kết quả commit `9a8ab44`: đủ 469/469 bản ghi |
| Cổng Q-G1: có ≥ 18 instance có patch có khác biệt | ✅ đạt | 55 instance |
| HQ1 (Q3 > 0,5, nhị thức chính xác một phía) | ❌ không ủng hộ | 6/55 = 10,9% (Wilson 5,1% – 21,8%), p ≈ 1 |
| Q1 phễu; Q2, Q4 tỉ lệ (Wilson, bootstrap gom cụm); Q5 hệ số phóng đại | ✅ | Dùng được 245/469; Q2 = 43,1%; Q4 = 11,1%; Q5 = 3,88 theo giao thức (công cụ ghi 1,16 theo định nghĩa khác) |
| Phân tích độ nhạy (a) đến (d) | ✅ | Cùng kết luận; G0 1,2% so với G2 10,4% |
| Viết `STUDY_Q_RESULT.md` | ✅ | ALIGNMENT_WITH_FSE không sửa (thuộc freeze của Study P) |
| Amendment Q-A1: chạy lại 55 đơn vị HQ1 có lưu đầu ra + chấm tay (bổ sung sau khi thấy kết quả) | ✅ | 36/55 tái tạo được; 154 mục; đồng thuận 87,7%; 8/36 = 22,2% (Wilson 11,7% – 38,1%) không có hồi quy đã xác nhận. HQ1 "không ủng hộ" đứng vững |

**Ngân sách:** model chỉ dùng để sinh chương trình G2, khoảng 0,01 USD mỗi instance, dưới 10 USD tổng.

## 4. Kết quả Q sẽ quyết định khẳng định nào trong bài

Bảng này được suy ra từ ALIGNMENT_WITH_FSE (mục sau RQ5) và giao thức Q. **Chọn nhánh nào là quyết định của người hướng dẫn.**

| Kết quả Study Q | Khẳng định trong bài A\* |
|---|---|
| Bác bỏ H0 của HQ1 (phần lớn khác biệt ngây thơ không phải hồi quy theo hợp đồng) | (a) patch plausible hiếm khi hồi quy trên đầu vào hợp lệ; (b) oracle ngây thơ phóng đại nhiều lần (Q5). Kết luận RQ5 được xác nhận trên dữ liệu độc lập |
| **← Kết quả thực tế (31/10):** không bác bỏ, Q-G1 đạt (55 instance) | Báo cáo mô tả; kết luận RQ5 chỉ là thăm dò, giới hạn ở dữ liệu của Study P. Điều dữ liệu ủng hộ: khoảng 11% patch resolved khác bản fix trên đầu vào hợp lệ (cần chấm tay); kết quả phụ thuộc nguồn đầu vào (G0 so với G2) |

## 5. Review bài FSE (song song; chi tiết ở [REVIEW_FSE](paper/REVIEW_FSE.md) và [PAPER_AUDIT](paper/PAPER_AUDIT.md))

PDF gốc: [`paper/source/`](paper/source/), đã đối chiếu toàn văn ngày 31/10/2026. Bài do AI sinh, mọi số là projected.

| Nhóm | Mục | Kết luận | Trạng thái |
|---|---|---|---|
| Toán | T1 Định lý 4: hằng số | Đúng là 2ξ_s | ✅ có câu sửa · ⏳ sửa bài |
| Toán | T2 Định lý 4: ngân sách α | Phải cấp theo ô (kỹ năng, phạm vi), kể cả tổ hợp | ✅ có câu sửa · ⏳ sửa bài |
| Toán | T3 Retirement / admit lại | Cần sổ cái 6/(π²(k+1)²) (đã cài trong repo) | ✅ |
| Toán | T4, T5 Định lý 7 | Cận chặt 1 + min(a, b); "không có g" sai | ✅ có phát biểu thay thế · ⏳ sửa bài |
| Toán | T6 Mệnh đề 9 | Tỉ lệ 1 + 2σ_T²/σ_S²; "lợi ròng 1,55×" đếm sai | ⏳ sửa bài |
| Toán | T7 Mệnh đề 6 | Lượng từ thừa; phạm vi áp dụng | ⏳ sửa bài |
| Toán | T8 Hệ quả 8 | d̄ = 0,34 mâu thuẫn với 11,4% cặp giao nhau | ⏳ sửa bài |
| Toán | T9 Giả định 3 | i.i.d. với tập task hữu hạn; loss phải chặn tại 1 | ⏳ sửa bài |
| Số liệu | S1 CI so với biên 5 điểm | Cận dưới 3,1 < 5: không vượt cổng go/no-go | ⏳ sửa bài |
| Số liệu | S2 Mẫu số | 5,1%, 11,5%, 22,7% không nguyên trên 63 cặp | ⏳ sinh lại số |
| Số liệu | S3, S4 Mục 10.3 | Diễn giải sai về θ và ξ_s | ⏳ sửa bài |
| Số liệu | S5 đến S7 | Clean reuse không khớp; công thức hoà vốn; BH (FDR) so với FWER | ⏳ sửa bài |
| Trình bày | N1 đến N5 | Ví dụ retry/async mâu thuẫn; 7 trích dẫn placeholder; tài liệu bị nhắc nhưng không tồn tại | ⏳ |
| Kiến thức | R1 đến R3 (STR, e-process + Ville, alpha ledger) | Đúng | ✅ |

## 6. Việc còn mở ngoài Study Q

- B9: **HOLD**. Study J: **BLOCKED**.
- Hai lưu ý toán về Định lý 4 (cận 2·TV) và Định lý 7 (composition) cần trao đổi với tác giả bản nháp.
- Các trích dẫn đánh dấu VERIFY trong reading list, và trích dẫn "OpenAI 2024" cho SWE-bench Verified, cần kiểm tra lại.
- Giới hạn cần ghi trong bài: một nửa số ca trong vùng của Study P đến từ bài tập của sinh viên; người chấm thứ hai ở RQ5 cùng họ model với model sinh patch.

## 7. Nhật ký

| Ngày (UTC) | Việc |
|---|---|
| 31/10/2026 06:47 | Đóng băng Study Q (`94c87bc`) |
| 31/10/2026 06:50, 07:59 | Stream run #1 và #2 lỗi ở bước plan (`only=3`) |
| 31/10/2026 08:21 | Đưa patch `study_q_stream_msg` lên main (`4898596`) |
| 31/10/2026 08:29 | Smoke run #3 (3 instance): thành công |
| 31/10/2026 08:33 | Che token Vertex (`206da51`); bắt đầu part 0 (run #4) |
| 31/10/2026 08:35 | Thêm TRACKING_FSE.md (`9ea7356`) |
| 31/10/2026 | Thêm REVIEW_FSE.md (`635eebc`): review công thức, kiểm lại bằng số |
| 31/10/2026 09:11 | Part 0 xong: 235/235 thành công |
| 31/10/2026 09:14 | Bắt đầu part 1 (run #5); ghi nhận lệch giao thức về lưu đầu ra |
| 31/10/2026 | Đưa 3 PDF lên `docs/paper/source/`; kiểm tra toàn bài (PAPER_AUDIT.md); sắp xếp lại repo (`docs/`, `archive/`); part 0 vẫn đang chạy |
| 31/10/2026 09:59 | Part 1 xong: 234/234 thành công |
| 31/10/2026 ~10:05 | Tổng hợp: HQ1 không được ủng hộ; Q4 = 11,1%; viết STUDY_Q_RESULT.md |
| 31/10/2026 ~10:15–12:30 | Amendment Q-A1: chạy lại 55 đơn vị, chấm tay hai người; kết luận HQ1 giữ nguyên |
