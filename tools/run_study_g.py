"""Study G runner: registers the extension transform, then runs the frozen Study D runner
unchanged.  python tools/run_study_g.py study_g/config_study_g.json TARGET out_dir"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext.none_identity import register  # noqa: E402

register()
import run_study_d  # noqa: E402

if __name__ == "__main__":
    sys.exit(run_study_d.main(*sys.argv[1:4]))
