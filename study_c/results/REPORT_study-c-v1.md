# Gatekeeper-Lite — study-c-v1

Thời điểm chạy (UTC): 2026-10-19T12:14:22+00:00 · Python 3.12.15 · config `d2020f699660`

> **Loại bằng chứng: PROSPECTIVE_REGIME_A_UNSEEN_REVISIONS.** Bản phát hành chưa từng chạy của repository đã dùng khi phát triển (regime A); protocol đóng băng trước khi chạy.

## Tham số đã đóng băng

- θ (benefit margin): 0.1 · α tổng: 0.1 · ngân sách: 24 task/cặp · seed: 20261102
- Bằng chứng: discordant_sign {'q0': 0.6, 'q1': 0.9, 'harm_eps': 0.05, 'harm_alt': 0.5} · ưu tiên task: ['gk_metamorphic'] · lọc task: reach_baseline

## Từng cặp skill–target

| Target | Regime | Skill | Bind | Nhãn thật | B2 | B6-R | B8 | Gatekeeper | Task GK dùng |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C_click_8_1_8 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_1_8 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_1_8 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_1_8 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_2_0 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_2_0 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_2_0 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_2_0 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_2_2 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_2_2 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_2_2 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 14 |
| C_click_8_2_2 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_0 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_0 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_0 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_0 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_1 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_1 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_1 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_1 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_2 [objects] | A | empty-default-guard-family | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_2 [lazy] | A | empty-default-guard-family | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |
| C_click_8_3_2 [objects] | A | click-guard-v3 | áp dụng | BENEFICIAL | ADMIT | ADMIT | ADMIT | ADMIT | 24 |
| C_click_8_3_2 [lazy] | A | click-guard-v3 | áp dụng | HARMFUL | ADMIT | ADMIT | REJECT | REJECT_HARM | 3 |

## Tổng hợp (số đếm thô)

Mẫu số: 24 cặp · có hại 12 · có lợi 12 · không đổi 0 · không áp dụng được 0

| Comparator | Cặp có hại bị admit | Cặp có lợi được admit | Cặp có lợi bị bỏ lỡ | Chi phí (lượt chạy task) |
| --- | --- | --- | --- | --- |
| B2 · dùng bừa | 12/12 | 12/12 | 0 | 0 |
| B6-R · replay + fingerprint | 12/12 | 12/12 | 0 | 0 |
| B8 · luôn retest | 0/12 | 12/12 | 0 | 17824 |
| Gatekeeper-Lite | 0/12 | 12/12 | 0 | 528 |

## Phân tích độ nhạy (lớp task khai báo trước)

| Target | Skill | Nhãn gốc | Bỏ lazy |
| --- | --- | --- | --- |
| C_click_8_1_8 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_1_8 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_1_8 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_1_8 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_0 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_0 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_0 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_0 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_2 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_2 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_2 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_2_2 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 16, hỏng 0) |
| C_click_8_3_0 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_0 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_0 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_0 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_1 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_1 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_1 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_1 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_2 | empty-default-guard-family | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_2 | empty-default-guard-family | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_2 | click-guard-v3 | BENEFICIAL | BENEFICIAL (sửa 12, hỏng 0) |
| C_click_8_3_2 | click-guard-v3 | HARMFUL | BENEFICIAL (sửa 12, hỏng 0) |

## Giới hạn

- A task is one oracle case inside one target; tasks are not i.i.d. contexts.
- B6-R is a reconstruction of the paper's B6, not the original system.
- Counts are descriptive; no population rate or superiority claim.
