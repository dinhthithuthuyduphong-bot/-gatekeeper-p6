# Study T amendments

## T-A1 (written after the census, before any trial; the census has no outcome)

**What the census showed (sizes only).** 60 targets, 2,578 cells (2,436 Ruff, 142 R2), 235 skills; Ruff version 0.17.3.

**Fairness correction (before any outcome).** The protocol fixed the fixed-sample test at n = 99 draws, a number computed for 16
cells. With K = 2,578 cells, certifying zero harm at level α/K needs n_FS = ⌈log(α/K)/log(1−η)⌉ = 198 draws for *any* method; at
n = 99 FS could never admit, which would make it a strawman. FS therefore uses n_FS = 198 (admit iff the exact one-sided binomial
test rejects h ≥ η at level α/K, i.e. zero changes in 198 draws).

**Gatekeeper (G), fixed here.** Harm certificate (c = 0.9, η = 5%) and harm alarm (fires at 20) on the cell's gate draws, stopped
at the first of: e ≥ K/α, alarm, or the budget of 200 draws; e = 0 if the alarm fired; admission by **e-Holm** over all K cells
at α = 0.1 (Proposition "Fixed families: e-Holm"), K = 2,578 fixed from the census (cells that turn out unusable keep e = 0, which
is conservative). Mean draws of G count every draw up to its stopping time.

**Trials.**
- Per cell, up to 5 touched functions (census order: file, then qualified name; `<module>` and nested functions skipped).
- The cell's draw distribution: uniform over its usable functions, then a signature-generated input (Study S harness S-A5:
  receivers from constructor signatures, `bool` for `int` with probability 1/4, fixed hash seed, each version run twice; an input
  counts only if stable in the original and the variant).
- Two independent streams per function: **gate** (seed 1, 200 inputs) and **reference** (seed 2, 200 inputs).
- Gate draws are interleaved round-robin over the cell's functions.
- **Ground truth:** pooled change rate on the reference stream (mean over the cell's usable functions of the per-function change
  rate); harmful iff ≥ η.
- A cell is usable iff at least one function has ≥ 50 stable inputs in both streams.
- Ruff fixes applied with `ruff check --isolated --select RULE --fix --unsafe-fixes` (all of the cell's sites); R2 families with
  their transform on every file.
- Environment: Python 3.12 venv; the release installed from PyPI with its dependencies, then the package itself uninstalled so that
  the extracted sdist is imported (as Study S).

**Baselines on the usable cells.**
- U: admit all.
- RS: Ruff applicability `safe` for every site of the cell (R2 cells: not applicable, reported separately).
- B6R: the rule's documentation example, fixed by the same Ruff version, equals the documented "Use instead" code (AST
  equality); the fingerprint matches by construction (one environment).
- S20: no change in the first 20 gate draws.
- FS: no change in the first 198.
- B8: no change in all 200.

LJ (model judge) and T (test suites) follow in amendments T-A2 and T-A3, written before they run.

**Win criteria W1–W4 unchanged.**
