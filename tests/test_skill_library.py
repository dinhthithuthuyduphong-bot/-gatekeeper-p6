"""Study R2 skill families: rewrite, abstain, and a witness input on which each rewrite changes behaviour (protocol table)."""
import sys
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import skill_library as L  # noqa: E402
from gatekeeper_lite import transforms as T  # noqa: E402

L.register_all()
warnings.filterwarnings("ignore", category=SyntaxWarning)


def rw(name, src):
    return T.make(name).apply(src, single_site=False).source


def run(src, fn, *args):
    ns = {}
    exec(compile(src, "<t>", "exec"), ns)
    try:
        return ("ok", ns[fn](*args))
    except BaseException as exc:  # noqa: BLE001 - the witness may be KeyboardInterrupt
        return ("raise", type(exc).__name__)


class SkillLibraryTest(unittest.TestCase):
    def check(self, name, before, after, fn=None, witness=(), ordinary=()):
        got = rw(name, before)
        self.assertEqual(got, after)
        if fn:
            for args in ordinary:      # same behaviour on ordinary inputs
                self.assertEqual(run(before, fn, *args), run(after, fn, *args), args)
            for args in witness:       # different behaviour on the protocol's witness
                self.assertNotEqual(run(before, fn, *args), run(after, fn, *args), args)

    def test_type_eq_isinstance(self):
        self.check("type_eq_isinstance", "def f(x):\n    return type(x) == int\n", "def f(x):\n    return isinstance(x, int)\n",
                   "f", witness=[(True,)], ordinary=[(3,), ("a",)])
        self.assertEqual(rw("type_eq_isinstance", "def f(x):\n    return type(x) is not dict\n"),
                         "def f(x):\n    return not isinstance(x, dict)\n")
        with self.assertRaises(T.Abstain):
            rw("type_eq_isinstance", "def f(x):\n    return type(x) == type(None)\n")

    def test_eq_bool_identity(self):
        self.check("eq_bool_identity", "def f(x):\n    return x == True\n", "def f(x):\n    return x is True\n",
                   "f", witness=[(1,)], ordinary=[(True,), (False,), (None,)])
        self.assertEqual(rw("eq_bool_identity", "def f(a, b):\n    return a or b != False\n"),
                         "def f(a, b):\n    return a or b is not False\n")

    def test_is_literal_eq(self):
        src = 'import warnings\nwarnings.simplefilter("ignore")\ndef f(x):\n    return x is 1000\n'
        self.check("is_literal_eq", src, src.replace("is 1000", "== 1000"), "f", witness=[(int("1000"),)], ordinary=[(None,), (3,)])

    def test_len_zero_falsy(self):
        self.check("len_zero_falsy", "def f(x):\n    return len(x) == 0\n", "def f(x):\n    return not x\n",
                   "f", witness=[(None,)], ordinary=[([],), ([1],), ("",)])
        self.assertEqual(rw("len_zero_falsy", "def f(a, b):\n    return len(a + b) != 0\n"), "def f(a, b):\n    return bool(a + b)\n")
        with self.assertRaises(T.Abstain):
            rw("len_zero_falsy", "len = 3\ndef f(x):\n    return len(x) == 0\n")

    def test_dict_keys_membership(self):
        before = ("class M(dict):\n    def keys(self):\n        return ['k']\n"
                  "def f(d):\n    return 'k' in d.keys()\n")
        self.check("dict_keys_membership", before, before.replace("in d.keys()", "in d"), "f", ordinary=[({"k": 1},), ({},)])
        ns = {}
        exec(compile(before, "<t>", "exec"), ns)
        ns2 = {}
        exec(compile(rw("dict_keys_membership", before), "<t>", "exec"), ns2)
        self.assertNotEqual(ns["f"](ns["M"]()), ns2["f"](ns2["M"]()))

    def test_mutable_default(self):
        before = 'def f(x, acc=[]):\n    """doc"""\n    acc.append(x)\n    return len(acc)\n'
        after = 'def f(x, acc=None):\n    """doc"""\n    if acc is None:\n        acc = []\n    acc.append(x)\n    return len(acc)\n'
        self.assertEqual(rw("mutable_default", before), after)
        ns, ns2 = {}, {}
        exec(before, ns)
        exec(after, ns2)
        self.assertEqual((ns["f"](1), ns["f"](1)), (1, 2))       # shared state before
        self.assertEqual((ns2["f"](1), ns2["f"](1)), (1, 1))     # not after
        self.assertEqual(T.make("mutable_default").apply(before, single_site=False).sites[0].function, "f")
        with self.assertRaises(T.Abstain):
            rw("mutable_default", "def f(a={}): return a\n")
        self.assertEqual(rw("mutable_default", "def f(*, a=dict()):\n    return a\n"),
                         "def f(*, a=None):\n    if a is None:\n        a = dict()\n    return a\n")

    def test_bare_except(self):
        before = "def f(g):\n    try:\n        g()\n    except:\n        return 'caught'\n    return 'ok'\n"
        def interrupt():
            raise KeyboardInterrupt
        def boom():
            raise ValueError
        self.check("bare_except", before, before.replace("except:", "except Exception:"), "f",
                   witness=[(interrupt,)], ordinary=[(boom,), (lambda: None,)])

    def test_reraise_bare(self):
        before = "def f(g):\n    try:\n        g()\n    except ValueError as e:\n        raise e\n"
        self.assertEqual(rw("reraise_bare", before), before.replace("raise e", "raise"))
        with self.assertRaises(T.Abstain):
            rw("reraise_bare", "def f(g):\n    try:\n        g()\n    except ValueError as e:\n        e = TypeError()\n        raise e\n")

    def test_open_encoding(self):
        self.assertEqual(rw("open_encoding", "def f(p):\n    return open(p).read()\n"),
                         'def f(p):\n    return open(p, encoding="utf-8").read()\n')
        self.assertEqual(rw("open_encoding", "def f(p):\n    return open(p, 'w',)\n"), "def f(p):\n    return open(p, 'w', encoding=\"utf-8\",)\n")
        for src in ("def f(p):\n    return open(p, 'rb')\n", "def f(p):\n    return open(p, encoding='latin-1')\n",
                    "def f(p, m):\n    return open(p, m)\n"):
            with self.assertRaises(T.Abstain):
                rw("open_encoding", src)

    def test_yaml_safe_load(self):
        self.assertEqual(rw("yaml_safe_load", "import yaml\ndef f(s):\n    return yaml.load(s)\n"),
                         "import yaml\ndef f(s):\n    return yaml.safe_load(s)\n")
        with self.assertRaises(T.Abstain):
            rw("yaml_safe_load", "import yaml\ndef f(s):\n    return yaml.load(s, Loader=yaml.FullLoader)\n")

    def test_manifests_load_and_bind(self):
        from gatekeeper_lite.skill import Skill
        paths = sorted((ROOT / "study_r2/skills").glob("*.json"))
        self.assertEqual(len(paths), 10)
        self.assertEqual({Skill.load(p).pi["transform"] for p in paths}, {c.name for c in L.FAMILIES})
        for p in paths:
            self.assertIsInstance(Skill.load(p).transform(), T.Transform)


if __name__ == "__main__":
    unittest.main()
