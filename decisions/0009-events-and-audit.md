# 0009: Events and audit (optional profile)

- Status: proposed (decision record only; the profile text follows if accepted)
- Date: 2026-10-21
- Question: should FTEF define an interoperable record of what happened to a partner (state changes, acceptances,
  lapses, evidence changes, band changes), and how do events from outside stay safe?

## Context
- 5.7 records state changes, but there is no exchange format for them, and no audit of acceptances, lapses and
  evaluations that another party could read or replay.
- Section 9 already treats event streams (Shared Signals, CAEP) as advisory input and keeps upgrades decided.
- Implementations of access-request tools keep typed audit event lists with actor, channel and reason, end records
  instead of deleting them, and expire pending requests; their signed approval links can be replayed within their
  expiry unless the identifier is single-use.

## Proposed direction (profile 8.4, optional)
1. Each state change, acceptance, lapse, evidence change, withdrawal and band change is a CloudEvents 1.0 event with a
   deterministic `id` (the idempotency key) and the digest of the record it was derived from.
2. Delivery is at least once; consumers deduplicate by `id` for at least the longest disconnection they tolerate
   (decision 0008).
3. Events never widen: only a verified downgrade acts on an event; a move up always needs a decision (6.6).
4. Inbound Security Event Tokens (RFC 8417) are checked for `jti`, `iat`, audience and age, wrapped with the token
   kept, and refused when older than the isolation horizon.
5. Audit events are typed (an enumerated list), carry the actor as an opaque reference, the channel and the reason,
   and are never deleted, only ended.

## Open questions
- The payload: OCSF has identity and access classes but none for partner trust; is a compliance or entity class a fit,
  or should FTEF define its own small payload? (unverified)
- The status of the Shared Signals specifications should be checked before they are referenced normatively.
