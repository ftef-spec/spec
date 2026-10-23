# Releasing FTEF

How a version of FTEF is released, so that what is published never changes afterwards (section 7.4 of the
specification). The maintainer signs every tag; nobody else can.

## Versions and paths
- A release is a signed tag `vMAJOR.MINOR.PATCH` on `main`. Tags are immutable (ruleset).
- Schemas live under `schemas/MAJOR.MINOR/` and are served at `https://ftef.vdhome.be/schema/MAJOR.MINOR/`, from release
  tags only (`.github/workflows/pages.yml`). The site follows `main`.
- From the first release of a MAJOR.MINOR, the files under its path never change. A PATCH release changes wording
  only; it never changes what validates.

## Before a MINOR release
1. Every issue and pull request in the version's milestone is merged, or deferred with a reason in the roadmap issue.
2. `main` is green: `python tools/check.py`, `ruff check`, `reuse lint`, CodeQL. Check `main` itself, not only the pull
   requests.
3. A fuzz run on the release candidate has no findings.
4. Migration notes from the previous version list every breaking change.
5. The specification header, `CITATION.cff` and the README status table name the new version.

## The release
1. Tag the commit and check the signature:
   `git tag -s vX.Y.0 <commit> -m "FTEF X.Y.0"`, then `git tag -v vX.Y.0`, then `git push origin vX.Y.0`.
2. The tag runs `pages.yml`, which publishes the schemas of every release. It refuses to publish when a release
   changes a file that an earlier release published.
3. Check that each served schema equals the file at the tag, for example
   `curl -s https://ftef.vdhome.be/schema/X.Y/policy.schema.json | sha256sum` against
   `git show vX.Y.0:schemas/X.Y/policy.schema.json | sha256sum`.
4. Close the roadmap issue and the milestone.

## Right after a MINOR release: open the next version
The first change on `main` after `vX.Y.0` opens `X.(Y+1)`, before any normative change:
- copy `schemas/X.Y/` to `schemas/X.(Y+1)/` and set `$id` and the `ftef` value to the new version;
- point the examples, the conformance vectors and `tools/check.py` at the new version;
- from then on `schemas/X.Y/` stays as it was released.

Every normative change then lands under the new version. Changing a released version's schema means a new version.

## 0.1
`v0.1.0` was tagged on 2026-10-23, after proposals for 0.2 had already changed `schemas/0.1/` on `main`. The published
0.1 schemas are those of the tag. Opening 0.2 (roadmap #19) therefore also restores `schemas/0.1/` to `v0.1.0`, and
from then on a check in CI keeps every released version's directory equal to its tag.
