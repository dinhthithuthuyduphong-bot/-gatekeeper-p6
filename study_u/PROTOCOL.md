# Study U: rare partial harm in market patches (written before it is computed)

**Why.** In Study T, harm on lint fixes was blatant, and a 20-draw smoke test matched Gatekeeper. The certificate's claimed advantage
is rare partial harm (harm rate just above η), the regime of the phase diagram (Table 1) and Study H, which so far was only
constructed. Study U measures it on real market artifacts: patches written by LLM coding agents on SWE-bench Verified (Study Q),
all *resolved* (they pass the benchmark's tests), many of which change behaviour on a minority of inputs.

**Data (already recorded, Study Q).** For every scored patch: the number of function-level inputs (G0 and G2, about 400 stable
inputs) on which the patch behaves differently from the developers' fix, both as a *naive difference* and as a *contract
regression* (Study Q's definitions). No new runs.

**Design.**
- **Cell:** one patch.
- **Ground truth and gate draws:** each patch's stable inputs are split at random (seeded per patch) into gate draws
  (first half) and reference draws (second half). Inputs were generated i.i.d., so given the counts, the positions of harmful
  inputs are exchangeable; the split and the order of gate draws are drawn uniformly with a fixed seed.
- **Harm:** contract regression (primary); naive difference (secondary).
- A patch is **harmful** if its reference harm rate is ≥ η = 5%.

**Decision rules (all on the gate draws):**
- **U:** admit every patch. This is "the benchmark's tests pass", since every patch is resolved.
- **S20:** no harm in the first 20.
- **FS:** no harm in the first n_FS = ⌈log(α/K)/log(1−η)⌉ draws, K = number of patches.
- **B8:** no harm in all gate draws.
- **G:** harm certificate (c = 0.9) with alarm, stop at K/α, budget = gate draws; e-Holm at α = 0.1.

**Win criteria (fixed here).**
- **U1:** G admits at most ⌈α·H⌉ harmful patches (H = number of harmful), and fewer than S20 and U.
- **U2:** G admits at least as many non-harmful patches as FS and B8.
- **U3 (rare-harm regime):** among patches with reference harm rate in [5%, 20%), G admits fewer than S20.

**Seeds:** `sha256("study-u:" + patch sha)`. Script `tools/rare_harm_study.py`; workflow `Gatekeeper Study U rare harm`.

## U-A1 (post hoc, written before it is computed): false-discovery control for screening
Retention criterion U2 was lost (Gatekeeper 303 vs always-retest 621 harmless patches kept), because family-wise control over 693
patches needs about 190 clean draws per patch. For screening, false discovery rate is the usual target. U-A1 adds **G-FDR**: the
same e-values, admitted by e-BH at q = 0.1 (Wang & Ramdas 2022) instead of e-Holm. Reported next to G, labelled post hoc; it does not
replace the pre-registered result.
