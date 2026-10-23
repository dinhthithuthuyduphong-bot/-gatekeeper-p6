"""Patch-level admission (closes the gap 'one scope admitted, another only quarantined').

The patch is deployed as a whole, so the hypothesis is stated for the PATCH:
    H0(patch) = A or B,  A: no scope has benefit beyond theta with low harm,
                         B: some scope has harm rate >= eta.
With fixed-time e-values (e_ben_s, e_cert_s) of every declared scope s (S scopes):
    under A every min(e_ben_s, e_cert_s) is an e-value, so their MEAN is an e-value;
    under B the offending scope's e_cert_s is an e-value, so MIN_s e_cert_s is one.
    e_patch = min(mean_s min(e_ben_s, e_cert_s), min_s e_cert_s) is an e-value for A or B.
Patches are then admitted by e-Holm over the family of patches.  A patch with a persistent
census regression or a fired harm alarm in any scope gets e_patch = 0."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess  # noqa: E402


def scope_evalues(trace, theta, eta, n_max, alpha_alarm=0.05):
    ben, cert, al = BettingEProcess(theta), HarmCertEProcess(eta), HarmAlarmEProcess(eta)
    alarm = False
    for z, reg in trace[:n_max]:
        ben.update(z); cert.update(bool(reg)); al.update(bool(reg))
        alarm = alarm or al.value >= 1 / alpha_alarm
    return ben.value, cert.value, alarm


def patch_evalue(scope_traces, theta, eta, n_max, census_bad=False):
    vals = [scope_evalues(t, theta, eta, n_max) for t in scope_traces.values()]
    if census_bad or any(a for _, _, a in vals) or not vals:
        return 0.0
    mean_part = sum(min(b, c) for b, c, _ in vals) / len(vals)
    return min(mean_part, min(c for _, c, _ in vals))
