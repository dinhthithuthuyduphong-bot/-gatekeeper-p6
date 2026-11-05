"""T-A4: JUnit parsing, a real pytest run on a synthetic package, and the TS analysis on synthetic records."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import test_oracle as TO  # noqa: E402
import test_oracle_analyze as TA  # noqa: E402


class Junit(unittest.TestCase):
    def test_outcomes(self):
        p = Path(tempfile.mkdtemp()) / "r.xml"
        p.write_text('<testsuites><testsuite><testcase classname="t" name="a"/><testcase classname="t" name="b"><failure/></testcase>'
                     '<testcase classname="t" name="c"><skipped/></testcase><testcase classname="t" name="d"><error/></testcase>'
                     '</testsuite></testsuites>')
        self.assertEqual(TO.junit_outcomes(p), {"t::a": "pass", "t::b": "fail", "t::c": "skip", "t::d": "fail"})
        self.assertEqual(TO.junit_outcomes(p.parent / "missing.xml"), {})

    def test_root_path_normalised(self):
        """T-A4a: a test parametrised by its own path keeps its id between the original and the patched copy."""
        d = Path(tempfile.mkdtemp())
        for root in ("/w/src/pkg-1", "/w/snap"):
            (d / "r.xml").write_text('<testsuite><testcase classname="tests.t" name="test_p[%s/tests/t.py]"/></testsuite>' % root)
            self.assertEqual(TO.junit_outcomes(d / "r.xml", root), {"tests.t::test_p[<ROOT>/tests/t.py]": "pass"})


class RealRun(unittest.TestCase):
    def test_pytest_detects_change(self):
        try:
            import pytest_timeout  # noqa: F401
        except ImportError:
            self.skipTest("pytest-timeout not installed")
        root = Path(tempfile.mkdtemp())
        (root / "pkg").mkdir()
        (root / "pkg/__init__.py").write_text("def f(x):\n    return x + 1\n")
        (root / "tests").mkdir()
        (root / "tests/test_f.py").write_text("from pkg import f\n\ndef test_f():\n    assert f(1) == 2\n")
        work = Path(tempfile.mkdtemp())
        r = TO.pytest_run(Path(sys.executable), root, "", work, "o")
        self.assertEqual(list(r["outcomes"].values()), ["pass"])
        (root / "pkg/__init__.py").write_text("def f(x):\n    return x + 2\n")
        r = TO.pytest_run(Path(sys.executable), root, "", work, "c")
        self.assertEqual(list(r["outcomes"].values()), ["fail"])

    def test_collection_error_does_not_stop_the_run(self):
        try:
            import pytest_timeout  # noqa: F401
        except ImportError:
            self.skipTest("pytest-timeout not installed")
        root = Path(tempfile.mkdtemp())
        (root / "tests").mkdir()
        (root / "tests/test_ok.py").write_text("def test_ok():\n    assert True\n")
        (root / "tests/test_broken.py").write_text("import module_that_does_not_exist\n")
        r = TO.pytest_run(Path(sys.executable), root, "", Path(tempfile.mkdtemp()), "o")
        self.assertIn("pass", r["outcomes"].values())


class Analysis(unittest.TestCase):
    def test_scores_and_criteria(self):
        d = Path(tempfile.mkdtemp())
        rows = [{"cell": "p/A", "rule": "A", "r2": False, "harmful": True, "U": True, "RS": True, "B6S": False, "S20": True, "B8": False, "G": False},
                {"cell": "p/B", "rule": "B", "r2": False, "harmful": False, "U": True, "RS": False, "B6S": True, "S20": True, "B8": True, "G": True},
                {"cell": "p/C", "rule": "C", "r2": False, "harmful": False, "U": True, "RS": True, "B6S": True, "S20": True, "B8": True, "G": True},
                {"cell": "p/D", "rule": "D", "r2": False, "harmful": False, "U": True, "RS": True, "B6S": True, "S20": True, "B8": True, "G": True}]
        (d / "STUDY_T_RESULT.json").write_text(json.dumps({"rows": rows}))
        (d / "TS_p.json").write_text(json.dumps({"project": "p", "applicable": True, "cells": {
            "A": {"status": "run", "admit": True, "seconds": 3},
            "B": {"status": "run", "admit": True, "seconds": 3},
            "C": {"status": "run", "admit": False, "confirmed": False, "seconds": 3},
            "D": {"status": "not run (budget)"}}}))
        (d / "TS_q.json").write_text(json.dumps({"project": "q", "applicable": False, "cells": {}}))
        r = TA.analyse(d)
        self.assertEqual((r["cells_run"], r["harmful"], r["safe"], r["not_run_budget"]), (3, 1, 2, 1))
        self.assertEqual(r["scores"]["TS"]["harmful_admitted"], 1)
        self.assertEqual(r["scores"]["G"]["harmful_admitted"], 0)
        self.assertEqual(r["scores"]["U"]["harmful_admitted"], 1)
        self.assertTrue(r["TS_W1"])
        self.assertEqual((r["g_admitted"], r["g_admitted_ts_confirmed_reject"], r["g_admitted_ts_unconfirmed_reject"]), (2, 0, 1))
        self.assertEqual(r["packages"]["not_applicable"], ["q"])
        self.assertFalse(r["TS_W2"])   # 0/2: the Wilson upper bound is far above 5%


if __name__ == "__main__":
    unittest.main()
