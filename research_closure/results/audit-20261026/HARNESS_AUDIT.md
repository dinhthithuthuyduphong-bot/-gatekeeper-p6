# Audit of the test-mutation development runner

Base: 616a67f2bd024b96b24d5de958cfaa69e1fe9926. No runtime tests executed by this review.

| Finding | Source | Consequence | Supplied correction |
|---|---|---|---|
| `all_four` omits `no_missing_outcomes` | gatekeeper_ext/testmut.py, analyze | A future partial trace could pass all_four despite missing pairs. Current D5 did not falsely pass because other checks failed | Central completeness check is required for pass |
| Raw run directory deleted in finally | tools/tm_check.py | Per-arm XML and collection diagnostics unavailable in current small artifacts | Preserve selected evidence outside disposable snapshots; write inventory |
| Subprocess return codes ignored when XML exists | testmut.py, run_tests | Collection/internal errors can be summarized as ordinary outcomes | Record exit status; reject abnormal statuses even if XML exists |
| stdout/stderr discarded on successful runs | testmut.py | Missing and nondeterminism cannot be diagnosed from summary | Persist logs, command receipts, records and signatures |
| `tests.py` excluded by filename predicate | testmut.py, expand_files | Cerberus reports zero files despite its pinned upstream suite | Include this legacy name generically; do not modify study_d manifest |
| Output JSON written only after try/finally | tm_check.py | Exceptions can leave only console output | Write status and RESULT.md in finally and retain diagnostics |
| Entire matrix always runs | tm-dev.yml | Repeated expensive D1 work before cheap integrity checks | Target selection, unit-only option, unit-check dependency |
| Gold comparison and nondeterministic signatures | testmut.py | Apparent trigger can arise without reliable function-level semantics | Retain explicit limitation/self-comparison fields; no claim that this patch solves oracle validity |
| Unique mutation rejection sampling | make_mutants | Not the primary iid input process | Development-only label; requires separate inference design before statistical admission |
| Assertions can be mutated | _sites | Modified tests are not unchanged upstream regression oracles | Explicit limitation; input-only candidate redesign must be versioned and evaluated separately |

Seven added test cases exercise missing-outcome veto, raw preservation, timeout receipt, abnormal exit handling, zero-file short-circuit, legacy tests.py discovery and bytes-literal serialization. They are queued for CI, not claimed to pass yet.

The patch does not retrospectively alter G1 results or fix the original call-replay harness. It does not change the mutation value distribution, signature normalizer, statistical thresholds or paid release gate. Supporting tests.py changes development file discovery and is therefore recorded as a new development-harness version; old/new measurements must not be pooled.

Raw preservation is limited to produced files. Original five artifacts lack per-arm raw evidence; a summary cannot recover it. Root causes of D5 missing outcomes and D3/D4/A1 nondeterminism remain open until a recorded rerun.

## Final-run update

Run 40223310552 ended in failure. D1 timed out after 1800 seconds in orig_0; its artifact contains no result JSON. The new runner records timeout receipts and stops after the first invalid arm, preserving partial outputs. This does not make arbitrary mutated tests fast: input size/loop-bound mutations can turn a fast baseline test into a very long execution. Per-draw resource isolation is an open design requirement, not solved by increasing the timeout.
