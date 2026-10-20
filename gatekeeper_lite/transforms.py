"""Skill procedures (pi) as deterministic AST-guided source rewrites.

Every transform:
  * locates candidate sites in the target source (AST matching),
  * checks applicability preconditions and ABSTAINS (fails closed) when unsure,
  * rewrites only the matched source span, so formatting/comments elsewhere survive,
  * reports the interaction footprint K of what it touched.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


class Abstain(Exception):
    """Raised when a transform refuses to apply (fail closed)."""

    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


@dataclass
class Site:
    lineno: int
    function: str
    snippet: str


@dataclass
class ApplyResult:
    source: str
    sites: List[Site]
    footprint: List[str] = field(default_factory=list)


# ---------------------------------------------------------------- helpers
def _parents(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child._gk_parent = node  # type: ignore[attr-defined]


def _parent(node: ast.AST) -> Optional[ast.AST]:
    return getattr(node, "_gk_parent", None)


def _enclosing_function(node: ast.AST) -> str:
    cur = _parent(node)
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
        cur = _parent(cur)
    return "<module>"


def _bound_names(tree: ast.AST) -> set:
    """Names (re)bound anywhere in the module: assignments, defs, imports, args."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, ast.arg):
            names.add(node.arg)
    return names


def _defined_symbol(tree: ast.Module, name: str) -> bool:
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if any((a.asname or a.name.split(".")[-1]) == name for a in node.names):
                return True
        elif isinstance(node, ast.ClassDef) and node.name == name:
            return True
        elif isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == name for t in node.targets
        ):
            return True
    return False


class _Offsets:
    """Convert AST (line, utf-8 column) positions into string offsets."""

    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines(keepends=True)
        self.starts = [0]
        for line in self.lines:
            self.starts.append(self.starts[-1] + len(line))

    def offset(self, lineno: int, col_utf8: int) -> int:
        line = self.lines[lineno - 1]
        col = len(line.encode("utf-8")[:col_utf8].decode("utf-8", errors="ignore"))
        return self.starts[lineno - 1] + col

    def span(self, node: ast.AST) -> Tuple[int, int]:
        return (self.offset(node.lineno, node.col_offset),
                self.offset(node.end_lineno, node.end_col_offset))

    def text(self, node: ast.AST) -> str:
        a, b = self.span(node)
        return self.source[a:b]


def _apply_edits(source: str, edits: List[Tuple[int, int, str]]) -> str:
    out = source
    for start, end, text in sorted(edits, key=lambda e: e[0], reverse=True):
        out = out[:start] + text + out[end:]
    return out


def _same(a: ast.AST, b: ast.AST) -> bool:
    return ast.dump(a) == ast.dump(b)


def _is_isinstance(node: ast.AST, subject: Optional[ast.AST] = None,
                   type_name: Optional[str] = None) -> bool:
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "isinstance" and len(node.args) == 2):
        return False
    if subject is not None and not _same(node.args[0], subject):
        return False
    if type_name is not None:
        t = node.args[1]
        names = [e.id for e in t.elts if isinstance(e, ast.Name)] if isinstance(t, ast.Tuple) \
            else ([t.id] if isinstance(t, ast.Name) else [])
        return type_name in names
    return True


# -------------------------------------------------------------- base class
class Transform:
    name = "base"
    behaviors: Tuple[str, ...] = ()
    shadow_sensitive: Tuple[str, ...] = ()

    def find(self, tree: ast.Module) -> List[ast.AST]:
        raise NotImplementedError

    def check(self, tree: ast.Module, node: ast.AST) -> Optional[str]:
        return None

    def edits(self, tree: ast.Module, node: ast.AST, off: _Offsets) -> List[Tuple[int, int, str]]:
        raise NotImplementedError

    def module_edits(self, tree: ast.Module, off: _Offsets) -> List[Tuple[int, int, str]]:
        return []

    def touched(self, node: ast.AST) -> List[str]:
        return []

    def apply(self, source: str, single_site: bool = True) -> ApplyResult:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise Abstain("PARSE_ERROR", str(exc))
        _parents(tree)
        nodes = self.find(tree)
        if not nodes:
            raise Abstain("NO_MATCH")
        shadowed = sorted(set(self.shadow_sensitive) & _bound_names(tree))
        if shadowed:
            raise Abstain("BUILTIN_SHADOWED", ",".join(shadowed))
        live = []
        for node in nodes:
            reason = self.check(tree, node)
            if reason:
                if single_site:
                    raise Abstain(reason, f"line {node.lineno}")
                continue
            live.append(node)
        if not live:
            raise Abstain("NO_APPLICABLE_SITE")
        if single_site and len(live) > 1:
            raise Abstain("MULTIPLE_MATCHES", f"{len(live)} sites")
        off = _Offsets(source)
        edits, sites, footprint = [], [], set(f"behavior:{b}" for b in self.behaviors)
        for node in live:
            edits.extend(self.edits(tree, node, off))
            func = _enclosing_function(node)
            sites.append(Site(node.lineno, func, off.text(node)))
            footprint.add(f"func:{func}")
            footprint.update(self.touched(node))
        edits.extend(self.module_edits(tree, off))
        new_source = _apply_edits(source, edits)
        ast.parse(new_source)  # the rewrite must stay valid Python
        return ApplyResult(new_source, sites, sorted(footprint))


