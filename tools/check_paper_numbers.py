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
Q3 = lambda: J("research_closure/results/study_q/qa1/QA1_THREE_RATERS.json")  # noqa: E731
TH = lambda: J("research_closure/results/theory/THEORY_CHECKS.json")     # noqa: E731
LS = "research_closure/results/library_sim/LIBRARY_SIMULATION.json"
QR = "research_closure/results/study_q/Q_ROBUSTNESS.json"
R2 = "research_closure/results/study_r2/LIBRARY_CENSUS.json"
RG = "research_closure/results/study_r2/LIBRARY_SIMULATION_GRAPH.json"
SS = "research_closure/results/study_s/COMPOSITION_STUDY.json"
SA = "research_closure/results/study_s/COMPOSITION_STUDY_SA1.json"
S2 = "research_closure/results/study_s/COMPOSITION_STUDY_SA2.json"
S3 = "research_closure/results/study_s/COMPOSITION_STUDY_SA3.json"
S5 = "research_closure/results/study_s/COMPOSITION_STUDY_SA5.json"

TC = "research_closure/results/study_t/MARKET_CENSUS.json"
TR = "research_closure/results/study_t/STUDY_T_RESULT.json"
B9 = lambda: J("research_closure/results/study_t/B9_RESULT.json")  # noqa: E731
B9M = lambda: J("research_closure/results/study_t/B9_RESULT_medium.json")  # noqa: E731
B9S = lambda: J("research_closure/results/study_t/B9_RESULT_strong.json")  # noqa: E731
B9T = lambda: [B9(), B9M(), B9S()]  # noqa: E731
UU = lambda: J("research_closure/results/study_u/STUDY_U_RESULT.json")["contract"]  # noqa: E731


def K(n):
    return "{:,}".format(n).replace(",", "{,}")


def t_g_draws():
    rows = [x for x in J(TR)["rows"] if not x["r2"]]
    return sum(x["g_draws"] for x in rows) / len(rows)


MARKET_ROWS = [("U", "Apply every fix (\\texttt{--unsafe-fixes})", "0"), ("RS", "Ruff's \\emph{safe} label (\\texttt{ruff --fix})", "0"),
               ("B6R", "Replay of the rule's documented example (B6-R)", "0"),
               ("B6S", "Replay on all other packages (B6-strong, post hoc)", "0"), ("LJ", "LLM judge reading the diff", "0"),
               ("S20", "Smoke test, $20$ draws", "20"), ("FS", "Fixed-sample test, $199$ draws", "199"),
               ("B8", "Always-retest (B8), $200$ draws", "200"), ("G", "Gatekeeper", None)]
MARKET_TABLE = """Apply every fix (\\texttt{--unsafe-fixes}) & 11 & 1{,}520 & 0 \\\\
Ruff's \\emph{safe} label (\\texttt{ruff --fix}) & 0 & 677 & 0 \\\\
Replay of the rule's documented example (B6-R) & 9 & 996 & 0 \\\\
Replay on all other packages (B6-strong, post hoc) & 2 & 1{,}256 & 0 \\\\
LLM judge reading the diff & 6 & 1{,}128 & 0 \\\\
Smoke test, $20$ draws & 0 & 1{,}518 & 20 \\\\
Fixed-sample test, $199$ draws & 0 & 1{,}492 & 199 \\\\
Always-retest (B8), $200$ draws & 0 & 1{,}506 & 200 \\\\
Gatekeeper & 0 & 1{,}512 & 198.5 \\\\"""


