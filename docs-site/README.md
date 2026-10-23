<!--
SPDX-FileCopyrightText: 2026 FTEF contributors
SPDX-License-Identifier: Apache-2.0
-->

# FTEF reading site

The site at https://ftef.vdhome.be is built from this repository by `.github/workflows/pages.yml`: first the reading
site, then the schemas of every release tag at their `$id` paths (section 7.4).

The reading site presents what is already in the repository; it adds no normative content.

| Page | Source |
|---|---|
| `/spec/0.1` (also `/spec/0.1/`), one page per release line | `spec/ftef.md` at the newest `v0.1.*` tag |
| `/spec/main` | `spec/ftef.md` on main, marked unreleased |
| `/decisions/` | `decisions/*.md` on main |
| `/glossary/` | section 3 of the newest release, with the sections that use each term |
| `/review` | how to review; the review periods are read from `CONTRIBUTING.md` |
| `/roadmap` | links to the roadmap issues and milestones |
| `/` | links, and the schemas of every release |

## Build

```sh
sh docs-site/build.sh [OUT]          # default OUT: _site; needs git, Node 22 with npm, Python 3, and the v* tags
python docs-site/check_site.py _site  # links, anchors, and no resource from another host
```

`build.sh` clones Quartz at a pinned tag and refuses to build when the tag does not resolve to the pinned commit
(`QUARTZ_TAG`, `QUARTZ_SHA`). It installs Quartz's own `package-lock.json` with `npm ci`, applies `patches/`, copies
`quartz.config.ts`, `quartz.layout.ts` and `custom.scss` into the checkout, and generates the content with
`build_content.py`. Everything it creates lives in `docs-site/.build/` (ignored by git).

## Rules
- Pinned: Quartz v4.5.2 (`4923affa`), Node 22.23.3 in CI. Update both on purpose, in a pull request of their own.
- Nothing at runtime from another host: no analytics, no web fonts (Inter if installed, else the system sans-serif),
  no CDN. Quartz features that load from a CDN stay off (mermaid, LaTeX); `patches/0001-no-cdn-preconnect.patch`
  removes Quartz's preconnect to a CDN. `check_site.py` fails the build if a page loads anything from another host.
- Colours from `brand/BRAND.md`; links reach 4.5:1 on the paper in both themes.
- Quartz is MIT licensed; `quartz.config.ts`, `quartz.layout.ts` and the patch are adapted from it (`LICENSES/MIT.txt`).
