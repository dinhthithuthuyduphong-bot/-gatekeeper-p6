# Study R2: a diverse skill library on real repositories (written before running)

**Why.** Studies D–G use two skill families. A reviewer can fairly say that the library-level claims (composite cells,
execution rule, Corollary 5.6) were never exercised on a library of realistic size and variety. R2 builds a library of
**twelve** families of reusable code changes (the two frozen ones plus ten new ones), and measures on the same 16 real
repositories what the theory depends on: how many cells a library produces, how often footprints overlap, and how often two
changes interact *syntactically* when applied to the same file. Descriptive; no hypothesis test; no model calls; no target
code runs.

**Library.** The two frozen families of Study R (`negative_type_guard` bool-excluded-from-int, `none_identity`) and ten new
families in `gatekeeper_ext/skill_library.py`, one JSON manifest each in `study_r2/skills/`. Each new family is a
single-statement, linter-style fix (PySStuBs / pycodestyle / flake8-bugbear / bandit style) that is behaviour-preserving
for ordinary inputs and behaviour-changing for some, so admission is a real decision:

| family | rewrite | changes behaviour when |
|---|---|---|
| `type_eq_isinstance` | `type(x) == T` / `type(x) is T` → `isinstance(x, T)` | x is an instance of a subclass of T |
| `eq_bool_identity` | `x == True/False` → `x is True/False` (E712) | x is 1/0, numpy bool, overridden `__eq__` |
| `is_literal_eq` | `x is <str/int/bytes literal>` → `x == literal` (F632) | non-interned equal values, overridden `__eq__` |
| `mutable_default` | `def f(a=[] / {} / set())` → `a=None` + `if a is None: a = ...` (B006) | caller relies on shared state or passes `None` |
| `bare_except` | `except:` → `except Exception:` (E722) | `KeyboardInterrupt`, `SystemExit`, `GeneratorExit` |
| `open_encoding` | text-mode `open(p[, mode])` → add `encoding="utf-8"` | non-UTF-8 locale or non-UTF-8 file |
| `yaml_safe_load` | `yaml.load(s)` without `Loader` → `yaml.safe_load(s)` | documents with Python tags |
| `len_zero_falsy` | `len(x) == 0` / `len(x) != 0` → `not x` / `bool(x)` | `__bool__` disagrees with `__len__` (numpy, custom) |
| `dict_keys_membership` | `k in d.keys()` → `k in d` | mappings whose `__contains__` and `keys()` disagree |
| `reraise_bare` | `except E as e: … raise e` → `raise` | traceback/`__context__` inspected |

Every family fails closed (abstains) on sites it cannot rewrite safely; each manifest records its scope.

**Targets.** Every target of Studies D, E, G, cloned at the pinned revision (the 16 of Study R). Non-test `.py` files only
(same rule as Study R).

**Measures.**
1. *Cells.* For each target, the families that bind at least one function (each is one single-skill cell, scope = target).
2. *Footprint overlap.* Functions (file, enclosing function) touched by each family; for every pair of families on a target,
   whether they share a function. Reported: overlapping pairs, footprint-connected components of the target's library, and
   the number of composite cells the execution rule requires (components with two or more families).
3. *Syntactic interaction (Assumption 4, syntactic part).* For every file and every ordered pair (A, B) of families that both
   apply to the file: does A followed by B give the same source as B followed by A; does applying A change the set of B's sites
   (enables or disables B). Reported separately for pairs that share a function and pairs that do not.
4. *Library simulation on the real overlap graph.* `tools/library_simulation.py --graph` re-runs the Section 7.2 simulation
   with the measured per-target libraries and footprints in place of synthetic regions; benefit/harm of individual skills and
   of overlapping pairs stay synthetic (same parameters as Section 7.2), and are labelled as such.

**Report.** Per target and in total, by `tools/library_census.py` in the workflow `Gatekeeper Study R2 library census`, and the
simulation by `Gatekeeper library simulation` (graph mode). Unit tests for every family in `tests/test_skill_library.py` run
before the census.

**Deviation rule.** A target that cannot be cloned or parsed is reported, not replaced. A family that turns out to bind
nowhere is reported with zero, not dropped. Families are not changed after the census has run; a fix would be a new
amendment with its own commit.

**What R2 does not measure.** Whether any of these rewrites is *harmful* on a target (that needs per-target oracles and is
Studies D–H's job); the simulation's risks are synthetic.
