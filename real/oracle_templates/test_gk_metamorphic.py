"""Gatekeeper-Lite metamorphic boundary oracle (format-independent; frozen).

Property (substitution): an option whose default is an object D must render the same
help text as the same command whose default is its string twin str(D).  It needs no
knowledge of the output format, so it applies unchanged to click, asyncclick and
rich_click (selected with env GK_CLI_FLAVOR).  Behaviour classes are declared up front:
strict-eq objects, array-like objects, lazy text, lazy empty text.  The lazy-empty class
encodes the declared expectation: a value equal to the empty string renders like it (decision D3).
"""
import asyncio
import inspect
import os

import pytest

FLAVOR = os.environ.get("GK_CLI_FLAVOR", "click")
if FLAVOR == "rich_click":
    import rich_click as cli
    from click.testing import CliRunner
elif FLAVOR == "asyncclick":
    import asyncclick as cli
    from asyncclick.testing import CliRunner
else:
    import click as cli
    from click.testing import CliRunner


class _StrictEq:
    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        if isinstance(other, str):
            raise ValueError("cannot compare to string")
        return NotImplemented

    __hash__ = object.__hash__

    def __str__(self):
        return self.label


class _Ambiguous:
    def __bool__(self):
        raise ValueError("truth value is ambiguous")


class _ArrayLike:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return _Ambiguous()

    __hash__ = object.__hash__

    def __str__(self):
        return f"array{self.n}"


class _LazyText:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def __eq__(self, other):
        return str(self) == other

    __hash__ = object.__hash__


CASES = (
    [(f"strict-{i}", _StrictEq(f"strict{i}")) for i in range(8)]
    + [(f"array-{i}", _ArrayLike(i)) for i in range(4)]
    + [(f"lazy-text-{w}", _LazyText(w)) for w in ("Hello", "Bonjour")]
    + [(f"lazy-empty-{i}", _LazyText("")) for i in range(6)]
)


def _help(default):
    @cli.command()
    @cli.option("--limit", default=default, show_default=True, help="Limit.")
    def tool(limit):  # pragma: no cover - never executed, only --help
        pass

    env = {"COLUMNS": "200", "TERM": "dumb", "NO_COLOR": "1"}
    result = CliRunner().invoke(tool, ["--help"], env=env, catch_exceptions=True)
    if inspect.isawaitable(result):
        result = asyncio.run(result)
    if result.exception is not None and not isinstance(result.exception, SystemExit):
        raise AssertionError(f"help rendering raised {type(result.exception).__name__}")
    return result.output


@pytest.mark.parametrize("default", [c[1] for c in CASES], ids=[c[0] for c in CASES])
def test_gk_metamorphic_default(default):
    assert _help(default) == _help(str(default))
