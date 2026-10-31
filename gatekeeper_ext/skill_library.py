"""Study R2 (study_r2/PROTOCOL.md): ten further skill families, so that the library-level machinery (composite cells,
execution rule, Corollary 5.6) can be measured on a library of realistic size and variety.

Each family is a single-statement, linter-style rewrite in the PySStuBs / pycodestyle / flake8-bugbear / bandit tradition:
behaviour-preserving for ordinary inputs and behaviour-changing for some (the "changes behaviour when" column of the
protocol), so admitting it is a real decision.  Every family fails closed: when a site cannot be rewritten safely it
abstains.  The classes plug into the frozen `gatekeeper_lite.transforms` registry at run time (`register_all()`); the frozen
module is not modified.
"""
import ast
import re

from gatekeeper_lite import transforms as T

# Operands that bind at least as tightly as a comparison can be written bare; anything else is parenthesised.
_ATOMIC = (ast.Name, ast.Attribute, ast.Call, ast.Subscript, ast.Constant, ast.BinOp, ast.List, ast.Tuple, ast.Dict,
           ast.Set, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.JoinedStr, ast.Await)


def _operand(node, off):
    text = off.text(node)
    if isinstance(node, ast.BinOp) or "\n" in text:
        return f"({text})"
    return text if isinstance(node, _ATOMIC) else f"({text})"


def _is_name_call(node, name, nargs=1):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
            and len(node.args) == nargs and not node.keywords
            and not any(isinstance(a, ast.Starred) for a in node.args))


def _single(node, ops):
    return isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], ops)


class LibTransform(T.Transform):
    """Transform whose site may be attributed to a function other than the one lexically enclosing the matched node
    (a default argument belongs to the function it parameterises, not to the scope that evaluates it)."""

    def __init__(self):
        pass

    def site_function(self, node):
        return T._enclosing_function(node)

    def apply(self, source, single_site=True):
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise T.Abstain("PARSE_ERROR", str(exc))
        T._parents(tree)
        nodes = self.find(tree)
        if not nodes:
            raise T.Abstain("NO_MATCH")
        shadowed = sorted(set(self.shadow_sensitive) & T._bound_names(tree))
        if shadowed:
            raise T.Abstain("BUILTIN_SHADOWED", ",".join(shadowed))
        live = []
        for node in nodes:
            reason = self.check(tree, node)
            if reason:
                if single_site:
                    raise T.Abstain(reason, f"line {node.lineno}")
                continue
            live.append(node)
        if not live:
            raise T.Abstain("NO_APPLICABLE_SITE")
        if single_site and len(live) > 1:
            raise T.Abstain("MULTIPLE_MATCHES", f"{len(live)} sites")
        off = T._Offsets(source)
        edits, sites, footprint = [], [], set(f"behavior:{b}" for b in self.behaviors)
        for node in live:
            edits.extend(self.edits(tree, node, off))
            func = self.site_function(node)
            sites.append(T.Site(node.lineno, func, off.text(node).split("\n")[0]))
            footprint.add(f"func:{func}")
            footprint.update(self.touched(node))
        new_source = T._apply_edits(source, edits)
        ast.parse(new_source)
        return T.ApplyResult(new_source, sites, sorted(footprint))


