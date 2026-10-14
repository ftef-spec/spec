# Scope

This Working Group develops the **Federated Trust Evidence Framework (FTEF)**: how a relying party in one
administrative domain evaluates, records and acts on the security posture of a federation partner in another domain,
on the basis of evidence.

In scope:

1. A data model for partner records:
   - classes of evidence and how long each stays fresh;
   - trust bands;
   - risk acceptances, with their bounds and limits;
   - partner states, their transitions, and their status history.
2. Evaluation rules that derive a partner's trust band from its evidence, its state, time and the relying party's situation level, and that govern transitions between states.
3. Conformance requirements for producers of partner records, for relying parties that evaluate them, and for registries that publish them.
4. Profiles that carry FTEF data over existing specifications, including OpenID Federation trust marks, the IETF Token Status List, DIF Trust Establishment and the ToIP Trust Registry Query Protocol.

Out of scope:
- authentication and identity protocols themselves;
- cryptographic algorithms;
- the internal security controls of any domain;
- the risk assessment methods a domain uses internally;
- transport protocols, except as profiled.

Any changes of Scope are not retroactive.
