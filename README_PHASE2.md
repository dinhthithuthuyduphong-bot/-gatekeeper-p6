# Gatekeeper-Lite — Phase 2: Statistical + B6-R V2 + Study F scoring audit

**Status:** reviewable add-only code; NOT merged in GitHub. Built from
`main` commit `8639bc59e31148ec7173119cdb136497de1d870a` (PR #1).

## Scope and strict research safeguards

- This stage is **zero paid model API calls**. GitHub Actions runner usage can
  depend on account/plan; check available minutes and quotas separately.
- Never run B9 `record`, re-freeze Study F, or modify prior D/E/F outcomes here.
- The Phase-2 pipeline only reads frozen inputs, writes fresh exploratory
  artifact outputs and runs deterministic fixture tests.
- `pre_b9/RELEASE_GATE.json` stays `HOLD`. A successful Phase-2 audit
  does NOT authorize paid B9; blockers are intentionally reported.

## Added files

| Path | Role |
|---|---|
| `.github/workflows/phase2-audit.yml` | Free PR + manual audit, uploads result artifact |
| `tools/phase2_cs_audit.py` | Recomputes conservative, 95% time-uniform and family-simultaneous CS from stopped portions of frozen traces |
| `tools/phase2_b6r_v2.py` | Proposed stronger B6-R gate; needs independently pinned provenance, replay and predeclared VISIBLE smoke |
| `tools/phase2_integrity_audit.py` | Flags missing hash, e-Holm/family implementation and documentation issues in Study F |
| `tests/test_phase2_zero_cost.py` | 9 deterministic synthetic tests, zero API calls |
| `pre_b9/phase2/B6R_V2_CONTRACT.json` | Explicitly NOT READY; prevents fabricated source/environment evidence |
| `docs/PHASE2_RESEARCH_AUDIT.md` | Research interpretation, known gaps, and independent reviewer checklist |

Nothing in `study_d/`, `study_e/`, `study_f/`, `gatekeeper_lite/`,
`tools/freeze_study.py`, `tools/run_b9.py`, or `tools/score_heldout.py` is modified.

## No-VS-Code GitHub upload

1. Create new branch on GitHub from **current main**, named
   `audit/phase2-b6r-stat-heldout-20261022`.
2. Download ZIP, extract it, then upload **the contents** into that branch,
   preserving relative folder names. Do not nest under `Gatekeeper_Phase2...`.
3. Open a PR to `main`. `Gatekeeper Phase 2 audit (no model API)` runs on PR.
4. Check workflow: all tests and freeze D/E/F verification should pass.
   Download `GATEKEEPER_PHASE2_ZERO_COST_AUDIT` from the run's Artifacts.
5. The output `INTEGRITY_FINDINGS.md` should report `REVIEW_REQUIRED`,
   **not** `GO`; this is expected and is not a test failure.
6. Review CS tables and B6-R evidence gaps before merging. No B9 Actions.

## How to run locally (optional)

From the repository root, Python 3.12:

```bash
python -m unittest discover -s tests -v
python tools/freeze_study.py verify study_d
python tools/freeze_study.py verify study_e
python tools/freeze_study.py verify study_f
python tools/phase2_cs_audit.py --out out_phase2
python tools/phase2_b6r_v2.py --out out_phase2/B6R_V2_READINESS.json
python tools/phase2_integrity_audit.py --out out_phase2
```

## What counts as progress

**Delivered**: reproducible post-freeze CS summaries, baseline-evidence
readiness with fail-closed semantics, machine-readable scoring blockers.

**Still open**: genuine stronger B6-R empirical comparator; independently
verifiable source package provenance and visible smoke; E2/E3 independent
oracles; D5 reached-line/path coverage; second skill; evidence-aware Study F
amendment defining e-Holm family, repeated-run multiplicity, scorer hash;
real B9 model evaluation. Do not equate a successful CI with completion of
these research tasks.

## Important interpretive notes

The 95% conservative Hoeffding CS are not calibrated identically to the
frozen betting certificates and can be much wider. A harm CS upper endpoint
above `eta` does **not** invalidate an e-based low-harm certificate.
Post-hoc confidence reporting does not change historical admissions.

The B6-R V2 checker uses deliberately narrow numeric version grammar
and fails closed for prerelease/complex PEP 440 versions. A production
implementation should evaluate such versions with a pinned standards
library and independent tests, not silently strip suffixes.

The frozen Study F `k_cells=48` is four models times six targets times
two scopes, while the protocol mentions three repetitions. The final
multiplicity structure across those repetitions needs to be explicit
before paid calls; a missing global aggregator must not be glossed over.
