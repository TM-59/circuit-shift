# Circuit Shift contribution rules

- Python 3.14, uv, FastAPI and Pydantic; no arbitrary dependency major caps.
- M1 is vocabulary, package boundaries, health API and verification only.
- The domain uses the standard library and owns all puzzle rules.
- Application owns use cases and repository ports. Infrastructure implements ports.
- Presentation translates HTTP data; composition alone wires concrete adapters.
- Run `make check` locally. Keep generated results, databases and credentials untracked.
- Use one small issue and pull request per purpose. Do not add author signatures.
- CI runs lint, typing, architecture and unit checks on pull requests only.
- No containers, third-party artwork, external model services or deployment.
