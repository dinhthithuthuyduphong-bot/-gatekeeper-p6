| Check | Statement | Held | Key numbers |
|---|---|---|---|
| C1_per_cell_validity | per-cell false admission <= alpha | True | rate=0.0655, wilson95=[0.055468358869967115, 0.07719761632487863] |
| C2_budget_per_cell_vs_per_scope | shared per-scope threshold can exceed alpha family-wise; per-cell alpha/L does not | True | familywise_shared=0.4535, familywise_split=0.0505 |
| C3_bounded_shift | |STR_Q - STR_P| <= 2 TV, attained; draft bound (TV) violated | True | ratio_gap_over_tv=2.0, max_ratio_random=1.5924 |
| C4_composition | STR(S1 o S2) <= 1 + min(STR1, STR2); attained by the construction | True | violations=0, construction_str_composite=0.9 |
| C5_pairing | unpaired/paired variance ratio = 1 + 2 sT^2/sS^2 | True | measured_ratio=5.1989, corrected_formula=5.2 |
| C6_alpha_ledger | sum over epochs of 6/(pi^2 (k+1)^2) <= 1 | True | partial_sum_1e6=1.0 |
| C7_corollary8_consistency | Corollary 8: d_bar implied by the overlap share | False | implied_mean_partners=10.602, draft_dbar=0.34 |
| C8_readmission_ledger | re-admission: full alpha per epoch can exceed alpha; the ledger does not | True | error_full_alpha_each_epoch=0.452, error_ledger=0.04 |
