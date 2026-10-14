# 0001: Evidence classes

- Status: accepted (maintainer, 2026-10-14); amended by decision 0002
- Date: 2026-10-14
- Question: are the five ordered classes of the starting model right? The maintainer asked for a red team, gap fill, best practice and prior art, then a reconsolidation to see whether we arrive at five or more. An extension point is wanted either way.

## Starting point
The five classes come from the trust model FTEF started from, ordered with a ceiling and a freshness period each:

| Class | Ceiling | Freshness |
|---|---|---|
| self-asserted | low | 365 days |
| audited | medium | 365 days |
| continuous | medium | 1 day |
| attested | high | 1 day |
| attested-release | high | per access |

## Red team (findings against the starting point)
1. **One ladder mixes independent axes.**
   - "Continuous" indicators are usually produced by the partner itself (first party), yet they sit above a third-party audit.
   - A twelve-month operating-effectiveness audit (SOC 2 Type 2 style) and a point-in-time audit share one class.

   Who asserts, how, and over what period are separate questions.
2. **Attested-release is not evidence about the partner.** It is a control at the relying party: data or keys are released only on attestation at the moment of access. It belongs with enforcement (limits, release conditions), not with evidence classes.
3. **Attestation proves what runs, not what is covered.** A verified policy engine says nothing about paths that bypass it. A ceiling of `high` without a coverage statement overclaims.
4. **Missing sources:**
   - the relying party's own assessment (second party, using contractual audit rights);
   - the relying party's own observation at the seam (probes, outside-in measurement), which needs no cooperation from the partner;
   - a first-party declaration with legal liability (a declaration of conformity), which weighs more than a plain self-assertion.
5. **Scope match is missing.** A certificate whose scope excludes the service at the seam is worth nothing for that seam, whatever its class.
6. **The assessor's standing is missing.** A third-party audit is only as good as the recognition of its assessor (accreditation, mutual recognition).
7. **Transparency is missing.** Evidence recorded in a public append-only log cannot be shown differently to different relying parties; that raises its value.
8. **Freshness is measured from the wrong point.** For evidence covering a period, freshness should run from the end of the period covered, not from the report date.
9. **No corroboration rule.** Two independent pieces of `medium` evidence are stronger than one, unless they share a source (common mode). The starting point takes only the best single class.
10. **Negative evidence is outside the class model.** Incidents, advisories and downgrades are handled by the ladder, but not named as evidence.

## Prior art (2026-10-14)
Every row was checked against a primary source on 2026-10-14, except SOC 2 (secondary only).

| Source | What it grades, and how | Status |
|---|---|---|
| ISO/IEC 17000:2020 [1] | who assesses: first party (provider), second party (user), third party (independent); declaration (ISO/IEC 17050) as first-party attestation | read in the official sample (4.3 to 4.5): first party includes an assessor acting for and controlled by the provider (4.3 Note 2); second party includes an external auditor acting for the user (4.4 Note 2); third party is independent of the provider and has no user interest (4.5). The ISO/IEC 17050 declaration is by title only |
| NIST SP 800-53A r5 [2] | method (examine, interview, test), with depth and coverage (basic, focused, comprehensive) | read in the full text (lines 1091 to 1097) |
| SOC 2 / ISAE 3000 [3] | time basis: Type I (design at a date) or Type II (operation over a period) | secondary source only: AICPA's own pages did not load; the time-basis axis rests on [4] and [5] as well |
| FedRAMP 20x KSI [4] | continuous validation that protections function | read |
| IETF RATS, RFC 9334 [5] | roles (evidence, endorsements, reference values, attestation results); freshness by an epoch compared with a local expiry, with three approaches (section 10) | read |
| EAT, RFC 9711 [6] | the relying party may "trust, not trust, or partially trust" | read |
| AR4SI draft [7] | a trustworthiness *vector* (identity, executables, hardware, configuration ...), not one level | read |
| EU Cybersecurity Act, Art. 52 [8] | scheme levels basic, substantial and high (Art. 52(5) to (7)); an EU statement of conformity refers only to basic (recitals) | read in the official text (EUR-Lex) |
| NIST SP 800-63-4 [9] | separate scales IAL (identity proofing), AAL (authentication), FAL (federation) instead of one level | read |
| SLSA v1.0 build levels [10] | one axis: provenance exists, signed, hardened build | read |
| CRA module A [11] | internal control (module A): the manufacturer "ensures and declares on its sole responsibility" (Annex VIII) | read in the official text (EUR-Lex) |
| SCITT, RFC 9943 [12] | registration "akin to notarization"; an irrevocable, auditable history | read |
| Outside-in observation | no standard grades it | none found |

