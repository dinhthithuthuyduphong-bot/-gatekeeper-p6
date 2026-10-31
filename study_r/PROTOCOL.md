# Study R: footprint census of the two real skill families (written before running)

**Question.** Do the two frozen skill families of Studies D–G touch the same code on real repositories? This measures how often a
composite cell would be needed (paper, Corollary 5.6) and whether Assumption 4 (non-interaction of disjoint footprints) is ever put
to the test on our targets. Descriptive; no hypothesis test; no model calls.

**Skills (frozen, unchanged):**
- `study_d/skills/bool-excluded-from-int.json` (transform `negative_type_guard`);
- `study_g/skills/none-identity.json` (transform `none_identity`, registered by `gatekeeper_ext.none_identity`).

**Targets:** every target of Studies D, E, G (`study_{d,e,g}/eval_targets/*/gk_target.json`), cloned at the pinned revision.

**Measures, for each target:**
1. *Declared modules:* `bind_modules` of each skill alone on the target's declared modules → binding sites (module, function).
2. *Whole repository:* each skill's transform applied to every `.py` file of the repository outside test directories (`test`, `tests`,
   `testing`, files named `test_*.py` / `*_test.py`); files that do not parse are skipped and counted.
3. **Overlap:** functions (module, qualified name as reported by the transform) touched by **both** families; and
   `gatekeeper_lite.gatekeeper.footprint_overlap` of the two footprints.

**Report:** per target and in total: functions touched by each family, functions touched by both, files scanned and skipped, clone
failures. Every number is produced by `tools/footprint_census.py` in the workflow `Gatekeeper Study R footprint census`.

**Deviation rule:** a target that cannot be cloned or parsed is reported, not replaced.
