"""Study T analysis (T-A1): ground truth, every decision rule, and the win criteria W1-W4 from the raw trial records.

python tools/market_analyze.py RESULTS_DIR      (reads TRIALS_*.json, MARKET_CENSUS.json, REPLAY.json; writes STUDY_T_RESULT.json)

python tools/market_analyze.py --replay RESULTS_DIR   (B6R: each Ruff rule's documentation example fixed by the pinned Ruff
                                                       equals its "Use instead" code; writes REPLAY.json)
"""
import ast
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import e_holm  # noqa: E402

ETA, ALPHA, C_STAKE, ALARM, N_MAX = 0.05, 0.1, 0.9, 20.0, 200


# ------------------------------------------------------------------ B6R replay
def doc_examples(explanation):
    """(example, use_instead) code blocks from a Ruff rule explanation, or None."""
    m = re.search(r"## Example\s*```(?:python|py)?\n(.*?)```(.*?)Use instead:?\s*```(?:python|py)?\n(.*?)```", explanation or "", re.S)
    return (m.group(1), m.group(3)) if m else None


def same_ast(a, b):
    try:
        return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
    except SyntaxError:
        return False


def replay_rule(code, explanation):
    ex = doc_examples(explanation)
    if not ex:
        return {"replay": False, "why": "no example"}
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "example.py"
        p.write_text(ex[0])
        subprocess.run(["ruff", "check", "--isolated", "--no-cache", "--select", code, "--fix", "--unsafe-fixes", "--exit-zero",
                        str(p)], capture_output=True, text=True, timeout=60)
        fixed = p.read_text()
    ok = same_ast(fixed, ex[1])
    return {"replay": ok, "why": "" if ok else "fixed example differs from 'Use instead'"}


def replay_all(res_dir):
    r = subprocess.run(["ruff", "rule", "--all", "--output-format", "json"], capture_output=True, text=True, check=True)
    rules = {d["code"]: d.get("explanation", "") for d in json.loads(r.stdout)}
    census = json.loads((res_dir / "MARKET_CENSUS.json").read_text())
    used = sorted({rule for p in census["packages"] for rule in p["cells"] if not rule.startswith("R2:")})
    out = {code: replay_rule(code, rules.get(code, "")) for code in used}
    (res_dir / "REPLAY.json").write_text(json.dumps(out, indent=1))
    return out


# ------------------------------------------------------------------ per cell
def usable_functions(cell):
    return [f for f in cell.get("functions", []) if f.get("gate", {}).get("usable") and f.get("ref", {}).get("usable")]


def ground_truth(funcs):
    rates = [sum(map(int, f["ref"]["flags"])) / len(f["ref"]["flags"]) for f in funcs]
    pooled = sum(rates) / len(rates)
    return pooled, pooled >= ETA


def gate_sequence(funcs, n_max=N_MAX):
    """Round-robin over the cell's functions: draw i comes from function i mod m, input i // m."""
    seqs = [list(map(int, f["gate"]["flags"])) for f in funcs]
    out, i = [], 0
    while len(out) < n_max:
        s = seqs[i % len(seqs)]
        j = i // len(seqs)
        if j >= len(s):
            break
        out.append(s[j])
        i += 1
    return out


def gatekeeper(seq, k_cells):
    """Harm certificate and alarm (Proposition 'Harm certificate'); stop at e >= K/alpha, alarm, or the budget.
    Returns (e at the stopping time, 0 if the alarm fired; draws used)."""
    lam = C_STAKE / (1 - ETA)
    nu = min((0.5 - ETA) / (ETA * (1 - ETA)), 0.95 / ETA)
    w = wa = 0.0
    thr, athr = math.log(k_cells / ALPHA), math.log(ALARM)
    for i, x in enumerate(seq, 1):
        w += math.log(1 - C_STAKE) if x else math.log(1 + lam * ETA)
        wa += math.log(1 + nu * (1 - ETA)) if x else math.log(1 - nu * ETA)
        if wa >= athr:
            return 0.0, i
        if w >= thr:
            return math.exp(w), i
    return math.exp(w), len(seq)


def fs_n(k_cells):
    return math.ceil(math.log(ALPHA / k_cells) / math.log(1 - ETA))


