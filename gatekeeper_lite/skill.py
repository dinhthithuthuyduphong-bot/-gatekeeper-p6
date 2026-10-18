"""Skill package S = <pi, D, I, P, K> and target context x = (repo, revision, env, task)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from . import transforms


@dataclass
class Skill:
    skill_id: str
    version: str
    pi: dict                       # {"transform": name, "params": {...}}
    D: dict                        # declared environment contract
    I: List[str]                   # input-assumption predicates
    P: List[dict]                  # source evidence: before/after examples
    K: dict                        # declared behaviours (footprint hints)
    scope: str
    root: Path = field(default=Path("."), repr=False)

    @classmethod
    def load(cls, path: Path) -> "Skill":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(root=Path(path).parent, **{k: data[k] for k in
                   ("skill_id", "version", "pi", "D", "I", "P", "K", "scope")})

    def transform(self) -> transforms.Transform:
        return transforms.make(self.pi["transform"], self.pi.get("params"))

    @property
    def single_site(self) -> bool:
        return "single_site" in self.I

    def digest(self) -> str:
        payload = json.dumps({k: getattr(self, k) for k in
                              ("skill_id", "version", "pi", "D", "I", "P", "K", "scope")},
                             sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Target:
    target_id: str
    root: Path
    manifest: dict

    @classmethod
    def load(cls, root: Path) -> "Target":
        root = Path(root)
        manifest = json.loads((root / "gk_target.json").read_text(encoding="utf-8"))
        return cls(manifest.get("target_id", root.name), root, manifest)

    @property
    def module(self) -> str:
        return self.manifest["module"]

    @property
    def regime(self) -> str:
        return self.manifest.get("regime", "?")

    def source(self) -> str:
        return (self.root / self.module).read_text(encoding="utf-8")

    def environment(self) -> dict:
        return {k: self.manifest.get(k) for k in ("python", "platform", "packages")}

    def fingerprint(self) -> str:
        env = json.dumps(self.environment(), sort_keys=True)
        return hashlib.sha256(env.encode("utf-8")).hexdigest()[:16]

    def with_environment(self, **changes) -> "Target":
        manifest = dict(self.manifest)
        manifest.update(changes)
        return Target(self.target_id, self.root, manifest)
