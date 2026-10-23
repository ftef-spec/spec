# Federated Trust Evidence Framework (FTEF)

### Version 0.1.0-pre

### Status: Pre-draft

## Contents
- Foreword
- Introduction
- 1 Scope
- 2 Normative references
- 3 Terms and definitions
- 4 Principles
- 5 Data model
- 6 Evaluation
- 7 Conformance
- 8 Profiles
- 9 Security considerations
- 10 Privacy considerations
- Annex A (informative) Lineage
- Annex B (informative) Examples
- Annex C (informative) RECOMMENDED defaults
- Annex D (informative) Posture exchange
- Bibliography

## Foreword
This specification is developed under the Community Specification License 1.0 (see `02-scope.md`, `04-license.md`).

Version 0.1 covers the relying party: the partner record, evaluation, risk acceptance, the partner ladder, and status
carried by profile 8.1. Posture exchange between partners (levels per area, outlook, watch) is informative in 0.1 and
planned as normative for 0.2. FTEF fixes invariants. Numeric values (acceptance length, ceilings, freshness) are the
relying party's policy, with RECOMMENDED defaults.
It began as part of a private platform design at VDHome and is written to be independent of
any product.

## Introduction
Domains federate: people, workloads and data cross from one administrative domain into another. Identity federation
says *who* is on the other side. It does not say whether the other side enforces what the relying party needs, nor
what to do when that changes. Existing work grades evidence (audits, attestation), carries status (trust marks, status
lists) and queries recognition (trust registries). None of it binds a partner's evidence and its changes to what the
partner may do at the relying party's boundary.

FTEF defines that binding: a partner record, the evidence it rests on, the band it earns, the bounded risk acceptance
that may lift it, the states a partner moves through, and the rules a relying party applies.

## 1 Scope
See `02-scope.md`.

## 2 Normative references
- RFC 2119 and RFC 8174 (requirement keywords)
- RFC 3339 (date and time)
- JSON Schema draft 2020-12
- OpenID Federation 1.0 (for profile 8.1)
- IETF Token Status List, draft-ietf-oauth-status-list (for profile 8.1)

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",
"NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119,
RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 3 Terms and definitions
- **Domain:** an administrative domain with its own policy decision and enforcement.
- **Relying party:** the domain that evaluates a partner and decides what the partner may do at its boundary.
- **Partner:** a domain the relying party federates with, whoever operates it.
- **Seam:** the boundary at which a relying party enforces what a partner may do.
- **Evidence:** a dated, attributable statement about a partner's security posture.
- **Evidence class:** the kind of evidence (5.3), with a ceiling and a freshness period.
- **Band:** an ordered trust level: `none` < `low` < `medium` < `high`.
- **Partner record:** what a relying party holds about one partner (5.1).
- **Risk acceptance:** a decision to treat a partner above its evidenced band, with bounds and limits (5.5).
- **Partner state:** a step on the partner ladder (5.6).
- **Situation level:** the relying party's own ordered threat level (for example normal, elevated, high, severe).
- **Common mode:** a dependency that partner and relying party share, so that they fail together.

NOTE: FTEF is not related to "TEF" (Threat Event Frequency) in Open FAIR.

## 4 Principles
1. **One contract.** A relying party applies the same rules to every partner, whoever operates it.
2. **Outcomes, not policy texts.** Partners exchange required outcomes and evidence, never their internal policy text or risk register.
3. **Evidence earns trust.** A partner's band never exceeds what its fresh evidence supports, except through a bounded risk acceptance.
4. **Trust is a lease.** Evidence ages. Trust lapses unless evidence renews it, and events cut it early.
5. **Down fast, up decided.** Lowering trust is automatic and immediate. A partner moves up a state only through a named decision, one step at a time.
6. **Both ways.** Fresher or better evidence, and a lower situation level, raise trust as readily as their opposites lower it, within rule 5.
7. **Common mode counts.** Partners that share a dependency with the relying party do not count as independent.

## 5 Data model
The normative schemas are `schemas/0.1/partner-record.schema.json` and `schemas/0.1/policy.schema.json` (JSON Schema
draft 2020-12). Where this text and a schema disagree, this text applies.

