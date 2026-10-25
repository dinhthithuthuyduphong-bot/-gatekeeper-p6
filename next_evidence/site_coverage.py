"""Small physical-line trace reports using the public CoverageData API.

An AST continuation line must be compared with raw trace lines, not with the
statement-normalized executed_lines from coverage's JSON analysis report.
Reach alone is neither bool-input coverage nor an oracle certificate.
"""
import hashlib
from pathlib import Path

FORMAT = "RAW_TRACE_SITES_V1"


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def site_rows(data, source, sites):
    source = Path(source).resolve()
    measured = {}
    for name in data.measured_files():
        measured.setdefault(Path(name).resolve(), []).append(name)
    rows, cache, seen = [], {}, set()
    for site in sites:
        key = (site["file"], site["line"])
        if key in seen or type(site["line"]) is not int or site["line"] <= 0:
            raise ValueError("Duplicate or invalid candidate site")
        seen.add(key)
        target = (source / site["file"]).resolve()
        if not target.is_relative_to(source):
            raise ValueError("Candidate file escapes the pinned checkout")
        names = measured.get(target, [])
        if len(names) != 1:
            raise ValueError("Raw coverage file missing or ambiguous: " + site["file"])
        if target not in cache:
            cache[target] = (set(data.lines(names[0]) or []), data.contexts_by_lineno(names[0]) or {})
        lines, by_line = cache[target]
        contexts = sorted(set(by_line.get(site["line"], [])))
        reached = site["line"] in lines
        if reached != bool(contexts):
            raise ValueError("Raw trace lines and contexts disagree: " + str(key))
        calls = sorted({c.rsplit("|", 1)[0] for c in contexts if c.endswith("|call")})
        rows.append(dict(site, executed=reached, executed_in_test_call=bool(calls),
                         test_call_contexts=calls, all_contexts=contexts))
    return rows


def site_report(data, source, sites, data_file, coverage_version):
    source = Path(source).resolve()
    rows = site_rows(data, source, sites)
    return {
        "format": FORMAT,
        "coverage_version": coverage_version,
        "coverage_data_sha256": sha256(data_file),
        "source_sha256": {name: sha256(source / name) for name in sorted({s["file"] for s in sites})},
        "sites": rows,
        "meaning": "Physical source lines present in raw coverage trace, with pytest-phase contexts.",
        "limitation": "Does not establish bool inputs, changed semantics, an independent oracle, benefit, or harm.",
    }
