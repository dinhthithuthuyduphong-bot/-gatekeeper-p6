"""Study G oracle for web2py/pydal (HARM candidate, provenance tier 1).

pydal's own tests (tests/nosql.py, e.g. lines 425-426 and 628-638 at the pinned commit) assert
that `field == None` / `!= None` build IS NULL / IS NOT NULL queries:
    assertEqual(db(db.tt.aa == None).count(), 0); assertEqual(db(db.tt.aa != None).count(), 3)
    assertTrue(db.tt(id, aa=None) == None)
Expected behaviour is therefore computed from the rows inserted by the draw (ground truth).
Scope 'null': queries involving None.  Scope 'plain': queries without None (differential).
"""


def scopes():
    def null_gen(rng):
        n = rng.randint(1, 8)
        return {"nulls": [rng.random() < 0.5 for _ in range(n)],
                "q": rng.choice(["eq_none_count", "ne_none_count", "lookup_first_none", "all_count"])}

    def plain_gen(rng):
        n = rng.randint(1, 8)
        return {"vals": [rng.randint(-50, 50) for _ in range(n)], "v": rng.randint(-50, 50),
                "q": rng.choice(["eq_count", "gt_count", "all_ids"])}
    return {"null": null_gen, "plain": plain_gen}


def execute(d):
    from pydal import DAL, Field
    try:
        db = DAL("sqlite:memory")
        db.define_table("t", Field("a", "integer"))
        if "nulls" in d:
            for i, isnull in enumerate(d["nulls"]):
                db.t.insert(a=None if isnull else i + 1)
            q = d["q"]
            if q == "eq_none_count":
                out = db(db.t.a == None).count()      # noqa: E711  (pydal query semantics)
            elif q == "ne_none_count":
                out = db(db.t.a != None).count()      # noqa: E711
            elif q == "lookup_first_none":
                out = db.t(1, a=None) is not None
            else:
                out = db(db.t).count()
        else:
            for v in d["vals"]:
                db.t.insert(a=v)
            q = d["q"]
            if q == "eq_count":
                out = db(db.t.a == d["v"]).count()
            elif q == "gt_count":
                out = db(db.t.a > d["v"]).count()
            else:
                out = [r.id for r in db(db.t).select(db.t.id, orderby=db.t.id)]
        db.close()
        return {"ok": True, "out": out}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "null":
        nulls = d["nulls"]
        expected = {"eq_none_count": sum(nulls), "ne_none_count": len(nulls) - sum(nulls),
                    "lookup_first_none": bool(nulls[0]), "all_count": len(nulls)}[d["q"]]
        ok = lambda o: o["ok"] and o["out"] == expected
        return ok(without), ok(with_)
    return True, with_ == without
