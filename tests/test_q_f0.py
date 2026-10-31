import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import q_f0 as Q  # noqa: E402

PATCH = "diff --git a/django/db/models/x.py b/django/db/models/x.py\n--- a/django/db/models/x.py\n+++ b/django/db/models/x.py\n@@ -1 +1 @@\n-a\n+b\n" \
        "diff --git a/tests/test_x.py b/tests/test_x.py\n--- a/tests/test_x.py\n+++ b/tests/test_x.py\n@@ -1 +1 @@\n-a\n+b\n"


class QF0(unittest.TestCase):
    def test_image_name(self):
        self.assertEqual(Q.image_name("django__django-11099"), "swebench/sweb.eval.x86_64.django_1776_django-11099:latest")

    def test_edited_modules_skip_tests(self):
        self.assertEqual(Q.edited_modules(PATCH), ["django/db/models/x.py"])

    def test_paging_and_stratified_sample(self):
        rows = [{"instance_id": "r%d__p-%d" % (i % 4, i), "repo": "r%d" % (i % 4), "patch": PATCH} for i in range(250)]
        pages = {o: {"rows": [{"row": r} for r in rows[o:o + 100]]} for o in (0, 100, 200)}
        got = Q.fetch_rows(get=lambda u: pages[int(u.split("offset=")[1].split("&")[0])])
        self.assertEqual(len(got), 250)
        s = Q.stratified(got, 3)
        self.assertEqual(len(s), 12)
        self.assertEqual(s, Q.stratified(list(reversed(got)), 3))                 # independent of input order


if __name__ == "__main__":
    unittest.main()
