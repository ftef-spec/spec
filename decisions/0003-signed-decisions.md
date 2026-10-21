# 0003: Decisions are signed, bound and separated

- Status: proposed
- Date: 2026-10-21
- Question: 0.1 records the decider of a move up or a risk acceptance as free text (`decidedBy`). Can a relying party
  verify a decision, refuse a replayed or stale one, and stop the requester from deciding their own request?

## Context
- `decidedBy` is a string. Nothing makes a decision verifiable, bound to what was decided, or unusable after the record
  changed.
- Nothing stops the person who asked for a move up or an acceptance from deciding it.
- The policy does not say who may decide, so an empty set of deciders has no defined outcome.
- A widening change to the relying party's own policy (a higher ceiling, a longer freshness) is not treated as a
  decision at all.

## Prior art
- Open-source access-request tools (discord/access, GoogleCloudPlatform/jit-groups, aws-samples TEAM) authenticate
  the approver and record the click; they sign nothing about what was approved. jit-groups sends signed approval
  tokens with an expiry and an identifier, which can be replayed within their expiry unless the identifier is
  single-use. TEAM fails closed when no approver exists.
- RFC 8785 gives a canonical JSON form to sign. W3C WebAuthn assertions are bound to an origin and a challenge, which
  allows purpose separation.

## Decision (proposed)
New section 6.6 and a `decision` object in the partner-record schema:
1. Admission, every move up and every risk acceptance carry a decision: decider role, opaque decider reference,
   purpose, digest of the canonical record, nonce, `notAfter`, signature. A decision that does not verify counts as
   absent.
2. A decision applies only while the record digest matches and before `notAfter`: a stale decision is refused.
3. The policy names decider roles for admission, acceptances and each state's move up (`deciders`). An empty set means
   the move cannot happen.
4. The requester never decides (`requestedBy`). Two-person rules compare persons, not accounts.
5. Decision signatures are separated by purpose from each other and from authentication.
6. A policy change that widens is itself a decision, by someone other than its author.

## Consequences
- Schemas: `decision` and `requestedBy` in `stateChange` and `acceptance`; `deciders` in the policy and per state.
- The checker verifies shape, roles, requester separation and `notAfter`; it cannot verify the fictional signatures.
- Valid examples gain decisions; four new invalid examples (self-decided acceptance, admission without decision,
  wrong decider role, decision applied after `notAfter`) and one invalid policy (state without deciders).
- `decidedBy` stays as a human-readable label next to the signed decision.

## Open questions
- Should FTEF name signature algorithms or leave them to profiles (out of scope today)?
- Is a role plus an opaque reference enough for the visibility duty of 7.2(6) (see decision 0010)?
