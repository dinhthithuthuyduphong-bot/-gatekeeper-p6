# Paper alignment and corrections — 26 October 2026

## Claim boundaries

The current evidence supports scope-conditioned admission for two frozen transformations and selected prospective/retrospective examples. It does not show a new learned-skill synthesis algorithm, general safe reuse, broad composition robustness, or cross-model performance. Study L's failed feasibility gate is useful negative evidence about the attempted call-replay mechanism on exposed targets, not proof that automatic oracles cannot work.

Use “gold-reference differential oracle”, not “oracle-free”. Gold fixes are a reference with limited intended domain, not universal semantic truth. Type-confusion tests and mutated assertions may leave that domain. A candidate equal to gold gives a vacuous no-harm comparison; show that column separately.

L-A1 changes the benefit criterion to upstream fail-to-pass qualification while the registered comparison table still mentions theta. State this as a substantive protocol clarification/change before outcomes, with exact chronology. Do not describe the whole amendment as merely adding tool hashes. A fresh confirmatory study must reconcile the estimand and comparator contracts before freeze.

## Correction to the P0 snippet: certificate inversion

The code `HarmCertEProcess(eta, frac=0.9)` uses lambda = c/(1-eta). On a zero-harm path, for a candidate threshold m:

    E_n(m) = [1 + c*m/(1-m)]^n
    q = 160^(1/n)
    U_c = (q - 1)/(q - 1 + c), c = 0.9

For the illustrative family-Bonferroni threshold 160:

| Zero-harm draws | Inverting this c=0.9 certificate | Fixed-n zero-success binomial upper bound at alpha=1/160 |
|---:|---:|---:|
| 110 | 4.9850% | 4.5090% |
| 300 | 1.8604% | 1.6775% |

Therefore 4.5% / 1.7% in `paper_snippets/P0_AND_PHASE_DIAGRAM.md` are not the inversion of this c=0.9 process. The fixed-n binomial formula is `1 - alpha^(1/n)`; it must not be presented as an anytime-valid interval at an adaptively selected stopping time. At n=300 fixed in advance, the usual one-sided 95% zero-harm binomial bound is about 0.9936%; it is a different confidence level and is not a simultaneous family certificate.

These are elementary formula recalculations, not new simulation results. The separate claims of 12,000 repetitions and 0.63%/0.56% in the snippet were not backed by a corresponding raw receipt in the files examined here. Do not replace measured primary tables with a pooled 0.6% until seeds, scripts, event definitions and raw outputs have been matched. The original 0.9% and 0.2% may come from distinct simulations; numerical disagreement alone does not establish that they estimate exactly the same event.

## Phase diagram is a conditional harm-only analysis

`tools/gate_phase_diagram.py` samples only Bernoulli harm indicators. It does not run a benefit process, and uses threshold 10 for one patch, not 160 for 16 cells. “Always helps (help rate 0.5)” is internally inconsistent wording; use “benefit assumed qualified; harm-only comparison”. Its output is not empirical evidence of partial harm on real patches.

The code also stores alarm_t as a zero-based index, while adm_t is one-based. The tie convention may be intentional (alarm priority), but the reported mean consumed draws on alarm paths is one too small. Keep the frozen output unchanged and correct this in a separately versioned analysis with a documented tie rule and uncertainty intervals before reporting draw savings.

For c=0.9, eta=0.05, positive expected log-growth requires:

    h < log(1+c*eta/(1-eta)) / [log(1+c*eta/(1-eta)) - log(1-c)]
      = 0.0197034465.

This is a power/growth property of one betting strategy. The policy tolerance remains eta=5%; do not relabel its risk guarantee as 2%. Mixture vs fixed-sample comparisons must match horizon, family size and operational error criterion; 1000 vs 300 draws is not equal budget.

## A* research route: ordered milestones, not acceptance promises

1. **Measurement validity first.** Run the supplied integrity patch on D5/D2, inspect retained collection and signatures, then D4. Stop generating empirical claims while missingness/nondeterminism is unresolved. Known-good gold controls need held-out independent assertions or multiple references. Test error text is a diagnostic signal, not itself a calibrated functional-loss oracle.
2. **Freeze a new measurement design.** Define valid input domain, observation abstraction, environmental-error treatment, exact sampling law, discovery versus confirmation split and exposure ledger. If mutation units are sampled without replacement, derive the finite-population procedure or use genuinely fresh iid sampling; do not replay an iid proof onto deduplicated units. Prefer revising input literals while retaining assertions, and quantify excluded/invalid draws without post-outcome selection.
3. **Measure real patch utility.** First screen public plausible patches without paid generation. Count exclusions and dependency clusters. Estimate held-out harm with confidence intervals and keep boundary-ambiguous patches unclassified; 10,000 draws is not exact ground truth. Do not select only patches where Gatekeeper beats smoke.
4. **Compare strong matched policies.** Census-only, replay+full environment/dependency fingerprint, smoke, B8+, fixed-sample IUT and sequential admission. Report harmful admitted, useful retained, useful rejected, neutral admitted, and ambiguous/invalid separately at patch and repository levels. D5 illustrates a policy-margin tradeoff, not automatically a failure of statistics.
5. **Test utility and cost on the new cohort.** Same observations and target budget; stop actual execution for the sequential policy. Include oracle construction, setup, census, generation and execution accounting; report paired differences and uncertainty by target. No delay injection represented as a real workload. Negative outcomes remain publishable only with a substantive generalizable insight, not because a gate was preregistered.
6. **Model robustness only when measured.** Compare raw and gated outcomes for the same patch, then vary model under controlled context/scaffold/budget. Public outputs of different agents conflate those factors. Paid B9 remains HOLD until measurement and comparison contracts are sound. Model calls are not automatically required for a narrowly framed non-model methodological paper.

Study L's internal thresholds 5/6, 40 instances, 150 patches, 15 partial-harm patches and 40% savings are planning gates, not A* acceptance standards. Do not lower them after failure. New-method development can continue under a new protocol; it cannot erase the failed attempt.

## Venue and paper packaging

FSE 2027's official Research Track CFP lists originality, significance, soundness, evaluation and related work as criteria. It currently states the extended submission deadline was 3 October 2026 AoE; this is already past. Do not invent a forthcoming FSE 2027 initial submission window. Verify the next appropriate A* cycle before fixing a schedule.

The original private FSE-2027-13 draft explicitly labels all numeric results as projected. Its title and private identifier do not establish a published, peer-reviewed baseline. Position this work as an independently evidenced bounded study, and distinguish inherited theory from new technical/empirical contributions. The newest G1/TM and correction material also means the previously generated 18-page report is now an older checkpoint, not a current submission-ready manuscript.

Primary venue source: https://conf.researchr.org/track/fse-2027/fse-2027-papers (checked 26 October 2026, Asia/Bangkok).
