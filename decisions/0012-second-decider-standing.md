# 0012: Independence and standing of the decider

- Status: proposed
- Date: 2026-10-23
- Question: 6.6 voids a decision by the requester. What else makes the decider of a move up or a risk acceptance
  independent of the person who asked for it? (#36)

## Context
- 6.6 compares persons, so a requester cannot decide their own request, but anyone else with the role can: a colleague
  in the same unit, or a peer who approves the requester's moves in return.
- In a relying-party model, "anyone other than the requester" let peers approve each other routinely. The people
  actually trusted as deciders (a security officer, an operator) often hold no other role.

## Decision (proposed)
1. **Standing.** The decider holds a role the policy names for the purpose (already 6.6). Appointments and delegated
   decider power with an end date follow with delegation (#32), in 0.3.
2. **Unit.** Where the relying party records organisational units (`requestedByUnit` on the request, `deciderUnit` on
   the decision, both opaque references), a decider from the requester's own unit does not count.
3. **Reciprocity.** Two people who decided each other's requests within the policy's `reciprocityDays` (RECOMMENDED
   default 30) do not count as each other's decider; the later decision is void. A window of 0 keeps reciprocity as a
   recorded signal only.
4. **No eligible decider.** The move does not happen (6.6), and the relying party SHOULD say so before a request is
   made, naming how a decider can be appointed.
5. **Re-checked.** The rules apply when a decision is evaluated, not only when it is made. A tightening policy change
   SHOULD first list the decisions that would stop counting.

## Consequences
- Schema: optional `deciderUnit` on a decision, optional `requestedByUnit` on a state change and an acceptance;
  optional `deciders.reciprocityDays` in the policy.
- Checker: same-unit and reciprocal decisions within one record are invalid (two invalid examples); the valid accepted
  example records units. Reciprocity across records is the relying party's check.
- Units are opaque references, like decider references (section 10): no names of people or teams.

## Not decided here
- The rule that the holder of the highest authority never counts as a second decider, and independence from a chain of
  delegated decider power: both need delegation (#32) and move to 0.3.
- Whether a different decider role may stand in for a different unit when the relying party records no units.
