# Gatekeeper-Lite — study-b-v1

Thời điểm chạy (UTC): 2026-10-19T08:02:34+00:00 · Python 3.12.15 · config `223a3139c67b`

> **Loại bằng chứng: PROSPECTIVE_FROZEN_REAL_TARGETS.** Target thật, chưa từng chạy trước khi đóng băng protocol; oracle gồm bộ test gốc của target và oracle metamorphic khai báo trước.

## Tham số đã đóng băng

- θ (benefit margin): 0.1 · α tổng: 0.1 · ngân sách: 24 task/cặp · seed: 20261101
- Bằng chứng: discordant_sign {'q0': 0.6, 'q1': 0.9, 'harm_eps': 0.05, 'harm_alt': 0.5} · ưu tiên task: ['gk_metamorphic'] · lọc task: reach_baseline

## Từng cặp skill–target

| Target | Regime | Skill | Bind | Nhãn thật | B2 | B6-R | B8 | Gatekeeper | Task GK dùng |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1_rich_click | B | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 9 |
| B1_rich_click | B | click-guard-v3 | ABSTAIN ABSTAIN_SCOPE_MISMATCH | NOT_APPLICABLE | OUT_OF_SCOPE | REJECT | OUT_OF_SCOPE | OUT_OF_SCOPE | 0 |
| B2_asyncclick | B | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 9 |
| B2_asyncclick | B | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 9 |

## Tổng hợp (số đếm thô)

Mẫu số: 4 cặp · có hại 3 · có lợi 0 · không đổi 0 · không áp dụng được 1

| Comparator | Cặp có hại bị admit | Cặp có lợi được admit | Cặp có lợi bị bỏ lỡ | Chi phí (lượt chạy task) |
| --- | --- | --- | --- | --- |
| B2 · dùng bừa | 3/3 | 0/0 | 0 | 0 |
| B6-R · replay + fingerprint | 3/3 | 0/0 | 0 | 0 |
| B8 · luôn retest | 0/3 | 0/0 | 0 | 2224 |
| Gatekeeper-Lite | 0/3 | 0/0 | 0 | 1166 |

## Phân tích độ nhạy (lớp task khai báo trước)

| Target | Skill | Nhãn gốc | Bỏ lazy |
| --- | --- | --- | --- |
| B1_rich_click | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 8, hỏng 0) |
| B2_asyncclick | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 8, hỏng 0) |
| B2_asyncclick | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 8, hỏng 0) |

## Giới hạn

- A task is one oracle case inside one target; tasks are not i.i.d. contexts.
- B6-R is a reconstruction of the paper's B6, not the original system.
- Counts are descriptive; no population rate or superiority claim.
