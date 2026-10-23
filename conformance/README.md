# FTEF conformance vectors

Test vectors for section 7.5 of the specification. They are part of every release.

| File | What a vector holds | What an implementation shows |
|---|---|---|
| `evaluation.json` | a partner record and a policy, a time, a situation level, whether status is reachable | that it computes the expected band, evidenced band, acceptance and limits (6.1 to 6.5, 8.1) |
| `validity.json` | one document and its kind (partner record, policy, trust mark) | that it accepts or rejects the document as expected |

Every vector names the rule it shows (`rule`, a section number). `vector.schema.json` describes the format.

Documents are given as a `base` file in this repository plus an optional `patch`: the `add`, `remove` and `replace`
operations of RFC 6902 JSON Patch. Members whose names start with `_` (comments in the examples) are removed before
the patch. `expect` lists only the outputs a vector is about; an implementation compares those.

`python tools/check.py` runs every vector against the reference evaluator and checker. Every normative change adds or
changes vectors in the same pull request (`CONTRIBUTING.md`). Vectors use fictional parties on `.example` domains only.
