"""Second skill family (Study G, draft): compare with None by identity (pycodestyle E711).

    X == None   ->  X is None
    X != None   ->  X is not None
    None == X   ->  X is None        (operands swapped so the subject stays on the left)

Only two-operand comparisons are rewritten; chained comparisons are skipped.  The rewrite is
behaviour-preserving for ordinary objects and behaviour-CHANGING for objects whose __eq__ is
overridden (numpy arrays, SQLAlchemy column expressions, pandas objects, proxies).
"""
import ast

from gatekeeper_lite import transforms as T


class NoneIdentity(T.Transform):
    name = "none_identity"
    behaviors = ("comparison",)

    def __init__(self):
        self.shadow_sensitive = ()

    @staticmethod
    def _is_none(n):
        return isinstance(n, ast.Constant) and n.value is None

    def find(self, tree):
        out = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Compare) and len(node.ops) == 1
                    and isinstance(node.ops[0], (ast.Eq, ast.NotEq))
                    and (self._is_none(node.comparators[0]) or self._is_none(node.left))):
                out.append(node)
        return out

    def check(self, tree, node):
        if self._is_none(node.left) and self._is_none(node.comparators[0]):
            return "BOTH_NONE"
        return None

    def edits(self, tree, node, off):
        a, b = off.span(node)
        subject = node.comparators[0] if self._is_none(node.left) else node.left
        op = "is" if isinstance(node.ops[0], ast.Eq) else "is not"
        return [(a, b, f"{off.text(subject)} {op} None")]

    def touched(self, node):
        subject = node.comparators[0] if self._is_none(node.left) else node.left
        return [f"subject:{T._unparse(subject)}", "compare:None"]


def register():
    """Make `transforms.make('none_identity')` work by adding the class to the frozen module's
    registry at run time (the module file itself is not modified)."""
    T.REGISTRY.setdefault(NoneIdentity.name, NoneIdentity)
