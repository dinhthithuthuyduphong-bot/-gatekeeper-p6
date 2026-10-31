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
| C9_harm_certificate | harm certificate at h = eta certifies with rate <= alpha | True | certification_rate_at_boundary=0.1035, growth_threshold_over_eta=0.3941, clean_draws_family16=110 |
| C10_decision_rule_studies_DH | Studies D-H rule: FWER <= alpha and E[min(e_ben, e_cert) at the stopping time] <= 1 at both null boundaries | True | benefit_boundary={"familywise_false_admission": 0.024, "wilson95": [0.016180052367186296, 0.03546315508705749], "mean_e_at_stop": 1.0862218530339116, "mean_e_se": 0.056036111071434434}, harm_boundary={"familywise_false_admission": 0.073, "wilson95": [0.058458786926264744, 0.09080938446651278], "mean_e_at_stop": 0.8026669949703062, "mean_e_se": 0.08932905129068158} |
| C11_library_ledger | library ledger and simulation allocation: total over all cells and epochs <= alpha | True | max_total_capacity_1_to_200=0.0998, simulation_total_12_skills=0.1 |
