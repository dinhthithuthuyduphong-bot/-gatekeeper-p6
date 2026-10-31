import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import pin_actions as P  # noqa: E402

WF = """jobs:
  a:
    steps:
      - uses: actions/checkout@v6
      - uses: actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f
      - name: auth
        uses: google-github-actions/auth@v2
      - uses: ./local-action
"""


class PinActionsTest(unittest.TestCase):
    def test_rewrites_tags_keeps_shas_and_upgrades(self):
        calls = []

        def resolver(repo, tag):
            calls.append((repo, tag))
            return ("a" if repo.startswith("actions") else "b") * 40

        new, n, unpinned = P.rewrite(WF, {"google-github-actions/auth": "v3"}, resolver, {})
        self.assertEqual(n, 2)
        self.assertIn("uses: actions/checkout@" + "a" * 40 + " # v6", new)
        self.assertIn("uses: google-github-actions/auth@" + "b" * 40 + " # v3", new)
        self.assertIn("upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f", new)
        self.assertIn("uses: ./local-action", new)
        self.assertEqual(sorted(calls), [("actions/checkout", "v6"), ("google-github-actions/auth", "v3")])
        self.assertEqual(sorted(unpinned), ["actions/checkout@v6", "google-github-actions/auth@v2"])

    def test_peels_annotated_tags(self):
        responses = {"repos/o/r/git/ref/tags/v1": {"object": {"type": "tag", "sha": "t" * 40}},
                     "repos/o/r/git/tags/" + "t" * 40: {"object": {"type": "commit", "sha": "c" * 40}}}
        self.assertEqual(P.resolve("o/r", "v1", api=responses.__getitem__), "c" * 40)


if __name__ == "__main__":
    unittest.main()
