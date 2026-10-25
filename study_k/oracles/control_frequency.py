"""Exploratory SISO response oracle; separate from the unchanged upstream smoke test.

Inputs are freshly constructed each call. H(s) = gain / (s*s + a*s + b)
is evaluated independently with Python complex arithmetic in the coordinator.
The draw adapter is researcher-authored; it is not a tier-1 upstream test.
"""
import math
import sys


def scopes():
    def make(rng, supplied):
        return {"supplied": supplied, "function": rng.choice(["bode", "nyquist"]),
                "gain": rng.uniform(0.2, 3.0), "a": rng.uniform(0.5, 4.0),
                "b": rng.uniform(0.5, 4.0),
                "omega": sorted(10 ** rng.uniform(-1, 1) for _ in range(rng.randint(3, 12)))}
    return {"array_frequencies": lambda rng: make(rng, True),
            "default_frequencies": lambda rng: make(rng, False)}


def execute(d):
    import control
    from control import freqplot
    import numpy as np
    system = control.TransferFunction([d["gain"]], [1.0, d["a"], d["b"]])
    omega = np.asarray(d["omega"]) if d["supplied"] else None
    seen = set()
    def trace(frame, event, arg):
        if frame.f_code.co_filename == freqplot.__file__:
            if event == "line":
                seen.add(frame.f_lineno)
            return trace
        return None
    previous = sys.gettrace()
    sys.settrace(trace)
    try:
        if d["function"] == "bode":
            mag, phase, w = freqplot.bode_plot(system, omega, Plot=False, deg=False, dB=False, Hz=False)
            real = mag * np.cos(phase)
            imag = mag * np.sin(phase)
        else:
            real, imag, w = freqplot.nyquist_plot(system, omega, Plot=False)
        result = {"ok": True, "real": real.tolist(), "imag": imag.tolist(), "omega": w.tolist()}
    except Exception as exc:
        result = {"ok": False, "exception": type(exc).__name__, "message": str(exc)}
    finally:
        sys.settrace(previous)
    result.update(module=control.__file__, reached_lines=sorted(seen))
    return result


def valid(d, out):
    if not out.get("ok"):
        return False
    w, re, im = out.get("omega", []), out.get("real", []), out.get("imag", [])
    if not w or len(w) != len(re) or len(w) != len(im):
        return False
    if not all(isinstance(x, (float, int)) and math.isfinite(x) for x in w + re + im):
        return False
    if d["supplied"] and w != d["omega"]:
        return False
    for omega, real, imag in zip(w, re, im):
        s = 1j * omega
        expected = d["gain"] / (s*s + d["a"]*s + d["b"])
        if abs(complex(real, imag) - expected) > 1e-8 * max(1.0, abs(expected)):
            return False
    return True


def judge(scope, d, without, with_):
    return valid(d, without), valid(d, with_)
