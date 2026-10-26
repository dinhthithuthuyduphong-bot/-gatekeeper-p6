"""Development run of the version-2 vetting on one shard (A* half only; NOT a registered study stage).

python tools/vet_dev.py CANDIDATES.json OUT_DIR SHARD K [LIMIT] [TIMEOUT_SECONDS]
Reuses the frozen shard logic of tools/vet_slice.py, with tools/vet_target2.py as the vetting tool.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_slice  # noqa: E402


def runner(spec_path, out_dir, timeout):
    return subprocess.run([sys.executable, str(ROOT / "tools" / "vet_target2.py"), str(spec_path), str(out_dir)],
                          capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(vet_slice.run(a[0], a[1], a[2], a[3], *(a[4:6] or []), runner=runner) if len(a) <= 6 else 2)