# ------------------------------------------------------------------ comparisons
class TypeEqIsinstance(LibTransform):
    """type(x) == T / type(x) is T -> isinstance(x, T); != / is not -> not isinstance(x, T)."""
    name, behaviors, shadow_sensitive = "type_eq_isinstance", ("type-check",), ("type", "isinstance")

    @staticmethod
    def _parts(node):
        left, right = node.left, node.comparators[0]
        if _is_name_call(left, "type") and isinstance(right, (ast.Name, ast.Attribute)):
            return left.args[0], right
        if _is_name_call(right, "type") and isinstance(left, (ast.Name, ast.Attribute)):
            return right.args[0], left
        return None

    def find(self, tree):
        return [n for n in ast.walk(tree) if _single(n, (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)) and self._parts(n)]

    def check(self, tree, node):
        subj, typ = self._parts(node)
        if isinstance(typ, ast.Name) and typ.id in ("None", "type"):
            return "NOT_A_PLAIN_CLASS"
        return None

    def edits(self, tree, node, off):
        subj, typ = self._parts(node)
        neg = isinstance(node.ops[0], (ast.NotEq, ast.IsNot))
        a, b = off.span(node)
        return [(a, b, ("not " if neg else "") + f"isinstance({off.text(subj)}, {off.text(typ)})")]

    def touched(self, node):
        subj, typ = self._parts(node)
        return [f"subject:{T._unparse(subj)}", f"type:{T._unparse(typ)}"]


class EqBoolIdentity(LibTransform):
    """x == True / x != False -> x is True / x is not False (pycodestyle E712)."""
    name, behaviors, shadow_sensitive = "eq_bool_identity", ("comparison",), ()

    @staticmethod
    def _is_bool(n):
        return isinstance(n, ast.Constant) and type(n.value) is bool

    def _parts(self, node):
        if self._is_bool(node.comparators[0]) and not isinstance(node.left, ast.Constant):
            return node.left, node.comparators[0].value
        if self._is_bool(node.left) and not isinstance(node.comparators[0], ast.Constant):
            return node.comparators[0], node.left.value
        return None

    def find(self, tree):
        return [n for n in ast.walk(tree) if _single(n, (ast.Eq, ast.NotEq)) and self._parts(n)]

    def edits(self, tree, node, off):
        subj, val = self._parts(node)
        op = "is" if isinstance(node.ops[0], ast.Eq) else "is not"
        a, b = off.span(node)
        return [(a, b, f"{_operand(subj, off)} {op} {val}")]

    def touched(self, node):
        subj, val = self._parts(node)
        return [f"subject:{T._unparse(subj)}", f"compare:{val}"]


class IsLiteralEq(LibTransform):
    """x is "s" / x is 1 -> x == "s" / x == 1 (pyflakes F632, SyntaxWarning since Python 3.8)."""
    name, behaviors, shadow_sensitive = "is_literal_eq", ("comparison",), ()

    @staticmethod
    def _lit(n):
        return isinstance(n, ast.Constant) and type(n.value) in (str, bytes, int, float)

    def find(self, tree):
        return [n for n in ast.walk(tree) if _single(n, (ast.Is, ast.IsNot))
                and (self._lit(n.left) or self._lit(n.comparators[0]))]

    def check(self, tree, node):
        if self._lit(node.left) and self._lit(node.comparators[0]):
            return "BOTH_LITERALS"
        return None

    def edits(self, tree, node, off):
        op = "==" if isinstance(node.ops[0], ast.Is) else "!="
        a, b = off.span(node)
        return [(a, b, f"{_operand(node.left, off)} {op} {_operand(node.comparators[0], off)}")]

    def touched(self, node):
        subj = node.comparators[0] if self._lit(node.left) else node.left
        return [f"subject:{T._unparse(subj)}", "compare:literal"]


class LenZeroFalsy(LibTransform):
    """len(x) == 0 -> not x;  len(x) != 0 -> bool(x)  (pylint C1802 use-implicit-booleaness-not-len)."""
    name, behaviors, shadow_sensitive = "len_zero_falsy", ("truthiness",), ("len", "bool")

    def find(self, tree):
        return [n for n in ast.walk(tree) if _single(n, (ast.Eq, ast.NotEq)) and _is_name_call(n.left, "len")
                and isinstance(n.comparators[0], ast.Constant) and type(n.comparators[0].value) is int
                and n.comparators[0].value == 0]

    def edits(self, tree, node, off):
        subj = node.left.args[0]
        a, b = off.span(node)
        if isinstance(node.ops[0], ast.Eq):
            return [(a, b, f"not {_operand(subj, off)}")]
        return [(a, b, f"bool({off.text(subj)})")]

    def touched(self, node):
        return [f"subject:{T._unparse(node.left.args[0])}", "len:0"]