### 5.1 Partner record
A partner record MUST contain:
- the partner and the relying party, each identified by a URI;
- the partner's current state;
- its state history;
- its evidence.

It MAY contain a risk acceptance, the dependencies shared with the relying party (`shares`), recourse terms, and the result of the last evaluation.

### 5.2 Evidence item
An evidence item MUST state:
- its class;
- its axes (5.3);
- its issuer;
- when it was issued;
- what it covers (`covers`): the systems, services or processes the evidence is about.

Evidence ids are unique within a partner record and MUST NOT be reused. A withdrawn item's id is recorded in
`withdrawnEvidence` and never counts again; new evidence takes a new id. Withdrawals merge as a union.

An item MAY state `result` `adverse`: it shows a required outcome failing for what it covers.

Evidence whose time basis is `period` MUST state the period covered (`coversFrom`, `coversUntil`). Evidence bound as `signed-transparent` MUST carry its transparency receipt.

The `scope` axis is the relying party's judgement of how far `covers` reaches across its own seam. A producer cannot know another party's seam, so the relying party MUST set `scope` itself and MUST NOT take it from the producer. Evidence shared by producers and registries carries `covers` and no `scope`.

### 5.3 Evidence axes and classes
Evidence is described by axes:

| Axis | Values |
|---|---|
| source | `first-party`, `second-party` (the relying party itself), `third-party`, `verifier` |
| assessor | `none`, `accredited`, `mutually-recognised` |
| timeBasis | `point-in-time`, `period`, `continuous`, `at-access` |
| binding | `unsigned`, `signed`, `signed-transparent`, `hardware-rooted` |
| scope | `full`, `partial`, `none` (set by the relying party, 5.2) |
| liability | `none`, `contractual`, `legal` |

A class is a named combination of axis values with a maximum ceiling:

| Class | Required axes | Maximum ceiling |
|---|---|---|
| `self-declared` | source `first-party` | low |
| `self-measured` | source `first-party`, timeBasis `continuous`, binding at least `signed` | medium |
| `observed` | source `second-party` (measurement at the seam) | low |
| `assessed-by-relying-party` | source `second-party` (examination or test) | medium |
| `independently-assessed` | source `third-party`, assessor `accredited` or `mutually-recognised` | medium |
| `attested` | source `verifier`, binding `hardware-rooted`, timeBasis `continuous` or `at-access` | high |

The `source` values follow ISO/IEC 17000:2020 (4.3 to 4.5):
- An assessor that acts on behalf of, and is controlled by, the partner is `first-party`. An example is a consultant performing internal audits.
- An external auditor acting on behalf of the relying party is `second-party`.
- `third-party` requires independence from the partner, and no user interest.
- `verifier` is the Verifier role of RFC 9334: it appraises evidence from the partner's components against reference values. It counts as `verifier` only if the relying party's appraisal policy trusts it, and it is operated by the relying party or by a party independent of the partner. A verifier operated or controlled by the partner is `first-party`.

Rules for classes:
- An evidence item MUST satisfy the required axes of its class.
- A relying party's policy MAY set a lower ceiling for a class, and MUST NOT set a higher one.
- A profile MAY define an extension class, identified by a URI, as a combination of axis values. Its ceiling MUST NOT exceed the highest maximum ceiling among the named classes whose required axes it satisfies, or `low` if it satisfies none.

### 5.4 Bands
Bands are ordered `none` < `low` < `medium` < `high`. Profiles MAY map them to other scales, and MUST preserve the order.

### 5.5 Risk acceptance
A risk acceptance MUST state:
- who decided it, and when;
- its end date and the band it grants;
- the reason;
- the situation level at the time of the decision;
- its basis: the evidence items it was decided on;
- its residual risk on the relying party's own scale (the scale and method stay internal, principle 2);
- at least one limit (6.5);
- its decision (6.6), and, where someone asked for it, who asked (`requestedBy`).

The band it grants MUST NOT be `high`.

