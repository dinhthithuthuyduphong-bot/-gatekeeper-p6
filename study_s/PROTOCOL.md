# Study S: behaviour of real compositions (written before running; to-do 7.4, scorecard S7)

**Why.** Theorem "Composition" says individual risks do not bound composite risk, and Study R2 found real functions touched
by two families. Until now harm of compositions has only been simulated. S measures, on the real functions of R2, whether the
behaviour of a composition is predicted by the behaviour of its parts, and what the gate decides for singles and composites.
No model calls (inputs from the signature-driven generator G0 only); 0 USD.

**Units (fixed by R2, commit 193b136, before any outcome is seen).**
1. Every (target, file, function) touched by two or more families in `LIBRARY_CENSUS.json` (21 regions on 5 targets), and
   every pair of families touching it (a region with three families gives three pairs).
2. The two enabling pairs of R2 (pycubrid `protocol.py`, pydal `backends/oracle.py`): the functions where one family creates a
   site of the other.
A unit is a concrete function definition (qualified name) whose lines contain sites of both families; a name with several
definitions gives one unit per definition that qualifies.

**Snapshots per unit.** O (original at the pinned revision), A, B (each family applied to the whole file), AB (A then B), BA
(B then A). Environment: Python 3.12 venv, `install` rule of the target's manifest (as `tools/rq3_target.py`).

**Inputs.** G0 (`gatekeeper_ext/fn_inputs.py`), n = 200, seed 0, generated once on O and replayed on every snapshot; each call
in a fresh process (`tools/fn_probe_inner.py`). An input is *stable* if O gives the same outcome twice; only stable inputs
count. Outcome = return value or exception (type and masked message), as in Study P.

**Measures (per unit).** Loss of a snapshot on an input = 1 if its outcome differs from O, else 0.
- d_A, d_B, d_AB, d_BA: share of stable inputs with loss 1.
- Emergent: AB (or BA) differs from O on an input where neither A nor B does. Masking: A or B differs, AB does not.
  Order dependence: AB and BA differ.
- Non-additivity (Assumption 4 in loss form, l(AB) = l(A) + l(B) per input, losses capped at 1): share of inputs where it fails.
- Gate: for each cell (A, B, AB, BA) the harm certificate and alarm of Studies D–H (eta = 5%, alpha_alarm = 0.05) on the stable
  inputs in generation order, e-Holm at alpha = 0.1 over all cells of the study. Reported: units where both singles are admitted
  and a composite is not, and the reverse.

**Report.** Per unit and in total, by `tools/composition_study.py` in workflow `Gatekeeper Study S compositions`. Units that
cannot be imported or called (e.g. methods of classes that need constructor arguments), or with fewer than 50 stable inputs,
are reported as unusable with the reason, not replaced.

**What S does not show.** "Harm" here is any behaviour change from the original on G0 inputs, not a defect judged by a
developer; G0 inputs may be unrealistic. Descriptive; no hypothesis test.
