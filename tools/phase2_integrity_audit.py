"""Read-only Phase-2 audit of the existing Study F scoring and release gate.

This is a blocker inventory, not a change to frozen preregistration.
No API/network/model invocation or target execution.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root: Path) -> dict:
    fpath=root/"study_f/FREEZE.json"
    cfg_path=root/"study_f/config_study_f.json"
    gate_path=root/"pre_b9/RELEASE_GATE.json"
    s_path=root/"tools/score_heldout.py"
    wf_path=root/".github/workflows/study-f-score.yml"
    frozen=json.loads(fpath.read_text(encoding="utf-8"))["files"]
    cfg=json.loads(cfg_path.read_text(encoding="utf-8"))
    release=json.loads(gate_path.read_text(encoding="utf-8"))
    scoring=s_path.read_text(encoding="utf-8")
    wf=wf_path.read_text(encoding="utf-8")
    issues=[]
    def note(code,severity,observed,needed):
        issues.append({"code":code,"severity":severity,"observation":observed,"required_next":needed})
    score_hash=sha256(s_path)
    if "tools/score_heldout.py" not in frozen:
        note("F-SCORER-UNPINNED","BLOCKER",
             f"score_heldout.py digest {score_hash} not in frozen manifest",
             "Prospective amendment pinning scorer source BEFORE future model outcomes")
    if "tools/score_heldout.py" in frozen and frozen["tools/score_heldout.py"]!=score_hash:
        note("F-SCORER-MISMATCH","BLOCKER","Scorer digest differs from registered manifest",
             "Do not rerun or overwrite; investigate amendment/provenance")
    if "def gate(" in scoring and '"ADMIT"' in scoring and "e_holm(" not in scoring:
        note("F-EHOLM-FAMILY-REVIEW","BLOCKER",
             "score_heldout.py has per-scope ADMIT check without e_holm call",
             "Prove conservative shortcut and implement frozen family aggregation with clear 48-vs-144 multiplicity accounting")
    if "python tools/score_heldout.py" in wf and "aggregate" not in wf.lower():
        note("F-AGGREGATOR-PATH","BLOCKER",
             "Study F workflow invokes per-target scoring but no separate aggregate/family step",
             "Add verified separate family-level aggregator in prospective amendment")
    if int(cfg.get("k_cells",0)) != len(cfg.get("b9_configs",{}))*len(cfg.get("cells",[]))*2:
        note("F-K-FAMILY-MISMATCH","BLOCKER","k_cells inconsistent with models×targets×two-scopes",
             "Correct before prospective evaluation with explicit amendment")
    if int(cfg.get("k_cells",0))==48:
        note("F-REPETITIONS-MULTIPLICITY","REVIEW",
             "k_cells=48 while each model/target may have 3 independent repetitions",
             "Clarify FWER target: one family per repetition vs 144-cell family vs another preregistered structure")
    protocol=(root/"study_f/STUDY_F_PROTOCOL.md").read_text(encoding="utf-8")
    if cfg.get("status")=="FROZEN" and "BẢN NHÁP, chưa đóng băng" in protocol:
        note("F-DOC-STATUS","DOCUMENTATION",
             "Frozen config but protocol heading still says draft",
             "Leave original frozen file intact; annotate in amendment")
    if release.get("status")!="HOLD":
        note("PAID-RELEASE-NOT-HOLD","BLOCKER",f"Paid release status {release.get('status')!r}",
             "Restore HOLD until statistical and provenance audit complete")
    note("PAID-DIRECT-INVOCATION","REVIEW",
         "B9 run tool may be called outside protected Actions workflow after date gate",
         "Do not regard workflow HOLD as a provider billing hard limit")
    return {"type":"PHASE2_READ_ONLY_AUDIT", "status":"REVIEW_REQUIRED" if any(i["severity"]=="BLOCKER" for i in issues) else "AUDITED_NO_KNOWN_BLOCKER",
            "base_study_f_status":cfg.get("status"),"release_status":release.get("status"),
            "study_f_manifest_entries":len(frozen),
            "score_heldout_sha256":score_hash,"findings":issues}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,default=Path("out_phase2"))
    a=p.parse_args()
    dest=a.out if a.out.is_absolute() else a.root/a.out
    dest.mkdir(parents=True,exist_ok=True)
    result=inspect(a.root)
    (dest/"INTEGRITY_FINDINGS.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    lines=["# Pre-B9 phase-2 integrity audit","",f"Overall: **{result['status']}**", "",
           f"Study F manifest entries: {result['study_f_manifest_entries']}",
           f"Paid B9 gate: **{result['release_status']}**", "",
           "| Code | Severity | Evidence | Required follow-up |",
           "|---|---|---|---|"]
    for f in result["findings"]:
        esc=lambda s: str(s).replace("|","/")
        lines.append("| "+" | ".join(map(esc,(f["code"],f["severity"],f["observation"],f["required_next"])))+" |")
    lines += ["","This is a static inspection, not proof of correct statistical inference.",
              "The original FROZEN study files and results have NOT been changed.",""]
    (dest/"INTEGRITY_FINDINGS.md").write_text("\n".join(lines),encoding="utf-8")
    print(f"Phase-2 audit: {result['status']}; findings={len(result['findings'])}; "
          f"blockers={sum(x['severity']=='BLOCKER' for x in result['findings'])}")


if __name__=="__main__":
    main()
