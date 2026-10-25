# Gate G1 result

| Instance | Eligible | (a) bug detected | (b) no regression | (c) deterministic | (d) mutant caught | bug-trigger rate | Pass |
|---|---|---|---|---|---|---|---|
| D1_py_ecc | yes | False | True | True | False | 0.0% | no |
| D2_cerberus | no: no call of an edited function was recorded | | | | | | no |
| D3_speckit | no: no call of an edited function was recorded | | | | | | no |
| D4_openfeature | yes | True | True | True | True | 0.7% | **yes** |
| D5_pycubrid | yes | True | True | True | True | 8.7% | **yes** |
| A1_speckit_catalog | yes | False | True | True | True | 0.0% | no |

**2 of 6 instances pass.  Gate G1: FAIL** (threshold: at least 5 of 6).

- D4_openfeature: skill does not bind on this instance; the gold fix is used as the known-good patch (criterion (b) is then vacuous)
- A1_speckit_catalog: skill does not bind on this instance; the gold fix is used as the known-good patch (criterion (b) is then vacuous)
