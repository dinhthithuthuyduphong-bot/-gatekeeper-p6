import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_target2 as T  # noqa: E402

PYPROJECT = '''
[project]
name = "pkg"
[project.optional-dependencies]
test = ["pytest-mock"]
docs = ["sphinx"]
ml = ["numpy"]
[dependency-groups]
dev = ["freezegun>=1.0", "moto[s3]; python_version>'3.8'"]
lint = ["ruff"]
[tool.poetry.group.test.dependencies]
pytest-asyncio = "^0.21"
python = "^3.10"
[tool.poetry.dev-dependencies]
responses = "*"
[tool.hatch.envs.default]
dependencies = ["httpx"]
[tool.hatch.envs.docs]
dependencies = ["mkdocs"]
'''


def tree(files):
    d = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return d


class Parsing(unittest.TestCase):
    def test_extras_groups_and_environments(self):
        d = tree({"pyproject.toml": PYPROJECT, "setup.cfg": "[options.extras_require]\nall = x\n"})
        self.assertEqual(T.declared_extras(d), ["all", "ml", "test"])                  # docs skipped
        deps = T.group_dependencies(d)
        for want in ("freezegun>=1.0", "moto[s3]", "pytest-asyncio", "responses", "httpx"):
            self.assertIn(want, deps)
        for unwanted in ("ruff", "mkdocs", "python"):
            self.assertNotIn(unwanted, deps)

    def test_requirement_files_order_and_docs_excluded(self):
        d = tree({"requirements.txt": "a", "requirements-test.txt": "b", "docs-requirements.txt": "c",
                  "requirements/ci.txt": "d", "tests/requirements.txt": "e"})
        self.assertEqual(T.requirement_files(d), ["requirements.txt", "requirements-test.txt", "requirements/ci.txt", "tests/requirements.txt"])

    def test_tox_deps(self):
        d = tree({"tox.ini": "[testenv]\ndeps =\n    pytest\n    -rrequirements.txt\n    mock>=4\ncommands = pytest\n"})
        self.assertEqual(T.tox_deps(d), ["pytest", "mock>=4"])

    def test_modules_and_packages(self):
        self.assertEqual(T.missing_modules("E   ModuleNotFoundError: No module named 'yaml'\nNo module named 'google.protobuf'"), ["google", "yaml"])
        self.assertEqual((T.package_for("yaml"), T.package_for("pytest_asyncio"), T.package_for("requests")), ("PyYAML", "pytest-asyncio", "requests"))
        d = tree({"mypkg/__init__.py": "", "src/other/__init__.py": "", "conftest.py": ""})
        self.assertTrue({"mypkg", "other", "conftest"} <= T.local_modules(d))

    def test_broken_pyproject_is_tolerated(self):
        self.assertEqual(T.declared_extras(tree({"pyproject.toml": "[project\n"})), [])


class FakeSh:
    def __init__(self, fail_first=0):
        self.calls, self.fail_first = [], fail_first

    def __call__(self, cmd, check=True, cwd=None, timeout=None, **kw):
        self.calls.append((list(cmd), cwd))
        code = 1 if self.fail_first > 0 and "install" in cmd and "--upgrade" not in cmd else 0
        if code:
            self.fail_first -= 1
        return types.SimpleNamespace(returncode=code, stdout="", stderr="")


class Provisioning(unittest.TestCase):
    def test_order_and_fallback(self):
        d = tree({"pyproject.toml": PYPROJECT, "requirements.txt": "x", "tox.ini": "[testenv]\ndeps = mock\n"})
        fake = FakeSh(fail_first=1)                                 # the all-extras install fails once
        old, T.V.sh = T.V.sh, fake
        try:
            log = []
            T.provision("/py", d, ["test", "dev"], log)
        finally:
            T.V.sh = old
        args = [c[0][5:] for c in fake.calls]          # [py, -m, pip, install, -q, ...]
        self.assertEqual(args[0], ["--upgrade", "pip", "setuptools", "wheel"])
        self.assertTrue(args[1][0].endswith("[ml,test]"))         # every non-docs extra first
        self.assertTrue(args[2][0].endswith("[test]"))            # then the fallback chain
        self.assertIn(["-r", "requirements.txt"], args)
        self.assertIn(["mock"], args)
        self.assertEqual(args[-1], ["pytest"])
        self.assertEqual(len(log), len(fake.calls))

    def test_missing_modules_are_installed_in_both_arms(self):
        outputs = {"pre": ["No module named 'yaml'\nNo module named 'mypkg'", ""], "gold": ["No module named 'requests'", ""]}
        installs = {"pre": [], "gold": []}
        old_c, old_p = T.collect, T.pip
        T.collect = lambda py, src, tests: outputs[py].pop(0)
        T.pip = lambda py, args, log, cwd=None: installs[py].append(args[0]) or 0
        try:
            repairs = []
            src = tree({"mypkg/__init__.py": ""})
            T.repair({"pre": ("pre", src), "gold": ("gold", src)}, ["t.py"], repairs)
        finally:
            T.collect, T.pip = old_c, old_p
        self.assertEqual(installs["pre"], ["requests", "PyYAML"])
        self.assertEqual(installs["pre"], installs["gold"])       # identical environments on both arms
        self.assertEqual(repairs[0]["installing"], ["requests", "yaml"])
        self.assertEqual(repairs[-1]["installing"], [])            # stops when nothing new is missing

    def test_classification_matches_the_frozen_tool(self):
        pre = {"a": {"passed": False}, "b": {"passed": True}, "::f.py": {"passed": False}}
        gold = {"a": {"passed": True}, "b": {"passed": True}, "c": {"passed": True}}
        coll, cls = T.classify(pre, gold)
        self.assertEqual(coll, {"::f.py"})
        self.assertEqual(cls, {"a": "F->P", "b": "P->P", "c": "ERR(pre)"})


if __name__ == "__main__":
    unittest.main()
