# 0014: Conformance test vectors

- Status: proposed
- Date: 2026-10-23
- Question: the evaluation is normative text plus one reference evaluator. How does a second implementation show that
  it decides the same? (#40)

## Context
- A policy engine, a registry or a relying party's own code has no shared way to compare its results with the
  reference evaluator.
- In a relying-party model the same rules, kept in application code and in a policy language, drifted within a day:
  a fix landed in one and not the other, and nothing failed.
- `tools/check.py` held its evaluator cases as Python code, which no other implementation can run.

## Decision (proposed)
1. Each release publishes vectors under `conformance/` (section 7.5):
   - evaluation vectors: a partner record and a policy, a time, a situation level and status, with the expected band,
     evidenced band, acceptance and limits;
   - validity vectors: one document of a stated kind, with whether it is valid.
2. Documents are a `base` file plus RFC 6902 JSON Patch operations (`add`, `remove`, `replace`), so a vector is small
   and any language can build it. Every vector names its rule.
3. A relying party claiming 7.2 produces every evaluation vector's outputs and rejects every invalid document of the
   kinds it reads; a producer and a registry never emit one.
4. Every normative change adds or changes vectors in the same pull request; the reference evaluator runs them all.
5. The documents of an evaluation vector must themselves be valid: a vector never asks for an output on a document
   the specification rejects.

## Consequences
- `conformance/evaluation.json` (24 vectors: 6.1, 6.2, 6.3, 8.1), `conformance/validity.json` (28 vectors: every
  invalid example, the profile 8.1 invalid trust marks, and the valid examples), `conformance/vector.schema.json` and
  a README.
- `tools/check.py` runs the vectors and prints how many each rule has. The former inline evaluator cases became
  vectors; two cases on documents that fail their schema stay in `check.py` as robustness checks, since they are not
  valid documents.
- 7.5 in the specification; `CONTRIBUTING.md` lists the vectors among what a normative change updates.
- Rules not yet shown by an evaluation vector (6.4 and 6.6 are about records, not outputs) are covered by validity
  vectors only.

## Open questions
- Should validity vectors also name the expected reason, from a shared reason vocabulary (#39)?
- Should vectors move to their own published path (`https://ftef.vdhome.be/conformance/MAJOR.MINOR/`) with the
  schemas?
