"""Post-freeze, read-only anytime-valid confidence sequences for Study D/E.

Assumptions: i.i.d. draws within each frozen declared scope, bounded paired
loss difference Z in [-1,1], and regression indicator X in {0,1}. This is
an EXPLORATORY presentation layer, NOT the frozen e-process decision rule.

For each study separately, 95% family-simultaneous, time-uniform, two-sided
Hoeffding CS are formed by a union bound across 2*K series and all n >= 1:
  delta = alpha_family / (2*K)
  delta_n = delta / (n*(n+1))
  width_n = (b-a)*sqrt(log(2/delta_n)/(2*n)).
The telescoping series sum_n 1/(n(n+1)) = 1. The intervals are simultaneous
over all times and cells (under stated assumptions); dependency across cells
does not harm the union bound. The CS need not be tight and do NOT replace
the frozen harm certificate. Scope with no draws is not estimable.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def bounded_cs(sample_mean: float, n: int, lo: float, hi: float, delta: float) -> tuple[float, float]:
    if not n > 0 or not 0 < delta < 1 or not lo < hi:
        raise ValueError("n > 0, 0 < delta < 1, lo < hi required")
    if not lo <= sample_mean <= hi:
        raise ValueError("sample mean outside known bounds")
    delta_n = delta / (n * (n + 1))
    radius = (hi - lo) * math.sqrt(math.log(2 / delta_n) / (2 * n))
    return max(lo, sample_mean - radius), min(hi, sample_mean + radius)


def cell_row(cell: str, result: dict, alpha_family: float, K: int) -> dict:
    target_id, scope = cell.split("/", 1)
    scopes = result.get("scopes", {})
    sc = scopes.get(scope)
    if not sc:
        return {"cell": cell, "n": 0, "status": "OUT_OF_SCOPE", "estimable": False}
    n = sc["draws"]
    if n <= 0:
        return {"cell": cell, "n": 0, "status": sc["decision"], "estimable": False}
    trace = sc["trace"]
    if len(trace) < n:
        raise ValueError(f"{cell}: trace shorter than actual stopped draw count")
    prefix = trace[:n]  # later full-budget B8 draws CANNOT influence stopping-time CS
    zs = [float(pair[0]) for pair in prefix]
    xs = [int(pair[1]) for pair in prefix]
    if any(z not in (-1.0, 0.0, 1.0) for z in zs):
        raise ValueError(f"{cell}: unexpected non-discrete Z; inspect raw trace")
    if any(x not in (0, 1) or x != int(z > 0) for x, z in zip(xs, zs)):
        raise ValueError(f"{cell}: inconsistent regression and paired-loss trace")
    counts = {"help": sum(z < 0 for z in zs), "tie": sum(z == 0 for z in zs),
              "hurt": sum(z > 0 for z in zs)}
    for key in counts:
        if counts[key] != sc["counts"][key]:
            raise ValueError(f"{cell}: prefix count mismatch for {key}")
    mu = sum(zs) / n
    h = sum(xs) / n
    delta_per_series = alpha_family / (2 * K)
    ci_mu = bounded_cs(mu, n, -1, 1, delta_per_series)
    ci_h = bounded_cs(h, n, 0, 1, delta_per_series)
    return {"cell": cell, "n": n, "status": sc["decision"],
            "estimable": True, "mu": mu, "h": h,
            "mu_CS": ci_mu, "h_CS": ci_h, "trace_total": len(trace),
            "counts": counts}


def analyze(root: Path, study: str, alpha_family: float = .05) -> dict:
    if study not in ("study_d", "study_e"):
        raise ValueError("study must be study_d or study_e")
    sroot = root / study
    config = json.loads((sroot / ("config_study_d.json" if study == "study_d" else "config_study_e.json")).read_text())
    cells = config["cells"]
    results = {}
    for f in (sroot / "results").glob("RESULT_*.json"):
        if not f.name.startswith("RESULT_B9_"):
            data = json.loads(f.read_text())
            if data["target"] in results:
                raise ValueError("Duplicate target in raw results")
            results[data["target"]] = data
    expected_targets = {c.split("/")[0] for c in cells}
    if not expected_targets <= set(results):
        raise ValueError(f"Missing raw targets: {sorted(expected_targets - set(results))}")
    rows = [cell_row(cell, results[cell.split("/")[0]], alpha_family, len(cells))
            for cell in cells]
    return {"study": study, "analysis": "POST_FREEZE_EXPLORATORY",
            "family_confidence": 1 - alpha_family, "simultaneous_for": "both mu/h across all declared K cells and all n",
            "K": len(cells), "rows": rows}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--out", type=Path, default=Path("out_phase2"))
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = [analyze(args.root, s) for s in ("study_d", "study_e")]
    (args.out / "CS_D_E_EXPLORATORY.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    rows = ["# Frozen Study D/E — exploratory time-uniform confidence sequences", "",
            "95% family-simultaneous CS per study (2*K outcomes, all stopping times).",
            "**Not** the e-Holm decision rule; post-freeze descriptive computation.",
            "**Important:** Upper harm CS may exceed eta even if the *e-based harm certificate* admitted.",
            "The two inferential methods have different widths and spending designs.",
            "", "| Study | Cell | n stopped | Status | mu_hat | mu CS | h_hat | h CS |",
            "|---|---|---:|---|---:|---|---:|---|"]
    for group in results:
        for row in group["rows"]:
            if not row["estimable"]:
                rows.append(f'| {group["study"]} | {row["cell"]} | 0 | {row["status"]} | — | — | — | — |')
                continue
            mi,ma=row["mu_CS"];hi,ha=row["h_CS"]
            rows.append(f'| {group["study"]} | {row["cell"]} | {row["n"]} | {row["status"]} | '
                        f'{row["mu"]:+.3f} | [{mi:+.3f}, {ma:+.3f}] | '
                        f'{row["h"]:.3f} | [{hi:.3f}, {ha:.3f}] |')
    rows += ["", "Assumptions: bounded i.i.d. draws within each declared scope; no claims about independent cells.",
             "Full B8 trace tails are excluded after the actual Gatekeeper stopping draw.",
             "Rows with no admitted sample are not estimated; no artificial zeros.",
             ""]
    (args.out / "CS_D_E_EXPLORATORY.md").write_text("\n".join(rows),encoding="utf-8")
    print("Generated family-simultaneous CS for D/E, no API calls")


if __name__=="__main__":
    main()