### 5.6 Partner states
The states, from most to least trusted, are `member`, `watch`, `restricted`, `suspended`, `joining`, `withdrawn` and `exited`. A move towards `exited` in this order is a move down; a move towards `member` is a move up.
- `joining` is a partner not yet admitted. Admission (`joining` to `member`) is a move up.
- `withdrawn` can only move up to `joining`: re-admission starts again.
- `exited` is final.
- A relying party's policy gives `member`, `watch`, `restricted`, `suspended` and `withdrawn` each a cap on the band and a freshness scale. `joining` and `exited` have no band (6.1).
- The policy gives `restricted` its own list of limits, which apply whatever the band (6.5).
- The policy names, for each state except `member` and `exited`, the higher state it moves up to (`upTo`) and the condition for it. It also names the triggers that move a partner down (6.4).

### 5.7 Status and history
Every state change is recorded with its time, its trigger and, for a move up, its decider and its decision (6.6). History is append-only: each entry SHOULD carry the digest of the previous one (`prev`), and the head of the chain SHOULD be witnessed by a party other than the one that writes it. Status is published through a profile (8.1).

## 6 Evaluation
The numeric values are the relying party's policy (`policy.schema.json`). Annex C gives RECOMMENDED defaults. The invariants in this section are normative whatever the values.

### 6.1 Band from evidence
Before an item counts, the relying party MUST verify its binding:
- the signature for `signed`;
- the signature and the transparency receipt for `signed-transparent`;
- a verifier's attestation result for `hardware-rooted`, from a verifier that the relying party's appraisal policy trusts.

An item whose binding cannot be verified is treated as `unsigned`. An item whose class the relying party's policy does not list counts as `none`.

Then, for each item:
1. Take the policy's ceiling for its class.
2. If its scope is `partial`, lower it by one band. If its scope is `none`, the item counts as `none`.
3. If the result is `high` and the verified binding is not `hardware-rooted`, lower it to `medium`.
4. If the item is stale (6.2), lower it by one band. If its age exceeds twice its freshness, or it is dated in the future, the item counts as `none`.

Contradiction resolves towards less trust. An adverse item that is still in play (not older than twice its
freshness, not dated in the future) and has no `resolution` cancels every item that covers the same thing: those items
count as `none` until a decider resolves the contradiction (6.6, purpose `resolution`). An adverse item never raises
the band. Items about different coverage are not in contradiction.

The evidenced band is the highest result over all items, capped by the cap of the partner's state. The partner's band
is therefore never better than the weakest of its state and its best evidence. A partner in `joining` or `exited` has
no band (`none`). In 0.1, independent items do not combine into a higher band.

### 6.2 Freshness
An item is fresh while its age is at most the class freshness, multiplied by the freshness scales of the partner's state and of the current situation level.
- Age runs from `coversUntil` for `period` evidence, and from `issuedAt` otherwise.
- For `period` evidence, `coversFrom` MUST NOT be after `coversUntil`, and `coversUntil` MUST NOT be after `issuedAt`. Otherwise the item counts as `none`, so that a period reaching into the future cannot buy freshness.
- A freshness of 0 means the item counts only at the moment of access.
- A higher situation level MUST NOT lengthen freshness. A lower one restores it at once.
- Clock error only ever narrows trust. With the policy's `clockSkewSeconds`, anything that keeps or raises trust (an
  item being fresh, an acceptance having started and not yet ended) is judged as if the clock were wrong in the unsafe
  direction, and anything that lowers trust (an adverse item being in play, an expiry) as if it were wrong the other
  way.
- Ends are judged on the earlier of the wall clock and the time elapsed since the input was received, measured on a
  monotonic clock. After a detected clock jump, a relying party applies moves down only, until its clock is trusted
  again.

### 6.3 Risk acceptance
- An acceptance MUST NOT run longer than the policy's `acceptance.maxDays`, measured from `decidedAt` to `until`.
- It requires at least one evidence item in the partner record.
- A relying party MUST NOT grant a new acceptance for the same partner within `maxDays` after the previous one ended, unless the partner has presented an evidence item issued after the previous acceptance was decided. Without this, acceptances could be chained indefinitely.

