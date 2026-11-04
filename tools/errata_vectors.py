# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Evaluator cases for the 0.1 errata. Fictional data only. Each case is (name, passed)."""
from __future__ import annotations

import copy

import evaluate as E
from evaluate import _t, evaluate

AT = "2026-10-14T12:00:00Z"
ASSESSED = {"id": "ev-a", "class": "independently-assessed",
            "axes": {"source": "third-party", "assessor": "accredited", "timeBasis": "period", "binding": "signed", "scope": "full"},
            "issuer": {"id": "https://assessor.vdhauditco.example"}, "issuedAt": "2026-03-01T00:00:00Z",
            "coversFrom": "2025-03-01T00:00:00Z", "coversUntil": "2026-02-28T23:59:59Z"}
ADVERSE = {"id": "ev-x", "class": "observed", "result": "adverse",
           "axes": {"source": "second-party", "timeBasis": "point-in-time", "binding": "signed", "scope": "full"},
           "issuer": {"id": "https://probe.vdhrelyingparty.example"}, "issuedAt": "2026-10-04T12:00:00Z"}


def _with(record: dict, evidence: list, state: str = "member") -> dict:
    r = copy.deepcopy(record)
    r.pop("evaluation", None)
    r["evidence"] = copy.deepcopy(evidence)
    if state != r["state"]:
        r["stateHistory"].append({"state": state, "since": "2026-10-01T00:00:00Z", "trigger": "registry status watch"})
        r["state"] = state
    return r


