from fakedb import FakeDB, TransientError
from store import save


def _flaky(k):
    db = FakeDB(precommit_failures=k)
    assert save(db, {"id": k}) is True
    assert db.records == [{"id": k}]


def _nonblocking(i):
    db = FakeDB()
    save(db, {"id": i})
    assert db.blocking_calls == 0, "blocking API used"


def _normal(i):
    db = FakeDB()
    save(db, {"id": i})
    assert len(db.records) == 1


def _no_duplicates(k, i):
    db = FakeDB(ack_loss=k)
    try:
        save(db, {"id": i})
    except TransientError:
        pass
    assert len(db.records) <= 1, f"duplicate writes: {len(db.records)}"


def cases():
    out = [(f"flaky_precommit_{k}", lambda k=k: _flaky(k)) for k in (1, 2)]
    out += [(f"nonblocking_{i}", lambda i=i: _nonblocking(i)) for i in range(3)]
    out += [(f"normal_{i}", lambda i=i: _normal(i)) for i in range(3)]
    out += [(f"no_duplicate_writes_{k}_{i}", lambda k=k, i=i: _no_duplicates(k, i))
            for k in (1, 2, 3) for i in range(2)]
    return out
