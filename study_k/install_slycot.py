"""Install one checksum-pinned conda-forge Slycot binary into a fresh Linux CPython 3.8 venv.

This is a dependency restore, not a target-code shim. BLAS/LAPACK/gfortran shared
libraries must already be installed. No provider credentials or model calls.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import sysconfig
import tarfile
import urllib.request

URL = "https://api.anaconda.org/download/conda-forge/slycot/0.4.0.0/linux-64/slycot-0.4.0.0-py38hf9f4372_4.tar.bz2"
SHA256 = "6ca4f5e8df4140f3ee9361a6449b4074226e3422f67976a5967946ee174b4fd3"


def main(output):
    if sys.version_info[:2] != (3,8) or sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("This pinned binary is only for Linux x86_64 CPython 3.8")
    site = Path(sysconfig.get_paths()["purelib"]).resolve()
    if (site / "slycot").exists():
        raise RuntimeError("Use a fresh environment; do not overwrite an existing Slycot installation")
    with urllib.request.urlopen(URL, timeout=90) as response:
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise RuntimeError("Slycot archive checksum mismatch")
    prefix = "lib/python3.8/site-packages/"
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:bz2") as archive:
        for member in archive.getmembers():
            if not member.name.startswith(prefix) or not member.isfile():
                continue
            rel = Path(member.name[len(prefix):])
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError("Unsafe archive path")
            dest = site / rel
            try:
                dest.resolve().relative_to(site)
            except ValueError:
                raise RuntimeError("Archive destination escapes site-packages")
            payload = archive.extractfile(member).read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(payload)
            files[str(rel)] = hashlib.sha256(payload).hexdigest()
        metadata = json.loads(archive.extractfile("info/index.json").read())
    command=[sys.executable,"-c","import slycot; from slycot import tb04ad; print(slycot.__version__, slycot.__file__)"]
    check=subprocess.run(command,capture_output=True,text=True)
    record={"source_url":URL,"sha256":SHA256,"metadata":metadata,"installed_sha256":files,
            "command":command,"returncode":check.returncode,"stdout":check.stdout,"stderr":check.stderr}
    Path(output).write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({k:record[k] for k in ("source_url","sha256","returncode","stdout","stderr")}),flush=True)
    if check.returncode:
        raise RuntimeError("Slycot shared-library/import check failed; see receipt")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt",required=True)
    main(parser.parse_args().receipt)

# Study K — exploratory python-control transfer

This is an **explicitly retrospective follow-up**, not a new prospective study.
The frozen `none_identity` skill was applied to historical python-control
`fb5ebf6296079229705792cc508ad23d45e326aa`. The transformed module is AST-equivalent
to the same module in upstream fix `60aba3ab39cef2ac11c4bc08c2b08a9abd084205`.
No learned rule, gate threshold, or upstream test was edited.

See [RESULT_VI.md](RESULT_VI.md) and the raw result at
[results/local-20261025-clean/RESULT.md](results/local-20261025-clean/RESULT.md).
The complete selected 16-test FRD module is run for all three arms, three times.
The 15 baseline-passing tests form the regression census; the known failing
upstream `testNyquist` is the repair witness. No test is deselected or rewritten.

## Evidence boundaries

- Upstream `testNyquist` is a **no-exception smoke test**. Its provenance is
  strong; it does not assert numerical accuracy or plot quality.
- The separate draw oracle checks the analytic complex frequency response of
  `gain / (s*s + a*s + b)`. It is researcher-authored, not an upstream tier-1 test.
- `array_frequencies` and `default_frequencies` are two scopes of one repository,
  not two independent targets. The 300 draws and three repetitions are not
  independent repositories either.
- Two of the three rewritten comparison sites are reached by the declared
  scopes. `gangof4_plot` is unexercised. The result is neither full-repo safety
  nor admission for unrestricted use of the entire patch.
- The engine executes all 300 draws per scope for diagnostics. A stopping index
  is reported, but this run is **not** a measured production cost saving.
- Historical code is evaluated with a pinned compatibility environment from
  later years; this is not reconstruction of the original 2014 environment.
- Prior D/E/G/H data and Study I results are unchanged; B9 remains HOLD.

## Read-only audit

From the repository root with Python 3.12, without target dependencies:

```bash
python study_k/verify.py --results study_k/results/local-20261025-clean --output study-k-verified.json
```

This recomputes labels, exact generator draws/ordering, test counts, stopped
e-values, the complete two-cell e-Holm family, line reach and state-check results
from XML/JSONL. It fails on missing or contradictory evidence.

## Run again

Use GitHub Actions **Gatekeeper Study K zero-cost reproduction**, branch `main`.
It restores Python 3.8.20 with uv, compiles Matplotlib 2.2.5 with the declared
system headers, restores a checksum-pinned conda-forge Slycot binary, fetches
the exact source commit, and executes `study_k/run.py`. The result artifact is
**study-k-python-control**. No API key or paid provider is used.

The workflow records setup logs before reproduction, so setup failures are
visible in the artifact. It has `contents: read`; it never updates the repository.
This workflow has been parsed and its Python commands exercised locally; a new
GitHub-hosted run is still required after the user updates main.

Local Linux x86_64 reproduction requires a fresh CPython 3.8.20 environment,
the packages in `requirements-build.txt`, Matplotlib 2.2.5, and the Slycot binary
installed by `install_slycot.py`. Native dependencies are listed in the workflow.
Use a new output directory on every run:

```bash
python -u study_k/run.py --output study-k-new-run
```

## Search and installation history

[search_evidence/SEARCH_RESULT.md](search_evidence/SEARCH_RESULT.md) records
the additional unsuccessful searches and the independent Airflow revert lead.
`results/pilot_attempts/` preserves collection failure, missing-Slycot failures
and the first successful paired test. `results/environment_setup/` preserves
failed and successful installation attempts. The first complete measured run
in `results/local-20261025/` had stale duplicate Matplotlib distribution metadata;
the reported run is a full rerun in a fresh environment at
`results/local-20261025-clean/`. The outcome is the same. Neither run is discarded.

The license for the upstream source is retained in the full module headers in
`vendor/`; the test file is an unmodified byte-for-byte copy. Slycot is downloaded
from conda-forge under its upstream license; no compiled binary is distributed
in this repository or update ZIP.

# Pin the Python/build dependencies before building Matplotlib 2.2.5.
cycler==0.12.1
exceptiongroup==1.3.1
iniconfig==2.1.0
kiwisolver==1.4.7
nose==1.3.7
numpy==1.17.5
packaging==26.2
pillow==10.4.0
pluggy==1.5.0
pyparsing==3.1.4
pytest==7.4.4
python-dateutil==3.0.0
scipy==1.4.1
setuptools==59.8.0
six==1.17.0
tomli==2.5.0
typing-extensions==4.13.2
tzdata==2026.5
wheel==0.45.1

# Python-control — thêm một target có lợi cho skill thứ hai

**Đã tái lập được một trường hợp có lợi bằng test upstream không đổi.** Đây là
kết quả hồi cứu, không phải bằng chứng tiến cứu hoặc khái quát trên mọi repo.
Ngày đóng gói: 25/10/2026. Chi phí API: 0 USD. B9 vẫn HOLD.

| Bằng chứng | Kết quả |
|---|---|
| Baseline, toàn bộ module `control/tests/frd_test.py` | 15 pass, 1 fail chức năng |
| Áp skill `none_identity` đã đóng băng | 16 pass, 0 fail |
| Áp bản sửa upstream cho cùng module nguồn | 16 pass, 0 fail |
| Lặp | Ba tiến trình mới mỗi nhánh; kết quả nhất quán |
| Regression trên 15 test baseline đang pass | 0 |
| Scope cấp mảng tần số | 300 help / 0 tie / 0 hurt; dừng chẩn đoán ở draw 65 |
| Scope tần số mặc định | 0 help / 300 tie / 0 hurt; QUARANTINE |
| Kiểm tra state/thứ tự | 100 draws/scope, worker mới mỗi 25 draws; 0 sai khác |
| Reach của vị trí sửa | 100% draws đi qua một vị trí sửa; tổng cộng 2/3 vị trí được bao phủ |

Nguồn:

- Parent: [fb5ebf6296079229705792cc508ad23d45e326aa](https://github.com/python-control/python-control/commit/fb5ebf6296079229705792cc508ad23d45e326aa).
- Fix: [60aba3ab39cef2ac11c4bc08c2b08a9abd084205](https://github.com/python-control/python-control/commit/60aba3ab39cef2ac11c4bc08c2b08a9abd084205).
- Test gốc: `TestFRD.testNyquist`, có sẵn tại parent. Baseline ném `ValueError`
  tại `omega == None` khi nhận NumPy array; skill đổi thành phép so sánh identity.
- Mã skill tạo ra tương đương AST với file `control/freqplot.py` của fix upstream.
  Chỉ module đã khai báo được sửa, không áp toàn bộ commit upstream.

**Không gộp chất lượng nguồn oracle với độ mạnh của assertion:** test upstream này
là smoke test “chạy không exception”, không kiểm tra giá trị số hay hình đồ thị.
Oracle draw riêng kiểm tra đáp ứng phức theo công thức giải tích và phải được ghi
là do nghiên cứu viên viết. Đã chạy toàn bộ module 16 test, không deselect test lỗi.

Runtime: CPython 3.8.20, NumPy 1.17.5, SciPy 1.4.1, Matplotlib 2.2.5, Slycot
0.4.0.0. Đây là môi trường tương thích được ghim, không phải runtime nguyên gốc
năm 2014. Các lần thất bại khi dựng môi trường đều được giữ trong artifact.

Raw chính: [RESULT.md](results/local-20261025-clean/RESULT.md),
`RESULT.json`, `PRE_EXECUTION.json`, 9 XML + log, `draws.jsonl`,
`statelessness.jsonl`, `skill.patch` và `VERIFIED.json` cùng thư mục.
Runner và bộ kiểm toán không gọi model hoặc mở khóa paid B9.

**Còn thiếu:** cohort mới được đóng băng công khai trước treatment; target gây
hại độc lập tiếp theo; kiểm chứng các API/vị trí ngoài scope (đặc biệt
`gangof4_plot`); so sánh thêm với smoke/census mạnh và kết quả theo model.
Không nâng kết quả này thành chứng nhận triển khai toàn patch trên toàn repo.

"""Reproduce the retrospective python-control transfer with zero model calls.

