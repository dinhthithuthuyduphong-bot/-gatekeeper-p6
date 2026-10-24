# Study I — exploratory extension of the frozen second skill

Status: **EXPLORATORY / RETROSPECTIVE**. Prepared on 24 October 2026.
No paid model calls; B9 remains HOLD. This directory does not amend Studies D/E/G
or their frozen results. The name “Study I” identifies a new extension, not a
claim that these already-inspected targets were prospectively registered.

## Question and candidate selection

Can the unchanged `none-identity` skill exhibit both upstream-test-confirmed
harm outside pydal and upstream-test-confirmed benefit in another repository?
The skill is sourced from Study G's frozen hera_pspec replay. No target-specific
repair rule, new guard, hand-applied fix, or revised skill is introduced.

Candidate discovery was outcome-informed. SQLAlchemy was inspected for
overloaded comparisons; NetworkX was found through historical None-comparison
fixes and later upstream tests. All findings are retrospective validation and
generator diagnostics. `PRE_EXECUTION.json` is a local run manifest, not public
preregistration. Do not pool these data into the original prospective results.

## Exact source and oracle pins

See `targets.json` for full revisions, file selections, software versions and
SHA-256 checks of the frozen Gatekeeper code and vendored upstream files.

* SQLAlchemy: `10f4d1e2d706a7722ca78e79ce05b00333a7aa5b`.
  The four matched sites are in associationproxy, ORM relationships and schema.
  Three unchanged upstream test modules provide the functional oracle. This is
  an ORM/associationproxy harmful target; no harmful pure-Core result is claimed.
* NetworkX baseline: `585bb3ee251ab681e7725c07e4e8a569a0e511d5`.
  Upstream fix: `2ae63c50fe8eb6647db18ee352bed08b21f21d91` (23 July 2015).
  The frozen skill changes exactly three comparisons in `drawing/layout.py`.
  The full resulting module must equal the gold module's AST.
* NetworkX witness: unchanged `TestLayout.test_spring_args`, from
  `networkx/drawing/tests/test_layout.py` at
  `0b6f608d46601fb180a0f42eaa8a9a2ca9a42ecf` (NetworkX 1.11 release snapshot).
  **The witness is from a later release, not a test introduced by the fix commit.**
  The whole source test file is vendored unchanged; only this method is selected.
  The baseline census uses two complete test modules at the buggy revision.

The NetworkX experiment executes historical code under Python 3.8.20 and NumPy
1.17.5. It establishes a compatibility repair in that declared environment; it
does not claim the original 2015 dependency stack produced the same exception.

## Upstream tests, repeats and errors

Each arm/group runs in three fresh interpreter processes. Test identities and
outcomes must be stable. Repetitions are reproducibility checks, not independent
targets or extra statistical evidence. Baseline census failures, unknown errors,
missing XML, collection failures and empty inventories abort validation.

Nose represents the NetworkX witness's uncaught target-call `ValueError` as an
XML `error`. Only the explicitly checked traceback containing the ambiguous
array truth-value error in `_fruchterman_reingold` is classified as functional.
Imports/setup/collection errors are not credited as repairs. The complete raw
traceback remains available. Census tests and the upstream witness are never
rewritten. Selected-module census does not mean whole-repository test coverage.

The gold NetworkX arm is an offline positive control. It does not generate the
skill patch or contribute additional samples to the admission evidence.

## Four diagnostic cells

The draw adapters are researcher-authored and are kept separate from the
unchanged upstream tests used as tier-1 behavioral witnesses.

| Target / scope | Generator and oracle |
|---|---|
| SQLAlchemy / null_semantics | A fresh in-memory SQLite database for every draw; randomly choose a relationship or association proxy, and 1–8 values from None/1/2. Check actual returned row IDs against the upstream NULL-query semantics. |
| SQLAlchemy / plain_queries | Same construction with ordinary equality queries; paired behavioral control. |
| NetworkX / given_positions | 3–12 nodes, random edges at probability 0.3, dense/sparse backend with equal probability, explicit floating-point positions and a nonempty proper fixed-node subset. Check successful finite 2D output and preservation of fixed coordinates. |
| NetworkX / default_positions | Same graph/backend construction with default positions. Reset NumPy seed for each arm/draw; require valid output and identical paired coordinates. |

NetworkX runs five layout iterations per draw. These tests do not measure layout
quality or optimality. SQLAlchemy resets the database, session and mapper
registry for each draw. Environment/setup exceptions cause harness failure and
invalidate the run; they cannot be counted as beneficial repairs.

The unchanged Gatekeeper draw engine uses paired outcomes and
`Z = loss(with skill) - loss(without skill)`. Parameters are
`theta=0.2`, `eta=0.05`, `alpha=0.1`, `alpha_alarm=0.05`, `n_max=300` and seed
`20261024`. RNG strings include target and scope as in the existing engine.
The mean process uses the existing predictable variance-based stake with cap
`0.5/(1+theta)`; the harm certificate uses `0.9/(1-eta)`.

The family contains all four cells. Admission screening stops at
`min(e_benefit,e_cert) >= K/alpha = 40`; a harm alarm stops at 20.
Final closed e-Bonferroni/e-Holm uses the stopped e-values. A census regression
vetoes **every cell of that patched target**, setting their family e-values to
zero. These cells remain in the family. Neutral cells are quarantined.

`b8_full=true` continues observation to 300 draws after the sequential stopping
point, without updating the stopped admission e-values. Full-budget frequencies
are diagnostics, not additional independent replications. A diagnostic admission
is labeled `ADMIT_DIAGNOSTIC`; selection of target/scope after inspecting evidence
precludes treating it as a new confirmatory discovery with an unconditional 90%
guarantee. There is no guarantee for arbitrary repositories or future inputs.

## Measurement and integrity

Store commands, full stdout/stderr, exit codes, wall-clock seconds, XML test
identities, environment versions, source hashes, patch and raw paired draws.
The coordinator wrapper logs each observation but does not change the oracle,
stake, stop rule or frozen core files. No aggregate may substitute for missing
raw observations.

Separately replay 100 recorded draws per scope in shuffled order, with fresh
workers after every 25 draws. Compare semantic outputs and paired labels. This
checks observed state/order sensitivity; it does not prove independence.

`verify.py` requires both targets, every arm/group/repetition, all 1,200 original
paired observations and all 400 state/order checks. It recomputes labels, counts,
stopped evidence and the four-cell family. Missing rows, altered labels and empty
result files must fail closed. This audit does not call models or run target code.

Reported wall time is machine-specific. Execution was extended to full budget
and repeated for validation; no end-to-end production cost saving is claimed.
Fixed collection/import/database costs remain visible in logs. Cash paid to
model APIs for this extension is zero; local/CI computation still uses resources.

## Boundary of the contribution

This extension supplies one additional harmful repository and one historically
validated beneficial target for skill 2. SQLAlchemy harm is already detected by
upstream tests, so it does not establish superiority over full regression testing.
The beneficial NetworkX scope is deliberately concentrated on affected inputs.
Neither result establishes broad transfer rates, model independence, B9 results,
or that all reviewer weaknesses have been resolved.

A future confirmatory study should register new unseen targets, source pins,
scope mixtures, oracle provenance, the complete hypothesis family and stopping
rules before collecting its new evaluation outcomes. Rerunning these same known
targets with a new seed must not be labeled independent prospective discovery.
