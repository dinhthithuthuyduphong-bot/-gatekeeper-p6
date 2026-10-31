# Study R2 amendments

## R2-A1 (post hoc, written after the first census run 41223600552)

**What was seen.** Measure 3 found two files (pycubrid `protocol.py`, pydal `backends/oracle.py`) where `type_eq_isinstance`
creates a site for the frozen bool-exclusion guard (`negative_type_guard`) in a function the guard did not touch: the two
rewrites do not commute although their footprints on the original code are disjoint. On pydal the static execution rule puts
the two families in different components, so it would let them run together without a composite certificate.

**What is added (analysis only; no family, target or measure changed).**
- `gatekeeper_ext.execution`: optional `edges` (enabling pairs) joined to the footprint-overlap graph.
- `tools/library_census.py`: `with_enabling_edges`, components and composite cells with the measured non-commuting or
  site-changing pairs as extra edges (derived from measures 2 and 3, no re-scan).
- `tools/library_simulation.py --graph`: enabling edges count as overlap.

**Labelled post hoc** in the paper. The census and simulation are re-run by the same workflow so that every reported number
comes from it.
