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

## T-A5 (post hoc, written before it is computed): a strong B6, faithful to the original paper
**Why.** The original paper's decisive baseline B6 is GSE replay verification (B5: the skill's recorded tests replayed on the
**source repositories** where it was learned and used) plus environment fingerprints. Our B6-R replayed only a hand-built fixture
(Studies D/E) or the rule's documentation example (Study T); it is weaker than B6 on the replay side
(`study_d/PROVENANCE_B6R.md`). This amendment adds **B6-strong**, computed from the existing Study T records. It is post hoc
(Study T's outcomes have been seen), but it is written down before it is computed.

**Definition.**
- **Sources** of cell (rule R, package p): every *other* package of Study T with a usable cell for R.
- **Replay on sources passes** iff R changed behaviour on **no** draw of **any** source (gate and reference streams of the source
  cell; this is source evidence, never target evidence).
- **Fingerprint:** interpreter version, operating system and Ruff version of the source and target environments. In Study T these
  are identical by construction (one runner image, Python 3.12, Ruff 0.17.3), so the fingerprint matches. This is the
  environment-level check of B6; repository content is not an environment fingerprint.
- **Admit** iff replay on sources passes. If R has no other usable source, fall back to B6-R (the documented example).
- **Variant B6-majority:** admit iff R changed behaviour on fewer than half of its sources (a lenient version, for retention).

**Reported:** harmful and safe admissions of B6-strong and B6-majority next to Table `tab:market`; W1, W2 and W4 recomputed with
B6-strong replacing B6-R. A loss is reported as such.

## T-A6 (written before it runs): B9, the model applies the change itself
**Why.** The original paper's co-primary question: is admission worth more than spending the budget on direct repair by a model
(B9)? In Study T the natural B9 is: instead of certifying Ruff's deterministic fix, ask a model to apply the rule to each touched
function directly, and use its output without trials.

**Sample (fixed by seed, before any call).** All 11 harmful Ruff cells plus 139 other usable Ruff cells drawn uniformly
(seed `sha256("study-t-b9")`); up to 5 functions per cell, as in the trials.

**B9 call.** gemini-3.8-flash, temperature 0, one call per function. The model sees the rule code, the rule's name and the first
800 characters of Ruff's explanation, and the function's source. Prompt fixed here: *"Apply the lint rule below to this Python
function. Keep its behaviour identical for every caller. Return only the complete rewritten function (no decorators, no
explanation) in one ```python block; if the rule does not apply, return the function unchanged."* The returned function replaces
the original (same indentation); a reply that does not parse leaves the function unchanged and is counted as a failed attempt.
Hard cap 3 USD.

**Measures.**
- B9 output harm: the same harness, reference stream, and η = 5% as the ground truth of the trials.
- Cost:
  - B9: USD, tokens and wall seconds of the calls.
  - Gatekeeper: wall seconds of the gate-stream trials of the same cells (re-timed in the same job), converted to USD at the
    GitHub-hosted Linux runner price (0.008 USD per minute).

**Win criterion B9-W:** among the sampled cells, Gatekeeper admits fewer harmful changes than B9 applies, at lower or equal cost per
cell.

## T-A7 (written before it runs): B9 with medium and strong models
**Why.** T-A6 used the cheapest configuration. A stronger model might apply the rules more faithfully, so Gatekeeper's advantage
could shrink.

**Configurations, on the same 150 cells, prompt and harness as T-A6:**
- *medium:* gemini-3.8-flash with `reasoning_effort: high`, cap 4 USD;
- *strong:* gemini-4-argon with `reasoning_effort: low`, cap 10 USD (the model the repository already uses as its strong model).

**Reported per configuration:** cells whose output changed behaviour on ≥ 5% of reference inputs (and those where Ruff's own fix is
harmless), unparsable replies, USD and seconds per cell, against Gatekeeper on the same cells. B9-W is evaluated per configuration.

### T-A7 incident (run 41264163363)
A variable in `tools/market_b9.py` overwrote the tier tag, so the shard files were named by a hash; the medium and strong tiers
processed the same cells, produced identical names, and half of the files overwrote the other half when artifacts were merged. The
analysis then wrote empty results without failing. **Kept:** medium shards 0 and 2, strong shards 1 and 3 (each file records its
model and effort), renamed to their tier. **Fixed:** the variable; the analysis now refuses an empty or mixed-model tier.
**Re-run:** medium shards 1 and 3, strong shards 0 and 2, same code path and prompt. No outcome was used to change anything.
