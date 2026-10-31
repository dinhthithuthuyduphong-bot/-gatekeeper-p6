# Giai đoạn 2.1: mọi con số trong bản nháp → nguồn thật, hoặc BỎ

**Quy tắc:** một con số chỉ được ở lại trong bài nếu nó có trong một tệp kết quả của repo (cột "Nguồn") và một run trên GitHub Actions (xem [EVIDENCE_LEDGER](../../EVIDENCE_LEDGER.md)).
- Mọi số của bản nháp là **projected** (banner trang 1), nên mặc định là **BỎ**.
- Cột "Thay bằng" là số đo được **gần nghĩa nhất** đang có; không có thì để "—" và câu đó phải bỏ.

Trạng thái: ✅ thay bằng số thật · ❌ BỎ (không có dữ liệu) · 🔁 giữ dưới dạng ví dụ minh hoạ, ghi rõ không phải số đo.

## Abstract và Introduction

| Số trong bản nháp | Ý | Quyết định | Thay bằng (nguồn) |
|---|---|---|---|
| 180 cặp / 25 repo (SkillShift-SE) | quy mô benchmark | ❌ | Benchmark chưa được xây. Bằng chứng thật: Study D–G có 8 + 5 + 1 target thật, 28 ô (`study_d/results/`, `study_e/results/`, `study_g/results/`) |
| 22,7% → 5,1% (so với B2) | giảm chấp nhận có hại | ✅ (thay ý) | Trên 4 ô có hại thật (E1, E2, E3 bool; G1 null): **B2 và B6-R admit 4/4, Gatekeeper admit 0/4** (REJECT_HARM; E1–E3 sau 2 lần rút). Nguồn: `study_e/results/RESULTS_SUMMARY_study-e-v1.md`, `study_g/results/RESULTS_SUMMARY_study-g-v1.md` |
| 11,5% → 5,1%, biên 6,4 điểm (so với B6) | biên so với baseline quyết định | ✅ (thay ý) | Như trên: B6-R 4/4 so với Gatekeeper 0/4. **Không** được viết như tỉ lệ phần trăm trên quần thể (n = 4 ô) |
| 84,3% clean reuse | giữ lại tái dùng có lợi | ✅ (thay ý) | Study D: Gatekeeper admit **2/3** ô có lợi; bỏ lỡ D5 vì lợi ích −0,11 nhỏ hơn biên θ = 0,2. B6-R admit 3/3 **nhưng cũng admit 9 ô không đổi**. Nguồn: `study_d/results/RESULTS_SUMMARY_study-d-v1.md` |
| 17,6 điểm | biên "nịnh" | ❌ | — |
| 31/33 biến fingerprint (Hình 1) | ví dụ động lực | 🔁 | Giữ như ví dụ **giả định**; ghi "illustrative" |

## §5 Approach, §6 Theory, §7 Implementation

| Số | Quyết định | Thay bằng (nguồn) |
|---|---|---|
| "giảm số lần thử khoảng 3×" (ghép cặp) | ❌ | Chỉ giữ công thức R của Proposition 2.7; không có số đo |
| 88,6% cặp rời footprint | ❌ | — |
| d̄ = 0,34 (Hệ quả 8) | ❌ | Tự mâu thuẫn với 11,4% (C7 của `research_closure/results/theory/THEORY_CHECKS.md`) |
| σ_T²/σ_S² = 2,1; 3,1; 1,55× | ❌ | Công thức đúng là 1 + 2σ_T²/σ_S² (C5); không có số đo |
| khoảng 10,9 nghìn dòng Python | ✅ (đo lại) | Đếm lại từ `gatekeeper_lite/` + `gatekeeper_ext/` khi viết |
| 4 dòng phiên bản phụ thuộc; 94 kỹ năng; 17 lớp phạm vi; 52 kỹ năng lỗi thời; 46 cặp khó, 4 cơ chế | ❌ | Bằng chứng thật: **2 họ kỹ năng** (guard `isinstance(x, bool)`; `== None` → `is None`), đều là phép viết lại AST viết tay |
| 0,39η; 110 lần rút sạch (số của chứng chỉ tác hại) | ✅ | C9, `research_closure/results/theory/THEORY_CHECKS.md`; Remark trong `latex/sections/theory.tex` |

## Bảng 1 (SkillShift-SE)

| Số | Quyết định | Thay bằng |
|---|---|---|
| 68 / 74 / 38 cặp; 14 / 27 / 22 có hại; 20,6% / 36,5% / 57,9%; 2,8× | ❌ | — (không có benchmark ba chế độ). Có thể nói định tính: Study D là chuyển giao chéo repo của **một** kỹ năng học từ PySStuBs, có lợi ở 3/5 target dương |
| 46 cặp tổ hợp; 11,4% cặp giao nhau | ❌ | — (không có dữ liệu tổ hợp thật) |

## Bảng 2 (kết quả chính) và RQ1

