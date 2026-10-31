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
