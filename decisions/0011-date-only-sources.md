# 0011: Date-only sources start at midnight UTC

- Status: proposed
- Date: 2026-10-23
- Question: many sources of evidence carry a date, not a time (audit reports, certificates). Which instant does a
  relying party record, so that two relying parties compute the same freshness on the same day? (#16)

## Context
- 6.2 measures age between instants: `issuedAt`, `coversFrom` and `coversUntil` are date-times.
- A date has no instant. One implementation stores the start of the day, another the end, a third the time it read
  the report. For classes with a freshness of one day (`self-measured`, `attested`) the band then depends on that
  choice and on the hour at which the relying party evaluates.

## Decision (proposed)
1. A source that states only a date is recorded at the start of that date in UTC (`T00:00:00Z`), in `issuedAt`,
   `coversFrom` and `coversUntil` alike (6.2), and a producer does so (7.1).
2. The start, not the end: the item then ages from the earliest instant of the date in UTC, so it is never fresher
   than any time on that date would make it (uncertainty resolves towards less trust, as conflicts do in 0004).

## Consequences
- Specification: one bullet in 6.2, one clause in 7.1 item 3.
- Schema: unchanged; a date-only value is not distinguishable from a date-time at midnight, and need not be.
- Conformance: two evaluation vectors at the boundary (fresh at exactly one day, stale one second later).
- A source dated in a time zone east of UTC is recorded up to 14 hours later than its local midnight; the rule trades
  that for one answer everywhere. A producer that knows the time of issue records the time, not the date.

## Open questions
- Should a record say that a time was derived from a date (for example `issuedAtPrecision: date`), so that a reader
  can tell midnight from a date? Not needed for the evaluation; possibly useful for audit.
