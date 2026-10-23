# 0006: Risk acceptance in aggregate

- Status: proposed
- Date: 2026-10-21
- Question: 0.1 bounds one acceptance (an end, never `high`, at least one limit). Does that stop a relying party from
  lifting a partner with no evidence far above it, splitting one large risk into many small acceptances, or letting
  accepted trust leak into other decisions?

## Context
- A partner whose evidence counts as `none` can today be accepted to `medium`.
- Nothing limits acceptances in aggregate: their number, their summed residual, or days per partner over time;
  withdrawing and re-admitting a partner resets the no-chaining rule.
- An acceptance does not say what it was decided on or how much risk it leaves, so it cannot lapse when its basis goes.
- `no-transit` is an optional limit, so accepted trust can be passed on.

## Decision (proposed)
1. **One band at most.** An acceptance lifts at most one band above the evidenced band.
2. **A budget.** `acceptance.budget`: maximum active acceptances in all and per partner, a maximum summed residual, and
   acceptance days per partner per window; a tombstone of the partner identifier survives re-admission.
3. **Basis and residual.** Every acceptance names its basis (evidence ids) and records its residual on the relying
   party's own scale; it lapses when an item of its basis is withdrawn or removed.
4. **No propagation.** Accepted trust never feeds another trust computation; `no-transit` applies while it lifts.
5. **Requested versus granted.** A decider may grant less; the record keeps what was requested.

## Consequences
- Schema: `basis`, `residual` (required) and `requested` on acceptances; `acceptance.budget` in the policy.
- Reference evaluator: one-band cap, basis lapse, implied `no-transit`. Three evaluator cases, one invalid example.
- Budgets span partners, so they are a relying-party duty the single-record checker shows only for internal
  consistency.

## Open questions
- Should the residual be on a normative scale, or stay purely local? Principle 2 forbids exchanging it either way.
- Should a missing required evidence area (0.2 posture exchange) also block an acceptance?
