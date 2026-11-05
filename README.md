# Circuit Shift

A circuit tile rotation puzzle built with Python 3.14 and FastAPI. Turn wire tiles
to connect a source to every lamp within a move budget. The domain stays separate
from HTTP validation and persistence.

**Current stage: M1 scaffold.** The health API and architecture checks work.
Puzzle rules, storage and a playable browser screen are planned, not implemented.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```sh
make sync
make check
make serve
```

Visit http://localhost:8000/health for the status response. The root is currently
404. Automatic documentation UIs are disabled to avoid loading remote assets;
/openapi.json remains available. The server binds to localhost only.

`make test` runs the unit suite. `make check` also runs Ruff, strict mypy and
Import Linter. Both keep native JUnit and summary.json in ignored test-results
folders. A new run preserves previous results, including failures and timeouts.

## Structure and next steps

See [domain language and boundaries](docs/domain.md) and
[M1 requirements](docs/requirements.md). The src/circuit_shift package contains
domain, application, infrastructure and presentation layers; composition wires
adapters. Core and storage packages are empty until their own milestones.

- M1: vocabulary, boundaries, health API and checks (this version).
- [M2](https://github.com/TM-59/circuit-shift/issues/2): Board aggregate, tile values,
  rotation, connectivity and events; domain tests.
- [M3](https://github.com/TM-59/circuit-shift/issues/3): start/rotate/read use cases,
  repository port and SQLite transactions.
- [M4](https://github.com/TM-59/circuit-shift/issues/4): one browser screen to rotate
  tiles, see powered lamps and restart a board.

No deployment, external artwork or database is included in M1. Gameplay, usability
and cross-platform behavior remain unverified. WASM is a later optional experiment.
