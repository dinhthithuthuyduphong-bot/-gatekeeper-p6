"""Researcher-authored draw oracle derived from upstream NULL query tests.

Tier-1 evidence is the unchanged upstream pytest modules, not this adapter.
SQLite is in memory. The entire database and mapper registry are fresh per draw.
"""


def scopes():
    def make(rng, null):
        return {"null": null, "kind": rng.choice(["relationship", "proxy"]),
                "values": [rng.choice([None, 1, 2]) for _ in range(rng.randint(1, 8))]}
    return {"null_semantics": lambda rng: make(rng, True),
            "plain_queries": lambda rng: make(rng, False)}


def execute(d):
    import sqlalchemy as sa
    from sqlalchemy.orm import Session, declarative_base, relationship
    from sqlalchemy.ext.associationproxy import association_proxy
    Base = declarative_base()

    class Parent(Base):
        __tablename__ = "parents"
        id = sa.Column(sa.Integer, primary_key=True)
        detail_id = sa.Column(sa.ForeignKey("details.id"), nullable=True)
        detail = relationship("Detail")
        detail_value = association_proxy("detail", "value")

    class Detail(Base):
        __tablename__ = "details"
        id = sa.Column(sa.Integer, primary_key=True)
        value = sa.Column(sa.Integer, nullable=True)

    class Child(Base):
        __tablename__ = "children"
        id = sa.Column(sa.Integer, primary_key=True)
        parent_id = sa.Column(sa.ForeignKey("parents.id"), nullable=True)
        parent = relationship("Parent")

    engine = sa.create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as s:
            s.add_all([Detail(id=1, value=None), Detail(id=2, value=1)])
            if d["kind"] == "relationship":
                s.add_all([Parent(id=1), Parent(id=2)])
                s.add_all([Child(id=i+1, parent_id=v) for i,v in enumerate(d["values"])])
            else:
                s.add_all([Parent(id=i+1, detail_id=v) for i,v in enumerate(d["values"])])
            s.commit()
            # Fixture/import failures above are harness failures, not functional evidence.
            try:
                if d["kind"] == "relationship":
                    parent = s.get(Parent, 1)
                    predicate = Child.parent != parent if d["null"] else Child.parent == parent
                    q = sa.select(Child.id).where(predicate).order_by(Child.id)
                else:
                    predicate = Parent.detail_value == None if d["null"] else Parent.detail_value == 1  # noqa: E711
                    q = sa.select(Parent.id).where(predicate).order_by(Parent.id)
                return {"ok": True, "ids": s.scalars(q).all(), "sql": str(q),
                        "module": sa.__file__}
            except Exception as exc:
                return {"ok": False, "exception": type(exc).__name__, "message": str(exc),
                        "module": sa.__file__}
    finally:
        engine.dispose()
        Base.registry.dispose()


def judge(scope, d, without, with_):
    if d["kind"] == "relationship":
        chosen = lambda v: v != 1 if d["null"] else v == 1
    else:
        chosen = lambda v: v in (None, 1) if d["null"] else v == 2
    expected = [i+1 for i,v in enumerate(d["values"]) if chosen(v)]
    return (without.get("ok") and without.get("ids") == expected,
            with_.get("ok") and with_.get("ids") == expected)
