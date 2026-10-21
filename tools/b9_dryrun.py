"""B9 dry run on the REAL Study D targets at 0 cost: the "model" answers with the upstream
gold fix (git diff pre..gold restricted to the target's editable modules), written into a
cassette that the UNCHANGED frozen tools/run_b9.py then replays.  This exercises cloning,
installing, edit rights, git apply, the visible oracle check, census, hidden-oracle scoring
and the final verdict end to end.  These runs are pipeline acceptance only, NOT B9 evidence.

python tools/b9_dryrun.py D1_py_ecc out_dir [gold|skill]
  gold  : the answer is the upstream fix restricted to the editable modules (default)
  skill : the answer is the frozen skill's own rewrite as a diff (exercises scoring paths
          where the upstream fix needs files outside the edit rights, e.g. py_ecc utils.py)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import run_b9  # noqa: E402  (frozen; used unchanged)
from fetch_real_targets import _clone_ref  # noqa: E402
from gatekeeper_lite.b9 import CassetteClient, build_messages  # noqa: E402

VETTING = {"D1_py_ecc": "py_ecc_161", "D2_cerberus": "cerberus_144", "D3_speckit": "speckit_3268",
           "D4_openfeature": "openfeature_621", "D5_pycubrid": "pycubrid_479", "A1_speckit_catalog": "speckit_2589"}
GIT = ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false"]


def gold_diff(manifest: dict, spec: dict, modules: list) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        subprocess.run([*GIT, "init", "-q"], cwd=repo, check=True)
        subprocess.run([*GIT, "remote", "add", "origin", manifest["checkout"]["repo"]], cwd=repo, check=True)
        subprocess.run([*GIT, "fetch", "-q", "--depth", "1", "origin", manifest["checkout"]["ref"]], cwd=repo, check=True)
        pre = subprocess.run([*GIT, "rev-parse", "FETCH_HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
        subprocess.run([*GIT, "fetch", "-q", "--depth", "1", "origin", spec["gold"]], cwd=repo, check=True)
        gold = subprocess.run([*GIT, "rev-parse", "FETCH_HEAD"], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()
        return subprocess.run([*GIT, "diff", pre, gold, "--", *modules], cwd=repo, check=True,
                              capture_output=True, text=True).stdout


def skill_diff(root: Path, modules: list) -> str:
    import difflib
    from gatekeeper_lite import transforms as T
    from gatekeeper_lite.skill import Skill
    skill = Skill.load(ROOT / "study_d" / "skills" / "bool-excluded-from-int.json")
    out = []
    for rel in modules:
        src = (root / rel).read_text(encoding="utf-8")
        try:
            new = skill.transform().apply(src, single_site=False).source
        except T.Abstain:
            continue
        lines = difflib.unified_diff(src.splitlines(True), new.splitlines(True), fromfile=f"a/{rel}", tofile=f"b/{rel}")
        out.append(f"diff --git a/{rel} b/{rel}\n" + "".join(lines))
    return "".join(out)


def main(target_id: str, out_dir: str, source: str = "gold") -> int:
    base = ROOT / "study_d"
    b9 = json.loads((base / "b9_config.json").read_text())
    manifest = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    spec = json.loads((base / "targets" / f"{VETTING[target_id]}.json").read_text())
    inst = json.loads((base / "b9_instances" / f"{target_id}.json").read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:            # sources exactly as run_b9 will see them
        root = Path(tmp) / "t"
        _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], root)
        sources = {rel: (root / rel).read_text(encoding="utf-8") for rel in manifest["modules"]}
        diff = gold_diff(manifest, spec, manifest["modules"]) if source == "gold" else skill_diff(root, manifest["modules"])
    (out / f"{source.upper()}_DIFF_{target_id}.patch").write_text(diff)
    messages = build_messages(inst["issue"], sources, inst["visible_desc"])
    model = b9["models"][0]["name"]
    cassette = CassetteClient(out / f"cassette_{target_id}_{model}.json", "replay")
    reply = {"text": diff or "no diff available", "usage": {"input": sum(len(m["content"]) for m in messages) // 4,
                                                            "output": len(diff) // 4}}
    for rep in range(b9["repetitions"]):
        for i in range(b9["budget"]["max_calls"]):
            key = CassetteClient.key(model, messages, b9["budget"]["max_output_tokens"], 0.0 if i == 0 else 0.8,
                                     b9["seed"] + 100 * rep + i)
            cassette.data[key] = reply
    cassette.path.write_text(json.dumps(cassette.data))
    rc = run_b9.main(str(base / "b9_config.json"), str(base / "config_study_d.json"), target_id, model,
                     out_dir, "replay")
    # Mark the output so that no analysis tool can mistake it for B9 evidence.
    src = out / f"RESULT_B9_{target_id}_{model}.json"
    if src.exists():
        data = json.loads(src.read_text())
        data.update(evidence="DRYRUN_PIPELINE_ACCEPTANCE_NOT_B9", answer_source=source,
                    usage_note="token counts are estimates (characters/4) written by the dry-run tool, not provider usage")
        (out / f"DRYRUN_RESULT_B9_{target_id}_{source}.json").write_text(json.dumps(data, indent=2))
        src.unlink()
    return rc


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
