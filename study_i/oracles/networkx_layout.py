"""Exploratory layout scopes. Upstream witness is stored separately, unchanged.

The draw oracle is researcher-authored, based on the documented fixed-node
contract. It checks finite coordinates, output shape and fixed coordinates;
it does NOT establish optimal layout quality. Each call resets NumPy's RNG.
Both dense and sparse internal solvers are exercised on small graphs.
"""
import math


def scopes():
    def make(rng, given):
        n = rng.randint(3, 12)
        return {"n": n, "backend": rng.choice(["dense", "sparse"]),
                "given": given, "seed": rng.randrange(2**31),
                "positions": [[rng.uniform(-2, 2), rng.uniform(-2, 2)] for _ in range(n)],
                "fixed": sorted(rng.sample(list(range(n)), rng.randint(1, n - 1))),
                "edges": [[i, j] for i in range(n) for j in range(i + 1, n)
                          if rng.random() < 0.3]}
    return {"given_positions": lambda rng: make(rng, True),
            "default_positions": lambda rng: make(rng, False)}


def execute(d):
    import networkx as nx
    import numpy as np
    np.random.seed(d["seed"])
    graph = nx.Graph()
    graph.add_nodes_from(range(d["n"]))
    graph.add_edges_from(d["edges"])
    layout = nx.drawing.layout
    # Setup failures remain harness errors. Only target call exceptions are outcomes.
    if d["backend"] == "dense":
        matrix = nx.to_numpy_matrix(graph, dtype=float)
        function = layout._fruchterman_reingold
    else:
        matrix = nx.to_scipy_sparse_matrix(graph, dtype=float)
        function = layout._sparse_fruchterman_reingold
    kwargs = {"iterations": 5}
    if d["given"]:
        kwargs.update(pos=np.asarray(d["positions"], dtype=float),
                      fixed=np.asarray(d["fixed"], dtype=int))
    try:
        result = function(matrix, **kwargs)
        return {"ok": True, "positions": result.tolist(), "module": nx.__file__}
    except Exception as exc:
        return {"ok": False, "exception": type(exc).__name__, "message": str(exc),
                "module": nx.__file__}


def valid(d, outcome):
    if not outcome.get("ok"):
        return False
    pos = outcome.get("positions", [])
    if len(pos) != d["n"] or any(len(row) != 2 for row in pos):
        return False
    if not all(math.isfinite(x) for row in pos for x in row):
        return False
    return not d["given"] or all(
        abs(pos[i][j] - d["positions"][i][j]) < 1e-10
        for i in d["fixed"] for j in range(2))


def judge(scope, d, without, with_):
    if scope == "given_positions":
        return valid(d, without), valid(d, with_)
    return valid(d, without), (valid(d, with_) and
                              with_.get("positions") == without.get("positions"))
