"""Check that the measured numbers quoted in the paper's LaTeX sections match the result files they come from.
python tools/check_paper_numbers.py [LATEX_DIR]   (default docs/paper/latex/sections)

Each claim: (label, the exact string that must appear in the LaTeX, a function recomputing that string from a result file).
Exit 1 if any recomputed value differs from the quoted one or the quoted string is missing.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def J(rel):
    return json.loads((ROOT / rel).read_text())


def pct(x, d=1):
    return ("%." + str(d) + "f") % (100 * x)


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / den, (c + h) / den


QA = lambda: J("research_closure/results/study_q/Q_ANALYSIS.json")       # noqa: E731
QA1 = lambda: J("research_closure/results/study_q/qa1/QA1_RESULT.json")  # noqa: E731
PA = lambda: J("research_closure/results/study_p/P_ANALYSIS.json")       # noqa: E731
RQ3 = lambda: J("research_closure/results/rq3/RQ3_SUMMARY.json")         # noqa: E731
TH = lambda: J("research_closure/results/theory/THEORY_CHECKS.json")     # noqa: E731
LS = "research_closure/results/library_sim/LIBRARY_SIMULATION.json"
QR = "research_closure/results/study_q/Q_ROBUSTNESS.json"
RC = "research_closure/results/study_r/FOOTPRINT_CENSUS.json"

CLAIMS = [
    ("Q usable instances", "$245$ instances usable", lambda: "$%d$ instances usable" % QA()["Q1_funnel"]["FINISHED"]),
    ("Q scored patches", "$694$ patches", lambda: "$%d$ patches" % QA()["patches_scored"]),
    ("Q2 share", "$43.1\\%$", lambda: "$%s\\%%$" % pct(QA()["Q2_divergent"]["share"])),
    ("Q4 share and Wilson", "$11.1\\%$ (Wilson $9.0$--$13.6\\%$)",
     lambda: "$%s\\%%$ (Wilson $%s$--$%s\\%%$)" % (pct(QA()["Q4_contract_regression"]["share"]), pct(QA()["Q4_contract_regression"]["wilson95"][0]),
                                                pct(QA()["Q4_contract_regression"]["wilson95"][1]))),
    ("HQ1", "$6/55$ ($10.9\\%$, Wilson $5.1$--$21.8\\%$",
     lambda: "$%d/%d$ ($%s\\%%$, Wilson $%s$--$%s\\%%$" % (QA()["HQ1"]["without_contract_regression"], QA()["HQ1"]["units"], pct(QA()["HQ1"]["share"]),
                                                       pct(QA()["HQ1"]["wilson95"][0]), pct(QA()["HQ1"]["wilson95"][1]))),
    ("Q-A1 reproduced", "$36$ reproduced exactly", lambda: "$%d$ reproduced exactly" % QA1()["reproduced"]),
    ("Q-A1 agreement", "$87.7\\%$ of $154$ items", lambda: "$%s\\%%$ of $%d$ items" % (pct(QA1()["agreement_share"]), QA1()["items"])),
    ("Q-A1 main", "$8/36$ ($22.2\\%$, Wilson $11.7$--$38.1\\%$)",
     lambda: "$%d/%d$ ($%s\\%%$, Wilson $%s$--$%s\\%%$)" % (QA1()["without_confirmed_regression"]["k"], QA1()["without_confirmed_regression"]["n"],
                                                        pct(QA1()["without_confirmed_regression"]["share"]),
                                                        pct(QA1()["without_confirmed_regression"]["wilson95"][0]),
                                                        pct(QA1()["without_confirmed_regression"]["wilson95"][1]))),
    ("Q-A1 sensitivity", "$11/36$ ($18.0$--$46.9\\%$)",
     lambda: "$%d/36$ ($%s$--$%s\\%%$)" % (QA1()["without_confirmed_regression"]["k"] + 3, pct(wilson(QA1()["without_confirmed_regression"]["k"] + 3, 36)[0]),
                                          pct(wilson(QA1()["without_confirmed_regression"]["k"] + 3, 36)[1]))),
    ("P primary", "$16/205=7.8\\%$ (Wilson $4.9$--$12.3\\%$)",
     lambda: "$%d/%d=%s\\%%$ (Wilson $%s$--$%s\\%%$)" % (PA()["PRIMARY"]["in_band"], PA()["PRIMARY"]["plausible"], pct(PA()["PRIMARY"]["share"]),
                                                      pct(PA()["PRIMARY"]["wilson95"][0]), pct(PA()["PRIMARY"]["wilson95"][1]))),
    ("P census admits", "admitted all $16$ patches", lambda: "admitted all $%s$ patches" % PA()["RQ4"]["census_only"]["admits_inadmissible"].split("/")[0]),
    ("P smoke admits", "smoke test admitted $2$", lambda: "smoke test admitted $%s$" % PA()["RQ4"]["smoke20"]["admits_inadmissible"].split("/")[0]),
    ("RQ3 G2", "$11/14$ detection decisions (Cohen's $\\kappa=0.57$)",
     lambda: "$%d/%d$ detection decisions (Cohen's $\\kappa=%.2f$)" % (RQ3()["G2"]["agree"], RQ3()["G2"]["targets"], RQ3()["G2"]["kappa"])),
    ("RQ3 G0", "$8/14$ ($\\kappa=0.19$)", lambda: "$%d/%d$ ($\\kappa=%.2f$)" % (RQ3()["G0"]["agree"], RQ3()["G0"]["targets"], RQ3()["G0"]["kappa"])),
    ("theory C2", "family-wise\nfalse admission rate of our e-process is $0.45$, against $0.05$",
     lambda: "family-wise\nfalse admission rate of our e-process is $%.2f$, against $%.2f$" % (TH()["C2_budget_per_cell_vs_per_scope"]["familywise_shared"],
                                                                                         TH()["C2_budget_per_cell_vs_per_scope"]["familywise_split"])),
    ("theory C9 draws", "=110$ clean draws", lambda: "=%d$ clean draws" % TH()["C9_harm_certificate"]["clean_draws_family16"]),
    ("loss-weight sensitivity draws", "Recomputing all $7{,}200$ recorded draws",
     lambda: "Recomputing all $%s$ recorded draws" % "{:,}".format(J("research_closure/results/sensitivity/LOSS_WEIGHT_SENSITIVITY.json")["A_recorded_draws"]["draws"]).replace(",", "{,}")),
    ("library sim P1 q=0.3", "in $27.9\\%$ of the\nlibraries at $q=0.3$",
     lambda: "in $%s\\%%$ of the\nlibraries at $q=0.3$" % pct(J(LS)["main"]["P1"]["harmful_component_rate"])),
    ("library sim sweep", "($9.9\\%$ at $q=0.1$, $42.4\\%$ at $q=0.5$)",
     lambda: "($%s\\%%$ at $q=0.1$, $%s\\%%$ at $q=0.5$)" % (pct(J(LS)["sweep_bad_pair_prob"]["0.1"]["P1"]["harmful_component_rate"]),
                                                         pct(J(LS)["sweep_bad_pair_prob"]["0.5"]["P1"]["harmful_component_rate"]))),
    ("library sim P2 zero", "($0/1{,}000$ at every $q$",
     lambda: "($%d/1{,}000$ at every $q$" % max(round(r["P2"]["harmful_component_rate"] * 1000) for r in [J(LS)["main"]] + list(J(LS)["sweep_bad_pair_prob"].values()))),
    ("library sim reuse", "$3.59$ instead of $4.48$",
     lambda: "$%.2f$ instead of $%.2f$" % (J(LS)["main"]["P2"]["mean_beneficial_skills_executed"], J(LS)["main"]["P1"]["mean_beneficial_skills_executed"])),
    ("library sim masked", "harmful in only $5.4\\%$ of libraries",
     lambda: "harmful in only $%s\\%%$ of libraries" % pct(J(LS)["main"]["P1"]["harmful_execution_rate"])),
    ("abstract: library sim", "ran a harmful composition in $28\\%$ of libraries",
     lambda: "ran a harmful composition in $%d\\%%$ of libraries" % round(100 * J(LS)["main"]["P1"]["harmful_component_rate"])),
    ("Q robustness HQ1 range", "between\n$8.2\\%$ and $16.7\\%$ (largest Wilson upper bound $31.9\\%$",
     lambda: "between\n$%s\\%%$ and $%s\\%%$ (largest Wilson upper bound $%s\\%%$" % (pct(J(QR)["HQ1_share_range"][0]), pct(J(QR)["HQ1_share_range"][1]),
                                                                              pct(J(QR)["HQ1_max_upper_bound"]))),
    ("Q robustness Q4 range", "between $8.2\\%$ and\n$14.0\\%$",
     lambda: "between $%s\\%%$ and\n$%s\\%%$" % (pct(J(QR)["Q4_range"][0]), pct(J(QR)["Q4_range"][1]))),
    ("study R census", "scanned $655$ non-test source files: the \\texttt{bool} guard touches\n$104$ functions and the \\texttt{None}-comparison rewrite $16$, and only $1$ function is touched by both",
     lambda: "scanned $%d$ non-test source files: the \\texttt{bool} guard touches\n$%d$ functions and the \\texttt{None}-comparison rewrite $%d$, and only $%d$ function is touched by both" % (
         J(RC)["total"]["files_scanned"], J(RC)["total"]["repo_functions_bool"], J(RC)["total"]["repo_functions_none"], J(RC)["total"]["repo_functions_both"])),
    ("study R targets", "over all $16$ target repositories", lambda: "over all $%d$ target repositories" % J(RC)["total"]["cloned"]),
    # abstract (main.tex)
    ("abstract: plausible patches", "in $205$ plausible LLM patches", lambda: "in $%d$ plausible LLM patches" % PA()["PRIMARY"]["plausible"]),
    ("abstract: census admits", "the test census admitted all $16$ with partial\nbehavioural differences",
     lambda: "the test census admitted all $%s$ with partial\nbehavioural differences" % PA()["RQ4"]["census_only"]["admits_inadmissible"].split("/")[0]),
    ("abstract: factor ~4 (Q2/Q4)", "changes by a factor of about four with its definition",
     lambda: "changes by a factor of about %s with its definition" % {3: "three", 4: "four", 5: "five"}[round(QA()["Q2_divergent"]["share"] / QA()["Q4_contract_regression"]["share"])]),
]


def main(argv):
    d = Path(argv[0]) if argv else ROOT / "docs/paper/latex/sections"
    files = sorted(d.glob("*.tex")) + ([d.parent / "main.tex"] if (d.parent / "main.tex").is_file() else [])
    text = "\n".join(p.read_text() for p in files)
    flat = " ".join(text.split())
    bad = 0
    for label, quoted, fn in CLAIMS:
        try:
            got = fn()
        except (KeyError, FileNotFoundError) as exc:
            print("MISSING SOURCE  %-22s %s" % (label, exc))
            bad += 1
            continue
        q, g = " ".join(quoted.split()), " ".join(got.split())
        ok_match, ok_present = q == g, q in flat
        if not (ok_match and ok_present):
            bad += 1
        print("%-6s %-22s quoted=%r recomputed=%r in_latex=%s" % ("OK" if ok_match and ok_present else "FAIL", label, q, g, ok_present))
    print("%d/%d claims verified" % (len(CLAIMS) - bad, len(CLAIMS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