- An acceptance MUST NOT lift the band more than one band above the evidenced band. A partner whose evidence counts as
  `none` can be accepted to `low` at most.
- Acceptances are bounded in aggregate, not only one by one. The policy's `acceptance.budget` limits the number of
  active acceptances (in all and per partner), their summed residual, and the acceptance days per partner within a
  window, so that one risk cannot be split into many small ones. The count survives withdrawal and re-admission: a
  relying party keeps a tombstone of the partner identifier for the length of the window.
- The decider MAY grant less than was requested (an earlier end, a lower band, more limits). The record keeps what was
  requested (`requested`).

An acceptance lifts the band to the least of: its granted band, one band above the evidenced band, the policy's `acceptance.maxBand`, and the cap of the partner's state. It does so only while all of the following hold:
- the current time lies between `decidedAt` and `until`;
- it has not lapsed;
- the partner's status is reachable (8.1).

An acceptance **lapses**:
- when its end date passes;
- when the situation level rises above the one recorded in it;
- on any move down of the partner, including into `watch` or `restricted`;
- when an item of its basis is withdrawn or removed.

Accepted trust does not propagate. A band lifted by an acceptance MUST NOT be used as input to any other trust
computation: passing trust on to others, corroboration, or evidence about a third party. While an acceptance lifts the
band, `no-transit` applies whether or not the acceptance lists it.

When an acceptance lapses, the relying party MUST record `lapsedAt` and `lapseReason`. A lapsed acceptance MUST NOT apply again; a new decision is needed. An acceptance pauses without lapsing only while status is unreachable, and applies again when status returns. The situation level recorded in an acceptance MUST be one of the levels in the relying party's policy. While an acceptance lifts the band, its limits apply.

### 6.4 State transitions
- A move down MUST take effect without human approval when one of its triggers occurs. The policy names the triggers. At a minimum, a registry status lower than the local state (8.1) and a confirmed security incident at the partner are triggers.
- A move up MUST name a decider, and MUST go only to the state the policy names as `upTo` for the current state.
- Registry status (8.1) is input to the relying party's ladder, not a replacement for it:
  - a registry status lower than the local state moves the partner down at once;
  - a registry status higher than the local state moves the partner up only through a named decider;
  - if two recognised registries publish different states for one partner, the lower applies;
  - only the issuer of an evidence item, or the registry that issued a trust mark, withdraws it for every relying
    party. Any other party acts locally, and its signal is advisory input elsewhere.
- A standing decision MAY act as the decider for restorations that follow registry status, up to `watch`. A standing decision is recorded in the policy with its author, date and scope. Moves above `watch` always need an individual decision.
- The relying party MUST re-evaluate the band whenever evidence, state, status or situation level changes. It MUST also re-evaluate no later than the earliest time at which an input expires: an item's freshness, an acceptance's `until`, a trust mark's `exp`, or a status list's `ttl`.

### 6.5 Limits
A limit restricts what a partner may do at the seam.
- `data-ceiling`: the highest data classification it may receive. The value is a label from the relying party's own classification scheme. FTEF does not define labels.
- `no-transit`: it may not pass trust on to others.
- `no-automatic-actions`: its events may not trigger automatic actions.
- `reduced-lease`: its leases are multiplied by the given factor, a number greater than 0 and less than 1.
- `release-on-attestation`: data or keys are released only on attestation at the moment of access.

The limits of an active acceptance apply while it lifts the band. The policy's `restricted` limits apply to a partner in `restricted`, whatever its band.

### 6.6 Decisions
A name proves nothing. Every move up, admission and risk acceptance carries a decision as a signed object, so that it
can be verified, cannot be replayed and cannot be taken by the person who asked for it.
- A decision MUST state the decider's role, an opaque reference to the decider, its purpose (`admission`, `move-up` or
  `acceptance`), the digest of the canonical form (RFC 8785) of the record as decided, a nonce, `notAfter`, and the
  decider's signature over the canonical decision.
- A relying party MUST verify the signature before the decision takes effect. A decision whose signature does not
  verify counts as absent.
