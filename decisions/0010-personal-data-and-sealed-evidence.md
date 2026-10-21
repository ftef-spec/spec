# 0010: Personal data in partner records and sealed evidence

- Status: proposed (decision record only; the normative text follows if accepted)
- Date: 2026-10-21
- Question: section 10 keeps personal data out of evidence summaries. What about the people who decide, contacts,
  history retention, and sensitive assessment reports that a relying party must keep but should rarely read?

## Context
- Decision 0003 introduces decider references; 7.2(6) asks that accountable people can see active acceptances. Both
  touch personal data.
- History is append-only (decision 0005) with no retention class.
- Assessment reports behind a `reference` can be sensitive; today the trust mark carries references, not evidence, and
  nothing describes how a relying party keeps a report it must hold.

## Proposed direction
1. Deciders are recorded by role and an opaque, stable reference, never a name or mail address; the mapping stays with
   the relying party.
2. Contacts in `recourse` come from a role register, not free text.
3. History entries and acceptances carry a retention class; at its end, personal data is removed while digests keep
   the chain verifiable.
4. A `reference` MAY point to sealed evidence: encrypted per object, released only to a threshold of named custodians,
   for a recorded purpose, time-boxed and logged; at retention end the key is destroyed (cryptographic erasure, NIST
   SP 800-88) with a signed certificate of destruction, while the digest stays verifiable.

## Open questions
- Is a role plus an opaque reference enough for the visibility duty of 7.2(6), or do accountable people need names?
- Scope: does evidence about a partner's proofing of its own people (for example as OpenID Identity Assurance
  verified claims) belong in FTEF at all, or in a separate profile? FTEF judges partner domains, not persons.
