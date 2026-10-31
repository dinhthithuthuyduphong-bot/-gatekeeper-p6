# Study S amendments

## S-A1 (post hoc, written after run 41227728959; labelled as such in the paper)

**Registered result (stands):** 23 units, 2 usable, 0 with any behaviour change; all 8 cells admitted. Uninformative: 21 units
could not be called.

**Root causes (debug loop C of docs/PAPER_TODO.md):**
1. *Harness:* the frozen `fn_probe_inner.py` builds a receiver only for classes constructible without arguments
   (14 units); private methods are name-mangled (`Mongo.__select` is `_Mongo__select`; 1 unit).
2. *Environment:* hera_pspec (9 units) and cerberus (1 unit) failed to import; the install log was not kept, and every target
   ran under Python 3.12 although cerberus declares 3.8.

**Changes (no unit, input generator, seed, measure or gate changed):**
- `tools/composition_inner.py`: receivers built from the class constructor signature with G0 (same seed); an `__init__` unit is
  the construction itself; outcome = call outcome plus the receiver's state after the call; mangled names resolved.
- `tools/composition_study.py --s-a1`: Python version from the manifest, install return code and log tail recorded.
- Results in `COMPOSITION_STUDY_SA1.json`, next to the registered `COMPOSITION_STUDY.json`.

**Known limit (seen in the synthetic smoke test, not on targets):** G0 follows annotations, so a parameter annotated `int` never
receives a `bool`; witnesses of type-check rewrites may therefore be missed.

## S-A2 (written before running; post hoc with respect to S-A1's results, labelled as such)

**Why.** S-A1 left two gaps (docs/PAPER_TODO.md R16): (1) G0 follows annotations, so an `int` parameter never receives a
`bool`, the subtype on which the type-check rewrites change behaviour; (2) hera_pspec (9 units) could not be installed under
Python 3.12 (`uvtools>=0.2.0` has no matching distribution).

**Changes (units, seed, measures and gate unchanged):**
- *Subtype substitution:* after G0 generates a call, every `int` value (not `bool`) in the receiver's and the call's arguments is
  replaced, independently with probability 1/4 (seeded by the call index), by `True` or `False`. `bool` is a subclass of `int`,
  so these are valid values of the annotated type. n stays 200.
- *Install fallback:* if installing under the manifest's Python fails, the same install is tried once under Python 3.11; the
  attempt and its log are recorded.
- Results in `COMPOSITION_STUDY_SA2.json`; S and S-A1 results stay as they are.

**Prediction written before running:** the bool-sensitive rewrites (`type_eq_isinstance`, the bool guard) will show more
behaviour change than under S-A1; whether any composition becomes emergent, masking or order-dependent is open.

## S-A3 (written before running): replication of every variant

**Why.** S-A2 found the first order dependence on real code (pydal `QueryBuilder.parse`: on 1 of 200 inputs AB keeps the original
behaviour and BA does not), but only O was run twice; the variants were run once, so a non-deterministic function could produce
it.

**Change.** Same as S-A2, but every variant (A, B, AB, BA) is also run twice; an input counts only if O and every variant give the
same outcome in both runs. Stricter, so it can only remove differences. Results in `COMPOSITION_STUDY_SA3.json`.

**Decision rule written before running:** the order dependence is reported as real only if it survives S-A3.

### Outcome of S-A3 (run after the amendment above)
The order dependence of S-A2 did not survive (0 variant-unstable inputs in this run, and no difference on `QueryBuilder.parse`); by
the rule written before the run it is reported as noise. Probable cause (hypothesis, not tested): hash randomisation differs between
the fresh processes of each version (set or dict iteration order). Future runs should fix `PYTHONHASHSEED`.