# ----------------------------------------------------------- transforms
class EmptyStringGuard(Transform):
    """X == ""  ->  isinstance(X, str) and X == ""   (Click #3298 family)."""

    name = "empty_string_guard"
    behaviors = ("eq-empty-string", "default-display")
    shadow_sensitive = ("str", "isinstance")

    def __init__(self, functions=None, subjects=None, function_patterns=None):
        # Optional anchors: only sites inside these functions (exact names or name
        # substrings) and on these subject expressions.
        self.functions = set(functions or [])
        self.function_patterns = tuple(function_patterns or ())
        self.subjects = set(subjects or [])

    def find(self, tree):
        out = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Compare) and len(node.ops) == 1
                    and isinstance(node.ops[0], ast.Eq)
                    and isinstance(node.comparators[0], ast.Constant)
                    and node.comparators[0].value == ""
                    and not isinstance(node.left, ast.Constant)):
                func = _enclosing_function(node)
                if (self.functions or self.function_patterns) and not (
                        func in self.functions
                        or any(p in func for p in self.function_patterns)):
                    continue
                if self.subjects and ast.unparse(node.left) not in self.subjects:
                    continue
                out.append(node)
        return out

    def check(self, tree, node):
        parent = _parent(node)
        if isinstance(parent, ast.BoolOp) and isinstance(parent.op, ast.And):
            idx = parent.values.index(node)
            if any(_is_isinstance(v, node.left, "str") for v in parent.values[:idx]):
                return "ALREADY_GUARDED"
        return None

    def edits(self, tree, node, off):
        a, b = off.span(node)
        subject = off.text(node.left)
        return [(a, b, f"(isinstance({subject}, str) and {off.text(node)})")]

    def touched(self, node):
        return [f"subject:{ast.unparse(node.left)}"]


class NegativeTypeGuard(Transform):
    """isinstance(X, B)  ->  (isinstance(X, B) and not isinstance(X, T)), T a subtype of B."""

    name = "negative_type_guard"
    behaviors = ("type-check",)

    def __init__(self, base: str = "int", excluded: str = "bool"):
        self.base, self.excluded = base, excluded
        self.shadow_sensitive = ("isinstance", excluded)

    def find(self, tree):
        out = []
        for node in ast.walk(tree):
            if _is_isinstance(node, type_name=self.base):
                parent = _parent(node)
                ctx = parent
                if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
                    ctx = _parent(parent)          # `if not isinstance(v, int): reject`
                    if not ((isinstance(ctx, (ast.If, ast.While, ast.IfExp)) and ctx.test is parent)
                            or isinstance(ctx, (ast.BoolOp, ast.Return, ast.Assert))):
                        continue
                    out.append(node)
                    continue
                in_test = isinstance(parent, (ast.If, ast.While, ast.IfExp, ast.Assert)) and parent.test is node
                in_bool = isinstance(parent, ast.BoolOp)
                if in_test or in_bool or isinstance(parent, ast.Return):
                    out.append(node)
        return out

    def check(self, tree, node):
        subject = node.args[0]
        # already guarded anywhere in the same boolean expression (`... and not isinstance(v, bool)`
        # or `not isinstance(v, int) or isinstance(v, bool)`)
        cur = _parent(node)
        while isinstance(cur, (ast.BoolOp, ast.UnaryOp)):
            for sub in ast.walk(cur):
                if sub is not node and _is_isinstance(sub, subject, self.excluded):
                    return "ALREADY_GUARDED"
            cur = _parent(cur)
        return None

    def edits(self, tree, node, off):
        a, b = off.span(node)
        subject = off.text(node.args[0])
        return [(a, b, f"({off.text(node)} and not isinstance({subject}, {self.excluded}))")]

    def touched(self, node):
        return [f"subject:{ast.unparse(node.args[0])}", f"type:{self.base}"]


_RETRY_HELPER = '''

def _gk_retry(fn, exc, attempts):
    """Inserted by skill retry_write (bounded retry)."""
    for attempt in range(attempts):
        try:
            return fn()
        except exc:
            if attempt == attempts - 1:
                raise
'''


