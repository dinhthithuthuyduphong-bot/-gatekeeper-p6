"""Study G harmful-side runnability and oracle-evidence check (skill NEVER applied).
python tools/runnable_check_g.py study_g/harm_candidates.json NAME out_dir
Clones the pinned commit, installs it, runs the declared test command three times, and counts
upstream test lines that use `== None` / `!= None` on the code under test (tier-1 evidence)."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402

NONE_CMP = re.compile(r"[!=]=\s*None\b")


def main(spec_file, name, out_dir):
    spec = next(c for c in json.loads(Path(spec_file).read_text())["candidates"] if c["name"] == name)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"name": name, "python": sys.version.split()[0]}
    work = Path(tempfile.mkdtemp())
    try:
        root = work / "r"
        rec["commit"] = _clone_ref(spec["repo"], spec["ref"], root)
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        inst = subprocess.run([sys.executable, "-m", "pip", "install", "-q", f"{root}{spec.get('extras', '')}",
                               *spec.get("test_requirements", [])], env=env, capture_output=True, text=True)
        rec["install_ok"] = inst.returncode == 0
        rec["install_tail"] = (inst.stdout + inst.stderr)[-500:]
        evidence = []
        for p in root.rglob("*.py"):
            rel = p.relative_to(root).as_posix()
            if not re.search(r"(^|/)tests?/", rel):
                continue
            for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
                if NONE_CMP.search(line) and "assert" not in line.split("==")[0][-12:]:
                    evidence.append(f"{rel}:{i}: {line.strip()[:160]}")
        rec["test_lines_using_none_comparison"] = len(evidence)
        rec["examples"] = evidence[:25]
        runs = []
        for i in range(3):
            p = subprocess.run(spec["test_cmd"], shell=True, cwd=root, capture_output=True, text=True,
                               timeout=1800, env=dict(os.environ, PYTHONPATH=str(root)))
            tail = (p.stdout + p.stderr)[-1500:]
            m = re.search(r"(\d+) passed", tail) or re.search(r"Ran (\d+) tests", tail)
            runs.append({"exit": p.returncode, "passed_or_ran": int(m.group(1)) if m else 0, "tail": tail[-500:]})
        rec["runs"] = runs
        rec["runnable"] = rec["install_ok"] and all(r["passed_or_ran"] >= 5 for r in runs)
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"[:400]
        rec["runnable"] = False
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"RUNNABLE_{name.replace('/', '_')}.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps({k: rec.get(k) for k in ("name", "commit", "install_ok", "runnable", "test_lines_using_none_comparison")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