# ------------------------------------------------------------------ study
def analyse(res_dir):
    census = json.loads((res_dir / "MARKET_CENSUS.json").read_text())
    k = census["total"]["cells"]
    replay = json.loads((res_dir / "REPLAY.json").read_text()) if (res_dir / "REPLAY.json").exists() else {}
    rows, errors, unusable = [], [], {}
    for p in sorted(res_dir.glob("TRIALS_*.json")):
        t = json.loads(p.read_text())
        if t.get("error"):
            errors.append({"project": t["project"], "error": t["error"]})
            continue
        for rule, cell in t["cells"].items():
            funcs = usable_functions(cell)
            if not funcs:
                why = cell.get("why") or "no function with enough stable inputs in both streams"
                unusable[why] = unusable.get(why, 0) + 1
                continue
            pooled, harmful = ground_truth(funcs)
            seq = gate_sequence(funcs)
            e, used = gatekeeper(seq, k)
            rows.append({"cell": "%s/%s" % (t["project"], rule), "rule": rule, "r2": rule.startswith("R2:"),
                         "applicability": cell["applicability"], "pooled": pooled, "harmful": harmful, "e": e, "g_draws": used,
                         "n_gate": len(seq), "S20": not any(seq[:20]),
                         "FS": len(seq) >= fs_n(k) and not any(seq[:fs_n(k)]), "B8": not any(seq),
                         "RS": cell["applicability"] == "safe",
                         "B6R": bool(replay.get(rule, {}).get("replay")) if not rule.startswith("R2:") else None})
    evals = {r["cell"]: r["e"] for r in rows}
    adm = set(e_holm(evals, ALPHA)) if evals else set()
    for r in rows:
        r["G"] = r["cell"] in adm
        r["U"] = True
    return summarise(rows, errors, unusable, k)


def score(rows, rule):
    sel = [r for r in rows if r.get(rule) is not None]
    return {"cells": len(sel), "harmful_admitted": sum(1 for r in sel if r[rule] and r["harmful"]),
            "safe_admitted": sum(1 for r in sel if r[rule] and not r["harmful"]),
            "harmful_total": sum(1 for r in sel if r["harmful"]), "safe_total": sum(1 for r in sel if not r["harmful"])}


def summarise(rows, errors, unusable, k):
    rules = ["U", "RS", "B6R", "S20", "FS", "B8", "G"]
    ruff_rows = [r for r in rows if not r["r2"]]
    res = {"K": k, "usable_cells": len(rows), "harmful_cells": sum(r["harmful"] for r in rows), "package_errors": errors,
           "unusable_cells": unusable, "fs_draws": fs_n(k),
           "all_cells": {x: score(rows, x) for x in rules if x not in ("RS", "B6R")},
           "ruff_cells": {x: score(ruff_rows, x) for x in rules},
           "mean_draws": {"G": sum(r["g_draws"] for r in rows) / max(1, len(rows)), "S20": 20, "FS": fs_n(k),
                          "B8": sum(r["n_gate"] for r in rows) / max(1, len(rows))}}
    g, rc = res["ruff_cells"]["G"], res["ruff_cells"]
    h = res["harmful_cells"]
    res["W1"] = {"won": res["all_cells"]["G"]["harmful_admitted"] <= math.ceil(ALPHA * h)
                 and all(g["harmful_admitted"] < rc[b]["harmful_admitted"] for b in ("U", "RS", "B6R")),
                 "note": "LJ (T-A2) and T (T-A3) added when run"}
    res["W2"] = {"won": g["safe_admitted"] >= rc["RS"]["safe_admitted"]}
    res["W3"] = {"won": res["mean_draws"]["G"] <= 0.7 * 200 and res["mean_draws"]["G"] <= fs_n(k)}
    res["W4"] = {"won": not any(rc[b]["safe_admitted"] > g["safe_admitted"] and rc[b]["harmful_admitted"] < g["harmful_admitted"]
                                for b in rules if b != "G"),
                 "dominating": [b for b in rules if b != "G" and rc[b]["safe_admitted"] >= g["safe_admitted"]
                                and rc[b]["harmful_admitted"] <= g["harmful_admitted"]
                                and (rc[b]["safe_admitted"], rc[b]["harmful_admitted"]) != (g["safe_admitted"], g["harmful_admitted"])]}
    res["rows"] = rows
    return res


def main(argv):
    if argv[0] == "--replay":
        out = replay_all(Path(argv[1]))
        print(json.dumps({"rules": len(out), "replay_pass": sum(v["replay"] for v in out.values())}))
        return 0
    d = Path(argv[0])
    res = analyse(d)
    (d / "STUDY_T_RESULT.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
