"""pip-install the requirements declared by the targets of a config, then record pip freeze."""
import json
import subprocess
import sys
from pathlib import Path


def main(config: str, freeze_out: str) -> int:
    cfg_path = Path(config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    reqs = set()
    for manifest in (cfg_path.parent / cfg["targets_dir"]).glob("*/gk_target.json"):
        reqs.update(json.loads(manifest.read_text(encoding="utf-8")).get("requirements", []))
    if reqs:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", *sorted(reqs)], check=True)
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True,
                            text=True, check=True).stdout
    Path(freeze_out).write_text(freeze, encoding="utf-8")
    print(f"installed: {sorted(reqs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
