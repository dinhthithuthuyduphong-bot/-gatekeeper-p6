# Mô phỏng lực kiểm định (2000 thứ tự ngẫu nhiên mỗi ô)

Nguồn: `/home/claude/rc3/out_real/RESULT.json` · α/ô = 0.015 · ngưỡng 1/α (epoch 0) = 110

| Target | Skill | Pool (bất đồng: lợi/hại) | Thiết kế | Ngân sách | P(ADMIT) | P(REJECT_HARM) | Task dùng TB |
|---|---|---|---|---|---|---|---|
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | mean θ=0.1 | 120 | 0.00 | 0.00 | 109.0 |
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | dấu q0=0.6 | 24 | 0.00 | 0.12 | 23.3 |
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | dấu q0=0.6 | 120 | 0.00 | 1.00 | 55.2 |
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 1.00 | 7.4 |
| R1_click_3298_parent | click-empty-default-guard | 109 (9/6) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 1.00 | 7.1 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | mean θ=0.1 | 120 | 0.00 | 0.00 | 75.0 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | dấu q0=0.6 | 24 | 0.00 | 0.23 | 22.3 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | dấu q0=0.6 | 120 | 0.00 | 1.00 | 43.3 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 1.00 | 10.6 |
| R3_click_8_2_1 | click-empty-default-guard | 75 (12/6) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 1.00 | 10.7 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | mean θ=0.1 | 120 | 0.00 | 0.00 | 109.0 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | dấu q0=0.6 | 24 | 0.00 | 0.10 | 23.4 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | dấu q0=0.6 | 120 | 0.00 | 1.00 | 55.2 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 1.00 | 7.3 |
| R1_click_3298_parent | click-guard-v3 | 109 (9/6) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 1.00 | 7.2 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 61.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 | 120 | 0.00 | 0.00 | 61.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 0.00 | 61.0 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | mean θ=0.1 | 120 | 0.00 | 0.00 | 75.0 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | dấu q0=0.6 | 24 | 0.00 | 0.22 | 22.4 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | dấu q0=0.6 | 120 | 0.00 | 1.00 | 43.7 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 1.00 | 10.7 |
| R3_click_8_2_1 | click-guard-v3 | 75 (12/6) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 1.00 | 10.9 |
