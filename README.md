# FTEF: Federated Trust Evidence Framework

**Status: 0.1 pre-draft. Not stable; anything may change.**

FTEF specifies how a relying party in one administrative domain evaluates, records and acts on the security posture of
a federation partner in another domain, on the basis of evidence. Trust between domains is earned by evidence, leased
in time, and cut by events. One contract applies to every partner.

- Specification: [`spec/ftef.md`](spec/ftef.md)
- Schemas (JSON Schema 2020-12): [`schemas/0.1/`](schemas/0.1/), served at `https://ftef.vdhome.be/schema/0.1/`
- Examples (fictional parties only): [`examples/`](examples/), checked by [`tools/check.py`](tools/check.py)
- Decisions: [`decisions/`](decisions/)

## What is normative
- the text of `spec/ftef.md` marked with the key words of BCP 14 (RFC 2119, RFC 8174);
- the schemas under `schemas/`.

Annexes, examples and decisions are informative.

## Licences
| Content | Licence |
|---|---|
| The specification | Community Specification License 1.0 (`01-community-specification-license-v1.md`) |
| Schemas, examples and code | Apache License 2.0 (`LICENSES/Apache-2.0.txt`) |

See [`LICENSE.md`](LICENSE.md) and [`04-license.md`](04-license.md). The repository follows the
[REUSE](https://reuse.software/) specification.

## Contributing
Read [`CONTRIBUTING.md`](CONTRIBUTING.md). In short:
- contributions are accepted under the Community Specification Contributor License Agreement (`00-contributor-license-agreement.md`);
- every commit carries a DCO sign-off (`git commit -s`).

## Security
Report vulnerabilities in the specification or its tooling privately: see [`SECURITY.md`](SECURITY.md).

## Check locally
```
python -m pip install --require-hashes -r tools/requirements.txt
python tools/check.py
reuse lint
```
