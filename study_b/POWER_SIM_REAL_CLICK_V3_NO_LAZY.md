# Mô phỏng lực kiểm định (2000 thứ tự ngẫu nhiên mỗi ô)

Nguồn: `/home/claude/rc3/out_real/RESULT.json` · α/ô = 0.015 · ngưỡng 1/α (epoch 0) = 110 · loại bỏ: ['lazy']

| Target | Skill | Pool (bất đồng: lợi/hại) | Thiết kế | Ngân sách | P(ADMIT) | P(REJECT_HARM) | Task dùng TB |
|---|---|---|---|---|---|---|---|
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 103.0 |
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | dấu q0=0.6 | 120 | 0.00 | 0.00 | 103.0 |
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-empty-default-guard | 103 (9/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 0.00 | 103.0 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 69.0 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | dấu q0=0.6 | 120 | 1.00 | 0.00 | 64.7 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 1.00 | 0.00 | 12.0 |
| R3_click_8_2_1 | click-empty-default-guard | 69 (12/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 1.00 | 0.00 | 12.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 103.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | dấu q0=0.6 | 120 | 0.00 | 0.00 | 103.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 0.00 | 24.0 |
| R1_click_3298_parent | click-guard-v3 | 103 (9/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 0.00 | 103.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 61.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 | 120 | 0.00 | 0.00 | 61.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 0.00 | 0.00 | 24.0 |
| R2_click_8_1_7 | click-guard-v3 | 61 (1/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 0.00 | 0.00 | 61.0 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | mean θ=0.1 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | mean θ=0.1 | 120 | 0.00 | 0.00 | 69.0 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | dấu q0=0.6 | 24 | 0.00 | 0.00 | 24.0 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | dấu q0=0.6 | 120 | 1.00 | 0.00 | 64.7 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | dấu q0=0.6 + ưu tiên oracle biên | 24 | 1.00 | 0.00 | 12.0 |
| R3_click_8_2_1 | click-guard-v3 | 69 (12/0) | dấu q0=0.6 + ưu tiên oracle biên | 120 | 1.00 | 0.00 | 12.0 |
