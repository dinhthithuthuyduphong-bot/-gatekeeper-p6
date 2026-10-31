"""Sensitivity of every decision to the regression penalty lambda in the loss (paper: "one minus the held-out pass rate plus
0.5 per regression, clipped at 1"; reviewer point A14 in docs/paper/ANTICIPATED_REVIEWS.md).  No model calls.

python tools/loss_weight_sensitivity.py OUT_DIR [--lambdas 0,0.2,0.5,1,2,5]

Part A, recorded draws of Studies D, E, G, H (every scope's trace of [z, regressed]): each draw is one input with one oracle,
i.e. a one-test suite.  For each lambda the per-arm loss min(1, fail + lambda * regression) is recomputed and the paired
difference compared with the recorded z.
  Claim (proof below): for a one-test suite the clipped loss does not depend on lambda >= 0.  If the treated arm fails its loss is
  already 1; if it passes there is no regression to penalise.  So z(lambda) = z for every draw, and every decision, which is a
  deterministic function of the z-trace and the regression flags, is unchanged.
Part B, multi-test suites (the constructed demo targets): the experiment is re-run with gatekeeper_lite.runner.PairedRun.suite_loss
patched to each lambda, and every decision of every comparator, every ground-truth label and the reported Z_suite are compared.
  In the implementation, decisions consume the per-test z (PairedRun.z) and labels the set of new failures; suite_loss is only
  reported, so decisions should be identical and only Z_suite may change.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def loss_one_test(passed, regression, lam):
    return min(1.0, (0.0 if passed else 1.0) + lam * (1 if regression else 0))


def part_a(lambdas):
    draws, scopes, files = 0, 0, 0
    mismatches = {str(l): 0 for l in lambdas}
    for f in sorted(glob.glob(str(ROOT / "study_[degh]/results/RESULT_*.json"))):
        d = json.loads(Path(f).read_text())
        used = False
        for sc in (d.get("scopes") or {}).values():
            trace = sc.get("trace") if isinstance(sc, dict) else None
            if not trace:
                continue
            used, scopes = True, scopes + 1
            for z, regressed in trace:
                draws += 1
                # reconstruct the two outcomes from the record: z = fail_t - fail_w; regressed = passed_w and not passed_t
                if z > 0:
                    pw, pt = True, False
                elif z < 0:
                    pw, pt = False, True
                else:
                    pw = pt = True          # tie: both pass or both fail; both cases give the same losses below
                for lam in lambdas:
                    zl = loss_one_test(pt, pw and not pt, lam) - loss_one_test(pw, False, lam)
                    if abs(zl - z) > 1e-12:
                        mismatches[str(lam)] += 1
        files += used
    return {"studies": "D, E, G, H", "result_files": files, "scopes": scopes, "draws": draws,
            "draws_with_changed_z_per_lambda": mismatches, "decisions_changed": all(v == 0 for v in mismatches.values()) is False}


def run_demo(lam):
    from gatekeeper_lite import runner
    from gatekeeper_lite.experiment import run_experiment
    orig = runner.PairedRun.suite_loss

    def patched(self, arm):
        res = self.baseline if arm == "baseline" else self.treatment
        n = len(res.results)
        fail_rate = len(res.failed()) / n if n else 1.0
        regressions = len(self.new_failures) if arm == "treatment" else 0
        return min(1.0, fail_rate + lam * regressions)

    runner.PairedRun.suite_loss = patched
    try:
        return run_experiment(ROOT / "demo/config.json")
    finally:
        runner.PairedRun.suite_loss = orig


def decisions(result):
    out, zs = {}, {}
    for r in result.get("records") or result.get("pairs") or []:
        key = "%s|%s" % (r.get("cell"), r.get("target"))
        out[key] = {"truth": r.get("ground_truth"), "gatekeeper": (r.get("gatekeeper") or {}).get("decision"),
                    **{c: v.get("decision") for c, v in (r.get("comparators") or {}).items()}}
        zs[key] = (r.get("paired") or {}).get("Z_suite")
    for c in result.get("compositions") or []:
        key = "composition|%s|%s" % ("+".join(c["skills"]), c["target"])
        out[key] = {"truth": c.get("composite_truth"), "gatekeeper": c.get("gatekeeper_composite_decision")}
        zs[key] = c.get("composite_Z")
    return out, zs


def part_b(lambdas):
    base_dec, base_z = decisions(run_demo(0.5))
    rows = {}
    for lam in lambdas:
        dec, zs = decisions(run_demo(lam))
        rows[str(lam)] = {"cells": len(dec), "decisions_or_labels_changed": sorted(k for k in dec if dec[k] != base_dec.get(k)),
                          "z_suite_changed": sum(1 for k in zs if zs[k] != base_z.get(k))}
    return {"targets": "demo (constructed multi-test suites)", "reference_lambda": 0.5, "per_lambda": rows,
            "any_decision_changed": any(r["decisions_or_labels_changed"] for r in rows.values())}


def main(argv):
    out = Path(argv[0])
    lambdas = [float(x) for x in (argv[argv.index("--lambdas") + 1] if "--lambdas" in argv else "0,0.2,0.5,1,2,5").split(",")]
    a, b = part_a(lambdas), part_b(lambdas)
    res = {"lambdas": lambdas, "A_recorded_draws": a, "B_demo_multitest": b,
           "conclusion": ("no decision or label depends on the regression penalty"
                          if not a["decisions_changed"] and not b["any_decision_changed"] else "SOME DECISION DEPENDS ON LAMBDA")}
    out.mkdir(parents=True, exist_ok=True)
    (out / "LOSS_WEIGHT_SENSITIVITY.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0 if res["conclusion"].startswith("no decision") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
