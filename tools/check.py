# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Validate the FTEF 0.1 examples.

- Every valid example passes its schema and the invariants of sections 5 to 8. A recorded evaluation must equal the
  one tools/evaluate.py computes.
- Every invalid example fails, and for the reason it states: its `_expect` text must appear among the errors.
- Keys starting with "_" are annotations and are removed before validation.

Usage: python tools/check.py   (exit 1 on any failure)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import LADDER, evaluate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BANDS = ["none", "low", "medium", "high"]

# 5.3: the highest ceiling each class may have; a policy may set a lower one, never a higher one
CLASS_MAX = {"self-declared": "low", "self-measured": "medium", "observed": "low",
             "assessed-by-relying-party": "medium", "independently-assessed": "medium", "attested": "high"}
# 5.3: the axes each named class requires
CLASS_AXES = {
    "self-declared": {"source": {"first-party"}},
    "self-measured": {"source": {"first-party"}, "timeBasis": {"continuous"}, "binding": {"signed", "signed-transparent", "hardware-rooted"}},
    "observed": {"source": {"second-party"}},
    "assessed-by-relying-party": {"source": {"second-party"}},
    "independently-assessed": {"source": {"third-party"}, "assessor": {"accredited", "mutually-recognised"}},
    "attested": {"source": {"verifier"}, "binding": {"hardware-rooted"}, "timeBasis": {"continuous", "at-access"}},
}


