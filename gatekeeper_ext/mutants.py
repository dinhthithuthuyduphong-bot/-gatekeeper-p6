"""Deterministic AST mutants of the functions a fix edited (Study L, amendment L-A1, gate G1 (d)).

Operators, in this fixed rank: comparison flip, if-test negation, boolean-constant flip, and/or swap.
Candidates are listed in source order (line, column, operator rank); the first n that still compile are used.
No outcome is looked at when choosing them.  Compatible with Python 3.8 (no ast.unparse): replacements are
text edits at node spans, so formatting elsewhere is preserved.
"""
import ast
import re

_CMP = {ast.Eq: "!=", ast.NotEq: "==", ast.Lt: "<=", ast.LtE: "<", ast.Gt: ">=", ast.GtE: ">",
        ast.Is: "is not", ast.IsNot: "is", ast.In: "not in", ast.NotIn: "in"}
_CMP_RE = {ast.Eq: r"==", ast.NotEq: r"!=", ast.Lt: r"<(?!=)", ast.LtE: r"<=", ast.Gt: r">(?!=)", ast.GtE: r">=",
           ast.Is: r"\bis\b(?!\s+not\b)", ast.IsNot: r"\bis\s+not\b", ast.In: r"\bin\b", ast.NotIn: r"\bnot\s+in\b"}
RANK = {"cmp_flip": 0, "if_negate": 1, "bool_const": 2, "and_or": 3}


def functions(tree):
    """qualname -> (node, first line incl. decorators) for module-level functions and methods."""
    out = {}

    def visit(body, prefix):
        for n in body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[prefix + n.name] = (n, min([n.lineno] + [d.lineno for d in n.decorator_list]))
            elif isinstance(n, ast.ClassDef):
                visit(n.body, prefix + n.name + ".")
    visit(tree.body, "")
    return out


def _offsets(src):
    lines = src.splitlines(True)
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln)

    def at(lineno, col):                     # AST columns are UTF-8 byte offsets
        text = lines[lineno - 1]
        return starts[lineno - 1] + len(text.encode("utf-8")[:col].decode("utf-8", "ignore"))
    return at


def candidates(src, qualnames):
    tree = ast.parse(src)
    funcs = functions(tree)
    at = _offsets(src)
    found = []
    for q in qualnames:
        if q not in funcs:
            continue
        for stmt in funcs[q][0].body:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in _CMP:
                    a, b = at(node.left.end_lineno, node.left.end_col_offset), at(node.comparators[0].lineno, node.comparators[0].col_offset)
                    m = re.search(_CMP_RE[type(node.ops[0])], src[a:b])
                    if m:
                        found.append(("cmp_flip", node.lineno, node.col_offset, a + m.start(), a + m.end(), _CMP[type(node.ops[0])], q))
                elif isinstance(node, ast.If):
                    s, e = at(node.test.lineno, node.test.col_offset), at(node.test.end_lineno, node.test.end_col_offset)
                    found.append(("if_negate", node.test.lineno, node.test.col_offset, s, e, "not (" + src[s:e] + ")", q))
                elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
                    s, e = at(node.lineno, node.col_offset), at(node.end_lineno, node.end_col_offset)
                    found.append(("bool_const", node.lineno, node.col_offset, s, e, "False" if node.value else "True", q))
                elif isinstance(node, ast.BoolOp) and len(node.values) == 2:
                    a, b = at(node.values[0].end_lineno, node.values[0].end_col_offset), at(node.values[1].lineno, node.values[1].col_offset)
                    word = "and" if isinstance(node.op, ast.And) else "or"
                    m = re.search(r"\b%s\b" % word, src[a:b])
                    if m:
                        found.append(("and_or", node.lineno, node.col_offset, a + m.start(), a + m.end(),
                                      "or" if word == "and" else "and", q))
    found.sort(key=lambda c: (c[1], c[2], RANK[c[0]]))
    seen, out = set(), []
    for c in found:                           # drop exact duplicates (same span and replacement)
        key = (c[3], c[4], c[5])
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def mutants(src, qualnames, n=5):
    """Up to n mutated sources: list of (description, new_source)."""
    result = []
    for op, line, col, s, e, rep, q in candidates(src, qualnames):
        new = src[:s] + rep + src[e:]
        try:
            compile(new, "<mutant>", "exec")
        except SyntaxError:
            continue
        result.append(("%s at %s:%d:%d -> %r" % (op, q, line, col, rep), new))
        if len(result) >= n:
            break
    return result
