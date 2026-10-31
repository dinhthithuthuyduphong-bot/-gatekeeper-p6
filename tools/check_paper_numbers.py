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
R2 = "research_closure/results/study_r2/LIBRARY_CENSUS.json"
RG = "research_closure/results/study_r2/LIBRARY_SIMULATION_GRAPH.json"
SS = "research_closure/results/study_s/COMPOSITION_STUDY.json"
SA = "research_closure/results/study_s/COMPOSITION_STUDY_SA1.json"

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
    ("theory C10 decision rule", "family-wise false admission rate was $2.4\\%$ and $7.3\\%$",
     lambda: "family-wise false admission rate was $%s\\%%$ and $%s\\%%$" % (
         pct(TH()["C10_decision_rule_studies_DH"]["benefit_boundary"]["familywise_false_admission"]),
         pct(TH()["C10_decision_rule_studies_DH"]["harm_boundary"]["familywise_false_admission"]))),
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
    ("R2 census", "($655$ non-test files) found $59$ single-skill cells,\n$3.7$ per repository, touching $467$ functions, of which $21$ are touched by two or more families",
     lambda: "($%d$ non-test files) found $%d$ single-skill cells,\n$%.1f$ per repository, touching $%d$ functions, of which $%d$ are touched by two or more families" % (
         J(R2)["total"]["files_scanned"], J(R2)["total"]["cells"], J(R2)["total"]["mean_cells_per_target"], J(R2)["total"]["functions_touched"],
         J(R2)["total"]["functions_touched_by_two_or_more"])),
    ("R2 targets/families", "over all $16$ target repositories at their pinned revisions",
     lambda: "over all $%d$ target repositories at their pinned revisions" % J(R2)["total"]["cloned"]),
    ("R2 pairs", "Of the $136$ family pairs that\nmeet in some repository, $18$ overlap, and the execution rule requires $6$ composite cells",
     lambda: "Of the $%d$ family pairs that\nmeet in some repository, $%d$ overlap, and the execution rule requires $%d$ composite cells" % (
         J(R2)["total"]["family_pairs_possible"], J(R2)["total"]["family_pairs_overlapping"], J(R2)["total"]["composite_cells_required"])),
    ("R2 shared commute", "all $21$ such pairs that share a function commute",
     lambda: "all $%d$ such pairs that share a function commute" % (J(R2)["total"]["interaction_shared_function"]["file_pairs"]
                                                                   if J(R2)["total"]["interaction_shared_function"]["non_commuting"] == 0 else -1)),
    ("R2 disjoint non-commuting", "Two pairs\nwith \\emph{disjoint} footprints do not",
     lambda: "%s pairs\nwith \\emph{disjoint} footprints do not" % {2: "Two"}.get(J(R2)["total"]["interaction_disjoint_functions"]["non_commuting"], "?")),
    ("R2 missed by static", "In\n\\texttt{pydal} the original-code footprints",
     lambda: "In\n\\texttt{%s} the original-code footprints" % {"G1_pydal": "pydal"}[J(R2)["with_enabling_edges"]["total"]["missed_by_static"][0][0]]),
    ("R2 commuting disjoint", "among the $80$ such file pairs of Study R2 none",
     lambda: "among the $%d$ such file pairs of Study R2 none" % (J(R2)["total"]["interaction_disjoint_functions"]["file_pairs"]
                                                                  - J(R2)["total"]["interaction_disjoint_functions"]["non_commuting"])),
    ("R2 graph sim", "Re-running the simulation on the $13$ measured libraries",
     lambda: "Re-running the simulation on the $%d$ measured libraries" % J(RG)["libraries"]),
    ("R2 graph sim P1", "executed a harmful component in $7.1\\%$ of libraries at $q=0.3$ ($14.5\\%$ when every\noverlapping pair is harmful), ours in $0/1{,}000$",
     lambda: "executed a harmful component in $%s\\%%$ of libraries at $q=0.3$ ($%s\\%%$ when every\noverlapping pair is harmful), ours in $%d/1{,}000$" % (
         pct(J(RG)["main"]["P1"]["harmful_component_rate"]), pct(J(RG)["sweep_bad_pair_prob"]["1.0"]["P1"]["harmful_component_rate"]),
         round(1000 * J(RG)["main"]["P2"]["harmful_component_rate"]))),
    ("R2 graph sim reuse", "$1.64$ instead of $1.96$ beneficial skills executed",
     lambda: "$%.2f$ instead of $%.2f$ beneficial skills executed" % (J(RG)["main"]["P2"]["mean_beneficial_skills_executed"],
                                                                      J(RG)["main"]["P1"]["mean_beneficial_skills_executed"])),
    ("S registered usable", "As registered only $2$ of $23$ could be called",
     lambda: "As registered only $%d$ of $%d$ could be called" % (J(SS)["total"]["usable"], J(SS)["total"]["units"])),
    ("S-A1 usable", "(post hoc amendment S-A1) $12$ were usable",
     lambda: "(post hoc amendment S-A1) $%d$ were usable" % J(SA)["total"]["usable"]),
    ("S-A1 unusable split", "could not be installed ($9$, one repository) or called ($2$)",
     lambda: "could not be installed ($%d$, one repository) or called ($%d$)" % (
         sum(1 for u in J(SA)["units"] if not u.get("usable") and "import failed" in u.get("why", "")),
         sum(1 for u in J(SA)["units"] if not u.get("usable") and "import failed" not in u.get("why", "")))),
    ("S-A1 no emergent/order", "no composition changed behaviour where both of its parts\nkept it and none depended on the order",
     lambda: "no composition changed behaviour where both of its parts\nkept it and none depended on the order"
     if J(SA)["total"]["units_emergent"] == 0 and J(SA)["total"]["units_order_dependent"] == 0 else "CHANGED"),
    ("S-A1 IS_STRONG", "on\n$23$ of $200$ inputs",
     lambda: "on\n$%d$ of $%d$ inputs" % next((u["counts"]["B"], u["stable"]) for u in J(SA)["units"] if u.get("qualname") == "IS_STRONG.validate")),
    ("S-A1 gate", "over all $48$ cells, the gate rejected\nexactly the $3$ cells",
     lambda: "over all $%d$ cells, the gate rejected\nexactly the $%d$ cells" % (J(SA)["total"]["cells"], J(SA)["total"]["cells"] - J(SA)["total"]["cells_admitted"])),
    ("S-A1 admitted", "admitted the other $45$", lambda: "admitted the other $%d$" % J(SA)["total"]["cells_admitted"]),
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
