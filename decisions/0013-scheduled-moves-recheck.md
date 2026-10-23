# 0013: Scheduled moves re-check their reason when they run

- Status: proposed
- Date: 2026-10-23
- Question: relying parties implement later moves with scheduled jobs in other systems ("move down 30 days after the
  acceptance lapses", "remove the accounts 60 days after the partner left"). What must such a job check when it runs,
  and from when does the move count? (#38)

## Context
- 6.4 requires re-evaluation at the earliest expiry of an input, but says nothing about moves and actions scheduled
  for later.
- One widely used identity provider's scheduled workflow steps re-check the condition written on the job before they
  run, but not the event that started the job (measured on Keycloak 26.8.1). A job started by "the partner left" still
  runs after the partner was readmitted, unless its condition says "still not admitted". Steps also run up to the
  scheduler's interval (twelve hours by default there) after they are due.

## Decision (proposed)
1. A scheduled move or action re-checks, when it runs, that its reason still holds, and does not run when it does not.
   The reason is a condition on the current record and policy, not the event that started the schedule
   (level-triggered, not edge-triggered).
2. An action that cannot be undone carries that condition with it, so every system that runs it checks the same one.
3. A lapse or expiry takes effect at its due time, not when a job runs; a late run never extends trust. The relying
   party bounds how late a scheduled action may run.

## Consequences
- Specification: three bullets in 6.4.
- Schema and checker: unchanged. The evaluation (6.1 to 6.3) is already a function of the record and the time, so a
  lapse applies from its due time whatever a job does; the checker's acceptance cases show this.
- A move up is never scheduled on its own: it needs a decision (6.6), whose `notAfter` already bounds it.

## Open questions
- Should the policy carry the bound on lateness (for example `scheduleMaxDelay`), so a relying party can show it?
