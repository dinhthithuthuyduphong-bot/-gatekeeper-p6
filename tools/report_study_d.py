"""Final Study D report (Markdown) generated from the raw result files only.

python tools/report_study_d.py study_d/config_study_d.json RESULTS_DIR OUT.md [--b9 B9_DIR]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def row(cells):
    return "| " + " | ".join(str(c) for c in cells) + " |"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("results")
    ap.add_argument("out")
    ap.add_argument("--b9", default=None)
    a = ap.parse_args(argv)
    cfg_path = Path(a.config)
    cfg = json.loads(cfg_path.read_text())
    res_dir = Path(a.results)
    results = {f.stem.replace("RESULT_", ""): json.loads(f.read_text()) for f in res_dir.glob("RESULT_*.json")
               if not f.stem.startswith("RESULT_B9")}
    k, alpha = len(cfg["cells"]), cfg["alpha"]
    L = [f"# Study D — kết quả ({cfg['experiment_id']})", "",
         f"Trạng thái protocol: {cfg.get('status')} · đóng băng: {cfg.get('frozen_on', '—')} · "
         f"θ={cfg['theta']}, η={cfg['eta']}, α={alpha} (e-Holm, FWER), n_max={cfg['n_max']}, K={k}", ""]
    L += ["## 1. Bộ dữ liệu", "", row(["Target", "Vai trò", "Commit", "Skill áp dụng ở", "Skill từ chối ở"]),
          row(["---"] * 5)]
    for tid, r in sorted(results.items()):
        man = json.loads((cfg_path.parent / "eval_targets" / tid / "gk_target.json").read_text())
        b = r.get("bind", {})
        L.append(row([tid, man.get("role", ""), (r.get("commit") or "")[:10],
                      ", ".join(b.get("treated_modules", [])) or "—",
                      ", ".join(f"{m}: {why}" for m, why in b.get("abstained", {}).items()) or "—"]))
    from gatekeeper_lite.studyd_decisions import decide
    cells = decide(cfg, results)
    L += ["", "## 2. Quyết định theo ô", "",
          row(["Ô", "Giúp/hòa/hại (đến lúc dừng)", "Census", "B2", "B6-R", "B8 (đủ ngân sách)",
               "Gatekeeper (e-Holm)", "e-BH (phụ)", "Số lần rút GK"]), row(["---"] * 9)]
    for c in cells:
        sc, r = c["scope_result"], c["result"]
        cs = ("INVALID" if c["census_invalid"] else
              f"{len(r.get('census', {}).get('new_failures', []))} regression mới" if c["binds"] else "—")
        cnt = sc["counts"] if sc else {}
        L.append(row([c["cell"], f"{cnt.get('help', 0)}/{cnt.get('tie', 0)}/{cnt.get('hurt', 0)}" if sc else "—",
                      cs, c["B2"], c["B6R"], c["B8"], c["Gatekeeper"], c["eBH"], sc["draws"] if sc else 0]))
    L += ["", "## 3. Chi phí đo được (wall-clock thật trên runner)", "",
          row(["Target", "GK: lần rút", "B8: lần rút", "Census (giây)", "Khởi động worker (giây)",
               "GK tổng (giây)", "B8 tổng (giây)"]), row(["---"] * 7)]
    tot_gk = tot_b8 = 0.0
    for tid, r in sorted(results.items()):
        scs = r.get("scopes", {})
        if not scs:
            continue
        fixed = sum(r.get("census", {}).get("seconds", {}).values()) + sum(r.get("startup_seconds", {}).values())
        gk_s = fixed + sum(s.get("gatekeeper_seconds", 0.0) for s in scs.values())
        b8_s = fixed + sum(s.get("seconds", 0.0) for s in scs.values())
        tot_gk, tot_b8 = tot_gk + gk_s, tot_b8 + b8_s
        L.append(row([tid, sum(s["draws"] for s in scs.values()), sum(s["b8"]["draws"] for s in scs.values()),
                      round(sum(r.get("census", {}).get("seconds", {}).values()), 2),
                      round(sum(r.get("startup_seconds", {}).values()), 3), round(gk_s, 2), round(b8_s, 2)]))
    if tot_b8:
        L += ["", f"Tổng wall-clock: Gatekeeper {tot_gk:.2f} s, B8 {tot_b8:.2f} s "
                  f"(Gatekeeper / B8 = {tot_gk / tot_b8:.2f}). Chi phí cố định (census, khởi động) tính cho cả hai; "
                  "chỉ phần rút mẫu khác nhau."]
    if a.b9:
        L += ["", "## 4. B9 (sửa lỗi bằng LLM, khớp ngân sách)", "",
              row(["Target", "Model", "Lần lặp", "Kết luận cuối", "Patch", "Census", "Hại ở oracle kín",
                   "Lợi ở oracle kín", "Lần gọi", "USD"]), row(["---"] * 10)]
        for f in sorted(Path(a.b9).glob("RESULT_B9_*.json")):
            b = json.loads(f.read_text())
            for run in b["runs"]:
                h = run.get("hidden_oracle", {})
                cen = run.get("census", {})
                L.append(row([b["target"], b["model"], run["repetition"], run.get("verdict", "—"), run["status"],
                              ("INVALID" if cen.get("status") == "INVALID" else
                               f"{len(cen.get('new_failures', []))} regression mới") if cen else "—",
                              sum(v["hurt"] for v in h.values()) if h else "—",
                              sum(v["help"] for v in h.values()) if h else "—", run["calls"], run["cost_usd"]]))
    abl = subprocess.run([sys.executable, str(ROOT / "tools" / "ablation_study_d.py"), str(cfg_path), str(res_dir)],
                         capture_output=True, text=True)
    L += ["", "## 5. Ablation đăng ký trước (chạy lại trên dữ liệu đã ghi)", "", abl.stdout.strip(), "",
          "## 6. Giới hạn", "", "- Kết luận chỉ áp dụng cho các bộ sinh đã khai báo trên target ở commit đã ghim.",
          "- Đối chứng ngữ nghĩa (voluptuous) dùng hợp đồng của chính target; kết luận 'có hại' phụ thuộc hợp đồng đó.",
          "- Composition và retirement chỉ được minh hoạ trên dữ liệu phát triển."]
    Path(a.out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"written {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
