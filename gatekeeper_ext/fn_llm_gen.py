"""Study P, feasibility step 2: prompt a light model to WRITE an input generator for one edited function.
The design (what the model sees, two calls at most) is fixed in research_closure/results/STUDY_P_PLAN.md.  Stdlib only."""
import ast
import re
from pathlib import Path

from gatekeeper_ext.mutants import functions

SYSTEM = ("You write Python input generators for differential testing. Reply with ONE Python code block that defines "
          "make_inputs(rng, n). No explanation.")

TEMPLATE = """We will call the function `{qualname}` defined in `{file}` many times, once in the ORIGINAL version of the
repository and once in the version that contains the upstream fix, and compare the results.

Write a Python function:

    def make_inputs(rng, n):
        ...
        return items   # a list of n tuples (receiver, args, kwargs)

Rules:
- `rng` is a random.Random; use ONLY `rng` for randomness, so that the same seed gives the same inputs.
- For a module-level function, static method or class method, receiver is None. For an instance method, receiver is an
  instance of the class that you construct inside make_inputs.
- These names are available: `module` (the imported module of {file}), `target_class` (the class, or None),
  `target_name` ("{name}"), and `random`. You may import other names from `module` or from the standard library.
- Do not use the network, do not write files outside the current directory, keep each value small, return quickly.
- Make about half of the inputs ordinary uses of the function and about half inputs around the behaviour that the issue
  and the fix below are about, including edge cases.

Issue:
{issue}

Head of the module:
```python
{head}
```
{init_block}
Function in the ORIGINAL version:
```python
{source}
```

Change made by the upstream fix to this file:
```diff
{diff}
```
"""

RETRY = """Running your make_inputs in the original version failed with:

{error}

Write a corrected make_inputs(rng, n) following the same rules. Reply with one Python code block only."""


def function_context(orig_root, rel, qualname, head_lines=40):
    text = (Path(orig_root) / rel).read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text)
    node = functions(tree)[qualname][0]
    source = ast.get_source_segment(text, node) or ""
    init = ""
    if "." in qualname:
        cls = qualname.rsplit(".", 1)[0]
        f = functions(tree).get(cls + ".__init__")
        if f:
            init = ast.get_source_segment(text, f[0]) or ""
    head = "\n".join(text.splitlines()[:head_lines])
    return {"source": source[:6000], "init": init[:3000], "head": head[:4000]}


def build_messages(rel, qualname, ctx, issue_text, diff):
    init_block = ("\nConstructor of the class (original version):\n```python\n%s\n```\n" % ctx["init"]) if ctx["init"] else ""
    user = TEMPLATE.format(qualname=qualname, file=rel, name=qualname.rsplit(".", 1)[-1], issue=(issue_text or "(no issue text)")[:3000],
                           head=ctx["head"], init_block=init_block, source=ctx["source"], diff=(diff or "")[:4000])
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def extract_code(reply):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", reply or "", re.S)
    code = next((b for b in reversed(blocks) if "def make_inputs" in b), None)
    if code is None and "def make_inputs" in (reply or ""):
        code = reply
    return code