Single-axis scales (Common Criteria EAL, levels of assurance, SLSA, Art. 52) each grade one property. The mature identity and attestation work (800-63, AR4SI) moved to several axes, because one ladder mixes them. No framework formalises the relying party's own observation as evidence.

## Decision (reconsolidated)
**Evidence is described by axes. Named classes are presets on those axes, and the extension point is a new preset.**

Each evidence item states:

| Axis | Values | Effect |
|---|---|---|
| source | `first-party`, `second-party` (the relying party itself), `third-party`, `verifier` (machine appraisal) | base ceiling |
| assessor | `none`, `accredited`, `mutually-recognised` (third party only) | a third party with no recognised assessor counts as first party |
| time basis | `point-in-time`, `period`, `continuous`, `at-access` | how freshness is measured; for `period`, from the end of the period covered |
| binding | `unsigned`, `signed`, `signed-transparent`, `hardware-rooted` | `high` requires a verified `hardware-rooted` binding (amended by decision 0002) |
| scope | `full`, `partial`, `none` (against the seam) | `partial` is one band lower; `none` gives `none` |
| liability | `none`, `contractual`, `legal` | recorded; it sets recourse, not the ceiling |

Named classes (presets), with their RECOMMENDED ceiling and freshness:

| Class | Axes | Ceiling | Freshness |
|---|---|---|---|
| `self-declared` | first party, declaration | low | 365 days |
| `self-measured` | first party, continuous, signed | medium | 1 day |
| `observed` | second party, measurement at the seam (probes, outside-in) | low | 7 days |
| `assessed-by-relying-party` | second party, examination or test, contractual audit rights | medium | 365 days |
| `independently-assessed` | third party, recognised assessor, point in time or period | medium | 365 days (from end of period) |
| `attested` | verifier, hardware-rooted, continuous or at access | high | 1 day |

Changes from the starting point:
- **`attested-release` leaves the classes.** It becomes a release condition among the limits (6.5): data or keys are released only on attestation at the moment of access.
- **`continuous` becomes `self-measured`,** which names who produces it.
- **`audited` becomes `independently-assessed`,** with the assessor and time basis as attributes.
- **New: `observed`,** which needs no cooperation from the partner.
- **New: `assessed-by-relying-party`,** for second-party audits under contract.

Rules:
- **Scope wins.** Evidence that does not cover the seam counts for nothing.
- **No corroboration lift in 0.1.** Independent items do not add up to a higher band; this is an open question for 0.2.
- **Adverse evidence moves the ladder, not the ceiling.** Incidents, advisories and downgrade events act on the partner's state (5.6).
- **Extension:** a profile may define a class as a combination of axis values. Its ceiling MUST NOT exceed what the axes allow.

So we arrive at **six** classes, not five.

## References
1. ISO/IEC 17000:2020: https://www.iso.org/standard/73029.html
2. NIST SP 800-53A Rev. 5: https://csrc.nist.gov/pubs/sp/800/53/a/r5/final
3. SOC 2 Type I and Type II (secondary): https://compliancedocshq.com/learn/soc-2-type-i-vs-type-ii
4. FedRAMP 20x Key Security Indicators: https://www.fedramp.gov/2026/providers/20x/key-security-indicators/
5. RFC 9334: https://www.rfc-editor.org/rfc/rfc9334.html
6. RFC 9711: https://www.rfc-editor.org/rfc/rfc9711.html
7. draft-ietf-rats-ar4si: https://datatracker.ietf.org/doc/draft-ietf-rats-ar4si/
8. Regulation (EU) 2019/881, Art. 52: https://www.legislation.gov.uk/eur/2019/881/article/52
9. NIST SP 800-63-4: https://csrc.nist.gov/pubs/sp/800/63/4/final
10. SLSA v1.0 levels: https://slsa.dev/spec/v1.0/levels
11. CRA module A (secondary): https://reglyze.com/en/cra/cra-self-assessment-module-a
12. RFC 9943: https://www.rfc-editor.org/info/rfc9943/
13. ISO/IEC 17000:2020 official sample: https://cdn.standards.iteh.ai/samples/73029/85d71fef4e794bba895d06c47a2856c0/ISO-IEC-17000-2020.pdf
14. NIST SP 800-53A Rev. 5 full text: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53Ar5.pdf
15. Regulation (EU) 2019/881: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0881
16. Regulation (EU) 2024/2847 (CRA): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R2847
17. Implementing Regulation (EU) 2015/1502: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32015R1502
18. NIST SP 800-63-4: https://pages.nist.gov/800-63-4/sp800-63.html