- A decision applies only while the record's digest equals `recordDigest` and the current time is before `notAfter`.
  If the record changed after signing, the decision MUST be given again.
- The policy MUST name the decider roles for admission, for risk acceptances and for each state's move up. If no
  eligible decider exists, the move MUST NOT happen.
- A decision by the person who requested the move or the acceptance is void. Rules that need two people compare
  persons, not accounts.
- Decision signatures MUST be separated by purpose from each other and from authentication signatures, so that a
  sign-in can never pass as a decision.
- A change to the relying party's policy that widens (a higher ceiling or cap, a longer freshness or `maxDays`, a
  removed limit or trigger) is itself a decision, by a decider other than the change's author.

### 6.7 Replayable evaluation
State and band are a pure function of the signed records, the policy and the time. A relying party SHOULD record in
each evaluation the digests of the record and the policy it used (`inputs`), so that any party holding them can
recompute the result.

## 7 Conformance
An implementation claims one or more conformance classes. A claim names the FTEF version and the profiles implemented.

### 7.1 Producer
Issues evidence items or partner records. A conformant producer:
1. MUST emit documents that validate against the 0.1 schemas;
2. MUST state the axes of every evidence item truthfully. In particular, it MUST NOT claim `third-party` for an assessor acting on behalf of, and controlled by, the partner (5.3);
3. MUST state the period covered for `period` evidence, and the receipt for `signed-transparent` evidence. It MUST NOT claim `verifier` for a verifier it operates or controls (5.3);
4. MUST NOT include risk registers, internal policy texts or attack paths in evidence it shares (principle 2).

### 7.2 Relying party
Evaluates partner records and enforces the outcome at its seam. A conformant relying party:
1. MUST hold a policy that validates against `policy.schema.json`, with class ceilings no higher than 5.3 allows;
2. MUST compute bands as in 6.1 to 6.3, and MUST re-evaluate when evidence, state, status or situation level changes;
3. MUST apply downward transitions without human approval, and MUST record a named decider and a verified decision for every upward transition and acceptance (6.4, 6.6);
4. MUST apply the limits of an active acceptance and of `restricted` (6.5);
5. SHOULD treat partners that share a dependency (`shares`) with each other or with the relying party as one wherever its own policy requires independent parties. FTEF 0.1 itself defines no such decision; corroboration in 0.2 will;
6. MUST make every active risk acceptance visible to the people accountable for it for as long as it holds, and SHOULD alert on it.

### 7.3 Registry
Publishes partner status for relying parties. A conformant registry:
1. MUST implement profile 8.1;
2. MUST publish a downward state change in its status list within the status list's `ttl`;
3. MUST keep the history of state changes (5.7).

### 7.4 Versions
- FTEF versions are MAJOR.MINOR.PATCH, and documents carry MAJOR.MINOR in `ftef`.
- A PATCH release changes wording only; it never changes what validates.
- A MINOR release before 1.0 may change anything; from 1.0 on, a MINOR release only adds optional fields.
- Schemas are published at `https://ftef.vdhome.be/schema/MAJOR.MINOR/`.
- While a version is a pre-draft, its schemas may change. From its first release, the files under its path never change, and a fix goes into a new version.

### 7.4.1 Record and policy versions
Partner records, policies and the evidence sets of trust marks carry a monotonic `version`. A relying party MUST
refuse a version lower than the highest it has seen for the same partner or policy.
- The relying party SHOULD keep the highest version seen outside the evaluator's own state as well (for example in the
  system that stores its decisions), and use the higher of the two. Losing or resetting the evaluator's state (a
  rebuild, a restored backup, a wiped cache) then cannot let an older, validly signed document apply again.
- Once a relying party has seen a versioned document for a partner or policy, a document for it without a `version`
  counts as lower than any version, and is refused.

A record MAY carry `notAfter`; after it, the record counts as unreachable status (8.1) until a newer version arrives.

## 8 Profiles

