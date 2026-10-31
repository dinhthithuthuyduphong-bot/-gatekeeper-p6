# Study T: market skills, broad targets, convincing baselines (written before running; to-do D1–D3)

**Goal.** Decide, for each reusable code change applied to each repository (a *cell*), whether it may be applied, and compare
Gatekeeper with the decision rules that practitioners actually use, on a broad, unhand-picked set of targets, with skills that
are on the market. Everything runs in GitHub Actions; model calls only for the LLM-judge baseline (capped).

## 1. Skills (market first)
- **Ruff autofix rules:** every stable rule of Ruff (`ruff check --select ALL`) that produces at least one fix on a target. Ruff is
  a widely used Python linter/autofixer; each rule's fix is a reusable code change applied daily in practice, and Ruff labels
  each fix `safe` or `unsafe` (unsafe: may change behaviour). The Ruff version is pinned in the census and reused by every later
  phase.
- **The twelve families of Study R2** (`gatekeeper_ext/skill_library.py`, frozen and `study_r2/skills`).
A *skill* is one rule (or family); a *cell* is (skill, package).

## 2. Targets (broad, not hand-picked)
The most-downloaded PyPI projects (hugovk/top-pypi-packages, 30-day file, snapshot committed with the census), in rank order,
keeping a project iff: (a) its latest release has a `py3-none-any` wheel (pure Python) and an sdist of at most 20 MB; (b) its
name does not start with `types-` and it is not a stub-only package; (c) the sdist contains at least 5 non-test `.py` files.
The first **60** qualifying projects are the targets. Non-test files only (same rule as Study R).

## 3. Phases
1. **Census (no outcome):** sites, cells, Ruff applicability per cell, touched functions. `tools/market_census.py`.
2. **Trials (written as an amendment before it runs, using the census only to size it):** for each cell, the skill applied to the
   whole package; the touched functions (at most 5 per cell, in a fixed order) called on signature-generated inputs with the
   `bool`-for-`int` substitution and repetition of Study S (S-A5 harness). Two **independent** input streams per function:
   *gate draws* (seen by the decision rules) and *reference draws* (n = 200, a different seed, seen only by the ground truth).
3. **Test-suite run** for packages whose sdist ships a test suite that runs with `pytest` in under 10 minutes (secondary oracle).

## 4. Ground truth (not seen by any decision rule)
A cell is **harmful** if, on the reference draws, the change alters behaviour (outcome differs from the original, on inputs
stable in both versions) on at least η = 5% of the draws of some touched function; otherwise **safe**. Secondary ground truth:
the package's own test suite (new failures = harmful). Both are reported; neither uses the gate's draws.

## 5. Decision rules compared (all on the same cells)
| Id | Rule | Represents |
|---|---|---|
| U | apply every fix (`--fix --unsafe-fixes`) | unrestricted reuse (B2) |
| RS | apply iff every fix of the cell is labelled `safe` by Ruff | industry default (`ruff --fix`) |
| T | apply iff the package's test suite passes after the change | CI gate |
| B6R | the rule's documentation example replays (Ruff's "Example" → "Use instead") and the environment fingerprint matches | replay + fingerprint (GSE-style) |
| LJ | a model reads the diff and answers safe/unsafe (gemini-3.8-flash, one call per cell, temperature 0, cap 3 USD) | LLM judge |
| S20 | no behaviour change in the first 20 gate draws | smoke test |
| FS | exact one-sided test of harm rate ≥ η at level α/K on n = 99 gate draws | fixed-sample test |
| B8 | no change in all 200 gate draws (and tests, where run) | always-retest |
| G | Gatekeeper: harm certificate (Proposition "Harm certificate"), threshold K/α, harm alarm, on the gate draws | ours |
K = number of cells; α = 0.1; η = 5%.

## 6. Win criteria (fixed before any trial runs)
- **W1 (safety):** G admits at most α·(number of harmful cells), rounded up, harmful cells, and strictly fewer harmful cells
  than each of U, RS, T, B6R and LJ.
- **W2 (retention):** G admits at least as many safe cells as RS (Ruff's own safe label).
- **W3 (cost):** G's mean number of gate draws per cell is at most 70% of B8's (200) and at most FS's (99).
- **W4 (Pareto):** no baseline admits both more safe cells and fewer harmful cells than G.
Each criterion is reported as won or lost with its numbers; a lost criterion is reported, not redefined.

## 7. Honesty
The gate and the ground truth use the same kind of oracle (behaviour difference on generated inputs) on independent draws, so
S20, FS, B8 and G compete on equal information and cost; U, RS, B6R, LJ and T use less or different information, and the
secondary ground truth (test suites) is independent of the draws. "Harm" is behaviour change, not a judged defect. Deviations
are amendments, written before their runs.
