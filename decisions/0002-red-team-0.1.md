# 0002: Red team of FTEF 0.1 before publication

- Status: accepted; fixes applied (maintainer, 2026-10-14), except the items under "Open" below
- Date: 2026-10-14
- Scope: the specification, schemas, examples, checker, CI and repository files, as committed locally before the first push.

## Own findings (author's adversarial pass)

### Critical
- **C1. Sign-offs made on the maintainer's behalf.** The local commits carry `Signed-off-by: Wombat164`. They were added by the drafting assistant, not typed by the maintainer. A DCO sign-off is a personal legal certification and must not be made for someone else.
  - **Fix:** before the first push, the maintainer reviews the content and either signs off themselves (`git rebase --signoff`) or the history is squashed into one commit they sign. AI assistance is disclosed with an `Assisted-by:` trailer.

### High
- **H1. Stale evidence never dies.** 6.1 lowers stale evidence by one band, with no floor in time. A year-old `attested` item would still give `medium` forever.
  - **Fix:** past twice its freshness, an item counts as `none`.
- **H2. Scope cannot be stated by the producer.** `scope` is defined against the relying party's seam, but producers and registries do not know any relying party's seam, and a producer can simply claim `full`.
  - **Fix:** producers state what the evidence covers (`covers`). The relying party sets `scope` and MUST NOT take it from the producer. Trust mark summaries carry `covers`, not `scope`.
- **H3. Status outage turns into mass suspension that needs manual recovery.** 8.1 says to treat the partner as `suspended` after twice the `ttl`. Read as a state transition, a network outage would suspend every partner, and each would need a named decision to come back: denial of service by blocking status.
  - **Fix:** the outage caps evaluation at `none` without changing state; evaluation recovers by itself when status returns.
- **H4. Registry status and the local ladder are not reconciled.** If a registry moves a partner back to VALID, the spec does not say whether the relying party's state follows.
  - **Fix:** registry status is input. A downward change applies at once. An upward change needs the relying party's decider, or a standing decision recorded in its policy that names who authorised it, limited to restorations up to `watch`.
- **H5. No reference evaluator.** No code computes bands. The `evaluation` blocks in the examples are asserted, not derived, so two implementers may differ undetected.
  - **Fix:** add `tools/evaluate.py` and check that every example's evaluation equals the computed one.

### Medium
- **M1. Undefined trust-anchor ceiling.** 6.1 caps by the anchor ceiling "where the profile defines one", and profile 8.1 defines none.
  - **Fix:** remove it from 0.1, or define it in 8.1.
- **M2. The situation level in an acceptance is not checked** against the policy's levels.
  - **Fix:** a checker rule.
- **M3. No versioning rule.** The schemas pin `"ftef": "0.1"`, so a 0.1.1 fix has no defined effect.
  - **Fix:** a versioning section: MAJOR.MINOR in documents, patches never change validation.
- **M4. `trust_mark_type` URL does not resolve.**
  - **Fix:** serve a page at that path.
- **M5. Weak typing.** `reduced-lease` carries its factor as a string, and `data-ceiling` uses relying-party-local labels.
  - **Fix:** a numeric factor; state that labels are local.
- **M6. `shares` is free text,** so common mode is not interoperable.
  - **Fix:** a small vocabulary plus URIs.

### Low
- **L1.** No `TRADEMARK.md`, no `CITATION.cff`.
- **L2.** Workflows have no `timeout-minutes`.
- **L3.** Annex D promises normative exchange in 0.2 without an issue to track it.

## Independent review
A second reviewer, without the author's reasoning, read the repository adversarially and ran the checker. It
confirmed C1, H1, H3 to H5 and M1 to M3, and found:

| ID | Severity | Finding |
|---|---|---|
| R-C1 | critical | `joining` was ranked most trusted, so admission counted as a move down and needed no decision |
| R-C2 | critical | bindings were credited on the producer's word; `high` could rest on a label |
| R-C3 | critical | a verifier run by the partner earned `high`; the valid example did exactly that |
| R-H2 | high | a `coversUntil` in the future bought freshness |
| R-H5 | high | expiry of an input was not a re-evaluation trigger |
| R-H6 | high | the OpenID Federation status endpoint answers `active` for watch, restricted and suspended |
| R-H7 | high | trust marks could be self-issued, and the registry need not be recognised by the trust anchor |
| R-H8 | high | a partner record could not be built from a trust mark (no `id`, no `issuer`) |
| R-M2 | medium | the common-mode rule never applied in 0.1 |
| R-M4 | medium | acceptances could be chained indefinitely, even with no evidence |
| R-M6 | medium | the profile example was stale at issuance |
| R-M7 | medium | the published schemas changed with every merge while the page promised they would not |
| R-M8 | medium | the checker did not recompute evaluations, nor check that invalid examples fail for their reason |
| R-M9 | medium | governance files unfilled: notices contact, maintainer designation, licence map gaps |
| R-L1 to R-L9 | low | third-party PDF host for ADatP-4774; jargon in decision 0001; dead `signed-transparent` route to `high`; rewritable release tags; DCO not tied to the author; no `ttl` rule; and others |

## Consolidated fixes
| Area | Change |
|---|---|
| States | trust order `member > watch > restricted > suspended > joining > withdrawn > exited`; admission and re-admission are decided moves up; `upTo` must name a higher state; `restricted` has its own limits; the policy names down triggers and standing decisions |
| Evidence | producers state `covers`, the relying party sets `scope`; bindings are verified before they count; a partner-controlled verifier is first party; period ordering is required; long-stale or future-dated evidence counts as none; only verified `hardware-rooted` evidence reaches `high` |
| Acceptance | at most `maxDays`; needs evidence; no chaining without new evidence; lapses on its end, on a higher situation level and on any move down, recorded with `lapsedAt`; pauses only while status is unreachable |
| Status | an outage caps the band at `none` without a state change; registry status is input to the local ladder; registries must include `ttl`; the OIDF endpoint never answers `active` below member; self-issued marks forbidden; the issuer must be listed by the trust anchor |
| Re-evaluation | also no later than the earliest expiry among the inputs |
| Profile 8.1 | summaries carry `id`, `issuer`, `covers`, period bounds, `reference` and `digest`, and the receipt where needed; `scope` is never shared; marks with short-lived evidence are reissued within its freshness |
| Versions | section 7.4; schemas published only from release tags; the pre-draft is marked as mutable |
| Checker | `tools/evaluate.py` recomputes every recorded evaluation; invalid examples must fail for their stated reason; 23 examples and 8 rule cases |
| Repository | `MAINTAINERS.md`, `TRADEMARK.md`, `CITATION.cff`; licence map and REUSE complete; DCO sign-off must match the commit author; workflow timeouts; release tags immutable; AI assistance disclosed, sign-off only by a person |
| History | squashed before the first push, signed off by the maintainer personally (C1) |

## Open (maintainer decisions)
- Code of Conduct contacts in `03-notices.md`: the licence asks for named individuals, ideally two.
- Confirm that no employer or IP-assignment agreement covers the patent commitment the maintainer makes as first contributor under the Community Specification License.
- The schema domain is under `vdhome.be`, chosen deliberately. A neutral domain can be added later with redirects; `$id` values stay as published.
- ADatP-4774 is cited from a public third-party copy, chosen deliberately. No official public copy was found.
