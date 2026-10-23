# 0005: Time, versions and rollback

- Status: proposed
- Date: 2026-10-21
- Question: freshness depends on clocks and on seeing the newest input. How does a relying party stay safe when its
  clock is off, when an older record is served again, and when someone wants to check an evaluation later?

## Context
- Clock handling is one sentence in section 9.
- Partner records, policies and trust-mark evidence sets carry no version, so an older one can be replayed and restore
  trust that was removed.
- History is a list with no chaining; an evaluation does not say what it was computed from.

## Prior art
- The Update Framework protects clients against rollback and freeze attacks with monotonic versions and expiry.
- RFC 9334 judges freshness against an epoch and a local expiry.
- Derived state (state as a pure function of facts and time) is the pattern of level-triggered reconcilers.

## Decision (proposed)
1. **Skew narrows.** `clockSkewSeconds` in the policy (at most 300 in the checker). Freshness and acceptances are judged
   as if the clock were wrong in the unsafe direction; adverse items and expiries the other way.
2. **Monotonic ends.** Ends use the earlier of the wall clock and monotonic time since receipt; after a clock jump, only
   moves down until the clock is trusted.
3. **Versions.** Records, policies and trust-mark evidence sets carry `version`; a lower one is refused. The highest
   version seen is kept outside the evaluator's own state as well, and the higher of the two applies, so a reset of
   the evaluator cannot readmit an older signed document. After a versioned document, one without a version counts as
   lower than any version. A record MAY carry `notAfter`, after which it counts as unreachable status.
4. **Chained history.** History entries SHOULD carry `prev`, the digest of the previous entry, with a witnessed head.
5. **Replayable evaluation.** Evaluations SHOULD record `inputs` (record and policy digests).

## Consequences
- Schema: `version`, `notAfter`, `stateChange.prev`, `evaluation.inputs`; policy `version`, `clockSkewSeconds`.
- Reference evaluator applies skew and `notAfter`; three evaluator cases; the default policy uses 30 seconds.
- Monotonic version checks across documents are a relying-party duty the checker cannot show with single examples.
- The high-water mark outside the evaluator, and an unversioned document counting as lowest, come from the review of
  #22: a mark kept only in the evaluator's own state is lost with it.

## Open questions
- Should `notAfter` be REQUIRED on records exchanged between parties, or only on trust marks (which already carry
  `exp`)?
