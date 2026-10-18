"""Gatekeeper-Lite boundary oracle template (frozen; injected unchanged into every Click target).

Mirrors the construction of Click's own #3298 regression test, over declared behaviour
classes of `default` values.  Expectations are researcher-declared (development oracle,
written after studying the P7 cases; NOT an independent evaluation oracle):
  * objects whose __eq__ refuses str comparison must render via str(obj), no exception;
  * values that compare equal to "" render as [default: ""]   (adversarial class: lazy text).
"""
import click
import pytest


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
    """gettext_lazy-style proxy: not a str subclass, compares and renders as its text."""

    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def __eq__(self, other):
        return str(self) == other

    __hash__ = object.__hash__


CASES = (
    [(f"strict-{i}", _StrictEq(f"strict{i}"), f"[default: strict{i}]") for i in range(8)]
    + [(f"array-{i}", _ArrayLike(i), f"[default: array{i}]") for i in range(4)]
    + [("plain-abc", "abc", "[default: abc]"), ("plain-x", "x", "[default: x]")]
    + [("empty-string", "", '[default: ""]')]
    + [(f"lazy-text-{w}", _LazyText(w), f"[default: {w}]") for w in ("Hello", "Bonjour")]
    + [(f"lazy-empty-{i}", _LazyText(""), '[default: ""]') for i in range(6)]
)


@pytest.mark.parametrize(("default", "expected"), [c[1:] for c in CASES], ids=[c[0] for c in CASES])
def test_gk_boundary_default_rendering(default, expected):
    opt = click.Option(["--limit"], default=default, show_default=True)
    ctx = click.Context(click.Command("cli"))
    message = opt.get_help_record(ctx)[1]
    assert expected in message
