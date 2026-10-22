# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Reference evaluation of an FTEF 0.1 partner record under a relying-party policy (section 6).

evaluate(record, policy, at, situation_level, status_reachable=True) -> {band, evidencedBand, accepted, limits}

The record is the relying party's own: its bindings are taken as verified and its scope as set by the relying party
(5.2, 6.1). Informative: where this code and the specification disagree, the specification applies, and this code is
a bug.
"""
from __future__ import annotations

from datetime import datetime, timedelta

BANDS = ["none", "low", "medium", "high"]
LADDER = ["member", "watch", "restricted", "suspended", "joining", "withdrawn", "exited"]   # 5.6, most trusted first


def _t(s: str) -> datetime:
    """RFC 3339 date-time as the schemas accept it: Z or z for UTC, and a leap second (:60) counted as :59."""
    if s[-1:] in ("Z", "z"):
        s = s[:-1] + "+00:00"
    if s[17:19] == "60":
        s = s[:17] + "59" + s[19:]
    return datetime.fromisoformat(s)


def _lower(b: str, n: int = 1) -> str:
    return BANDS[max(0, BANDS.index(b) - n)]


def _min(*bs: str) -> str:
    return min(bs, key=BANDS.index)


def _scale(policy: dict, state: str, level: str) -> float:
    levels = {x["level"]: x["freshnessScale"] for x in policy["situationLevels"]}
    return policy["states"].get(state, {}).get("freshnessScale", 1.0) * levels[level]


def _skew(policy: dict) -> timedelta:
    return timedelta(seconds=policy.get("clockSkewSeconds", 0))


def _shift(t: datetime, d: timedelta) -> datetime:
    """t + d, saturating at the ends of the calendar: near year 1 or 9999 a skew must not crash the evaluation."""
    try:
        return t + d
    except OverflowError:
        return (datetime.max if d > timedelta(0) else datetime.min).replace(tzinfo=t.tzinfo)


def item_band(item: dict, policy: dict, state: str, at: datetime, level: str) -> str:
    """6.1 and 6.2 for one evidence item. Clock skew only narrows: age is judged as if the clock were late, and an
    item counts only once it is issued even if the clock is early (6.2)."""
    late, early = _shift(at, _skew(policy)), _shift(at, -_skew(policy))
    cls = policy["classes"].get(item["class"])
    axes = item["axes"]
    if cls is None or axes.get("scope", "none") == "none":
        return "none"
    if axes["timeBasis"] == "period":
        if "coversFrom" not in item or "coversUntil" not in item:
            return "none"                               # 6.2 needs the period: without it the item buys nothing
        if not (_t(item["coversFrom"]) <= _t(item["coversUntil"]) <= _t(item["issuedAt"])):
            return "none"                               # 6.2: a period reaching into the future buys nothing
        start = item["coversUntil"]
    else:
        start = item["issuedAt"]
    band = cls["ceiling"]
    if axes["scope"] == "partial":
        band = _lower(band)
    if band == "high" and axes["binding"] != "hardware-rooted":
        band = "medium"
    age_days = (late - _t(start)).total_seconds() / 86400
    if early < _t(start) or early < _t(item["issuedAt"]):
        return "none"                                   # dated in the future (6.1)
    fresh = cls["freshnessDays"] * _scale(policy, state, level)
    if age_days > 2 * fresh:
        return "none"                                   # long stale: counts as missing
    if age_days > fresh:
        band = _lower(band)                             # stale: one band lower
    return band


def alive(item: dict, policy: dict, state: str, at: datetime, level: str) -> bool:
    """An item still in play: issued, not dated in the future, and not past twice its freshness (6.1, 6.2)."""
    cls = policy["classes"].get(item["class"])
    if cls is None:
        return False
    start = item["coversUntil"] if item["axes"]["timeBasis"] == "period" else item["issuedAt"]
    early, late = _shift(at, -_skew(policy)), _shift(at, _skew(policy))        # an adverse item narrows, so skew keeps it in play
    age_days = (early - _t(start)).total_seconds() / 86400
    return late >= _t(item["issuedAt"]) and age_days <= 2 * cls["freshnessDays"] * _scale(policy, state, level)


def counted(record: dict, policy: dict, state: str, at: datetime, level: str) -> list[dict]:
    """The items that may raise the band (6.1): never a withdrawn id, never an adverse item, and nothing about coverage
    that an unresolved adverse item in play contradicts. Contradiction resolves towards less trust."""
    gone = set(record.get("withdrawnEvidence", []))
    items = [i for i in record["evidence"] if i["id"] not in gone]
    blocked = {i["covers"] for i in items if i.get("result") == "adverse" and not i.get("resolution")
               and alive(i, policy, state, at, level)}
    return [i for i in items if i.get("result", "supports") == "supports" and i["covers"] not in blocked]


def lapsed(record: dict, policy: dict, situation_level: str, at: datetime) -> bool:
    """6.3: an acceptance lapses at its end, on a higher situation level, or on any move down after its decision."""
    a = record["acceptance"]
    if a.get("lapsedAt") or _shift(at, _skew(policy)) > _t(a["until"]):
        return True
    order = [x["level"] for x in policy["situationLevels"]]
    if a["situationLevel"] not in order:
        return True                                     # decided for a level this policy does not know: fail closed
    if order.index(situation_level) > order.index(a["situationLevel"]):
        return True
    hist = record["stateHistory"]
    return any(LADDER.index(b["state"]) > LADDER.index(p["state"]) and _t(b["since"]) >= _t(a["decidedAt"])
               for p, b in zip(hist, hist[1:]))


def evaluate(record: dict, policy: dict, at: str, situation_level: str, status_reachable: bool = True) -> dict:
    when = _t(at)
    state = record["state"]
    cap = "none" if state in ("joining", "exited") else policy["states"].get(state, {}).get("cap", "none")
    if record.get("notAfter") and _shift(when, _skew(policy)) > _t(record["notAfter"]):
        status_reachable = False                        # 7.4.1: an expired record counts as unreachable status
    if not status_reachable:
        cap = "none"                                    # 8.1: evaluation capped, state unchanged
    best = "none"
    for item in counted(record, policy, state, when, situation_level):
        best = max(best, item_band(item, policy, state, when, situation_level), key=BANDS.index)
    evidenced = _min(best, cap)
    limits = list(policy["states"].get(state, {}).get("limits", []))
    out = {"band": evidenced, "evidencedBand": evidenced, "accepted": False, "limits": limits}
    a = record.get("acceptance")
    if a and status_reachable and record["evidence"] and _t(a["decidedAt"]) <= _shift(when, -_skew(policy)) \
            and not lapsed(record, policy, situation_level, when):
        lifted = _min(a["band"], policy["acceptance"]["maxBand"], cap)
        if BANDS.index(lifted) > BANDS.index(evidenced):
            merged = limits + [x for x in a["limits"] if x not in limits]
            out.update(band=lifted, accepted=True, limits=merged)
    return out
