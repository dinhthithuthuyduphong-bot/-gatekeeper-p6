"""Applicability scan with any skill, including extension transforms (Study G draft).
python tools/applicability_scan_ext.py CANDIDATES.json OUT_DIR SKILL.json
Reuses tools/applicability_scan.py unchanged; only the skill is swapped."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext.none_identity import register  # noqa: E402
import applicability_scan as A  # noqa: E402
from gatekeeper_lite.skill import Skill  # noqa: E402

register()
_orig_load = Skill.load


def main(candidates, out_dir, skill_path):
    Skill.load = staticmethod(lambda _p: _orig_load(ROOT / skill_path))
    return A.main(candidates, out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
