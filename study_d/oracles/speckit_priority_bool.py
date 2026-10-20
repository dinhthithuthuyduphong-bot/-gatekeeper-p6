"""Study D oracle for spec-kit `extension set-priority` (frozen before evaluation).

Provenance: upstream PR #3268 test TestExtensionPriorityCLI::test_set_priority_repairs_corrupted_bool
and its fixtures (temp_dir, valid_manifest_data, extension_dir, project_dir), reproduced
here.  Spec: a stored boolean priority is corrupted and must be repaired: the command exits
0, does NOT report 'already has priority', reports 'priority changed', and the reloaded
priority equals the requested int and is not a bool.  Integer priorities: unchanged
behaviour (differential).
"""
import re
import shutil
import tempfile
from pathlib import Path

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
MANIFEST = {
    "schema_version": "1.0",
    "extension": {"id": "test-ext", "name": "Test Extension", "version": "1.0.0",
                  "description": "A test extension", "author": "Test Author",
                  "repository": "https://github.com/test/test-ext", "license": "MIT"},
    "requires": {"speckit_version": ">=0.1.0", "commands": ["speckit.tasks"]},
    "provides": {"commands": [{"name": "speckit.test-ext.hello", "file": "commands/hello.md",
                               "description": "Test command"}]},
    "hooks": {"after_tasks": {"command": "speckit.test-ext.hello", "optional": True,
                              "prompt": "Run test?"}},
    "tags": ["testing", "example"],
}


def scopes():
    def bool_gen(rng):
        stored = rng.random() < 0.5
        return {"stored": stored, "requested": 1 if stored else rng.randint(1, 20)}

    def int_gen(rng):
        stored = rng.randint(1, 30)
        return {"stored": stored, "requested": stored if rng.random() < 0.5 else rng.randint(1, 30)}
    return {"bool": bool_gen, "int": int_gen}


def execute(d):
    import yaml
    from unittest.mock import patch
    from typer.testing import CliRunner
    from specify_cli import app
    from specify_cli.extensions import ExtensionManager
    tmp = Path(tempfile.mkdtemp())
    try:
        ext = tmp / "test-ext"
        (ext / "commands").mkdir(parents=True)
        (ext / "extension.yml").write_text(yaml.dump(MANIFEST))
        (ext / "commands" / "hello.md").write_text('---\ndescription: "Test hello command"\n---\n\n# Test Hello Command\n\n$ARGUMENTS\n')
        proj = tmp / "project"
        (proj / ".specify").mkdir(parents=True)
        manager = ExtensionManager(proj)
        manager.install_from_directory(ext, "0.1.0", register_commands=False, priority=5)
        manager.registry.update("test-ext", {"priority": d["stored"]})
        with patch.object(Path, "cwd", return_value=proj):
            result = CliRunner().invoke(app, ["extension", "set-priority", "test-ext", str(d["requested"])])
        plain = _ANSI.sub("", result.output)
        reloaded = ExtensionManager(proj).registry.get("test-ext")["priority"]
        return {"ok": True, "exit": result.exit_code, "already": "already has priority" in plain,
                "changed": "priority changed" in plain, "stored_after": repr(reloaded),
                "is_bool": isinstance(reloaded, bool)}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def judge(scope, d, without, with_):
    if scope == "bool":
        def ok(o):
            return (o["ok"] and o["exit"] == 0 and not o["already"] and o["changed"]
                    and o["stored_after"] == repr(d["requested"]) and not o["is_bool"])
        return ok(without), ok(with_)
    return True, with_ == without
