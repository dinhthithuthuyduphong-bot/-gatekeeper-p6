# Study I: verified exploratory family

Retrospective target vetting and generator diagnostics; no prospective/generalization claim.

| Cell | Final decision | Draws to stop | Full help / tie / hurt |
|---|---|---:|---|
| I1_sqlalchemy/null_semantics | REJECT_CENSUS | 3 | 0 / 69 / 231 |
| I1_sqlalchemy/plain_queries | REJECT_CENSUS | 300 | 0 / 300 / 0 |
| I2_networkx/given_positions | ADMIT_DIAGNOSTIC | 80 | 300 / 0 / 0 |
| I2_networkx/default_positions | QUARANTINE | 300 | 0 / 300 / 0 |

Four cells are retained in the e-Holm family, including census-vetoed cells with e=0.
The full 300-draw traces were executed for diagnostics after each stopped decision. Do not call this a production cost saving.
The custom draw oracles are distinct from the unchanged upstream tests used to establish target behavior.
Model calls: 0. B9 remains HOLD.