### 8.1 OpenID Federation trust marks with the IETF Token Status List (mandatory for registries)
A registry issues, per partner, an OpenID Federation 1.0 Trust Mark (`typ` `trust-mark+jwt`) with:
- `iss`: the registry's Entity Identifier. It MUST differ from `sub`: a partner MUST NOT issue FTEF trust marks about itself. The registry MUST be listed for this trust mark type in the `trust_mark_issuers` of the Trust Anchor the relying party uses;
- `sub`: the partner's Entity Identifier;
- `trust_mark_type`: `https://ftef.vdhome.be/trust-mark/0.1/partner-evidence`;
- `iat`;
- `exp`: REQUIRED in this profile, because trust is a lease;
- `status`: a Token Status List reference (`status_list` with `idx` and `uri`);
- `ftef_evidence`: an array of evidence summaries, one per item. Each summary has:
  - `id`, `issuer`, `class`, `axes` (without `scope`, 5.2), `covers` and `issuedAt`;
  - for `period` evidence, `coversFrom` and `coversUntil`;
  - for any binding other than `unsigned`, `reference` and `digest`, so that the relying party can retrieve the evidence and verify its binding (6.1);
  - for `signed-transparent`, also `receipt`.

  A relying party builds the evidence of its partner record from the summaries and adds its own `scope`.

A trust mark is a snapshot. Its `exp` does not extend the freshness of the evidence in it. For evidence with a short freshness, such as `attested`, the registry SHOULD reissue the trust mark within that freshness, or relying parties SHOULD obtain fresh evidence through `reference`.

The trust mark carries evidence and state, never a band. Each relying party computes its own band under its own policy (6.1).

The partner state is carried in the Status List Token (`typ` `statuslist+jwt`, `bits` 4):

| State | Status value | Meaning in the Token Status List |
|---|---|---|
| `member` | `0x00` | VALID |
| `withdrawn`, `exited` | `0x01` | INVALID |
| `suspended` | `0x02` | SUSPENDED |
| `watch` | `0x0C` | application-specific (FTEF) |
| `restricted` | `0x0D` | application-specific (FTEF) |

`joining` has no trust mark yet.

Rules for status:
- A registry MUST include `ttl` in its Status List Token. A relying party MUST fetch the status list again within its `ttl`.
- If it cannot, it MUST treat the trust mark's evidence as stale (6.1).
- If it still cannot after twice the `ttl`, the status is unreachable: the relying party MUST cap the partner's band at `none` until status is fetched again.

This cap is an evaluation result, not a state transition. When status returns, evaluation recovers without a decision, so blocking status cannot force mass suspensions that need manual recovery.
- The OpenID Federation Trust Mark Status endpoint MAY also be offered, but an FTEF relying party MUST consult the Status List Token, because the endpoint has no value for `watch`, `restricted` or `suspended`. A registry that offers the endpoint MUST NOT answer `active` for a partner in any state other than `member`.
- Status value `0x01` (INVALID) is final for that trust mark. A withdrawn partner that is re-admitted gets a new trust mark with a new status list index.

### 8.2 DIF Trust Establishment topic (optional)
A registry MAY publish partner records as a DIF Trust Establishment document whose topic is the partner-record schema. The entries are keyed by partner identifier.

### 8.3 ToIP Trust Registry Query Protocol (optional)
A registry MAY answer TRQP recognition queries of the form "is partner X recognised in state S under FTEF 0.1". The answer is derived from the profile 8.1 status.

## 9 Security considerations
- **Forged or inflated evidence.** Producers can overstate their axes. A relying party credits a binding only after verifying it (6.1), sets scope itself (5.2), and treats a partner-controlled verifier as first party (5.3). Only verified `hardware-rooted` evidence supports `high`.
- **Assessor capture.** An assessor paid and controlled by the partner is first party (5.3). Relying parties SHOULD check the standing of a claimed accredited or mutually recognised assessor with the accreditation body.
- **Stale or withheld status.** A registry or network that withholds status must not keep a partner trusted. The rules in 8.1 bound this: stale after the `ttl`, and the band capped at `none` after twice the `ttl`, without a state change. Recovery needs no decision, so withholding status cannot force mass suspensions.
- **Equivocation.** A registry could show different status to different relying parties. Status lists give herd privacy but not proof of consistency. Registries SHOULD log trust marks and status list tokens in a transparency service such as SCITT.
- **Downgrade as denial of service.** Because downward transitions are automatic, a forged downgrade event harms a partner.
  - Triggers MUST be authenticated.
  - Event streams (for example SSF and CAEP) SHOULD be advisory input to the relying party's policy, with per-partner allow-lists and rate limits.
  - Upgrades remain decided.