def cases(policy: dict, att: dict, acc: dict) -> list:
    cov = att["evidence"][0]["covers"]
    good, bad = dict(ASSESSED, covers=cov), dict(ADVERSE, covers=cov)
    band = lambda r, lvl="normal", p=policy, **kw: evaluate(r, p, AT, lvl, **kw)["band"]
    out = []

    # adverse items: unscaled window, defects do not take them out of play
    unsigned_attested = dict(bad, issuedAt="2026-10-14T06:00:00Z", **{"class": "attested", "axes": {"source": "verifier", "timeBasis": "continuous",
                                                                   "binding": "unsigned", "scope": "full"}})
    out += [
        ("adverse in play cancels at every situation level and after a move down",
         [band(_with(att, [good, bad]), lvl) for lvl in ("normal", "elevated", "high", "severe")] == ["none"] * 4
         and band(_with(att, [good, bad], "watch")) == "none"),
        ("an adverse item failing its class axes still cancels", band(_with(att, [good, unsigned_attested])) == "none"),
        ("an unsigned adverse item cancels: less trust over availability", band(_with(att, [good, dict(bad, axes=dict(
            bad["axes"], binding="unsigned"))])) == "none"),
        ("an adverse item dated in the future cancels", band(_with(att, [good, dict(bad, issuedAt="2027-01-01T00:00:00Z")])) == "none"),
        ("an adverse item with impossible period dates cancels", band(_with(att, [good, dict(
            bad, axes=dict(bad["axes"], timeBasis="period"), coversFrom="2026-10-10T00:00:00Z",
            coversUntil="2026-10-20T00:00:00Z")])) == "none"),
        ("an adverse item is in play from the latest of its dates",
         E.in_play(dict(bad, issuedAt="2026-09-01T00:00:00Z", observedAt="2026-10-10T00:00:00Z"), policy, _t(AT))),
        ("an adverse item past twice its class freshness no longer cancels",
         band(_with(att, [good, dict(bad, issuedAt="2026-09-20T12:00:00Z")])) == "medium"),
        ("an adverse item of an unlisted class is left to the open adverse-source proposal",
         band(_with(att, [good, dict(bad, **{"class": "https://ext.vdhcert.example/advisory"})])) == "medium"),
    ]

    # coverage: overlap unless recorded disjoint; equal after normalisation can never be disjoint
    relay = dict(bad, covers="the partner's mail relay (fictional)")
    pair = {(cov, relay["covers"])}
    variants = [cov.upper() + " ", cov.replace("the", "the​", 1), cov.replace("p", "ｐ", 1)]
    out += [
        ("different coverage cancels unless the relying party recorded it disjoint",
         band(_with(att, [good, relay])) == "none" and band(_with(att, [good, relay]), disjoint=pair) == "medium"),
        ("case, invisible and compatibility variants are the same coverage",
         all(band(_with(att, [good, dict(bad, covers=v)]), disjoint={(cov, v)}) == "none" for v in variants)),
    ]

    # decisions: application time is the relying party's, strictly before notAfter; persons normalised; nonces
    nonce = acc["acceptance"]["decision"]["nonce"]
    ok_log, late_log = {nonce: "2026-10-14T09:30:00Z"}, {nonce: "2026-12-01T00:00:00Z"}
    edge_log = {nonce: acc["acceptance"]["decision"]["notAfter"]}
    acc_eval = lambda r, **kw: evaluate(r, policy, AT, "normal", **kw)["accepted"]
    alias = copy.deepcopy(acc)
    alias["acceptance"]["requestedBy"] = " RP:person:0007​"
    hist_back = copy.deepcopy(att)
    hist_back["stateHistory"].append({"state": "watch", "since": "2026-01-01T00:00:00Z", "trigger": "registry status watch"})
    hist_back["state"] = "watch"
    store = E.NonceStore(skew_seconds=300)
    first = store.admit("rp:person:0007", "n-cccccccccccccccc", "2026-10-14T10:00:00Z", "2026-10-14T09:00:00Z")
    again = store.admit("RP:person:0007 ", "n-cccccccccccccccc", "2026-10-14T10:00:00Z", "2026-10-14T09:10:00Z")
    after = store.admit("rp:person:0007", "n-cccccccccccccccc", "2026-10-14T11:00:00Z", "2026-10-14T10:06:00Z")
    out += [
        ("a decision applies only when the relying party applied it before notAfter",
         acc_eval(acc, applied=ok_log) and not acc_eval(acc, applied=late_log) and not acc_eval(acc, applied=edge_log)),
        ("a decision the relying party has no application record of does not apply", not acc_eval(acc, applied={})),
        ("a requester spelled differently is still the requester", not acc_eval(alias)),
        ("a nonce is refused again for the same decider until notAfter plus skew", first and not again and after),
        ("history dated backwards is refused at evaluation", band(hist_back) == "none"),
    ]
    res = {"deciderRole": "security-officer", "deciderRef": "rp:person:0001", "purpose": "resolution",
           "recordDigest": "sha256:" + "d" * 64, "nonce": "n-" + "e" * 20, "notAfter": "2026-10-14T11:00:00Z",
           "signature": "ZmljdGlvbmFsLXNpZ25hdHVyZQ"}
    resolved = _with(att, att["evidence"] + [dict(bad, issuedAt="2026-10-14T08:00:00Z", resolution=res)])
    out += [
        ("a resolution applied after the adverse item and before notAfter resolves it",
         band(resolved, applied={res["nonce"]: "2026-10-14T09:00:00Z"}) == "high"),
        ("a resolution applied before the adverse item existed resolves nothing",
         band(resolved, applied={res["nonce"]: "2026-10-14T07:00:00Z"}) == "none"),
        ("a resolution without an application record resolves nothing", band(resolved) == "none"),
    ]

    # classes: never above the claimed class; extension classes without known axes count none
    up = {"id": "ev-u", "class": "observed", "covers": cov, "issuer": {"id": "https://assessor.vdhauditco.example"},
          "axes": {"source": "third-party", "assessor": "accredited", "timeBasis": "point-in-time", "binding": "signed",
                   "scope": "full"}, "issuedAt": "2026-10-13T00:00:00Z"}
    ext_pol = copy.deepcopy(policy)
    ext_pol["classes"]["https://ext.vdhcert.example/hw"] = {"ceiling": "medium", "freshnessDays": 365}
    ext = dict(att["evidence"][0], **{"class": "https://ext.vdhcert.example/hw"})
    first_party = copy.deepcopy(att["evidence"][0])
    first_party["axes"]["source"] = "first-party"
    out += [
        ("an item never counts above its claimed class", band(_with(att, [up])) == "low"),
        ("an extension class without known axes counts as none", band(_with(att, [ext]), p=ext_pol) == "none"),
        ("attested from a first-party source counts as self-measured", band(_with(att, [first_party])) == "medium"),
        ("honest items keep their class", band(_with(att, att["evidence"][:1])) == "high"),
    ]

    # ladder clamped at evaluation
    loose = copy.deepcopy(policy)
    for s in ("suspended", "withdrawn"):
        loose["states"][s].update(cap="high", freshnessScale=1.0)
    rising = copy.deepcopy(policy)
    rising["states"]["watch"]["cap"], rising["states"]["restricted"]["cap"] = "low", "medium"
    out += [
        ("a policy giving suspended or withdrawn a band is clamped to none",
         [band(_with(att, att["evidence"][:1], s), p=loose) for s in ("suspended", "withdrawn")] == ["none", "none"]),
        ("a cap rising down the ladder is clamped", band(_with(att, [good], "restricted"), p=rising) == "low"),
    ]

    # acceptances
    dead = copy.deepcopy(acc)
    dead["evidence"][0]["issuedAt"] = "2023-01-01T00:00:00Z"
    long = copy.deepcopy(acc)
    long["acceptance"]["until"] = "2028-01-01T00:00:00Z"
    weak = copy.deepcopy(acc)
    weak["acceptance"]["band"] = "low"
    restricted = copy.deepcopy(acc)
    restricted["stateHistory"][0]["since"] = "2026-10-14T08:00:00Z"
    restricted["stateHistory"].append({"state": "restricted", "since": "2026-10-14T08:30:00Z",
                                       "trigger": "confirmed finding with a remediation plan"})
    restricted["state"] = "restricted"
    restricted["evidence"][0]["issuedAt"] = "2026-04-20T00:00:00Z"
    restricted["acceptance"].update(band="low", limits=[{"type": "reduced-lease", "value": 0.9},
                                                        {"type": "data-ceiling", "value": "public"}])
    r_out = evaluate(restricted, policy, "2026-10-25T00:00:00Z", "normal")
    w_out = evaluate(weak, policy, AT, "normal")
    out += [
        ("an acceptance on evidence dead when decided does not apply", not acc_eval(dead)),
        ("an acceptance past maxDays does not apply", not acc_eval(long)),
        ("an active acceptance's limits apply even when it does not lift",
         w_out["accepted"] is False and w_out["limits"] == acc["acceptance"]["limits"]),
        ("per type the strictest limit wins", r_out["accepted"] and
         [x["value"] for x in r_out["limits"] if x["type"] == "reduced-lease"] == [0.5]),
        ("an honest acceptance still applies", acc_eval(acc)),
    ]

    # status and trust marks
    now = int(_t(AT).timestamp())
    ids = [e["id"] for e in att["evidence"]]
    adv_rec = _with(att, att["evidence"] + [dict(bad, issuedAt="2026-10-14T08:00:00Z")])
    out += [
        ("a status value outside the table is suspended and not restorable by a standing decision",
         E.state_from_status(0x07) == "suspended" and not E.standing_restoration_allowed(0x07)
         and E.standing_restoration_allowed(0x02)),
        ("a status token issued beyond the clock skew does not count",
         not E.status_token_counts({"iat": now + 3600}, AT, 300) and E.status_token_counts({"iat": now + 60}, AT, 300)),
        ("an expired status token does not count", not E.status_token_counts({"iat": now - 900, "exp": now - 1}, AT)),
        ("supporting evidence of an expired trust mark counts as none",
         band(att, trust_marks=[{"exp": now - 60, "evidence": ids}]) == "none"),
        ("an adverse item from an expired trust mark still cancels",
         band(adv_rec, trust_marks=[{"exp": now - 60, "evidence": ["ev-x"]}, {"exp": now + 3600, "evidence": ids}]) == "none"),
    ]
    return out
