# SPDX-FileCopyrightText: 2026 FTEF contributors
# SPDX-License-Identifier: Apache-2.0
"""Reference evaluation of an FTEF 0.1 partner record under a relying-party policy (section 6).

evaluate(record, policy, at, situation_level, status_reachable=True, trust_marks=None, applied=None, disjoint=None)
    -> {band, evidencedBand, accepted, limits}

The record is the relying party's own: its bindings are taken as verified and its scope as set by the relying party
(5.2, 6.1). The optional inputs are the relying party's own logs: the trust marks the evidence came from, the time it
applied each decision (by nonce), and the coverage pairs it recorded as disjoint. Informative: where this code and the
specification disagree, the specification applies, and this code is a bug.
"""
from __future__ import annotations

import unicodedata
from datetime import datetime

BANDS = ["none", "low", "medium", "high"]
LADDER = ["member", "watch", "restricted", "suspended", "joining", "withdrawn", "exited"]   # 5.6, most trusted first
RATED = ["member", "watch", "restricted", "suspended", "withdrawn"]                       # 5.6: states with a cap
NO_BAND = ("suspended", "withdrawn")
# 5.3: the axes each named class requires
CLASS_AXES = {
    "self-declared": {"source": {"first-party"}},
    "self-measured": {"source": {"first-party"}, "timeBasis": {"continuous"}, "binding": {"signed", "signed-transparent", "hardware-rooted"}},
    "observed": {"source": {"second-party"}},
    "assessed-by-relying-party": {"source": {"second-party"}},
    "independently-assessed": {"source": {"third-party"}, "assessor": {"accredited", "mutually-recognised"}},
    "attested": {"source": {"verifier"}, "binding": {"hardware-rooted"}, "timeBasis": {"continuous", "at-access"}},
}
# 8.1: Status List Token values. 0x01 serves withdrawn and exited; both have no band.
STATUS_STATES = {0x00: "member", 0x01: "withdrawn", 0x02: "suspended", 0x0C: "watch", 0x0D: "restricted"}
# Unicode Default_Ignorable_Code_Point (DerivedCoreProperties): invisible, so never part of an identifier
_IGNORABLE = [(0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
              (0x180B, 0x180F), (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x206F), (0x3164, 0x3164),
              (0xFE00, 0xFE0F), (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3),
              (0x1D173, 0x1D17A), (0xE0000, 0xE0FFF)]


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


def _visible(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    return "".join(c for c in s if not any(lo <= ord(c) <= hi for lo, hi in _IGNORABLE))


def person(ref: str | None) -> str:
    """6.6: references to persons compared after NFKC, without invisible code points, case folded and trimmed."""
    return _visible(ref or "").casefold().strip()


def coverage(covers: str) -> str:
    """5.2: covers compared after NFKC, without invisible code points, case folded, white space collapsed."""
    return " ".join(_visible(covers).casefold().split())


# 5.6: the ladder at evaluation. A policy that lets a cap or a scale rise down the ladder is clamped, not obeyed.
def _above(state: str) -> list[str]:
    return RATED[:RATED.index(state) + 1] if state in RATED else RATED


def state_cap(policy: dict, state: str) -> str:
    if state not in RATED or state in NO_BAND:
        return "none"
    return _min(*(policy["states"].get(s, {}).get("cap", "none") for s in _above(state)))


def _scale(policy: dict, state: str, level: str) -> float:
    levels = {x["level"]: x["freshnessScale"] for x in policy["situationLevels"]}
    return min(policy["states"].get(s, {}).get("freshnessScale", 0.0) for s in _above(state)) * levels[level]


# 6.1: the class an item counts as
def meets(axes: dict, required: dict) -> bool:
    return all(axes.get(a) in allowed for a, allowed in required.items())


def class_axes(name: str, policy: dict) -> dict | None:
    """The required axes of a class: the named classes from 5.3; an extension class has none known here."""
    return CLASS_AXES.get(name)


def effective_class(item: dict, policy: dict) -> dict | None:
    """6.1: an item counts no higher than its claimed class, and no higher than the highest named class whose axes it
    meets (with the shorter freshness of the two); an item that meets none, or an extension class whose axes are not
    known, counts as nothing."""
    claimed = policy["classes"].get(item["class"])
    required = class_axes(item["class"], policy)
    if claimed is None or required is None:
        return None
    if meets(item["axes"], required):
        return claimed
    fits = [policy["classes"][c] for c in CLASS_AXES if c in policy["classes"] and meets(item["axes"], CLASS_AXES[c])]
    if not fits:
        return None
    best = max(fits, key=lambda c: (BANDS.index(c["ceiling"]), -c["freshnessDays"]))
    return {"ceiling": _min(best["ceiling"], claimed["ceiling"]),
            "freshnessDays": min(best["freshnessDays"], claimed["freshnessDays"])}


def _start(item: dict) -> str | None:
    """6.2: age runs from coversUntil whenever stated, else from issuedAt. None: the dates buy nothing."""
    axes = item["axes"]
    if axes["timeBasis"] == "period":
        if "coversFrom" not in item or "coversUntil" not in item:
            return None
        if not (_t(item["coversFrom"]) <= _t(item["coversUntil"]) <= _t(item["issuedAt"])):
            return None
    if "coversUntil" in item and _t(item["coversUntil"]) > _t(item["issuedAt"]):
        return None
    return item.get("coversUntil") or item["issuedAt"]


def item_band(item: dict, policy: dict, state: str, at: datetime, level: str) -> str:
    """6.1 and 6.2 for one supporting evidence item."""
    cls = effective_class(item, policy)
    axes = item["axes"]
    if cls is None or axes.get("scope", "none") == "none":
        return "none"
    start = _start(item)
    if start is None:
        return "none"
    band = cls["ceiling"]
    if axes["scope"] == "partial":
        band = _lower(band)
    if band == "high" and axes["binding"] != "hardware-rooted":
        band = "medium"
    age_days = (at - _t(start)).total_seconds() / 86400
    if age_days < 0 or at < _t(item["issuedAt"]):
        return "none"                                   # dated in the future (6.1)
    fresh = cls["freshnessDays"] * _scale(policy, state, level)
    if age_days > 2 * fresh:
        return "none"                                   # long stale: counts as missing
    if age_days > fresh:
        band = _lower(band)                             # stale: one band lower
    return band


def in_play(item: dict, policy: dict, at: datetime) -> bool:
    """6.1: an adverse item of a listed class is in play until twice its class freshness, unscaled, after the latest of
    its dates. Defects in its axes or dates never take it out of play; one dated in the future is in play."""
    cls = policy["classes"].get(item["class"])
    if cls is None:
        return False                                    # unlisted class: left to the open proposal on adverse sources
    dates = [_t(item[k]) for k in ("issuedAt", "observedAt", "coversUntil") if k in item]
    return (at - max(dates)).total_seconds() / 86400 <= 2 * cls["freshnessDays"]


# 6.6: decisions
def decision_holds(d: dict | None, roles: list, purpose: str, applied_at: str | None,
                   requested_by: str | None = None) -> bool:
    """Purpose, a role the policy names, not the requester (persons compared normalised), and applied by the relying
    party strictly before notAfter. applied_at is the relying party's own time of application; None means not applied.
    Signature, digest and nonce are verified before the record reaches here."""
    if not d or d.get("purpose") != purpose or d.get("deciderRole") not in roles or applied_at is None:
        return False
    if requested_by is not None and person(requested_by) == person(d.get("deciderRef")):
        return False
    return _t(applied_at) < _t(d["notAfter"])


def _applied(applied: dict | None, d: dict | None, recorded: str | None) -> str | None:
    """The relying party's application time of a decision: from its log by nonce when given, else the time its own
    record states (only valid for a record it wrote when it applied the decision)."""
    if not d:
        return None
    if applied is not None:
        return applied.get(d.get("nonce"))
    return recorded


def resolution_roles(policy: dict) -> list:
    """0.1 names no resolution roles: the admission roles decide resolutions."""
    return policy.get("deciders", {}).get("admission", [])


def resolved(item: dict, policy: dict, applied: dict | None) -> bool:
    """A resolution holds only as a decision for purpose resolution, applied before its notAfter and not before the
    adverse item was issued. Without a logged application time it is taken as applied now: it holds only until
    notAfter, after which the adverse item cancels again."""
    d = item.get("resolution")
    if not d:
        return False
    when = applied.get(d.get("nonce")) if applied is not None else None
    if when is not None and _t(when) < _t(item["issuedAt"]):
        return False
    return when is not None and decision_holds(d, resolution_roles(policy), "resolution", when)


class NonceStore:
    """6.6: nonces of applied, signature-verified decisions, kept per decider key until notAfter plus skew."""

    def __init__(self, skew_seconds: float = 0):
        self.skew, self.seen = skew_seconds, {}

    def admit(self, decider_key: str, nonce: str, not_after: str, now: str) -> bool:
        n = _t(now).timestamp()
        for k in [k for k, exp in self.seen.items() if exp < n]:
            del self.seen[k]
        key = (person(decider_key), nonce)
        if key in self.seen:
            return False
        self.seen[key] = _t(not_after).timestamp() + self.skew
        return True


def counted(record: dict, policy: dict, state: str, at: datetime, level: str, applied: dict | None = None,
            disjoint: set | None = None) -> list[dict]:
    """The items that may raise the band (6.1): never a withdrawn id, never an adverse item, and nothing that an
    unresolved adverse item in play overlaps. Coverage overlaps unless equal-normalised coverage is excluded by the
    relying party's record of disjoint pairs: when in doubt, overlap (decision 0004)."""
    gone = set(record.get("withdrawnEvidence", []))
    items = [i for i in record["evidence"] if i["id"] not in gone]
    adverse = {coverage(i["covers"]) for i in items if i.get("result") == "adverse"
               and not resolved(i, policy, applied) and in_play(i, policy, at)}
    pairs = {frozenset(coverage(c) for c in p) for p in (disjoint or set())}

    def free(i: dict) -> bool:
        c = coverage(i["covers"])
        return all(a != c and frozenset((a, c)) in pairs for a in adverse)
    return [i for i in items if i.get("result", "supports") == "supports" and free(i)]


def history_ok(record: dict) -> bool:
    """5.7: history only grows forwards; an entry dated before an earlier one is refused."""
    h = record["stateHistory"]
    return all(_t(b["since"]) >= _t(a["since"]) for a, b in zip(h, h[1:]))


def lapsed(record: dict, policy: dict, situation_level: str, at: datetime) -> bool:
    """6.3: an acceptance lapses at its end, on a higher situation level, or on any move down after its decision."""
    a = record["acceptance"]
    if a.get("lapsedAt") or at > _t(a["until"]):
        return True
    order = [x["level"] for x in policy["situationLevels"]]
    if a["situationLevel"] not in order:
        return True                                     # decided for a level this policy does not know: fail closed
    if order.index(situation_level) > order.index(a["situationLevel"]):
        return True
    hist = record["stateHistory"]
    return any(LADDER.index(b["state"]) > LADDER.index(p["state"]) and _t(b["since"]) >= _t(a["decidedAt"])
               for p, b in zip(hist, hist[1:]))


def state_at(record: dict, at: datetime) -> str:
    state = "joining"
    for h in record["stateHistory"]:
        if _t(h["since"]) <= at:
            state = h["state"]
    return state


def qualifies(record: dict, policy: dict, applied: dict | None = None, disjoint: set | None = None) -> bool:
    """6.3: a supporting item, still in the record, that counted at least low at decidedAt, under the recorded situation
    level and the state of that moment (a partner being admitted counts as member)."""
    a = record["acceptance"]
    when = _t(a["decidedAt"])
    if a["situationLevel"] not in [x["level"] for x in policy["situationLevels"]]:
        return False
    state = state_at(record, when)
    state = "member" if state == "joining" else state
    return any(item_band(i, policy, state, when, a["situationLevel"]) != "none"
               for i in counted(record, policy, state, when, a["situationLevel"], applied, disjoint))


def within_max_days(a: dict, policy: dict) -> bool:
    secs = (_t(a["until"]) - _t(a["decidedAt"])).total_seconds()
    return 0 < secs <= policy["acceptance"]["maxDays"] * 86400


def merge_limits(*groups: list) -> list:
    """6.5: per type the strictest wins: one reduced-lease with the smallest factor, every distinct data-ceiling (FTEF
    does not order labels, so each applies), flag limits once."""
    out, lease = [], None
    for lim in (x for g in groups for x in g):
        if lim["type"] == "reduced-lease":
            if lease is None:
                lease = dict(lim)
                out.append(lease)
            elif lim["value"] < lease["value"]:
                lease["value"] = lim["value"]
        elif lim not in out:
            out.append(dict(lim))
    return out


# 8.1: status
def state_from_status(value: int) -> str:
    """A value outside the table counts as suspended."""
    return STATUS_STATES.get(value, "suspended")


def standing_restoration_allowed(cause_value: int) -> bool:
    """6.4: a standing decision restores only a suspension caused by the registry's own suspended value, never one
    caused by a value outside the table."""
    return cause_value == 0x02


def status_token_counts(claims: dict, at: str, skew_seconds: float = 0) -> bool:
    """A Status List Token (signature verified) counts only unexpired and not issued in the future beyond the relying
    party's clock skew."""
    now = _t(at).timestamp()
    if "exp" in claims and claims["exp"] <= now:
        return False
    return claims["iat"] <= now + skew_seconds


def _expired_mark_items(trust_marks: list | None, when: datetime) -> set:
    """Supporting evidence carried only by expired trust marks counts as none until a new mark carries it."""
    if not trust_marks:
        return set()
    live = {i for m in trust_marks if m["exp"] > when.timestamp() for i in m["evidence"]}
    return {i for m in trust_marks for i in m["evidence"]} - live


def evaluate(record: dict, policy: dict, at: str, situation_level: str, status_reachable: bool = True,
             trust_marks: list | None = None, applied: dict | None = None, disjoint: set | None = None) -> dict:
    """trust_marks: [{"exp": NumericDate, "evidence": [ids]}]; applied: {nonce: time the relying party applied that
    decision}; disjoint: pairs of covers values the relying party recorded as not overlapping."""
    when = _t(at)
    state = record["state"]
    if not history_ok(record):
        return {"band": "none", "evidencedBand": "none", "accepted": False, "limits": []}
    cap = state_cap(policy, state)
    if not status_reachable:
        cap = "none"                                    # 8.1: evaluation capped, state unchanged
    expired = _expired_mark_items(trust_marks, when)
    best = "none"
    for item in counted(record, policy, state, when, situation_level, applied, disjoint):
        if item["id"] not in expired:
            best = max(best, item_band(item, policy, state, when, situation_level), key=BANDS.index)
    evidenced = _min(best, cap)
    limits = merge_limits(policy["states"].get(state, {}).get("limits", []))
    out = {"band": evidenced, "evidencedBand": evidenced, "accepted": False, "limits": limits}
    a = record.get("acceptance")
    if a and status_reachable and record["evidence"] and _t(a["decidedAt"]) <= when \
            and decision_holds(a.get("decision"), policy["deciders"]["acceptance"], "acceptance",
                               _applied(applied, a.get("decision"), a["decidedAt"]), a.get("requestedBy")) \
            and within_max_days(a, policy) and qualifies(record, policy, applied, disjoint) \
            and not lapsed(record, policy, situation_level, when):
        out["limits"] = merge_limits(limits, a["limits"])       # 6.5: an active acceptance's limits apply
        lifted = _min(a["band"], policy["acceptance"]["maxBand"], cap)
        if BANDS.index(lifted) > BANDS.index(evidenced):
            out.update(band=lifted, accepted=True)
    return out