- **Decisions shown one way and signed another.** The screen that asks for a decision can lie about what is signed. Implementations SHOULD render a decision for signing from the canonical record, independently of the requesting application, and SHOULD separate decision signatures from authentication signatures by purpose (6.6).
- **Acceptance abuse.** A risk acceptance can hide weak partners. The invariants bound it: an end date, never `high`, at most one band above the evidence, a budget over all acceptances, void on a downgrade, a higher situation level or a withdrawn basis, at least one limit, no propagation, and visibility under 7.2(6).
- **Common mode.** Partners that share a policy source, release pipeline or operator with the relying party fail together with it. Treating them as one (7.2(5)) prevents false independence.
- **Clock manipulation.** Freshness depends on time. Relying parties MUST use a trustworthy clock, SHOULD reject evidence dated in the future, and apply skew only towards less trust (6.2).
- **Rollback.** Re-serving an older record, policy or trust mark could restore trust that was removed. Monotonic versions and `notAfter` (7.4.1) and a chained history (5.7) bound it.

## 10 Privacy considerations
- **Evidence is about systems, not people.** Producers MUST NOT include personal data in evidence summaries, beyond the contact points in `recourse`.
- **Posture is sensitive.** A partner's state and evidence reveal its weak points.
  - Registries SHOULD limit status endpoints to federation members.
  - The trust mark carries evidence summaries and references, not the evidence itself.
  - Risk registers are never exchanged (principle 2).
- **Status list herd privacy.** Status lists SHOULD be large enough that fetching one does not reveal which partner a relying party is evaluating, as described in the Token Status List's privacy considerations.

## Annex A (informative) Lineage
Each part of FTEF names the public sources it takes from. The reasoning is recorded in `decisions/` in this repository.

| Part | Takes from |
|---|---|
| Evidence axes and classes (5.3) | ISO/IEC 17000 (parties), NIST SP 800-53A (methods), RFC 9334 and AR4SI (verifier, freshness, vectors), SLSA (binding grades), SCITT (transparency), EU Cybersecurity Act Art. 52 and NIST 800-63-4 (graded and multi-axis assurance) |
| Bands (6.1): the best evidence, capped by the state | NIST 800-63-4 (assurance limited by its weakest component, applied here to the state cap) |
| Trust as a lease (principle 4, 6.2) | RFC 9334 (epoch against expiry), OpenID CAEP (events that end trust early) |
| Risk acceptance (6.3) | NIST SP 800-37 (risk accepted explicitly by an authorising official) |
| Conflicts towards less trust (5.2, 6.1, 6.4) | two-phase sets (a removed element never returns), Mozilla Root Store Policy (distrust acts at once, restoration is decided) (decision 0004) |
| Time, versions and rollback (6.2, 6.7, 7.4.1) | The Update Framework (rollback and freeze protection), RFC 9334 (freshness against an epoch) (decision 0005) |
| Acceptance in aggregate (6.3) | NIST SP 800-37 (explicit acceptance), risk budgets in operational risk practice (decision 0006) |
| Decisions (6.6) | RFC 8785 (canonical form), W3C WebAuthn (purpose-bound assertions); prior art in access tools authenticates the approver's click but signs nothing (decision 0003) |
| The ladder (5.6, 6.4) | Paris MoU (tighter re-check for higher risk), Mozilla Root Store Policy (incident, remediation, restriction, removal), IETF Token Status List (reversible suspension), EUCC (suspension distinct from withdrawal) |
| Status (8.1) | OpenID Federation 1.0 (trust marks, trust mark status), IETF Token Status List |
| Equivalence by named profile or owned mapping (0.2) | TISAX, IEC 62443, NIST SP 800-47, ADatP-4774 |
| Common mode (principle 7) | none: FTEF's own |

