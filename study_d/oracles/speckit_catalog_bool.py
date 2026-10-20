"""Study D applicability-control oracle for spec-kit preset catalog priority (frozen).

Provenance: upstream PR #2589 test TestPresetCatalogMultiCatalog::
test_load_catalog_config_rejects_boolean_priority and its project_dir fixture.  Spec: a
catalog config with `priority: true/false` must raise PresetValidationError ('Invalid
priority' / 'expected integer').  Integer priorities: unchanged behaviour (differential).
The bug sits behind int(...) without an isinstance check, so the frozen skill is not
expected to fix it.
"""
import shutil
import tempfile
from pathlib import Path


def scopes():
    return {"bool": lambda rng: {"priority": rng.random() < 0.5},
            "int": lambda rng: {"priority": rng.randint(1, 100)}}


def execute(d):
    import yaml
    from specify_cli.presets import PresetCatalog, PresetValidationError
    tmp = Path(tempfile.mkdtemp())
    try:
        proj = tmp / "project"
        tpl = proj / ".specify" / "templates"
        (tpl / "commands").mkdir(parents=True)
        (tpl / "spec-template.md").write_text("# Core Spec Template\n")
        (tpl / "plan-template.md").write_text("# Core Plan Template\n")
        cfg = proj / ".specify" / "preset-catalogs.yml"
        cfg.write_text(yaml.dump({"catalogs": [{"name": "c", "url": "https://example.com/catalog.json",
                                                "priority": d["priority"]}]}))
        try:
            entries = PresetCatalog(proj)._load_catalog_config(cfg)
            return {"ok": True, "rejected": False,
                    "priorities": [getattr(e, "priority", None) for e in (entries or [])]}
        except PresetValidationError:
            return {"ok": True, "rejected": True}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["rejected"] is True
        return ok(without), ok(with_)
    return True, with_ == without
