"""Study Q classification of one input where the original agrees with the fix and the patch does not (protocol section 4).
Outcomes come from tools/q_probe_inner.py: ["ok", type, repr] or ["exc", type, message, "explicit"|"incidental"] or
["timeout"]."""


def category(gold, patch):
    if not isinstance(gold, list) or not isinstance(patch, list) or gold == ["timeout"] or patch == ["timeout"]:
        return "C3"
    if gold[0] == "ok":
        return "C1"                                   # the fix returns: any difference is a regression on a valid input
    if patch[0] == "ok" and len(gold) > 3 and gold[3] == "explicit":
        return "C2-D"                                 # the fix rejects on purpose (explicit raise in project code), the patch accepts
    return "C2-O"                                     # rejection that is incidental, or both reject


CONTRACT = ("C1", "C2-D")


def summarise(outcomes):
    """outcomes: list of {"source", "i", "orig", "gold", "patch", "patch_stable"} (capture mode of fn_draws)."""
    cats, by_source, n = {}, {}, 0
    for x in outcomes:
        if not x.get("patch_stable"):
            continue
        n += 1
        if x["orig"] != x["gold"] or x["patch"] == x["gold"]:
            continue
        c = category(x["gold"], x["patch"])
        cats[c] = cats.get(c, 0) + 1
        s = by_source.setdefault(x["source"], {})
        s[c] = s.get(c, 0) + 1
    naive = sum(cats.values())
    contract = sum(cats.get(c, 0) for c in CONTRACT)
    return {"scored": n, "categories": cats, "by_source": by_source, "naive_harm": naive, "contract_harm": contract,
            "c1_only_harm": cats.get("C1", 0), "divergent": sum(1 for x in outcomes if x.get("patch_stable") and x["patch"] != x["gold"])}