## Annex B (informative) Examples
Fictional partners only: `examples/valid/` and `examples/invalid/`, checked by `tools/check.py`.

## Annex C (informative) RECOMMENDED defaults
`examples/valid/policy-defaults.json`:
- **Acceptance:** at most 90 days, at most `medium`; a budget of 5 active acceptances, 1 per partner, a summed residual of 40 on the relying party's scale, and 180 acceptance days per partner in 365.
- **Class freshness:** self-declared and both assessed classes 365 days; observed 7 days; self-measured and attested 1 day.
- **State freshness scales:** watch, restricted and suspended 0.5; withdrawn 0.
- **Restricted limits:** no transit, no automatic actions, leases at half length.
- **Down triggers and a standing decision:** listed in the example policy; the standing decision restores to `watch` only after a suspension caused by registry status.
- **Situation levels:** normal 1.0, elevated 0.5, high 0.33, severe 0.2.

## Annex D (informative) Posture exchange (planned normative in 0.2)
A partner may publish a level per area or zone, carrying:
- target, achieved and capability levels;
- an outlook and a watch flag.

The evidence stays with the issuer.

## Bibliography
1. RFC 2119, RFC 8174: https://www.rfc-editor.org/rfc/rfc2119 , https://www.rfc-editor.org/rfc/rfc8174
2. RFC 3339: https://www.rfc-editor.org/rfc/rfc3339
3. JSON Schema draft 2020-12: https://json-schema.org/draft/2020-12/json-schema-core
4. OpenID Federation 1.0: https://openid.net/specs/openid-federation-1_0-final.html
5. IETF Token Status List (draft-ietf-oauth-status-list): https://datatracker.ietf.org/doc/draft-ietf-oauth-status-list/
6. OpenID Shared Signals Framework 1.0 and CAEP 1.0: https://openid.net/specs/openid-sharedsignals-framework-1_0.html , https://openid.net/specs/openid-caep-1_0-final.html
7. ISO/IEC 17000:2020: https://www.iso.org/standard/73029.html
8. NIST SP 800-53A Rev. 5: https://csrc.nist.gov/pubs/sp/800/53/a/r5/final
9. NIST SP 800-37 Rev. 2: https://csrc.nist.gov/pubs/sp/800/37/r2/final
10. NIST SP 800-47 Rev. 1: https://csrc.nist.gov/pubs/sp/800/47/r1/final
11. NIST SP 800-63-4: https://pages.nist.gov/800-63-4/sp800-63.html
12. RFC 9334 (RATS): https://www.rfc-editor.org/rfc/rfc9334
13. RFC 9711 (EAT): https://www.rfc-editor.org/rfc/rfc9711
14. draft-ietf-rats-ar4si: https://datatracker.ietf.org/doc/draft-ietf-rats-ar4si/
15. RFC 9943 (SCITT): https://www.rfc-editor.org/rfc/rfc9943
16. SLSA v1.0: https://slsa.dev/spec/v1.0/levels
17. Regulation (EU) 2019/881 (Cybersecurity Act): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019R0881
18. Regulation (EU) 2024/2847 (Cyber Resilience Act): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R2847
19. Paris MoU inspection regime: https://parismou.org/inspection-regime/
20. Mozilla Root Store Policy: https://www.mozilla.org/en-US/about/governance/policies/security-group/certs/policy/
21. DIF Trust Establishment: https://identity.foundation/trust-establishment/
22. ToIP Trust Registry Query Protocol: https://trustoverip.github.io/tswg-trust-registry-protocol/
23. TISAX: https://enx.com/en-US/TISAX/
24. IEC 62443-3-2: https://webstore.iec.ch/en/publication/30727
25. NATO ADatP-4774 Edition A Version 1 (public copy): https://www.jedi-sec.us/downloads/MISC_PDF/ADatP-4774%20EDA%20V1%20E.pdf
26. Commission Implementing Regulation (EU) 2024/482 (EUCC): https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R0482
