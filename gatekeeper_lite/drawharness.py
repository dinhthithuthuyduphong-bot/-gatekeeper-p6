"""Sequential paired evaluation on i.i.d. draws from declared scope generators (Study D).

Two persistent workers (baseline / treatment), each a separate Python process importing
its own snapshot.  For each scope the coordinator draws inputs one at a time from the
scope generator, sends the SAME draw to both workers, judges the pair with the oracle,
updates the e-processes and STOPS for real as soon as a decision is reached, so the
measured cost is the cost actually spent.  Oracle module API:
  scopes()                      -> {scope_name: generator(rng) -> draw (JSON-serialisable)}
  execute(draw)                 -> outcome dict (runs inside a worker)
  judge(scope, draw, out_without, out_with) -> (passed_without, passed_with)
"""
from __future__ import annotations

import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict

from .eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


class _Worker:
    def __init__(self, snapshot: Path, pythonpath, oracle_path: Path, seed: int):
        paths = [str(snapshot / p) for p in pythonpath] + [str(snapshot), str(PACKAGE_ROOT)]
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(paths), PYTHONHASHSEED=str(int(seed) % 4294967296),
                   PYTHONDONTWRITEBYTECODE="1")
        t0 = time.perf_counter()
        self.proc = subprocess.Popen([sys.executable, "-m", "gatekeeper_lite.drawworker",
                                      str(oracle_path)], cwd=str(snapshot), env=env,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
        ready = self.proc.stdout.readline()
        if not ready.strip():
            raise RuntimeError("worker failed to start: " + self.proc.stderr.read()[-800:])
        self.startup_seconds = time.perf_counter() - t0
        self.n = 0

    def run(self, draw) -> dict:
        self.n += 1
        self.proc.stdin.write(json.dumps({"id": self.n, "draw": draw}) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("worker died: " + self.proc.stderr.read()[-800:])
        return json.loads(line)["outcome"]

    def close(self):
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
        for stream in (self.proc.stdout, self.proc.stderr):
            try:
                stream.close()
            except Exception:
                pass


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("gk_draw_oracle_coord", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_draw_study(target, treated: Dict[str, str], oracle_path: Path, cfg: dict,
                   k_cells: int) -> dict:
    """treated: {module path relative to target root: rewritten source}."""
    oracle_path = Path(oracle_path).resolve()
    oracle = _load(oracle_path)
    work = Path(tempfile.mkdtemp(prefix="gk_draw_"))
    workers = {}
    try:
        snaps = {}
        for arm in ("baseline", "treatment"):
            snap = work / arm
            shutil.copytree(target.root, snap, symlinks=True,
                            ignore=shutil.ignore_patterns("__pycache__", ".git"))
            if arm == "treatment":
                for rel, src in treated.items():
                    (snap / rel).write_text(src, encoding="utf-8")
            snaps[arm] = snap
            workers[arm] = _Worker(snap, target.manifest.get("pythonpath", []), oracle_path,
                                   cfg["seed"])
        alpha, n_max = cfg["alpha"], cfg["n_max"]
        stop_admit = k_cells / alpha
        stop_alarm = 1.0 / cfg.get("alpha_alarm", 0.05)
        results = {}
        for scope, gen in oracle.scopes().items():
            rng = random.Random(f"{cfg['seed']}:{target.target_id}:{scope}")
            ben, cert = BettingEProcess(cfg["theta"]), HarmCertEProcess(cfg["eta"])
            alarm = HarmAlarmEProcess(cfg["eta"])
            counts = {"help": 0, "tie": 0, "hurt": 0, "harness_error": 0}
            trace = []          # [z, regressed] per draw: enables pre-registered ablation replays
            decision, t0, n = "UNDECIDED", time.perf_counter(), 0
            gk_n, gk_seconds = None, None
            b8_full = cfg.get("b8_full", False)   # keep drawing after the decision for B8 only
            for n in range(1, n_max + 1):
                draw = gen(rng)
                ow, ot = workers["baseline"].run(draw), workers["treatment"].run(draw)
                if "harness_error" in ow or "harness_error" in ot:
                    counts["harness_error"] += 1
                    pw, pt = True, False          # conservative: counts as harm
                else:
                    pw, pt = oracle.judge(scope, draw, ow, ot)
                z = (0.0 if pt else 1.0) - (0.0 if pw else 1.0)
                counts["help" if z < 0 else "hurt" if z > 0 else "tie"] += 1
                trace.append([z, bool(pw and not pt)])
                if gk_n is None:
                    ben.update(z)
                    cert.update(pw and not pt)
                    alarm.update(pw and not pt)
                    if alarm.value >= stop_alarm:
                        decision = "REJECT_HARM"
                    elif min(ben.value, cert.value) >= stop_admit:
                        decision = "ADMIT"
                    if decision != "UNDECIDED":
                        gk_n, gk_seconds = n, time.perf_counter() - t0
                        gk_counts = dict(counts)
                        if not b8_full:
                            break
            if gk_n is None:
                gk_n, gk_seconds, gk_counts = n, time.perf_counter() - t0, dict(counts)
            results[scope] = {"decision": decision, "draws": gk_n, "counts": gk_counts,
                              "gatekeeper_seconds": round(gk_seconds, 4),
                              "b8": {"draws": n, "counts": counts,
                                     "decision": "REJECT" if counts["hurt"] else "ADMIT"} if b8_full else None,
                              "e_benefit": ben.value, "e_cert": cert.value,
                              "e_alarm": alarm.value,
                              "e_min": min(ben.value, cert.value),
                              "trace": trace,
                              "seconds": round(time.perf_counter() - t0, 4)}
        return {"scopes": results,
                "startup_seconds": {a: round(w.startup_seconds, 4) for a, w in workers.items()},
                "stopped_by_decision": True}
    finally:
        for w in workers.values():
            w.close()
        shutil.rmtree(work, ignore_errors=True)