| Số | Quyết định | Thay bằng |
|---|---|---|
| Toàn bộ Bảng 2 (9 baseline × 5 cột) | ❌ | Thay bằng **bảng theo ô** của Study D, E, G (B2, B6-R, B8, Gatekeeper: ADMIT / REJECT / QUARANTINE) và **bảng pha** của Study H |
| CI [3,1; 9,8], "vượt biên 5 điểm" | ❌ | (lại còn sai: PAPER_AUDIT S1) |
| B8: 2,4% có hại; 79,3% clean reuse; chi phí 3,87× / 2,02× / 1,9× | ✅ (thay ý) | Study D: Gatekeeper **3.220** lần chạy thử so với B8 **3.600** (ít hơn 11%); wall-clock 0,99 (không claim tiết kiệm thời gian). B8 cũng admit 9 ô không đổi. Study E: **census (toàn bộ test của target: 1.287 / 51.524 / 130 test) không phát hiện regression nào** dù kỹ năng đổi hành vi ở 87–100% đầu vào bool; Study G: census bắt được (21 test fail mới) |
| 64% "đã đạt bởi cơ chế có sẵn" | ❌ | — |

## RQ2 (tổ hợp), RQ3 (chế độ, B9), RQ4 (retirement, hoà vốn)

| Số | Quyết định | Thay bằng |
|---|---|---|
| 41/46 cặp bắt được; 4–6; 0,19× | ❌ | — (chỉ có demo dựng sẵn: `demo/`, loại bằng chứng `CONSTRUCTED_DEMO_FIXTURES`) |
| 1,9 điểm (cùng repo), 21,0 điểm (đối kháng) | ❌ | — |
| B9: 49,8% so với 52,3%, 2,5 điểm, 8,2 điểm | ❌ | B9 **HOLD** (`pre_b9/RELEASE_GATE.json`); không có số |
| 0,61×; hoà vốn 2,4 và 6,8 lần dùng | ❌ | — |
| Retirement 1,0 so với 4,2 lần | 🔁 | Demo T1 (đổi phiên bản `clicklike` làm thu hồi); chỉ minh hoạ cơ chế |

## Bảng 3 (ablation) và §10.3 (phân tích định tính)

| Số | Quyết định | Thay bằng |
|---|---|---|
| Toàn bộ Bảng 3 | ❌ | Ablation đăng ký trước của Study D (`study_d/results/RESULTS_SUMMARY_study-d-v1.md`, mục 4): 6 biến thể cho cùng quyết định |
| 58% / 27% / 15% | ❌ | (lại còn diễn giải sai: PAPER_AUDIT S3, S4) |

## Các số mới, đo được, nên thêm (không có trong bản nháp)

| Kết quả | Số | Nguồn |
|---|---|---|
| Đồ thị pha các cổng (biên tác hại) | smoke 20 còn admit > 10% patch không chấp nhận được tới h ≈ 11%; zero-tolerance 300 giữ < 50% patch chấp nhận được khi h > 0,23%; cỡ mẫu cố định 300 an toàn như và **mạnh hơn** cổng tuần tự (92% so với 65% ở h = 2%) | `paper_snippets/P0_AND_PHASE_DIAGRAM.md`; `tools/gate_phase_diagram.py` |
| Study H (tác hại hiếm, target tổng hợp) | Gatekeeper admit sai **0/100** ở ρ ≥ η; B6-S(5) admit sai 38/50 và 27/50; B6-R 50/50 | `study_h/results/RESULTS_SUMMARY_study-h-v1.md` |
| Tính không trạng thái của harness | 12 target, 2.400 lần rút, 0 sai khác | `harness_checks/STATELESSNESS_SUMMARY.md` (**không** phải "0 tác hại". TRACKING viết nhầm, đã sửa; ALIGNMENT_WITH_FSE.md cũng viết nhầm nhưng thuộc freeze của Study P nên không sửa, ghi chú ở đây) |
| Study P (patch LLM, cohort xác nhận) | 16/205 = 7,8% patch plausible có θ̂ trong vùng (Wilson 4,9% – 12,3%); census admit 16/16 patch có θ̂ > 5%, smoke 20 admit 2/16, các cổng thống kê 0/16 | `research_closure/results/study_p/P_RESULT.md` |
| RQ5 | 97,5% đầu vào "hồi quy" là C2; hồi quy theo hợp đồng 1/205 – 3/205 | `research_closure/results/rq5/RQ5_RESULT.md` |
| RQ3 (oracle sinh tự động so với viết tay) | G2 đồng thuận 11/14 (kappa 0,57); G0 8/14 (0,19); `D2_cerberus`: viết tay không thấy, sinh tự động thấy 24–56/200 | `research_closure/results/rq3/RQ3_RESULT.md` |
| Study Q (SWE-bench Verified) | dùng được 245/469; Q2 = 299/694 = 43,1%; Q4 = 77/694 = 11,1% (Wilson 9,0% – 13,6%); HQ1 6/55 = 10,9% (không ủng hộ); Q5 = 3,88 | `research_closure/results/study_q/STUDY_Q_RESULT.md` |
| Q-A1 (chấm tay) | 36/55 tái tạo; đồng thuận 87,7%; 8/36 = 22,2% (11,7% – 38,1%) không có hồi quy đã xác nhận; độ nhạy: bỏ 3 đơn vị có đầu vào là đối tượng giả → 11/36 = 30,6% (18,0% – 46,9%) | `research_closure/results/study_q/qa1/QA1_RESULT.json`; mục 2.4 |