def market_table():
    rc = J(TR)["ruff_cells"]
    return "\n".join("%s & %s & %s & %s \\\\" % (label, K(rc[k]["harmful_admitted"]), K(rc[k]["safe_admitted"]), d or "%.1f" % t_g_draws())
                     for k, label, d in MARKET_ROWS)


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
    ("theory C9 draws", "needs $110$ clean draws", lambda: "needs $%d$ clean draws" % TH()["C9_harm_certificate"]["clean_draws_family16"]),
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
    ("S-A1 usable", "($12$ usable, S-A1)", lambda: "($%d$ usable, S-A1)" % J(SA)["total"]["usable"]),
    ("S-A5 usable", "In the final run $16$ functions were usable and $7$ could not be called",
     lambda: "In the final run $%d$ functions were usable and $%d$ could not be called" % (J(S5)["total"]["usable"],
                                                                                        J(S5)["total"]["units"] - J(S5)["total"]["usable"])),
    ("S-A5 final", "No\ncomposition changed behaviour where both of its parts kept it, none masked a change of a part, and none depended on the order",
     lambda: "No\ncomposition changed behaviour where both of its parts kept it, none masked a change of a part, and none depended on the order"
     if all(J(S5)["total"][k] == 0 for k in ("units_emergent", "units_masking", "units_order_dependent")) else "CHANGED"),
    ("S-A2 noise unit", "an apparent order\ndependence on one input of",
     lambda: "an apparent order\ndependence on %s input of" % {1: "one"}[sum(1 for u in J(S2)["units"] if u.get("order_dependent"))]),
    ("S-A3 IS_STRONG", "on $29$ of\n$200$ inputs",
     lambda: "on $%d$ of\n$%d$ inputs" % next((u["counts"]["B"], u["stable"]) for u in J(S5)["units"] if u.get("qualname") == "IS_STRONG.validate")),
    ("S-A5 gate", "over all $64$ cells, the gate rejected exactly the $3$ cells",
     lambda: "over all $%d$ cells, the gate rejected exactly the $%d$ cells" % (J(S5)["total"]["cells"], J(S5)["total"]["cells"] - J(S5)["total"]["cells_admitted"])),
    ("S-A5 admitted", "admitted the other $61$", lambda: "admitted the other $%d$" % J(S5)["total"]["cells_admitted"]),
    ("S-A5 limited", "the evidence is limited to $16$ functions", lambda: "the evidence is limited to $%d$ functions" % J(S5)["total"]["usable"]),
    ("Q-A1 generator changed", "re-generating it gave a different program for $17$ of the other $19$ units",
     lambda: "re-generating it gave a different program for $%d$ of the other $%d$ units" % (
         sum(1 for x in J("research_closure/results/study_q/qa1/REPRO.json")["units"] if not x["reproduced"] and not x["same_generator"]),
         sum(1 for x in J("research_closure/results/study_q/qa1/REPRO.json")["units"] if not x["reproduced"]))),
    ("Q-A1 three raters", "$5/36$ ($13.9\\%$, Wilson $6.1$--$28.7\\%$) units have no confirmed regression",
     lambda: "$%d/%d$ ($%s\\%%$, Wilson $%s$--$%s\\%%$) units have no confirmed regression" % (
         Q3()["without_majority_regression"]["k"], Q3()["without_majority_regression"]["n"], pct(Q3()["without_majority_regression"]["share"]),
         pct(Q3()["without_majority_regression"]["wilson95"][0]), pct(Q3()["without_majority_regression"]["wilson95"][1]))),
    ("rater calibration", "both model raters coded all $20$ items of a calibration set with known\ncodes correctly",
     lambda: "both model raters coded all $%d$ items of a calibration set with known\ncodes correctly" % (
         20 if all(J("research_closure/results/model_reviews/RATER_CALIBRATION_%s.json" % m)["accuracy"] == 1.0
                   for m in ("vertex-gemini-argon", "vertex-gemini-flash")) else -1)),
    ("T census", "The census found $2{,}578$ cells ($235$ skills)",
     lambda: "The census found $%s$ cells ($%d$ skills)" % (K(J(TC)["total"]["cells"]), J(TC)["total"]["skills_with_a_cell"])),
    ("T usable", "$1{,}559$ cells were usable ($1{,}531$ Ruff cells) and $12$ were harmful",
     lambda: "$%s$ cells were usable ($%s$ Ruff cells) and $%d$ were harmful" % (
         K(J(TR)["usable_cells"]), K(J(TR)["ruff_cells"]["G"]["cells"]), J(TR)["harmful_cells"])),
    ("T table body", MARKET_TABLE, market_table),
    ("T G vs RS", "Gatekeeper kept $1{,}512$ safe fixes\nagainst $677$, and admitted $771$ of the $788$ cells Ruff labels unsafe",
     lambda: "Gatekeeper kept $%s$ safe fixes\nagainst $%s$, and admitted $%s$ of the $%s$ cells Ruff labels unsafe" % (
         K(J(TR)["ruff_cells"]["G"]["safe_admitted"]), K(J(TR)["ruff_cells"]["RS"]["safe_admitted"]),
         K(sum(1 for x in J(TR)["rows"] if not x["r2"] and x["applicability"] == "unsafe" and x["G"])),
         K(sum(1 for x in J(TR)["rows"] if not x["r2"] and x["applicability"] == "unsafe")))),
    ("T draws", "($198.5$ draws per cell against $200$)", lambda: "($%.1f$ draws per cell against $200$)" % t_g_draws()),
    ("T smoke", "kept $1{,}518$ safe fixes and cost a tenth", lambda: "kept $%s$ safe fixes and cost a tenth" % K(J(TR)["ruff_cells"]["S20"]["safe_admitted"])),
    ("T unusable", "$1{,}019$ cells were unusable", lambda: "$%s$ cells were unusable" % K(J(TR)["K"] - J(TR)["usable_cells"])),
    ("T blatant", "above $30\\%$ in $8$ of the $11$ cells",
     lambda: "above $30\\%%$ in $%d$ of the $%d$ cells" % (sum(1 for x in J(TR)["rows"] if x["harmful"] and not x["r2"] and x["pooled"] > 0.3),
                                                         sum(1 for x in J(TR)["rows"] if x["harmful"] and not x["r2"]))),
    ("abstract: market", "admitted $9$ and $6$ of $11$, and it kept $2.2$ times as many safe fixes",
     lambda: "admitted $%d$ and $%d$ of $%d$, and it kept $%.1f$ times as many safe fixes" % (
         J(TR)["ruff_cells"]["B6R"]["harmful_admitted"], J(TR)["ruff_cells"]["LJ"]["harmful_admitted"], J(TR)["ruff_cells"]["G"]["harmful_total"],
         J(TR)["ruff_cells"]["G"]["safe_admitted"] / J(TR)["ruff_cells"]["RS"]["safe_admitted"])),
    ("T untestable share", "and $40\\%$ of the cells could not be\ntested",
     lambda: "and $%d\\%%$ of the cells could not be\ntested" % round(100 * (J(TR)["K"] - J(TR)["usable_cells"]) / J(TR)["K"])),
    ("T B6-strong", "It admitted $2$ harmful cells and kept $1{,}256$ safe ones",
     lambda: "It admitted $%d$ harmful cells and kept $%s$ safe ones" % (J(TR)["ruff_cells"]["B6S"]["harmful_admitted"], K(J(TR)["ruff_cells"]["B6S"]["safe_admitted"]))),
    ("U setup", "($44$ patches, $33$ of them between $5\\%$ and $20\\%$)",
     lambda: "($%d$ patches, $%d$ of them between $5\\%%$ and $20\\%%$)" % (UU()["harmful"], UU()["band_5_20"]["patches"])),
    ("U patches", "records of the $693$ resolved SWE-bench Verified", lambda: "records of the $%d$ resolved SWE-bench Verified" % UU()["patches"]),
    ("U smoke", "Passing the tests admitted all $44$, and the $20$-draw smoke test admitted $10$, all\nin the $5$--$20\\%$ band",
     lambda: "Passing the tests admitted all $%d$, and the $20$-draw smoke test admitted $%d$, %s\nin the $5$--$20\\%%$ band" % (
         UU()["scores"]["U"]["harmful_admitted"], UU()["scores"]["S20"]["harmful_admitted"],
         "all" if UU()["band_5_20"]["admitted"]["S20"] == UU()["scores"]["S20"]["harmful_admitted"] else "not all")),
    ("U retention", "Gatekeeper kept $303$ of $649$ harmless patches, the fixed-sample test $299$, and always-retest, which has no error\nguarantee, $621$",
     lambda: "Gatekeeper kept $%d$ of $%d$ harmless patches, the fixed-sample test $%d$, and always-retest, which has no error\nguarantee, $%d$" % (
         UU()["scores"]["G"]["safe_admitted"], UU()["safe"], UU()["scores"]["FS"]["safe_admitted"], UU()["scores"]["B8"]["safe_admitted"])),
    ("U zero", "Gatekeeper, the fixed-sample test and always-retest admitted none",
     lambda: "Gatekeeper, the fixed-sample test and always-retest admitted none" if all(UU()["scores"][x]["harmful_admitted"] == 0 for x in ("G", "FS", "B8")) else "X"),
    ("U draws", "(about $149$ on average)", lambda: "(about $%d$ on average)" % round(UU()["mean_draws"]["B8"])),
    ("abstract: U", "passing the tests admitted all $44$ harmful patches, the smoke test $10$, Gatekeeper none",
     lambda: "passing the tests admitted all $%d$ harmful patches, the smoke test $%d$, Gatekeeper %s" % (
         UU()["scores"]["U"]["harmful_admitted"], UU()["scores"]["S20"]["harmful_admitted"], "none" if UU()["scores"]["G"]["harmful_admitted"] == 0 else "some")),
    ("abstract: B6-strong", "(a strong B6) still admitted $2$", lambda: "(a strong B6) still admitted $%d$" % J(TR)["ruff_cells"]["B6S"]["harmful_admitted"]),
    ("abstract: U patches", "not on $693$ resolved SWE-bench agent patches", lambda: "not on $%d$ resolved SWE-bench agent patches" % UU()["patches"]),
    ("U-A1 e-BH", "kept $626$ harmless patches and still admitted no harmful one",
     lambda: "kept $%d$ harmless patches and still admitted %s harmful one" % (UU()["scores"]["G_FDR"]["safe_admitted"],
                                                                             "no" if UU()["scores"]["G_FDR"]["harmful_admitted"] == 0 else "a")),
    ("B9 harm", "in\n$10$ of $148$ evaluable cells, $2$ of them cells where Ruff's own fix is harmless, and $6$ of its replies did not parse",
     lambda: "in\n$%d$ of $%d$ evaluable cells, $%d$ of them cells where Ruff's own fix is harmless, and $%d$ of its replies did not parse" % (
         B9()["b9_harmful_applied"], B9()["evaluable_b9"], B9()["b9_harmful_among_truth_safe"], B9()["b9_unparsable_functions"])),
    ("B9 sample", "On $150$\nStudy T cells (all $11$ harmful ones and $139$ drawn at random)",
     lambda: "On $%d$\nStudy T cells (all $%d$ harmful ones and $%d$ drawn at random)" % (
         B9()["cells"], J(TR)["ruff_cells"]["G"]["harmful_total"], B9()["cells"] - J(TR)["ruff_cells"]["G"]["harmful_total"])),
    ("B9 G", "admitted no harmful cell.  The model cost", lambda: "admitted %s harmful cell.  The model cost" % ("no" if B9()["g_harmful_admitted"] == 0 else "a")),
    ("B9 cost", "$0.0080$ USD and $16.9$ seconds per cell, Gatekeeper's trials $2.3$ seconds of a hosted\nrunner ($0.0003$ USD)",
     lambda: "$%.4f$ USD and $%.1f$ seconds per cell, Gatekeeper's trials $%.1f$ seconds of a hosted\nrunner ($%.4f$ USD)" % (
         B9()["cost_per_cell"]["b9_usd"], B9()["cost_per_cell"]["b9_seconds"], B9()["cost_per_cell"]["g_seconds"], B9()["cost_per_cell"]["g_usd_runner"])),
    ("abstract: B9 tiers", "was $26$ to $88$ times as expensive and changed\nbehaviour in $9$ to $11$ cells",
     lambda: "was $%d$ to $%d$ times as expensive and changed\nbehaviour in $%d$ to $%d$ cells" % (
         min(round(t["cost_per_cell"]["b9_usd"] / t["cost_per_cell"]["g_usd_runner"]) for t in B9T()),
         max(round(t["cost_per_cell"]["b9_usd"] / t["cost_per_cell"]["g_usd_runner"]) for t in B9T()),
         min(t["b9_harmful_applied"] for t in B9T()), max(t["b9_harmful_applied"] for t in B9T()))),
    ("B9 medium", "changed\nbehaviour in $9$ of $123$ evaluable cells ($52$ replies did not parse",
     lambda: "changed\nbehaviour in $%d$ of $%d$ evaluable cells ($%d$ replies did not parse" % (
         B9M()["b9_harmful_applied"], B9M()["evaluable_b9"], B9M()["b9_unparsable_functions"])),
    ("B9 medium cost", "$0.0246$ USD per cell, and the strongest", lambda: "$%.4f$ USD per cell, and the strongest" % B9M()["cost_per_cell"]["b9_usd"]),
    ("B9 strong", "(gemini-4-argon) in $11$ of $148$, $2$ of them harmless under Ruff's\nfix, at $0.0147$ USD per cell",
     lambda: "(gemini-4-argon) in $%d$ of $%d$, $%d$ of them harmless under Ruff's\nfix, at $%.4f$ USD per cell" % (
         B9S()["b9_harmful_applied"], B9S()["evaluable_b9"], B9S()["b9_harmful_among_truth_safe"], B9S()["cost_per_cell"]["b9_usd"])),
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
