# Study M (nhánh A*): amendments

## MASTAR-A1 — materialize S1 candidate list and bind missing protocol inputs before S2

Prepared against commit 036f9eeff76523d4034e04aa6c1e251914251601.
This amendment is applied only by the Gatekeeper study amend workflow; the application timestamp is recorded in config_study_m_astar.json.

### Observed failure

Run 40296709754 / job 121484429311 verified 40 frozen files, then failed because study_m_astar/candidates.json was absent. The dependent vet jobs did not run. The initial freeze did not track the candidate list, GATES.md or DECISION_RULE.md.

### Recovery and provenance

Materialize the ASTAR subset from the already supplied STUDY_M_DISCOVERY.zip:
- source SHA256: f8ade6a1cd40cb1d9c11d4fc1ef06d67d2d13cdb906bbac0ab58e9aa4ed557dc
- M_ORDERED.json SHA256: 1f7565709d746df47f2b3d1872fa447ad7ab82ad462c3203482134019c01c735
- S1 seed: 722277585642093255
- same split rule as tools/split_candidates.py: SHA256 of seed:track:lowercase-repo-URL; odd = ASTAR.
- preserve S1 artifact order verbatim; do not call tools/order_candidates.py.
- 269 ASTAR candidates from 162 repos; RR complement has 231 candidates from 148 repos; no shared repo URL.
- keep S2 limit 250, original gate thresholds and decision rules unchanged.
- no outcome-based selection or target execution was used to construct the list.

Bind the candidate list, provenance, unchanged gate/decision documents and edit specification through extra_tracked. Do not edit the original frozen_on or seed_time_utc; tools/amend_study.py preserves the original ASTAR freeze hash. Candidate allocation continues to use the original S1 seed via check_track.py, not the later ASTAR seed time.

### Explicit limitations

The discovery log contains 8 file-fetch API failures, despite errors=[] for search requests. Keep these as recorded collection exclusions in this recovery; do not replace or retry them selectively. Their identities were not retained. The supplied candidate universe is therefore conditional on successful collection and the stated metadata filters.

Discovery order uses owner/repo while order_candidates.py uses a full repo URL. This recovery adopts the already collected discovery order explicitly; it does not establish that both historical scripts are equivalent.

The two protocol documents become hash-bound at this amendment, not retroactively at the initial freeze. Their contents and numerical gates are unchanged.

### Preconditions before applying

No subsequent S2 outcomes should have been observed. If S2 has since run, stop and document that fact before applying this pre-outcome amendment. If main has further changes to the tracked study inputs, review those changes instead of re-freezing them blindly.

### Addendum A (written before this amendment is applied; no S2 outcome exists)

**A1. Restored configuration.** A preflight run (run 40319363876) found `study_m_astar/config_study_m_astar.json` with status DRAFT, whereas the vet run 40296709754 had verified the study as FROZEN. The most likely cause is that a development package containing the DRAFT configuration was extracted over the frozen file after the freeze: several packages delivered earlier contained that file. The frozen bytes were restored from tag `study-m-astar-freeze` with the `Gatekeeper restore frozen file` workflow, which refuses unless the restored bytes match the hash recorded in FREEZE.json and FREEZE.json is unchanged since the tag. The original freeze time and hashes are therefore preserved; no second freeze was made.

**A2. Text of the two protocol documents.** `GATES.md` and `DECISION_RULE.md` were not hash-bound at the freeze (the freeze tool hashes only fixed patterns and `extra_tracked`). The text bound by this amendment is the text in the repository when it is applied; its sha256 is then recorded in FREEZE.json. It may differ from the text present at the freeze. The differences known to the author, all made before any S2 outcome existed, are:
1. `GATES.md`: "money" is defined as cash or a credit that does not expire soon; the Free Trial credit (expires 2027-01-20, unusable by the RR track) is not counted as money. M3 and the main patch generation for the A* half may run before the decision date, using only that credit. Previously M3 was not allowed before the decision date.
2. `DECISION_RULE.md`: F4 is made concrete (A*: Free Trial still valid and sufficient; RR: at least 28 USD from the Developer credit plus cash, because the Free Trial cannot be used after in-principle acceptance); rule 3 also selects A* when F4 fails for RR; the results of M3 and of the main generation are stated not to be inputs of the rule; the decision date is a last date and may be earlier.

The numerical thresholds of M1 to M4 and the band [1%, 10%] of M4 are unchanged.
