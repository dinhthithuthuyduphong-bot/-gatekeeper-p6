# Study J: independent validation design, not a completed study

Status: DRAFT_NO_NEW_OUTCOMES. API budget: USD 0. B9 stays HOLD.
The eligible target roster is deliberately empty: no unseen targets or oracle evidence are fabricated.
`tools/prospective_preflight.py` must report BLOCKED until the required evidence exists.

`CANDIDATE_SELECTION.json` and `CANDIDATE_ROSTER.json` record a preliminary,
convenience-ordered source-screening pool, not a publicly randomized cohort.
The completed static screen is `research_closure/results/candidate_screen/`:
12 pinned repositories, 37 bool-guard sites, no none-identity sites. No upstream
tests or treatment were executed. Possible test-name/literal references are
unverified leads, not tier-1 oracles. The candidate list cannot satisfy the
six-repositories-per-skill goal. The confirmatory selection procedure below
still needs a public, outcome-blind roster and independent baseline vetting.

## Question and scope

Does the fixed two-skill admission policy retain useful patches and block harmful
patches on independently selected repositories, relative to a stronger replay +
fingerprint + smoke baseline and fixed-size tests with the same risk allowance?
This study cannot establish model independence; Study F answers a separate,
within-model deployment-filter question when recorded provider evidence exists.

## Selection before treatment outcomes

1. Publicly commit the discovery policy and a closed candidate roster, with the
   order of inspection fixed by a future public random beacon. Include at least
   12 distinct repositories, at least six per skill. This is a feasibility target,
   not a promise of statistical power across repositories.
2. Exclude all previously outcome-inspected repositories. The checked-in list is
   a minimum exposure inventory extracted from repository manifests, not proof
   of never having seen any other repository. Record the researcher's additional
   disclosures. Do not call new commits/seeds of SQLAlchemy/NetworkX unseen repos.
3. Pin source commits, license, source replay and executable upstream oracle
   provenance. Establish baseline environment, collection and generator semantics
   without running the treatment. Record every screened candidate and reason for
   exclusion, including unbound, unavailable dependency, flaky and missing oracle.
4. Freeze the complete target manifest, skill hashes, scopes, mixture weights,
   selection ledger and runnable adapters in a public commit BEFORE treatment.
   Only after that obtain the beacon receipt. A local PRE_EXECUTION file or a
   commit made after discovering a helpful result is not public preregistration.
5. Keep every registered case in its declared family. Environment-invalid cases
   are reported, not replaced until a nice result appears. A baseline failure
   does not become evidence of beneficial repair.

Do not select only historical bug fixes: that selects on the desired outcome.
Do not impose a quota of positive/harmful outcomes after running treatment.

## Oracles and exposure

Upstream tests used as behavioral witnesses stay unchanged. Researcher-authored
generators are described and graded separately. For each generator report the
fraction of inputs reaching the edited lines and paths, ties, help and hurt.
The deployment distribution is the declared generator mixture, not an unknown
real-world workload. A stress-only scope must not be reported as overall usage.
Any post hoc stratification is a separate analysis with its own estimand.

## Deployment unit and statistical comparison

The unit admitted is an entire patch. Require benefit in at least one scope AND
low harm in every declared scope. Primary uses the existing F-A2 patch e-value,
full n_max=300 observations and e-Holm over all registered patches. Invalid census,
missing scope or alarm vetoes deployment. This full-budget policy makes no primary
claim about early-stop savings. Sequential alternatives are secondary candidates.

The fixed-size comparator uses n=200 and n=300, reported as TWO policies, never
choosing the winner after looking at outcomes. With S scopes, form

    p_patch = max(min(1, S * min_s p_benefit_s), max_s p_harm_s)

and apply Holm over the registered patches. Benefit p-values use bounded-mean
Hoeffding; harm p-values use a binomial lower tail. No extra alpha/2 split inside
the union null is needed. Report that Hoeffding can be conservative; this is not
a claim to implement the strongest possible fixed-size method.

## Strong comparators

- Source replay must use a pinned real upstream fix and upstream tests; a small
  self-authored replay fixture is separately labeled, not called full GSE.
- Fingerprints include interpreter, relevant dependency versions and declared
  compatibility rules. Rules are fixed before target outcomes; matching an
  inventory without a specified acceptance policy is not a baseline.
- The smoke variant adds five visible paired draws per scope on an independent
  seed; its selection inputs are distinct from held-out scoring inputs.
- Census-only is measured directly. SQLAlchemy already demonstrates a case in
  which census detects the harm; no superiority over census is presumed.
- Stronger baselines receive the same executable oracles and edit rights where
  the compared decision requires them. Count both generation and validation work.

## Metrics and failure conditions

For each repo: submitted patch, selected module census, all per-draw observations,
admission decision, held-out benefit/harm, errors, coverage, and wall-clock split
into install/download, setup/import, test execution and policy overhead.
Use paired within-repository contrasts. Repeats measure stability, not new repos.
Compare harmful deployment AND retention of beneficial patches; a reject-all
policy is not a successful system. Do not claim dominance if one endpoint worsens.
Report each skill separately. Twelve repos are still a small external-validity
sample; a wide interval or an inconclusive result is an allowed outcome.

## What is still blocked

New pinned eligible targets, executable independent oracles, a public freeze and
post-freeze outcomes are not present. This document and the preflight prevent
mislabeling old evidence; they do not substitute for the missing experiment.


## Exposure update, 25/10/2026

Study K inspected outcomes in historical python-control and published harmful outcomes in Airflow. Both are now in `EXCLUDED_PRIOR_REPOS.json`; neither is a fresh Study J target. The 11-repository static search and 14 snapshots in Study K add no eligible cohort. Study J remains BLOCKED.
