# 0008: Disconnected relying parties

- Status: proposed
- Date: 2026-10-21
- Question: 8.1 caps a partner's band at `none` when status is unreachable for twice its `ttl`. What else must hold
  when an evaluation point is cut off for longer, and in what order does it recover?

## Context
- 8.1 prevents mass suspension by capping evaluation instead of changing state. It has no outer horizon for other
  cached inputs (trust marks, evidence, policy) and no rule for what may change while disconnected.
- On reconnection nothing says which inputs come first, so a raise could be applied before a newer downgrade.

## Decision (proposed)
1. While disconnected: moves down only; no move up and no new acceptance.
2. An isolation horizon (`isolationHorizonDays`, RECOMMENDED 7) caps every cached input; past it nothing cached
   counts.
3. On reconnection: downgrades, withdrawals and issuer ceilings first; then lift the 8.1 outage cap; then re-derive.

## Consequences
- New 6.8; policy `isolationHorizonDays` (the checker refuses more than 30); Annex C default 7 days.
- No change to the reference evaluator: disconnection is the relying party's operating state, not a property of a
  record.

## Open questions
- Degraded mode: keep `none` after twice the `ttl` as the only rule, or allow a policy-defined cap (for example `low`
  with limits) for a disconnected point? This proposal does not decide it.
- Mass downgrade from one source on reconnection: apply and alert, or pause? A pause would break principle 5 (down
  fast); this proposal does not decide it.