def _strip(o):
    if isinstance(o, dict):
        return {k: _strip(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [_strip(v) for v in o]
    return o


def _t(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _host(uri: str) -> str:
    return (urlparse(uri).hostname or "").lower()


def _same_org(a: str, b: str) -> bool:
    """Heuristic for the examples: same registrable name (last two labels) means the same organisation."""
    return a.split(".")[-2:] == b.split(".")[-2:] if a and b else False


def _keys(o) -> set[str]:
    if isinstance(o, dict):
        return set(o) | {k for v in o.values() for k in _keys(v)}
    if isinstance(o, list):
        return {k for v in o for k in _keys(v)}
    return set()


def check_evidence_item(e: dict, partner_host: str, where: str) -> list[str]:
    errs = []
    for axis, allowed in CLASS_AXES.get(e["class"], {}).items():
        if e["axes"].get(axis) not in allowed:
            errs.append(f"{where}: class {e['class']} requires {axis} in {sorted(allowed)} (5.3)")
    issuer = e["issuer"]["id"] if isinstance(e.get("issuer"), dict) else e.get("issuer", "")
    if e["axes"].get("source") in ("verifier", "third-party") and _same_org(_host(issuer), partner_host):
        errs.append(f"{where}: a {e['axes']['source']} controlled by the partner is first-party (5.3)")
    if e["axes"].get("timeBasis") == "period" and "coversFrom" in e and "coversUntil" in e:
        if not (_t(e["coversFrom"]) <= _t(e["coversUntil"]) <= _t(e["issuedAt"])):
            errs.append(f"{where}: a period must satisfy coversFrom <= coversUntil <= issuedAt (6.2)")
    return errs


def check_decision(holder: dict, roles: list[str], purpose: str, applied_at: str, where: str) -> list[str]:
    """6.6: a decision is a signed object by a role the policy names, never by its requester, applied before notAfter.
    The checker cannot verify signatures of fictional examples; it checks their shape and the separation rules."""
    d = holder.get("decision")
    if not d:
        return [f"{where} carries no signed decision (6.6)"]
    errs = []
    if d["purpose"] != purpose:
        errs.append(f"{where}: decision purpose {d['purpose']} is not {purpose} (6.6)")
    if d["deciderRole"] not in roles:
        errs.append(f"{where}: {d['deciderRole']} is not a decider role the policy names for {purpose} (6.6)")
    if holder.get("requestedBy") and holder["requestedBy"] == d["deciderRef"]:
        errs.append(f"{where}: decided by the person who requested it (6.6)")
    if _t(applied_at) > _t(d["notAfter"]):
        errs.append(f"{where}: decision applied after its notAfter (6.6)")
    return errs


def invariants_record(r: dict, policy: dict) -> list[str]:
    errs = []
    hist = r["stateHistory"]
    if hist[-1]["state"] != r["state"]:
        errs.append("state differs from the last entry of stateHistory")
    if hist[0]["state"] != "joining" and not hist[0].get("decidedBy"):
        errs.append("admission to a state above joining names no decider (6.4)")
    if hist[0]["state"] != "joining":
        errs += check_decision(hist[0], policy["deciders"]["admission"], "admission", hist[0]["since"], "admission")
    for a, b in zip(hist, hist[1:]):
        if _t(b["since"]) < _t(a["since"]):
            errs.append("stateHistory is not in time order")
        if a["state"] == "exited":
            errs.append("exited is final (5.6)")
        if LADDER.index(b["state"]) < LADDER.index(a["state"]):          # a move up
            if not b.get("decidedBy"):
                errs.append(f"move up from {a['state']} to {b['state']} names no decider (6.4)")
            up_to = "member" if a["state"] == "joining" else policy["states"].get(a["state"], {}).get("upTo")
            if up_to != b["state"]:
                errs.append(f"{a['state']} moves up only to {up_to} (6.4)")
            if a["state"] == "joining":
                errs += check_decision(b, policy["deciders"]["admission"], "admission", b["since"], "admission")
            else:
                errs += check_decision(b, policy["states"].get(a["state"], {}).get("deciders", []), "move-up", b["since"],
                                       f"move up from {a['state']}")
    host = _host(r["partner"]["id"])
    for e in r["evidence"]:
        errs += check_evidence_item(e, host, f"evidence {e['id']}")
    a = r.get("acceptance")
    if a:
        secs = (_t(a["until"]) - _t(a["decidedAt"])).total_seconds()
        if secs <= 0 or secs > policy["acceptance"]["maxDays"] * 86400:
            errs.append(f"acceptance runs longer than {policy['acceptance']['maxDays']} days (6.3)")
        if not r["evidence"]:
            errs.append("an acceptance requires at least one evidence item (6.3)")
        errs += check_decision(a, policy["deciders"]["acceptance"], "acceptance", a["decidedAt"], "acceptance")
        if a["situationLevel"] not in [x["level"] for x in policy["situationLevels"]]:
            errs.append(f"acceptance situation level {a['situationLevel']} is not a level of the policy (6.3)")
        moved_down = any(LADDER.index(b["state"]) > LADDER.index(p["state"]) and _t(b["since"]) >= _t(a["decidedAt"])
                         for p, b in zip(hist, hist[1:]))
        if moved_down and not a.get("lapsedAt"):
            errs.append("the partner moved down after the acceptance was decided, so it lapsed and must record lapsedAt (6.3)")
    ev = r.get("evaluation")
    if ev:
        if ev["situationLevel"] not in [x["level"] for x in policy["situationLevels"]]:
            errs.append(f"evaluation situation level {ev['situationLevel']} is not a level of the policy")
        else:
            want = evaluate(r, policy, ev["at"], ev["situationLevel"])
            got = {k: ev.get(k, [] if k == "limits" else None) for k in ("band", "evidencedBand", "accepted", "limits")}
            if got != want:
                errs.append(f"evaluation does not follow from the rules (section 6): recorded {got}, computed {want}")
    return errs


def invariants_policy(p: dict) -> list[str]:
    errs = []
    scales = [s["freshnessScale"] for s in p["situationLevels"]]
    if scales != sorted(scales, reverse=True):
        errs.append("a higher situation level lengthens freshness (6.2)")
    for c, v in p["classes"].items():
        if c in CLASS_MAX and BANDS.index(v["ceiling"]) > BANDS.index(CLASS_MAX[c]):
            errs.append(f"class {c}: ceiling {v['ceiling']} above what its axes allow ({CLASS_MAX[c]}) (5.3)")
        elif c not in CLASS_MAX and not c.startswith("https://"):
            errs.append(f"class {c}: not an FTEF class and not an extension URI (5.3)")
        elif c not in CLASS_MAX and BANDS.index(v["ceiling"]) > BANDS.index("medium"):
            errs.append(f"extension class {c}: ceiling above medium needs the axes of attested (5.3)")
    for s, v in p["states"].items():
        if s != "member":
            if not v.get("upTo"):
                errs.append(f"state {s} names no state to move up to (5.6)")
            elif LADDER.index(v["upTo"]) >= LADDER.index(s):
                errs.append(f"state {s}: upTo {v['upTo']} is not higher (5.6)")
    if not p["states"]["restricted"].get("limits"):
        errs.append("restricted needs its own limits (5.6, 6.5)")
    for s, v in p["states"].items():
        if s != "member" and not v.get("deciders"):
            errs.append(f"state {s} names no decider role for its move up (6.6)")
    for k in ("admission", "acceptance"):
        if not p["deciders"].get(k):
            errs.append(f"no decider role for {k}: the move could never happen (6.6)")
    return errs


def check_trust_mark(tm: dict, schemas: dict) -> list[str]:
    rec = schemas["partner-record"]
    axes = json.loads(json.dumps(rec["$defs"]["axes"]))
    axes["required"] = [x for x in axes["required"] if x != "scope"]
    axes["properties"].pop("scope")                    # 5.2: scope is the relying party's, never shared
    summary = {"$schema": rec["$schema"], "$defs": rec["$defs"], "type": "object",
               "required": ["id", "issuer", "class", "axes", "covers", "issuedAt"],
               "properties": {"id": {"type": "string", "minLength": 1}, "issuer": {"type": "string", "format": "uri"},
                              "class": {"$ref": "#/$defs/evidenceClass"}, "axes": axes,
                              "covers": {"type": "string", "minLength": 1},
                              "issuedAt": {"type": "string", "format": "date-time"},
                              "coversFrom": {"type": "string", "format": "date-time"},
                              "coversUntil": {"type": "string", "format": "date-time"},
                              "reference": {"type": "string", "format": "uri"},
                              "digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
                              "receipt": {"type": "string", "format": "uri"}}}
    errs = [f"missing {m} (8.1)" for m in ("iss", "sub", "trust_mark_type", "iat", "exp", "status", "ftef_evidence") if m not in tm]
    if tm.get("iss") == tm.get("sub"):
        errs.append("a partner must not issue FTEF trust marks about itself (8.1)")
    if {"band", "evidencedBand", "trustBand"} & _keys(tm):
        errs.append("a trust mark must not carry a band (8.1)")
    sv = Draft202012Validator(summary, format_checker=FormatChecker())
    for i, e in enumerate(tm.get("ftef_evidence", [])):
        errs += [f"summary {i}: {x.message}" for x in sv.iter_errors(e)]
        if errs:
            continue
        b = e["axes"]["binding"]
        if b != "unsigned" and not ("reference" in e and "digest" in e):
            errs.append(f"summary {i}: binding {b} needs reference and digest (8.1)")
        if b == "signed-transparent" and "receipt" not in e:
            errs.append(f"summary {i}: signed-transparent needs receipt (8.1)")
        if e["axes"]["timeBasis"] == "period" and not ("coversFrom" in e and "coversUntil" in e):
            errs.append(f"summary {i}: period evidence needs coversFrom and coversUntil (8.1)")
        errs += check_evidence_item(e, _host(tm.get("sub", "")), f"summary {i}")
        if datetime.fromtimestamp(tm["iat"]).astimezone() < _t(e["issuedAt"]):
            errs.append(f"summary {i}: evidence issued after the trust mark")
    return errs


def main() -> int:
    schemas = {n: json.loads((ROOT / "schemas" / "0.1" / f"{n}.schema.json").read_text(encoding="utf-8"))
               for n in ("partner-record", "policy")}
    for s in schemas.values():
        Draft202012Validator.check_schema(s)
    policy = json.loads((ROOT / "examples" / "valid" / "policy-defaults.json").read_text(encoding="utf-8"))
    fail = 0
    for kind in ("valid", "invalid"):
        for f in sorted((ROOT / "examples" / kind).glob("*.json")):
            raw = json.loads(f.read_text(encoding="utf-8"))
            doc = _strip(raw)
            name = "policy" if f.name.startswith("policy") else "partner-record"
            v = Draft202012Validator(schemas[name], format_checker=FormatChecker())
            schema_errs = [e.message for e in v.iter_errors(doc)]
            sem = [] if schema_errs else (invariants_policy(doc) if name == "policy" else invariants_record(doc, policy))
            errs = schema_errs + sem
            if kind == "valid" and errs:
                fail += 1
                print(f"FAIL {f.name}: should be valid: {errs}")
            elif kind == "invalid":
                expect = raw.get("_expect", "")
                if not errs:
                    fail += 1
                    print(f"FAIL {f.name}: should be invalid ({raw.get('_invalid_because')})")
                elif not expect or not any(expect in e for e in errs):
                    fail += 1
                    print(f"FAIL {f.name}: fails, but not for its stated reason {expect!r}: {errs}")
                else:
                    print(f"ok   invalid {f.name}  ({expect})")
            else:
                print(f"ok   valid   {f.name}")
    for kind in ("valid", "invalid"):
        for f in sorted((ROOT / "examples" / "profile-8.1" / kind).glob("*.json")):
            raw = json.loads(f.read_text(encoding="utf-8"))
            errs = check_trust_mark(_strip(raw), schemas)
            expect = raw.get("_expect", "")
            ok = (not errs) if kind == "valid" else (bool(errs) and bool(expect) and any(expect in e for e in errs))
            print(f"{'ok  ' if ok else 'FAIL'} profile {kind} {f.name}" + ("" if ok else f": {errs}"))
            fail += 0 if ok else 1
    fail += evaluator_cases(policy)
    return 1 if fail else 0


def evaluator_cases(policy: dict) -> int:
    """Rules that no static example shows: status outage and acceptance lifetime (6.3, 8.1)."""
    att = json.loads((ROOT / "examples" / "valid" / "partner-attested.json").read_text(encoding="utf-8"))
    acc = json.loads((ROOT / "examples" / "valid" / "partner-accepted.json").read_text(encoding="utf-8"))
    at = "2026-10-14T12:00:00Z"
    cases = [
        ("status reachable: attested partner is high", evaluate(att, policy, at, "normal")["band"] == "high"),
        ("status unreachable: band capped at none, state unchanged",
         evaluate(att, policy, at, "normal", status_reachable=False)["band"] == "none" and att["state"] == "member"),
        ("status returns: band recovers without a decision", evaluate(att, policy, at, "normal")["band"] == "high"),
        ("acceptance pauses while status is unreachable",
         evaluate(acc, policy, at, "normal", status_reachable=False)["accepted"] is False),
        ("acceptance applies again when status returns", evaluate(acc, policy, at, "normal")["accepted"] is True),
        ("a higher situation level lapses the acceptance", evaluate(acc, policy, at, "elevated")["accepted"] is False),
        ("an acceptance never applies after its end", evaluate(acc, policy, "2027-01-13T00:00:00Z", "normal")["accepted"] is False),
        ("attested evidence two days old is long stale", evaluate(att, policy, "2026-10-16T12:00:00Z", "normal")["band"] == "medium"),
    ]
    bad = 0
    for name, ok in cases:
        print(f"{'ok  ' if ok else 'FAIL'} rule    {name}")
        bad += 0 if ok else 1
    return bad


if __name__ == "__main__":
    sys.exit(main())