Preserves the complete 16-test upstream module, including the failing witness.
No test is deselected. New directories are required so failed attempts survive.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from study_i.run import digest, run_command, write_json, xml_cases


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    require(not out.exists() or not any(out.iterdir()), "Choose a new output directory")
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((HERE / "target.json").read_text())
    require(list(sys.version_info[:3]) == cfg["python"], "Wrong Python version")
    for name, version in cfg["runtime_versions"].items():
        require(importlib.metadata.version(name) == version, "Wrong runtime package: " + name)
    for rel, sha in cfg["gatekeeper_sha256"].items():
        require(digest(ROOT / rel) == sha, "Frozen engine/skill changed: " + rel)
    for rel, sha in cfg["vendor_sha256"].items():
        require(digest(HERE / rel) == sha, "Vendor evidence changed: " + rel)
    os.environ.update(MPLBACKEND="Agg", OPENBLAS_NUM_THREADS="1",
                      PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    source = args.checkout.resolve() if args.checkout else out / "work/upstream"
    if not args.checkout:
        source.mkdir(parents=True)
        cmds = [["git", "init", "-q"], ["git", "fetch", "--depth=1",
                "https://github.com/" + cfg["repository"] + ".git", cfg["revision"]],
                ["git", "checkout", "--detach", "FETCH_HEAD"]]
        for i, cmd in enumerate(cmds):
            row = run_command(cmd, source, out / ("fetch_%s.log" % i), timeout=300)
            require(row["returncode"] == 0, "Checkout failed")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    require(revision == cfg["revision"], "Wrong source revision")
    require(not subprocess.check_output(["git", "diff", "HEAD"], cwd=source, text=True).strip(),
            "Tracked upstream files were modified")
    for rel, sha in cfg["source_sha256"].items():
        require(digest(source / rel) == sha, "Wrong source/test bytes: " + rel)
    from gatekeeper_ext.none_identity import register
    from gatekeeper_lite.gatekeeper import bind_modules, replay, screen
    from gatekeeper_lite.skill import Skill, Target
    register()
    skill = Skill.load(ROOT / "study_g/skills/none-identity.json")
    target = Target(cfg["target_id"], source, {"modules": [cfg["module"]],
                    "python": "3.8.20", "platform": "linux", "packages": {}, "pythonpath": []})
    bound = bind_modules([skill], target)
    require(len(bound["sites"]) == cfg["site_count"], "Binding count changed")
    require(replay(skill)["passed"] and screen(skill, target).in_scope, "Source replay/screen failed")
    gold = (HERE / "vendor/control_freqplot_gold.py").read_text()
    treated = bound["treated"][cfg["module"]]
    require(ast.dump(ast.parse(gold)) == ast.dump(ast.parse(treated)), "Skill differs from upstream fix")
    arms = {}
    for arm in ["baseline", "treated", "gold"]:
        path = out / "work" / arm
        shutil.copytree(source, path, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"))
        if arm != "baseline":
            (path / cfg["module"]).write_text(treated if arm == "treated" else gold)
        require(digest(path / cfg["test_module"]) == cfg["source_sha256"][cfg["test_module"]],
                "Upstream test was edited")
        arms[arm] = path
    patch = "".join(difflib.unified_diff((source / cfg["module"]).read_text().splitlines(True),
                   treated.splitlines(True), fromfile="a/"+cfg["module"], tofile="b/"+cfg["module"]))
    (out / "skill.patch").write_text(patch)
    code = {str(p.relative_to(ROOT)): digest(p) for p in
            [HERE / "run.py", HERE / "oracles/control_frequency.py", ROOT / "study_i/run.py"]}
    record = {"status": "RUNNING", "not_preregistered": True, "config": cfg,
              "config_sha256": digest(HERE / "target.json"), "code_sha256": code,
              "source_revision": revision, "source_test_sha256": cfg["source_sha256"],
              "started_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "environment": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()),
              "bindings": bound["sites"], "gold_ast_equal": True, "source_replay": replay(skill),
              "llm_calls": 0, "model_cost_usd": 0, "runs": []}
    write_json(out / "PRE_EXECUTION.json", record)
    states = {}
    for arm, path in arms.items():
        repetitions = []
        env = dict(os.environ, PYTHONPATH=str(path), PYTHONHASHSEED="0")
        for rep in range(1, cfg["repetitions"]+1):
            label = "%s_%s" % (arm, rep)
            xml = out / (label + ".xml")
            cmd = [sys.executable, "-m", "pytest", cfg["test_module"], "-q", "--tb=short",
                   "-o", "addopts=", "-p", "no:cacheprovider", "--junitxml="+str(xml)]
            row = run_command(cmd, path, out / (label + ".log"), env=env)
            require(row["returncode"] in (0, 1) and xml.exists(), "Collection/environment failure")
            cases = xml_cases(xml)
            require(len(cases) == cfg["n_tests"], "Test inventory changed")
            require(all(v["status"] in ("passed", "failure") for v in cases.values()),
                    "Setup/collection errors or skips invalidate the complete-module claim")
            if arm == "baseline":
                failures = [k for k,v in cases.items() if v["status"] == "failure"]
                require(len(failures) == 1 and failures[0].endswith("TestFRD::testNyquist"),
                        "Unexpected baseline failures; do not drop them")
                detail = cases[failures[0]]["detail"] + cases[failures[0]]["message"]
                require("truth value of an array" in detail and "nyquist_plot" in detail,
                        "Witness is not the target functional ValueError")
            labels = {k:v["status"] for k,v in cases.items()}
            repetitions.append(labels)
            row.update(arm=arm, repetition=rep, xml=xml.name, case_status=labels,
                       counts={s: sum(v == s for v in labels.values()) for s in ("passed", "failure")})
            record["runs"].append(row)
            write_json(out / "execution_progress.json", record)
        require(all(x == repetitions[0] for x in repetitions), "Unstable upstream outcomes")
        states[arm] = repetitions[0]
    require(set(states["baseline"]) == set(states["treated"]) == set(states["gold"]), "Test inventory mismatch")
    require(states["gold"] == states["treated"], "Gold/skill outcomes differ")
    regressions = [k for k,v in states["baseline"].items() if v == "passed" and states["treated"][k] != "passed"]
    resolved = [k for k,v in states["baseline"].items() if v == "failure" and states["treated"][k] == "passed"]
    require(not regressions and len(resolved) == 1, "Beneficial transfer did not reproduce")
    record.update(census_regressions=regressions, resolved_upstream_tests=resolved,
                  baseline_passing_census=15, selected_module_only=True)
    from gatekeeper_lite import drawharness
    original_load = drawharness._load
    oracle_path = HERE / "oracles/control_frequency.py"
    def logged_load(path):
        module = original_load(path)
        original_judge = module.judge
        count = {s:0 for s in module.scopes()}
        def judge(scope, d, ow, ot):
            pw, pt = map(bool, original_judge(scope, d, ow, ot))
            count[scope] += 1
            with (out / "draws.jsonl").open("a") as log:
                log.write(json.dumps({"scope":scope, "n":count[scope], "draw":d, "without":ow, "with":ot,
                                     "passed_without":pw, "passed_with":pt, "z":int(not pt)-int(not pw)}, allow_nan=False)+"\n")
            if count[scope] % 100 == 0:
                print("DRAW_PROGRESS", scope, count[scope], flush=True)
            return pw, pt
        module.judge = judge
        return module
    drawharness._load = logged_load
    try:
        record["diagnostic_draws"] = drawharness.run_draw_study(target, bound["treated"], oracle_path,
                                      cfg["diagnostic_draws"], k_cells=len(cfg["diagnostic_draws"]["cells"]))
    finally:
        drawharness._load = original_load
    require(not any(s["b8"]["counts"]["harness_error"] for s in record["diagnostic_draws"]["scopes"].values()),
            "Draw harness failure")
    # Fresh workers plus a different order test finite sample state sensitivity.
    oracle = original_load(oracle_path)
    observations = [json.loads(x) for x in (out / "draws.jsonl").read_text().splitlines()]
    summary = {}
    with (out / "statelessness.jsonl").open("w") as log:
        for scope in oracle.scopes():
            selected = [r for r in observations if r["scope"] == scope][:100]
            random.Random("study-k-shuffle:" + scope).shuffle(selected)
            mismatches = 0
            for offset in range(0, 100, 25):
                workers = {}
                try:
                    for arm in ["baseline", "treated"]:
                        workers[arm] = drawharness._Worker(arms[arm], [], oracle_path, cfg["diagnostic_draws"]["seed"])
                    for row in selected[offset:offset+25]:
                        ow, ot = workers["baseline"].run(row["draw"]), workers["treated"].run(row["draw"])
                        clean = lambda x: {k:v for k,v in x.items() if k != "module"}
                        mismatch = clean(ow) != clean(row["without"]) or clean(ot) != clean(row["with"])
                        mismatches += int(mismatch)
                        log.write(json.dumps({"scope":scope, "n":row["n"], "without":ow, "with":ot,
                                              "mismatch":mismatch}, allow_nan=False)+"\n")
                        log.flush()
                finally:
                    for worker in workers.values():
                        worker.close()
            summary[scope] = {"compared":100, "mismatches":mismatches}
            print("STATELESSNESS", scope, summary[scope], flush=True)
    require(not any(x["mismatches"] for x in summary.values()), "State/order mismatch")
    record.update(status="VERIFIED_EXPLORATORY", statelessness=summary,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    write_json(out / "RESULT.json", record)
    from study_k.verify import audit
    audit(out, out / "VERIFIED.json", out / "RESULT.md")


if __name__ == "__main__":
    main()

{
  "status": "EXPLORATORY_RETROSPECTIVE_NOT_PREREGISTERED",
  "research_base_commit": "fcdd1b8b179f0ba8a312a7b8ec60d489e3c9b293",
  "target_id": "K1_python_control",
  "repository": "python-control/python-control",
  "revision": "fb5ebf6296079229705792cc508ad23d45e326aa",
  "gold_revision": "60aba3ab39cef2ac11c4bc08c2b08a9abd084205",
  "python": [
    3,
    8,
    20
  ],
  "module": "control/freqplot.py",
  "test_module": "control/tests/frd_test.py",
  "witness": "TestFRD.testNyquist",
  "site_count": 3,
  "n_tests": 16,
  "repetitions": 3,
  "scope_note": "Only SISO frequency-response scopes; selected FRD test module, not the whole repository. gangof4_plot is changed by the module-level transform but not covered by these scopes.",
  "oracle_note": "Unchanged parent-revision testNyquist is a no-exception smoke test (not a numerical-accuracy assertion). The independent analytic response check in the draw adapter is researcher-authored.",
  "runtime_versions": {
    "numpy": "1.17.5",
    "scipy": "1.4.1",
    "matplotlib": "2.2.5",
    "slycot": "0.4.0.0",
    "pytest": "7.4.4"
  },
  "source_sha256": {
    "control/freqplot.py": "a9e928d1ad2b396c439f234a6c9346c691dcb22a989e3aa2ffbbcc858238f3e5",
    "control/tests/frd_test.py": "8991217c99fcd424ab2bfd539465df16d4376fcf7b948639bb45cef547eadd2d"
  },
  "vendor_sha256": {
    "vendor/frd_test.py": "8991217c99fcd424ab2bfd539465df16d4376fcf7b948639bb45cef547eadd2d",
    "vendor/control_freqplot_before.py": "a9e928d1ad2b396c439f234a6c9346c691dcb22a989e3aa2ffbbcc858238f3e5",
    "vendor/control_freqplot_gold.py": "42f8cb65d1f54ed63e2c0503175a71ab2cd7de374122255705fad510e134b2ea"
  },
  "gatekeeper_sha256": {
    "gatekeeper_ext/none_identity.py": "6844f735580719b690b2ff074b87d540c1c559a538bb707df793f3450ac18759",
    "gatekeeper_lite/gatekeeper.py": "a95038ccdb01d2d750f16f43ff462785b5e916aefce85ed53f2bf71de5af4659",
    "gatekeeper_lite/skill.py": "07fd5a3516f4f9f46315fd9181f31cee3686f92535bd8fbb38ace6ffc24bec4d",
    "gatekeeper_lite/screen.py": "56fbacba4cff58a1d0864c3ef852ee7c6d5f225f06749a1a84fd8efa2624f112",
    "gatekeeper_lite/transforms.py": "61c71e5626a08d84775f82c93a3b3e4741be1cee9bc5bc51b65a4367c0205bda",
    "gatekeeper_lite/eprocess.py": "1a4856af0bbc8fae4f93b25a55254da005245349f23e6d040bdee38b850d746d",
    "gatekeeper_lite/drawharness.py": "a1fa1b68cb1881e9c858166819f2b916875234cd16d52f41f16a2612ca2e72b2",
    "gatekeeper_lite/drawworker.py": "9feccd1ade4c3e3238375f4d23c124c8cee85d0dba08a54db7d8f9f42605561f",
    "study_g/skills/none-identity.json": "89351f56b7ae95df18ed47d4e7d18562a7d43dc0d8f5e540eb4266d8072f7995",
    "study_g/skills/replay/get_delays_before.py": "6e8fec9df8fd3ab7adc11f03da9650004384722b529f713b457b56a2b6ae3715",
    "study_g/skills/replay/get_delays_after.py": "8938e463790f938be6560360bb3e0e469da755830a3bcc07aa82d479797181b7"
  },
  "diagnostic_draws": {
    "seed": 20261025,
    "alpha": 0.1,
    "theta": 0.2,
    "eta": 0.05,
    "alpha_alarm": 0.05,
    "n_max": 300,
    "b8_full": true,
    "cells": [
      "K1_python_control/array_frequencies",
      "K1_python_control/default_frequencies"
    ]
  }
}

"""Recompute Study K from raw XML and every paired draw, without target packages."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from study_i.run import digest, write_json, xml_cases
from gatekeeper_lite.eprocess import BettingEProcess, HarmCertEProcess, HarmAlarmEProcess, e_holm


def require(value, message):
    if not value:
        raise ValueError(message)


def counts(values):
    return {"help":sum(z < 0 for z in values), "tie":sum(z == 0 for z in values),
            "hurt":sum(z > 0 for z in values), "harness_error":0}


def audit(directory, output=None, markdown=None):
    directory = Path(directory)
    cfg = json.loads((HERE / "target.json").read_text())
    result = json.loads((directory / "RESULT.json").read_text())
    require(result["status"] == "VERIFIED_EXPLORATORY" and result["not_preregistered"], "Invalid status")
    require(result["config"] == cfg and result["config_sha256"] == digest(HERE / "target.json"), "Config changed")
    require(result["source_revision"] == cfg["revision"] and result["source_test_sha256"] == cfg["source_sha256"], "Wrong source")
    require(result["llm_calls"] == 0 and result["model_cost_usd"] == 0, "Unexpected model use")
    required_code = {"study_k/run.py", "study_k/oracles/control_frequency.py", "study_i/run.py"}
    require(set(result["code_sha256"]) == required_code, "Missing measured code hash")
    for rel, sha in result["code_sha256"].items():
        require(digest(ROOT / rel) == sha, "Measured code changed: " + rel)
    for rel, sha in cfg["gatekeeper_sha256"].items():
        require(digest(ROOT / rel) == sha, "Frozen engine/skill changed: " + rel)
    for rel, sha in cfg["vendor_sha256"].items():
        require(digest(HERE / rel) == sha, "Upstream vendor file changed: " + rel)
    expected_runs = {(a,n) for a in ("baseline","treated","gold") for n in range(1,cfg["repetitions"]+1)}
    require(Counter((r["arm"],r["repetition"]) for r in result["runs"]) == Counter(expected_runs), "Missing/duplicate run")
    states = {}
    for run in result["runs"]:
        cases = xml_cases(directory / run["xml"])
        labels = {k:v["status"] for k,v in cases.items()}
        require(len(cases) == cfg["n_tests"] and all(s in ("passed","failure") for s in labels.values()), "Invalid test inventory/outcome")
        require(labels == run["case_status"], "XML/JSON disagreement")
        c = {s:sum(v == s for v in labels.values()) for s in ("passed","failure")}
        require(c == run["counts"] and run["returncode"] == int(c["failure"] > 0), "Exit/count mismatch")
        require(math.isfinite(run["seconds"]) and run["seconds"] > 0 and (directory/run["log"]).stat().st_size > 0, "Missing log/time")
        if run["arm"] == "baseline":
            failures = [k for k,v in labels.items() if v == "failure"]
            require(len(failures) == 1 and failures[0].endswith("TestFRD::testNyquist"), "Unexpected baseline failure")
            detail = cases[failures[0]]["detail"]+cases[failures[0]]["message"]
            require("truth value of an array" in detail and "nyquist_plot" in detail, "Unclassified functional failure")
        else:
            require(c["failure"] == 0, "Skill/gold module not clean")
        if run["arm"] in states:
            require(states[run["arm"]] == labels, "Unstable repetitions")
        states[run["arm"]] = labels
    require(states["treated"] == states["gold"] and set(states["treated"]) == set(states["baseline"]), "Gold/test inventory mismatch")
    resolved = sorted(k for k,v in states["baseline"].items() if v == "failure" and states["treated"][k] == "passed")
    require(resolved == sorted(result["resolved_upstream_tests"]) and result["census_regressions"] == [], "Transfer summary mismatch")
    spec = importlib.util.spec_from_file_location("control_oracle_audit", HERE/"oracles/control_frequency.py")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    observed = defaultdict(list)
    for line in (directory/"draws.jsonl").read_text().splitlines():
        row = json.loads(line)
        require("harness_error" not in row["without"] and "harness_error" not in row["with"], "Harness failure")
        require("/baseline/" in row["without"].get("module","") and "/treatment/" in row["with"].get("module",""), "Wrong imports")
        pw,pt = map(bool,oracle.judge(row["scope"],row["draw"],row["without"],row["with"]))
        require([pw,pt] == [row["passed_without"],row["passed_with"]] and row["z"] == int(not pt)-int(not pw), "Oracle/Z mismatch")
        observed[row["scope"]].append(row)
    require(set(observed) == set(oracle.scopes()) == set(result["diagnostic_draws"]["scopes"]), "Missing/extra scope")
    settings=cfg["diagnostic_draws"]
    cells=[]
    for scope, rows in observed.items():
        require(len(rows) == settings["n_max"] and [r["n"] for r in rows] == list(range(1,settings["n_max"]+1)), "Incomplete draws")
        rng=random.Random("%s:%s:%s" % (settings["seed"],cfg["target_id"],scope))
        generator=oracle.scopes()[scope]
        require(all(r["draw"] == generator(rng) for r in rows), "Generator/order/seed mismatch")
        raw=result["diagnostic_draws"]["scopes"][scope]
        trace=[[r["z"],r["passed_without"] and not r["passed_with"]] for r in rows]
        require(trace == raw["trace"] and raw["b8"]["draws"] == len(rows), "Raw trace mismatch")
        require(counts([r["z"] for r in rows]) == raw["b8"]["counts"], "Full counts mismatch")
        ben,cert,alarm=BettingEProcess(settings["theta"]),HarmCertEProcess(settings["eta"]),HarmAlarmEProcess(settings["eta"])
        decision,stop="UNDECIDED",len(rows)
        for n,(z,harm) in enumerate(trace,1):
            ben.update(z);cert.update(harm);alarm.update(harm)
            if alarm.value >= 1/settings["alpha_alarm"]:
                decision,stop="REJECT_HARM",n;break
            if min(ben.value,cert.value) >= len(settings["cells"])/settings["alpha"]:
                decision,stop="ADMIT",n;break
        require((decision,stop) == (raw["decision"],raw["draws"]), "Stopping mismatch")
        require(counts([r["z"] for r in rows[:stop]]) == raw["counts"], "Stopped counts mismatch")
        for field,value in (("e_benefit",ben.value),("e_cert",cert.value),("e_alarm",alarm.value),("e_min",min(ben.value,cert.value))):
            require(math.isfinite(raw[field]) and math.isclose(raw[field],value,rel_tol=1e-10,abs_tol=1e-12), "E-value mismatch: "+field)
        reach={str(s["line"]):sum(s["line"] in r["without"]["reached_lines"] for r in rows) for s in result["bindings"]}
        cells.append({"cell":cfg["target_id"]+"/"+scope,"raw_decision":decision,"draws_to_stop":stop,
                      "full_counts":raw["b8"]["counts"],"e_for_family":min(ben.value,cert.value),"baseline_line_reach":reach})
    require(Counter(c["cell"] for c in cells) == Counter(settings["cells"]), "Family mismatch")
    admitted=e_holm({c["cell"]:c["e_for_family"] for c in cells},settings["alpha"])
    for c in cells:
        c["final_decision"]="ADMIT_DIAGNOSTIC" if c["cell"] in admitted else "QUARANTINE"
    stability=[json.loads(x) for x in (directory/"statelessness.jsonl").read_text().splitlines()]
    require(Counter((r["scope"],r["n"]) for r in stability) == Counter((s,n) for s in observed for n in range(1,101)), "Missing/duplicate state check")
    clean=lambda x:{k:v for k,v in x.items() if k != "module"}
    for row in stability:
        original=observed[row["scope"]][row["n"]-1]
        require(not row["mismatch"] and clean(row["without"]) == clean(original["without"])
                and clean(row["with"]) == clean(original["with"]), "State/order mismatch")
    require(result["statelessness"] == {s:{"compared":100,"mismatches":0} for s in observed}, "State summary mismatch")
    receipt={"status":"VERIFIED_EXPLORATORY","not_preregistered":True,"model_calls":0,"B9":"HOLD",
             "runs":len(expected_runs),"upstream_test_executions":len(expected_runs)*cfg["n_tests"],
             "baseline_passing_tests_preserved":15,"resolved_upstream_tests":resolved,"new_regressions":0,
             "paired_draws":sum(map(len,observed.values())),"state_rechecks":len(stability),"cells":cells,
             "limitations":["Historical convenience selection; not prospective or population-representative.",
                            "Upstream testNyquist is a smoke oracle, not numerical accuracy.",
                            "Draw oracle is researcher-authored; only supplied SISO scopes are covered.",
                            "Selected 16-test module; not full repository census; gangof4_plot not covered.",
                            "Diagnostics execute the full draw budget; not a cost-saving experiment."]}
    if output:write_json(Path(output),receipt)
    if markdown:
        lines=["# Python-control: kết quả hồi cứu được kiểm tra từ log thô", "",
               "**VERIFIED_EXPLORATORY**; 0 lời gọi model; B9 HOLD.", "",
               "| Nhánh | Pass | Fail chức năng | Lặp tiến trình mới |", "|---|---:|---:|---:|",
               "| Baseline | 15 | 1 | 3 |", "| Skill đóng băng | 16 | 0 | 3 |", "| Gold upstream | 16 | 0 | 3 |", "",
               "Giữ nguyên toàn bộ 16 test của module upstream. Một test Nyquist F→P, 15 test đang pass được giữ; không có regression mới.", "",
               "| Scope | Quyết định chẩn đoán | Draws đến dừng | Help / tie / hurt trong 300 draws |", "|---|---|---:|---|"]
        for c in cells:
            n=c["full_counts"]
            lines.append("| %s | %s | %s | %s / %s / %s |"%(c["cell"],c["final_decision"],c["draws_to_stop"],n["help"],n["tie"],n["hurt"]))
        lines += ["", "Kiểm tra lại 100 draws/scope bằng thứ tự khác và worker mới mỗi 25 draws: không thấy sai khác.", "",
                  "Giới hạn: hồi cứu, một repo/phiên bản, selected-module census; test upstream là smoke test. Oracle số học riêng do nhóm nghiên cứu viết. Hai trong ba vị trí sửa được các draw scopes đi qua; gangof4_plot chưa được bao phủ. Không tuyên bố an toàn cho toàn repo, prospective success hay tiết kiệm chi phí từ lượt replay đầy đủ này.", "",
                  "Raw: RESULT.json, PRE_EXECUTION.json, 9 XML + log, skill.patch, draws.jsonl và statelessness.jsonl."]
        Path(markdown).write_text("\n".join(lines)+"\n")
    print(json.dumps(receipt,indent=2),flush=True)
    return receipt


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results",type=Path,required=True)
    p.add_argument("--output",type=Path)
    p.add_argument("--markdown",type=Path)
    a=p.parse_args();audit(a.results,a.output,a.markdown)
