# Study T amendments

## T-A1 (written after the census, before any trial; the census has no outcome)

**What the census showed (sizes only).** 60 targets, 2,578 cells (2,436 Ruff, 142 R2), 235 skills; Ruff version 0.17.3.

**Fairness correction (before any outcome).** The protocol fixed the fixed-sample test at n = 99 draws, a number computed for 16
cells. With K = 2,578 cells, certifying zero harm at level α/K needs n_FS = ⌈log(α/K)/log(1−η)⌉ = 199 draws for *any* method; at
n = 99 FS could never admit, which would make it a strawman. FS therefore uses n_FS = 199 (admit iff the exact one-sided binomial
test rejects h ≥ η at level α/K, i.e. zero changes in 199 draws).

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
- FS: no change in the first 199.
- B8: no change in all 200.

LJ (model judge) and T (test suites) follow in amendments T-A2 and T-A4, written before they run.

**Win criteria W1–W4 unchanged.**

## T-A2 (written before it runs): LLM-judge baseline LJ
- **Input to the model:** for every census cell, the unified diff of the cell's change on the package (the skill applied to the
  cell's files, as in the trials), truncated to its first 2,000 characters, plus the skill's name. The model sees no trial or
  reference outcome.
- **Model and settings:** gemini-3.8-flash, temperature 0, one call per cell, hard cap 3 USD (`SpendGuard`). If the cap is reached,
  the remaining cells are reported as *not judged* and LJ is compared on the judged cells only.
- **Prompt (fixed here):** *"You review an automated code change (a lint autofix or refactoring). Will applying it change the
  observable behaviour of the program for any caller (return values, raised exceptions, side effects)? Reply with JSON only:
  {"verdict": "safe" | "unsafe", "reason": "<one sentence>"}."*
- **Decision:** LJ admits iff the verdict is `safe`; an unparsable reply counts as `unsafe`.
- Tool `tools/market_judge.py`; workflow `Gatekeeper Study T LLM judge`; output `JUDGE_*.json`, merged into the analysis.

## T-A3 (written before the re-run of shard 7): memory cap for the inner process
**What happened.** Shard 7 (pygments, jinja2, googleapis-common-protos) was shut down by the runner twice, both times about 9
minutes in (runs 41237317062 attempts 1 and 2; exit 143), while the other 19 shards finished. Most likely a generated input made a
function allocate gigabytes (for example a width or count of 2^31−1), which exhausts the runner's memory.

**Change (shard 7 only).** Each inner process gets an address-space cap of 2 GB (`RLIMIT_AS`); a call that exceeds it raises
`MemoryError`, which is recorded as an outcome like any other exception. Nothing else changes. The 57 packages already run are not
re-run. A call that would allocate between 2 GB and the runner's memory was possible there and is not possible here, so the
packages are labelled by run in the results.

*(T-A3 was originally reserved for test suites; the test-suite baseline becomes T-A4.)*
