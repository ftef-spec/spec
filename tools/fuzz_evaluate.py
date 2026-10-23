# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Fuzz the reference evaluator with valid partner records and policies (Atheris).

Each input takes one of the valid example records and one of the valid example policies, and mutates either of them a
few times. A pair that fails its schema or the invariants of check.py is skipped, so any exception, or a result outside
the bands, is a bug in evaluate.py for a valid record under a valid policy. An exception inside check.py is a bug in
check.py: it must report on a schema-valid document, not crash on it.

    python tools/fuzz_evaluate.py -max_total_time=60      # needs tools/fuzz-requirements.txt

With FUZZ_COLLECT=<file>, distinct failures (exception type, file and line) are appended to the file and the run goes
on, to list every finding in one run instead of stopping at the first.
"""
from __future__ import annotations

import copy
import json
import os
import sys
import traceback
from pathlib import Path

import atheris

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

with atheris.instrument_imports():
    import evaluate as ev
from check import invariants_policy, invariants_record  # noqa: E402
from jsonschema import Draft202012Validator, FormatChecker  # noqa: E402

VALID = ROOT / "examples" / "valid"
SCHEMA = json.loads((ROOT / "schemas" / "0.1" / "partner-record.schema.json").read_text(encoding="utf-8"))
POLICY_SCHEMA = json.loads((ROOT / "schemas" / "0.1" / "policy.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
POLICY_VALIDATOR = Draft202012Validator(POLICY_SCHEMA, format_checker=FormatChecker())
SEEDS = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(VALID.glob("partner-*.json"))]
POLICIES = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(VALID.glob("policy*.json"))]


def _enums(o, out: set) -> set:
    if isinstance(o, dict):
        for v in o.get("enum", []):
            if isinstance(v, str):
                out.add(v)
        for v in o.values():
            _enums(v, out)
    elif isinstance(o, list):
        for v in o:
            _enums(v, out)
    return out


# Values the schema accepts that a parser or a comparison may not expect.
STRINGS = sorted(_enums(SCHEMA, set()) | _enums(POLICY_SCHEMA, set())) + [
    "2026-10-14T06:00:00Z", "2026-10-14T06:00:00z", "2026-10-14t06:00:00Z", "2026-10-14T05:59:60Z",
    "2026-10-14T06:00:00.123456789Z", "2026-10-14T06:00:00+14:00", "2026-10-14T06:00:00-12:00",
    "2025-03-01T00:00:00Z", "2027-01-13T00:00:00Z", "0001-01-01T00:00:00Z", "9999-12-31T23:59:59Z",
    "2026-10-14T06:00:00.5Z", "", "https://partner.vdhexample.example",
]


def _paths(o, here=()):
    yield here
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _paths(v, here + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _paths(v, here + (i,))


def _get(o, path):
    for p in path:
        o = o[p]
    return o


def _mutate(rec: dict, fdp: atheris.FuzzedDataProvider) -> None:
    paths = [p for p in _paths(rec) if p]
    path = paths[fdp.ConsumeIntInRange(0, len(paths) - 1)]
    parent, key = _get(rec, path[:-1]), path[-1]
    op = fdp.ConsumeIntInRange(0, 5)
    if op == 0:                                         # drop a key or a list item
        del parent[key]
    elif op == 1:                                       # a known enum value or a tricky time
        parent[key] = STRINGS[fdp.ConsumeIntInRange(0, len(STRINGS) - 1)]
    elif op == 2:                                       # free text
        parent[key] = fdp.ConsumeUnicodeNoSurrogates(24)
    elif op == 3:                                       # a number
        parent[key] = fdp.ConsumeIntInRange(-10, 10_000) if fdp.ConsumeBool() else fdp.ConsumeRegularFloat()
    elif op == 4 and isinstance(parent, list):          # duplicate a list item
        parent.insert(key, copy.deepcopy(parent[key]))
    elif op == 5:                                       # copy another field's value here
        other = paths[fdp.ConsumeIntInRange(0, len(paths) - 1)]
        parent[key] = copy.deepcopy(_get(rec, other))


COLLECT = os.environ.get("FUZZ_COLLECT")
SEEN: set = set()


def test_one_input(data: bytes) -> None:
    if not COLLECT:
        return _one(data)
    try:
        _one(data)
    except Exception as e:                              # noqa: BLE001 - collect mode lists every failure
        frame = [f for f in traceback.extract_tb(e.__traceback__) if Path(f.filename).name in ("evaluate.py", "check.py")]
        key = (type(e).__name__, Path(frame[-1].filename).name if frame else "?", frame[-1].lineno if frame else 0)
        if key not in SEEN:
            SEEN.add(key)
            with open(COLLECT, "a", encoding="utf-8") as f:
                f.write(f"{key[0]} at {key[1]}:{key[2]}: {str(e)[:160]}\n")


def _one(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    rec = copy.deepcopy(SEEDS[fdp.ConsumeIntInRange(0, len(SEEDS) - 1)])
    policy = copy.deepcopy(POLICIES[fdp.ConsumeIntInRange(0, len(POLICIES) - 1)])
    for _ in range(fdp.ConsumeIntInRange(1, 6)):
        try:
            _mutate(policy if fdp.ConsumeBool() else rec, fdp)
        except (KeyError, IndexError, TypeError):
            return
    if any(True for _ in POLICY_VALIDATOR.iter_errors(policy)):
        return
    if invariants_policy(policy) or any(True for _ in VALIDATOR.iter_errors(rec)) or invariants_record(rec, policy):
        return
    levels = [x["level"] for x in policy["situationLevels"]]
    at = STRINGS[fdp.ConsumeIntInRange(0, len(STRINGS) - 1)]
    if VALIDATOR.evolve(schema={"type": "string", "format": "date-time"}).is_valid(at) is False:
        at = "2026-10-14T12:00:00Z"
    out = ev.evaluate(rec, policy, at, levels[fdp.ConsumeIntInRange(0, len(levels) - 1)], fdp.ConsumeBool())
    if out["band"] not in ev.BANDS or out["evidencedBand"] not in ev.BANDS:
        raise AssertionError(f"band outside {ev.BANDS}: {out}")
    if ev.BANDS.index(out["band"]) < ev.BANDS.index(out["evidencedBand"]):
        raise AssertionError(f"band below the evidenced band: {out}")


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
