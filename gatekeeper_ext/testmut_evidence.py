"""Evidence retention for development-only test mutation; no admission or paid API calls."""
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path


def _json_value(value):
    if isinstance(value, bytes):
        return {"type": "bytes", "hex": value.hex()}
    if isinstance(value, Path):
        return str(value)
    raise TypeError("Unsupported evidence value: " + type(value).__name__)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=_json_value) + "\n", encoding="utf-8")


def execute_logged(command, cwd, env, prefix, timeout):
    """Keep stdout, stderr, exit status and elapsed time; never record environment values."""
    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"command": list(command), "cwd": str(cwd), "timeout_seconds": timeout,
               "returncode": None, "status": "STARTED"}
    started = time.perf_counter()
    try:
        with Path(str(prefix) + ".stdout.txt").open("w", encoding="utf-8") as stdout, \
             Path(str(prefix) + ".stderr.txt").open("w", encoding="utf-8") as stderr:
            proc = subprocess.run(command, cwd=str(cwd), env=env, stdout=stdout, stderr=stderr,
                                  timeout=timeout, check=False)
            receipt.update(status="COMPLETED", returncode=proc.returncode)
    except subprocess.TimeoutExpired:
        receipt["status"] = "TIMEOUT"
    except OSError as exc:
        receipt.update(status="LAUNCH_ERROR", error_type=type(exc).__name__, error=str(exc))
    finally:
        receipt["seconds"] = round(time.perf_counter() - started, 6)
        write_json(str(prefix) + ".command.json", receipt)
    return receipt


def feasibility_checks(patches, mutants, deterministic):
    a = bool(patches) and all(v.get("help", 0) > 0 for v in patches.values())
    b = bool(patches) and all(v.get("hurt", 0) == 0 for v in patches.values())
    d = any(m.get("hurt", 0) > 0 for m in mutants)
    rows = list(patches.values()) + list(mutants)
    complete = bool(rows) and all(v.get("missing") == 0 for v in rows)
    return {"a_detects_bug_with_known_good_patch": a, "b_no_regression_for_known_good_patch": b,
            "c_deterministic": bool(deterministic), "d_catches_a_mutant": d,
            "no_missing_outcomes": complete, "all_four": bool(a and b and deterministic and d and complete)}


def preserve_run(source, destination):
    """Preserve raw records and generated tests, excluding disposable repository snapshots."""
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        write_json(destination / "NO_RUN_OUTPUT.json", {"reason": "execution ended before analysis produced output"})
        return
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if len(rel.parts) > 1 and rel.parts[0].startswith("arm_"):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        dest = destination / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)


def write_inventory(root):
    root = Path(root)
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "EVIDENCE_INVENTORY.json":
            rows.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size,
                         "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    write_json(root / "EVIDENCE_INVENTORY.json", {"schema_version": 1, "files": rows,
               "excluded": "disposable arm_* repository directories; inventory does not hash itself"})


def write_result_md(result, path):
    check = result.get("checks", {})
    lines = ["# Test-mutation development result: " + result.get("target", "unknown"), "",
             "**DEVELOPMENT ONLY. No prospective admission, no model-performance evidence.**", "",
             "| Field | Observed value |", "|---|---|",
             "| Execution status | %s |" % result.get("status", "UNKNOWN"),
             "| Eligible | %s |" % result.get("eligible", False),
             "| Reason | %s |" % str(result.get("reason", "not applicable")).replace("|", "/").replace("\n", " "),
             "| Harness version | %s |" % result.get("harness_version", "legacy (not comparable)"),
             "| Compiled draw IDs | %s |" % result.get("draws_compiled", result.get("draws_run", "N/A")),
             "| Draws on which every arm only fails | %s |" % result.get("common_failure_fraction", "not recorded"),
             "| Complete IDs by patch | %s |" % result.get("complete_draws_by_patch", "not recorded"),
             "| Deterministic in measured repeats | %s |" % result.get("deterministic", "N/A"),
             "| No missing outcomes | %s |" % check.get("no_missing_outcomes", "N/A"),
             "| All checks, including completeness | %s |" % check.get("all_four", False),
             "| Gold used as its own candidate | %s |" % result.get("b_is_self_comparison", "not recorded"), "",
             "## Files and reproduction", "",
             "Read TM_<target>.json and evidence/<target>/EVIDENCE_INVENTORY.json together. Raw XML/JSON,",
             "command receipts, stdout/stderr, mutation catalog and per-arm signatures are retained when produced.",
             "Run the manual tm-dev.yml workflow at the recorded commit, choosing the same target and draw budget.",
             "Do not overwrite previous output directories. No model endpoint is used.", "",
             "## Interpretation", "",
             "A successful workflow means the diagnostic completed, not that the research hypothesis passed.",
             "Test mutations can alter assertions, and signature differences can reflect test noise.",
             "Missing outcomes, nondeterminism and self-comparisons do not certify a working oracle.",
             "The unique-mutant sampling design is not an iid deployment-input distribution.",
             "Study L G1 remains failed. These exposed targets cannot become a new confirmatory cohort."]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
