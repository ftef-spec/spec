# Contributing to FTEF

Thank you for helping. This repository is a Community Specification Working Group: the contribution policy is
[`06-contributing.md`](06-contributing.md), and the governance is [`05-governance.md`](05-governance.md).

## Before you start
- **Agreement.** By making a contribution you agree to the Community Specification Contributor License Agreement
  (`00-contributor-license-agreement.md`), which covers the Community Specification License, the governance and contribution policies, and the code of conduct.
- **DCO sign-off.** Every commit MUST carry a Developer Certificate of Origin sign-off
  (https://developercertificate.org/): `git commit -s`. CI rejects commits without it.
- **Open an issue first** for anything that changes normative text. Use a "Proposal:" title for new ideas and
  "Spec Change:" for concrete changes, as `06-contributing.md` describes.

## Changes
| Kind | What | Review period |
|---|---|---|
| editorial | wording that does not change meaning | at least 24 hours |
| fix | corrects an error, no new requirement | at least 72 hours |
| normative | adds, removes or changes a requirement, schema or invariant | at least 7 days, and a record in `decisions/` |

While there is one maintainer, the review periods are observed by the maintainer and are not enforced by branch rules (`MAINTAINERS.md`).

- A normative change updates the specification, the schema, the examples and `tools/check.py` in the same pull request, and keeps `python tools/check.py` and `reuse lint` green.
- Examples use fictional parties only, on `.example` domains.
- Never include real infrastructure, risk registers, attack paths or personal data (see section 10 of the specification).

## Use of AI tools
Contributions written with the help of AI tools are accepted, provided that the contributor has reviewed them, takes
responsibility for them, and can make the DCO sign-off truthfully. Disclose the help in the commit message with a
trailer such as `Assisted-by: <tool>` or `Co-Authored-By: <tool>`. Only a person signs off; a tool never adds a
`Signed-off-by` line.