class RetryWrap(Transform):
    """db.<method>(...)  ->  _gk_retry(lambda: db.<method>(...), Exc, n)."""

    name = "retry_write"
    behaviors = ("exception-handling", "write-path")

    def __init__(self, methods=("write", "write_async"), exception="TransientError", attempts=3):
        self.methods, self.exception, self.attempts = tuple(methods), exception, int(attempts)

    def find(self, tree):
        return [n for n in ast.walk(tree)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in self.methods]

    def check(self, tree, node):
        if not _defined_symbol(tree, self.exception):
            return "MISSING_SYMBOL"
        parent = _parent(node)
        if isinstance(parent, ast.Lambda):
            outer = _parent(parent)
            if isinstance(outer, ast.Call) and isinstance(outer.func, ast.Name) \
                    and outer.func.id == "_gk_retry":
                return "ALREADY_GUARDED"
        return None

    def edits(self, tree, node, off):
        a, b = off.span(node)
        return [(a, b, f"_gk_retry(lambda: {off.text(node)}, {self.exception}, {self.attempts})")]

    def module_edits(self, tree, off):
        if any(isinstance(n, ast.FunctionDef) and n.name == "_gk_retry" for n in tree.body):
            return []
        last_import = None
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import = node
        pos = off.span(last_import)[1] if last_import else 0
        return [(pos, pos, _RETRY_HELPER)]

    def touched(self, node):
        return [f"call:{node.func.attr}", f"receiver:{ast.unparse(node.func.value)}"]


class AsyncWrite(Transform):
    """db.write(...)  ->  db.write_async(...)  (non-blocking API migration)."""

    name = "async_write"
    behaviors = ("exception-handling", "write-path", "concurrency")

    def __init__(self, source_method="write", target_method="write_async"):
        self.source_method, self.target_method = source_method, target_method

    def find(self, tree):
        return [n for n in ast.walk(tree)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == self.source_method]

    def edits(self, tree, node, off):
        a, b = off.span(node.func)
        return [(a, b, f"{off.text(node.func.value)}.{self.target_method}")]

    def touched(self, node):
        return [f"call:{self.source_method}", f"call:{self.target_method}",
                f"receiver:{ast.unparse(node.func.value)}"]


class ExternalCommand(Transform):
    """Adapter for an existing binder (e.g. the project's anchored_binder.py v3).

    The command template receives {input}, {output} and {receipt} paths.  The external
    tool must write the rewritten source to {output} and a JSON receipt such as
    {"status": "APPLIED", "sites": [{"line": 12, "function": "f", "snippet": "..."}],
     "footprint": ["func:f"]}  or  {"status": "ABSTAIN", "reason": "NO_MATCH"}.
    """

    name = "external_command"

    def __init__(self, command, behaviors=(), timeout=60):
        self.command, self.behaviors, self.timeout = command, tuple(behaviors), timeout

    def apply(self, source: str, single_site: bool = True) -> ApplyResult:
        import json as _json
        import shlex
        import subprocess
        import sys
        import tempfile
        from pathlib import Path as _Path
        with tempfile.TemporaryDirectory(prefix="gk_ext_") as tmp:
            src, out, rec = (_Path(tmp) / n for n in ("input.py", "output.py", "receipt.json"))
            src.write_text(source, encoding="utf-8")
            cmd = [part.format(input=src, output=out, receipt=rec, python=sys.executable)
                   for part in shlex.split(self.command)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            if proc.returncode != 0 or not rec.exists():
                raise Abstain("EXTERNAL_ERROR", (proc.stderr or proc.stdout)[-200:])
            receipt = _json.loads(rec.read_text(encoding="utf-8"))
            if receipt.get("status") != "APPLIED":
                raise Abstain(receipt.get("reason", "EXTERNAL_ABSTAIN"))
            new_source = out.read_text(encoding="utf-8")
        ast.parse(new_source)
        sites = [Site(int(s.get("line", 0)), s.get("function", "?"), s.get("snippet", ""))
                 for s in receipt.get("sites", [])]
        if single_site and len(sites) > 1:
            raise Abstain("MULTIPLE_MATCHES", f"{len(sites)} sites")
        footprint = set(receipt.get("footprint", [])) | {f"behavior:{b}" for b in self.behaviors}
        footprint |= {f"func:{s.function}" for s in sites}
        return ApplyResult(new_source, sites, sorted(footprint))


REGISTRY: Dict[str, Callable[..., Transform]] = {
    ExternalCommand.name: ExternalCommand,
    EmptyStringGuard.name: EmptyStringGuard,
    NegativeTypeGuard.name: NegativeTypeGuard,
    RetryWrap.name: RetryWrap,
    AsyncWrite.name: AsyncWrite,
}


def make(name: str, params: Optional[dict] = None) -> Transform:
    if name not in REGISTRY:
        raise KeyError(f"unknown transform {name!r}")
    return REGISTRY[name](**(params or {}))


def ast_equal(a: str, b: str) -> bool:
    """Semantic AST equality, ignoring formatting and redundant parentheses."""
    return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
