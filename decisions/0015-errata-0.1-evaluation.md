# 0015: Errata to 0.1: evaluation corrections published with a security advisory

- Status: accepted
- Date: 2026-11-04
- Question: how are flaws in 0.1.0 that let a relying party grant more trust than the evidence supports corrected,
  when 0.1.0 is released and a PATCH release may change wording only (7.4)?

## Context
- An internal review of 0.1.0 (adversarial reading, an independent implementation from the text, property-based tests
  of the reference evaluator) found evaluation rules that grant more trust than the evidence supports; the list is in
  `errata/0.1.md` and in the security advisory.
- Section 7.4 allows a PATCH release to change wording only; these corrections change evaluation results, though
  nothing that validates.
- SECURITY.md publishes fixes to normative text as an erratum or a new version; CONTRIBUTING.md gives a normative
  change seven days of public review, which an embargoed fix cannot have before it is published.

## Decision
- The corrections are published as errata to 0.1.0 (`errata/0.1.md`), not as 0.1.1: every record and policy valid under
  0.1.0 stays valid; the reference evaluator and `tools/errata_vectors.py` implement them.
- They are prepared in the security advisory's private fork and merged when the advisory is published. The review
  period starts at publication; review comments are handled as follow-up fixes.
- Requirements that change what validates (an observation time, required requesters and summary results, decision
  digests, status token ratchets, extension-class axes, ladder schema rules) are proposals for 0.2, after the freeze.
- Decision 0004 is amended: coverage is compared after normalisation and overlaps unless recorded as distinct.

## Consequences
- 0.1 relying parties evaluate the same records more strictly; no valid input is refused.
- The decisions a relying party applies are judged against its own application time, so it keeps an application log
  and a nonce store.
