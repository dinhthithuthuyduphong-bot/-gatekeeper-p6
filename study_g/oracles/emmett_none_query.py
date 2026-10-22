"""Study G oracle for emmett (HARM candidate, provenance tier 1).

emmett's own test tests/test_orm_row.py::test_rowclass builds the database exactly as below
and queries `One.where(lambda m: m.id != None)`; `Model.all()` builds the same `id != None`
query internally (emmett/orm/models.py).  Expected results are computed from the rows the draw
inserts.  Scope 'null': queries that involve None; scope 'plain': queries without None
(differential).  The database is created once per worker process, as the upstream fixture does
once per module; each draw runs inside a fresh migration (up / down), as the upstream
function-scoped fixture does.
"""
import tempfile
import uuid

_STATE = {}


def _db():
    if "db" not in _STATE:
        from emmett import App, sdict
        from emmett.orm import Database, Field, Model

        class GkOne(Model):
            tablename = "gk_one"
            foo = Field.string(notnull=True)
            bar = Field.string()

        root = tempfile.mkdtemp(prefix="gk_emmett_")
        app = App(__name__, root_path=root)
        db = Database(app, config=sdict(uri=f"sqlite://{uuid.uuid4().hex}.db", auto_connect=True))
        db.define_models(GkOne)
        _STATE.update(db=db, model=GkOne)
    return _STATE["db"], _STATE["model"]


def scopes():
    def null_gen(rng):
        n = rng.randint(1, 8)
        return {"nulls": [rng.random() < 0.5 for _ in range(n)],
                "q": rng.choice(["id_ne_none_count", "all_count", "bar_eq_none_count", "bar_ne_none_count"])}

    def plain_gen(rng):
        n = rng.randint(1, 8)
        return {"bars": [f"v{rng.randint(0, 5)}" for _ in range(n)], "v": f"v{rng.randint(0, 5)}",
                "q": rng.choice(["bar_eq_count", "first_foo"])}
    return {"null": null_gen, "plain": plain_gen}


def execute(d):
    from emmett.orm.migrations.utils import generate_runtime_migration
    try:
        db, One = _db()
        migration = generate_runtime_migration(db)
        migration.up()
        try:
            if "nulls" in d:
                for i, isnull in enumerate(d["nulls"]):
                    One.create(foo=f"f{i}", bar=None if isnull else f"b{i}")
                q = d["q"]
                if q == "id_ne_none_count":
                    out = One.where(lambda m: m.id != None).count()      # noqa: E711  upstream test usage
                elif q == "all_count":
                    out = One.all().count()
                elif q == "bar_eq_none_count":
                    out = One.where(lambda m: m.bar == None).count()     # noqa: E711
                else:
                    out = One.where(lambda m: m.bar != None).count()     # noqa: E711
            else:
                for i, b in enumerate(d["bars"]):
                    One.create(foo=f"f{i}", bar=b)
                if d["q"] == "bar_eq_count":
                    out = One.where(lambda m: m.bar == d["v"]).count()
                else:
                    r = One.first()
                    out = r.foo if r else None
            db.commit()
        finally:
            migration.down()
        return {"ok": True, "out": out}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__, "msg": str(exc)[:160]}


def judge(scope, d, without, with_):
    if scope == "null":
        nulls = d["nulls"]
        expected = {"id_ne_none_count": len(nulls), "all_count": len(nulls),
                    "bar_eq_none_count": sum(nulls), "bar_ne_none_count": len(nulls) - sum(nulls)}[d["q"]]
        ok = lambda o: o["ok"] and o["out"] == expected
        return ok(without), ok(with_)
    return True, with_ == without
