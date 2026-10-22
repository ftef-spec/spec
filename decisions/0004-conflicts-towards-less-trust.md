# 0004: Conflicts resolve towards less trust

- Status: proposed
- Date: 2026-10-21
- Question: what does a relying party do when two current evidence items about the same coverage contradict each
  other, when two registries publish different states for one partner, and when a withdrawn item reappears?

## Context
- 6.1 takes the best item. An item showing a required outcome failing has no place in the model, so a favourable
  older item would simply win.
- Two recognised registries disagreeing is undefined.
- A withdrawn evidence item can come back under the same id; nothing forbids reuse.

## Decision (proposed)
1. **Adverse evidence.** An item may state `result` `adverse`. While in play and unresolved, it cancels every item that
   covers the same thing. Only a decision (purpose `resolution`, decision 0003) ends the contradiction. Automatic
   resolution only ever lowers trust; raising it needs a decider (principle 5).
2. **Registries.** If two recognised registries disagree, the lower state applies. Only the issuer of an item, or the
   registry that issued a trust mark, withdraws it for everyone; other parties act locally.
3. **Withdrawal is final.** Evidence ids are never reused. Withdrawn ids are recorded in `withdrawnEvidence`, never
   count again and merge as a union (a two-phase set).

## Consequences
- Schema: `result`, `resolution` on evidence items; `withdrawnEvidence` on the partner record; purpose `resolution`.
- Reference evaluator: `counted()` filters withdrawn ids, adverse items and contradicted coverage before 6.1.
- Checker: three evaluator cases (adverse cancels, resolution restores, withdrawn never counts) and one invalid
  example (a reused withdrawn id).
- "Same coverage" is compared by the `covers` value. Partial overlap needs the corroboration work of 0.2.

## Open questions
- Is "lowest wins on contradiction" compatible with "best item wins" for coverage that only partly overlaps, or should
  the 0.2 corroboration rules replace both?
