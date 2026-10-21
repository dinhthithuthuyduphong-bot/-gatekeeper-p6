# Gatekeeper-Lite — Pre-B9 zero-cash fixes (review package, 2026-10-22)

**Status: CI VERIFIED — PENDING MERGE.** The connected GitHub integration returned
`403 Resource not accessible by integration` on branch creation. The files here are
a reviewable patch set, not a claim that the repository has changed.

## Scientific integrity

- Base inspected: main commit `470e58bc05afa3671807f876b17c254860fb15d1`
  (`Freeze Study F`).
- Do NOT rewrite `study_d/`, `study_e/`, `study_f/`, `gatekeeper_lite/`, or frozen
  `tools/run_b9.py` as a silent correction. Existing hashes and prospective
  claims must remain auditable.
- No paid API calls, no new target outcomes, no simulated numbers represented
  as empirical results.
- `pre_b9/RELEASE_GATE.json` deliberately defaults to `HOLD`.
- The `HOLD` only protects the updated **GitHub Actions workflow**. It does NOT
  disable direct local execution of `tools/run_b9.py`, other workflows, or Cloud
  billing. It is not a spending cap.

## Files to copy to repository

1. Replace `.github/workflows/b9-run.yml` with the supplied version.
2. Add `tools/preflight_b9.py`.
3. Add `tools/b6r_contract_audit.py`.
4. Add `pre_b9/RELEASE_GATE.json` (keep `HOLD`).
5. Add `tests/test_preflight_b9.py`, `tests/test_b6r_contract_audit.py`,
   `tests/test_reviewer_stat_contract.py`, and
   `tests/test_reviewer_lambda_sensitivity.py`.
6. Add `tools/reviewer_lambda_sensitivity.py`; the included
   `pre_b9/LAMBDA_SENSITIVITY_EXPLORATORY.md` is **analytic only**, not observed data.

These changes live outside the current `study_f/FREEZE.json` tracked list.
**Check `python -m unittest discover -s tests -p 'test_reviewer_lambda_sensitivity.py' -v
python tools/reviewer_lambda_sensitivity.py --out pre_b9/LAMBDA_SENSITIVITY_EXPLORATORY.md
python tools/freeze_study.py verify study_d` and `verify study_f`
after copying**. If either fails, do not re-freeze silently.

## How to test — zero paid API cost

```bash
python -m unittest discover -s tests -p 'test_preflight_b9.py' -v
python -m unittest discover -s tests -p 'test_b6r_contract_audit.py' -v
python -m unittest discover -s tests -p 'test_reviewer_stat_contract.py' -v
python tools/freeze_study.py verify study_d
python tools/freeze_study.py verify study_f
python tools/b6r_contract_audit.py --out pre_b9/B6R_CONTRACT_INVENTORY.json
python tools/preflight_b9.py --config study_d/b9_config.json \
  --target D1_py_ecc --model deepseek-flash --mode record
```

The last command **MUST FAIL** with `PRE_B9_REVIEW_HOLD` (after 31 October).
Before that date it should fail with the date guard. This is intentional.

On Windows PowerShell, run the last Python command on one line rather than
using Bash backslashes.

## What is fixed vs. not fixed

| Reviewer issue | State in this package |
|---|---|
| Paid B9 before protocol review | **Guard prepared** for GitHub Actions; HOLD by default |
| Frozen Study F not verified by B9 workflow | **Guard prepared**; checks D and F |
| Wrong model/config mapping | **Guard prepared** |
| Concurrent duplicate paid jobs | **Guard prepared** via Actions concurrency |
| Weak B6-R fingerprint | **Auditor prepared**, baseline NOT yet upgraded |
| λ choice and e-process proof | **Deterministic contract tests prepared**, full sensitivity pending |
| `e=0` / e-Holm power | **Synthetic demonstration test prepared**, no retroactive family change |
| D5 scope-generator coverage | Pending; requires actual instrumented target runs |
| E2/E3 oracle provenance | Pending; independent upstream evidence needed |
| Multiple independent skills | Pending; skill #2 must be sourced and prospectively frozen |
| Confidence sequences | Pending; cannot infer valid CS from a point e-value alone |
| Neutral-cell futility stopping | Pending; needs a separately predeclared experiment |
| Costly B9 model-in-loop evidence | Deliberately NOT run |

## High-priority research blockers found in read-only audit

1. `study_d/skills/bool-excluded-from-int.json` declares `D={"python":">=3.8"}`.
   No source package-version constraints are present. This is an actual
   comparator limitation, not proof that all targets are unsafe.
2. `tools/score_heldout.py` is **not** listed in `study_f/FREEZE.json` even
   though it defines held-out scoring and the B9+Gatekeeper condition.
   It must be versioned/hashed in a new prospective amendment BEFORE any paid
   data collection, rather than quietly added to an old freeze.
3. `tools/score_heldout.py` has a comment saying that e-Holm over the Study F
   family is applied at aggregation, but its `gate()` function uses a
   per-scope `decision == "ADMIT"` criterion and the code inspected here does
   not itself implement the final 48-cell family-level decision. This needs
   a proof/code-path audit before any outcome claims. It may be conservative;
   do not label it anti-conservative without analysis.
4. B9 `tools/run_b9.py` labels a result `PAID_B9` based on `mode="record"`.
   A result's evidence status should ultimately be cross-checked with
   actual provider usage, cassette provenance and billing rather than
   trusting a string field.
5. `study_f/STUDY_F_PROTOCOL.md` still says "draft" in its heading although
   `config_study_f.json` is `FROZEN`; this is a documentation inconsistency.
   Do not edit the frozen protocol silently.

## Release criteria before removing HOLD

- Independent statistical audit of mean e-process, harm certificate,
  e-Holm family and any e=0 alternative.
- Real provenance and stronger comparator contract; smoke-test baseline
  must use **predeclared visible tests**, never hidden admission/held-out oracles.
- Oracle E1/E2/E3 tiers kept distinct; D5 coverage measured, not invented.
- Held-out scoring path, 48-cell family control, no hidden-oracle leakage,
  cassette/usage provenance and `score_heldout.py` hashing amended prospectively.
- Dry-run tests pass, project/credit eligibility verified, Google Cloud
  spending controls checked. A software budget is NOT a provider billing cap.
- Explicit new review/approval changes `RELEASE_GATE.json` from `HOLD` to `GO`.

**Do not flip GO merely to make a paid run work.**
