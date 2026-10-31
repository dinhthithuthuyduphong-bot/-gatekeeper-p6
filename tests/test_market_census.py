import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import market_census as M  # noqa: E402


def meta(name="pkg", wheel="pkg-1.0-py3-none-any.whl", sdist_size=1000):
    files = [{"packagetype": "bdist_wheel", "filename": wheel}]
    if sdist_size is not None:
        files.append({"packagetype": "sdist", "filename": "pkg-1.0.tar.gz", "size": sdist_size, "url": "u"})
    return {"info": {"name": name}, "urls": files}


class MarketCensusTest(unittest.TestCase):
    def test_selection_rules(self):
        self.assertTrue(M.qualifies(meta())[0])
        self.assertEqual(M.qualifies(meta(name="types-requests"))[1], "stub package")
        self.assertEqual(M.qualifies(meta(wheel="pkg-1.0-cp312-cp312-manylinux.whl"))[1], "no py3-none-any wheel")
        self.assertEqual(M.qualifies(meta(sdist_size=None))[1], "no sdist")
        self.assertEqual(M.qualifies(meta(sdist_size=30 * 1024 * 1024))[1], "sdist larger than 20 MB")

    def test_enclosing_function(self):
        src = "x = 1\nclass A:\n    def f(self):\n        def g():\n            return 1\n        return g\n"
        idx = M.function_index(src)
        self.assertEqual(M.enclosing(idx, 1), "<module>")
        self.assertEqual(M.enclosing(idx, 3), "A.f")
        self.assertEqual(M.enclosing(idx, 5), "A.f.<locals>.g")

    def test_cells(self):
        sites = [{"rule": "UP008", "file": "a.py", "function": "f", "applicability": "safe"},
                 {"rule": "UP008", "file": "b.py", "function": "g", "applicability": "safe"},
                 {"rule": "SIM108", "file": "a.py", "function": "f", "applicability": "unsafe"},
                 {"rule": "SIM108", "file": "a.py", "function": "h", "applicability": "safe"}]
        c = M.cells_of(sites)
        self.assertEqual(c["UP008"]["applicability"], "safe")
        self.assertEqual(c["SIM108"]["applicability"], "mixed")
        self.assertEqual(c["UP008"]["functions"], ["a.py::f", "b.py::g"])


if __name__ == "__main__":
    unittest.main()
