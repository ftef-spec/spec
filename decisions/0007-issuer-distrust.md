# 0007: Distrust of issuers and schemes

- Status: proposed
- Date: 2026-10-21
- Question: when an assessor, verifier, scheme or method is found weak, how does a relying party lower what all its
  evidence is worth, at once and everywhere?

## Context
- 0.1 has ceilings per evidence class only. An issuer found weak keeps its items at their class ceiling until each
  item expires.
- A producer could state a level about itself that the policy never granted.

## Prior art
- Root store programmes distrust a certificate authority from a date, while older certificates age out.
- Identity assurance frameworks retire proofing methods and re-check results produced with them.

## Decision (proposed)
1. `issuerCeilings` in the policy: an issuer, scheme or method URI, a lowered ceiling (never `high`), a date and a
   reason. From that date every item from it counts no higher.
2. The issuer is the identity established by the verified binding, never the document's own field.
3. A level the producer reports can only lower what the policy allows.
4. A lowered ceiling triggers re-evaluation at once and reaches disconnected evaluation points with the priority of
   status revocations.
5. Annex C maps external assurance levels onto bands, below the class and issuer ceilings.

## Consequences
- Policy schema `issuerCeilings`; the reference evaluator applies it; two evaluator cases and one invalid policy.
- The mapping of external levels is informative (Annex C).

## Open questions
- Should a registry publish issuer distrust for all its relying parties (a shared list), or stay with each relying
  party's own policy?
