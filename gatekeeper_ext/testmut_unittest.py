"""unittest collector with the same record schema as the parsed pytest junit file (used for offline tests).
python -m gatekeeper_ext.testmut_unittest OUT.json SELECT_SUBSTRING FILE.py [FILE.py ...]"""
import json
import sys
import time
import unittest


def main(argv):
    out, select, files = argv[1], argv[2], argv[3:]
    sys.path.insert(0, ".")
    loader, suite = unittest.TestLoader(), unittest.TestSuite()
    for f in files:
        suite.addTests(loader.loadTestsFromName(f[:-3].replace("/", ".")))
    tests = []

    def flatten(s):
        for t in s:
            flatten(t) if isinstance(t, unittest.TestSuite) else tests.append(t)
    flatten(suite)
    records = []
    for t in tests:
        name = getattr(t, "_testMethodName", str(t))
        if select and select not in name:
            continue
        res = unittest.TestResult()
        t0 = time.perf_counter()
        t.run(res)
        status, msg = "passed", ""
        if res.failures:
            status, msg = "failed", str(res.failures[0][1]).strip().splitlines()[-1][:300]
        elif res.errors:
            status, msg = "error", str(res.errors[0][1]).strip().splitlines()[-1][:300]
        elif res.skipped:
            status, msg = "skipped", str(res.skipped[0][1])[:200]
        records.append({"classname": "%s.%s" % (type(t).__module__, type(t).__name__), "name": name, "status": status,
                        "time": time.perf_counter() - t0, "msg": msg})
    with open(out, "w") as fh:
        json.dump(records, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