class DictKeysMembership(LibTransform):
    """k in d.keys() -> k in d (pylint C0201 consider-iterating-dictionary)."""
    name, behaviors, shadow_sensitive = "dict_keys_membership", ("membership",), ()

    @staticmethod
    def _keys(n):
        return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "keys"
                and not n.args and not n.keywords)

    def find(self, tree):
        return [n for n in ast.walk(tree) if _single(n, (ast.In, ast.NotIn)) and self._keys(n.comparators[0])]

    def edits(self, tree, node, off):
        call = node.comparators[0]
        a, b = off.span(call)
        return [(a, b, _operand(call.func.value, off))]

    def touched(self, node):
        return [f"subject:{T._unparse(node.comparators[0].func.value)}", "membership:keys"]


# ------------------------------------------------------------------ functions and exceptions
class MutableDefault(LibTransform):
    """def f(a=[]) -> def f(a=None): if a is None: a = []   (flake8-bugbear B006).  One site per function."""
    name, behaviors, shadow_sensitive = "mutable_default", ("signature",), ()
    _EMPTY_CALLS = ("list", "dict", "set")

    def _mutable(self, d):
        return (isinstance(d, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)) or
                (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id in self._EMPTY_CALLS
                 and not d.args and not d.keywords))

    def _pairs(self, fn):
        a = fn.args
        pos = list(getattr(a, "posonlyargs", [])) + list(a.args)
        out = list(zip(pos[len(pos) - len(a.defaults):], a.defaults))
        out += [(arg, d) for arg, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
        return [(arg, d) for arg, d in out if self._mutable(d)]

    def find(self, tree):
        return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and self._pairs(n)]

    def site_function(self, node):
        return node.name

    def _first(self, fn):
        body = fn.body
        if (isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            return body[1] if len(body) > 1 else None
        return body[0]

    def check(self, tree, node):
        first = self._first(node)
        if first is None:
            return "DOCSTRING_ONLY"
        if first.lineno == node.lineno or (node.decorator_list and first.lineno == node.decorator_list[0].lineno):
            return "ONE_LINE_DEF"
        names = {arg.arg for arg, _ in self._pairs(node)}
        for sub in ast.walk(node):
            if isinstance(sub, (ast.Global, ast.Nonlocal)) and names & set(sub.names):
                return "SCOPE_DECLARATION"
        return None

    def edits(self, tree, node, off):
        first = self._first(node)
        line = off.lines[first.lineno - 1]
        indent = re.match(r"[ \t]*", line).group(0)
        if len(line.encode("utf-8")[:first.col_offset].decode("utf-8", "ignore")) != len(indent):
            raise T.Abstain("STATEMENT_NOT_AT_LINE_START", f"line {first.lineno}")
        out, guard = [], ""
        for arg, d in self._pairs(node):
            a, b = off.span(d)
            out.append((a, b, "None"))
            guard += f"{indent}if {arg.arg} is None:\n{indent}    {arg.arg} = {T._unparse(d)}\n"
        start = off.starts[first.lineno - 1]
        out.append((start, start, guard))
        return out

    def touched(self, node):
        return [f"param:{arg.arg}" for arg, _ in self._pairs(node)]


class BareExcept(LibTransform):
    """except: -> except Exception:   (pycodestyle E722)."""
    name, behaviors, shadow_sensitive = "bare_except", ("exception-handling",), ("Exception",)

    def find(self, tree):
        return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler) and n.type is None]

    def edits(self, tree, node, off):
        a = off.offset(node.lineno, node.col_offset)
        if off.source[a:a + 6] != "except":
            raise T.Abstain("UNEXPECTED_TOKEN", f"line {node.lineno}")
        return [(a, a + 6, "except Exception")]

    def touched(self, node):
        return ["except:bare"]


