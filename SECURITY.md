# Security policy

FTEF is a specification. A security problem here is a flaw that lets a partner, a registry or a third party obtain
more trust than the evidence supports, avoid a downgrade, or harm a partner through a forged downgrade; or a flaw in
the schemas or tooling.

## Reporting
Please report privately through GitHub's private vulnerability reporting: the **Security** tab of this repository,
then **Report a vulnerability**. Do not open a public issue.

We acknowledge reports within 7 days and agree on a disclosure date with the reporter. Fixes to normative text are
published as an erratum or a new version, crediting the reporter unless they ask otherwise.

## Scope
In scope: `spec/`, `schemas/`, `examples/`, `tools/`. Out of scope: implementations by third parties (report to them),
and the security of the specifications FTEF profiles (OpenID Federation, the Token Status List and others).