class ReraiseBare(LibTransform):
    """except E as e: ... raise e -> raise   (pylint W0706-style; keeps the original traceback)."""
    name, behaviors, shadow_sensitive = "reraise_bare", ("exception-handling",), ()

    @staticmethod
    def _handler(node):
        cur = T._parent(node)
        while cur is not None:
            if isinstance(cur, ast.ExceptHandler):
                return cur
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                return None
            cur = T._parent(cur)
        return None

    def find(self, tree):
        out = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Name) and n.cause is None:
                h = self._handler(n)
                if h is not None and h.name == n.exc.id:
                    out.append(n)
        return out

    def check(self, tree, node):
        h = self._handler(node)
        for sub in ast.walk(h):
            if isinstance(sub, ast.Name) and sub.id == h.name and isinstance(sub.ctx, (ast.Store, ast.Del)):
                return "NAME_REBOUND"
        return None

    def edits(self, tree, node, off):
        a, b = off.span(node)
        return [(a, b, "raise")]

    def touched(self, node):
        return [f"exception:{node.exc.id}"]


# ------------------------------------------------------------------ library APIs
class OpenEncoding(LibTransform):
    """open(p) / open(p, "r") in text mode without encoding -> add encoding="utf-8"  (pylint W1514)."""
    name, behaviors, shadow_sensitive = "open_encoding", ("io",), ("open",)
    _OK_KW = {"mode", "buffering", "errors", "newline"}

    @staticmethod
    def _mode(node):
        if len(node.args) >= 2:
            return node.args[1]
        for k in node.keywords:
            if k.arg == "mode":
                return k.value
        return None

    def find(self, tree):
        return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "open" and n.args]

    def check(self, tree, node):
        if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
            return "STAR_ARGS"
        if len(node.args) > 3 or any(k.arg not in self._OK_KW for k in node.keywords):
            return "ENCODING_OR_UNKNOWN_ARG"
        m = self._mode(node)
        if m is not None and not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
            return "MODE_NOT_LITERAL"
        if m is not None and "b" in m.value:
            return "BINARY_MODE"
        return None

    def edits(self, tree, node, off):
        last = max(list(node.args) + [k.value for k in node.keywords], key=lambda n: (n.end_lineno, n.end_col_offset))
        _, b = off.span(last)
        return [(b, b, ', encoding="utf-8"')]

    def touched(self, node):
        return [f"file:{T._unparse(node.args[0])}", "io:encoding"]


class YamlSafeLoad(LibTransform):
    """yaml.load(s) without Loader -> yaml.safe_load(s)  (bandit B506)."""
    name, behaviors, shadow_sensitive = "yaml_safe_load", ("deserialisation",), ()

    def find(self, tree):
        return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "load" and isinstance(n.func.value, ast.Name) and n.func.value.id == "yaml"]

    def check(self, tree, node):
        if len(node.args) != 1 or node.keywords or isinstance(node.args[0], ast.Starred):
            return "LOADER_GIVEN"
        imported = any(isinstance(n, ast.Import) and any(a.name == "yaml" and a.asname is None for a in n.names)
                       for n in ast.walk(tree))
        return None if imported else "YAML_NOT_IMPORTED"

    def edits(self, tree, node, off):
        a, b = off.span(node.func)
        return [(a, b, "yaml.safe_load")]

    def touched(self, node):
        return [f"stream:{T._unparse(node.args[0])}", "yaml:loader"]


FAMILIES = (TypeEqIsinstance, EqBoolIdentity, IsLiteralEq, LenZeroFalsy, DictKeysMembership, MutableDefault, BareExcept,
            ReraiseBare, OpenEncoding, YamlSafeLoad)


def register_all():
    """Make `transforms.make(<name>)` work for the ten families and for none_identity."""
    from gatekeeper_ext.none_identity import register
    register()
    for cls in FAMILIES:
        T.REGISTRY.setdefault(cls.name, cls)
