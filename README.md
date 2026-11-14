# Circuit Shift

A circuit tile rotation puzzle built with Python 3.14 and FastAPI. Turn wire tiles
to connect a source to every lamp within a move budget. The domain stays separate
from HTTP validation and persistence.

**Current stage: M3, transactional persistence.** The domain rules and events use
the standard library. Start, read and rotate use cases persist board snapshots and
ordered events transactionally in SQLite; the HTTP side is still the health API,
and a playable browser screen is planned.

The rules can be tried from Python without FastAPI:

```sh
PYTHONPATH=src python3 -c "
from circuit_shift.domain import Cell, starter_board
board = starter_board()
for cell in (Cell(0, 1), Cell(0, 2), Cell(0, 2), Cell(1, 1)):
    print(board.rotate(cell))
print(board.state)
"
```

The starter board is 3 x 3 with one source and two lamps; four rotations solve it
and the budget is six.

**Theory handbook**: [docs/theory/](docs/theory/README.md) — 8 statements (the language, clockwise ports,
connections, power as reachability, a valid board, one rotation and its three states, the starter board's
solutions, the dependency rule), each with its rule, assumptions, derivation, code, tests and a figure.
`make theory-figs` regenerates the figures and the measured values; `make theory-check` checks the coverage table.

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

`make test` runs the unit suite. `make check` also runs SQLite integration tests,
Ruff, strict mypy and Import Linter. Both keep native JUnit and summary.json in
ignored test-results folders. A new run preserves previous results, including
failures and timeouts.
The server stores its local database at `test-results/circuit-shift.sqlite3` by
default; set `CIRCUIT_SHIFT_DB_PATH` to use another file.

## Structure and next steps

See [domain language and boundaries](docs/domain.md) and
[requirements](docs/requirements.md). The src/circuit_shift package contains
domain, application, infrastructure and presentation layers; composition wires
the SQLite adapter and health API.

- M1: vocabulary, boundaries, health API and checks.
- [M2](https://github.com/TM-59/circuit-shift/issues/2): Board aggregate, tile values,
  rotation, connectivity and events; domain tests.
- [M3](https://github.com/TM-59/circuit-shift/issues/3): start/rotate/read use cases,
  repository port, transactional SQLite persistence and restart tests (this version).
- [M4](https://github.com/TM-59/circuit-shift/issues/4): one browser screen to rotate
  tiles, see powered lamps and restart a board.

No deployment or external artwork is included. Gameplay, usability and cross-platform
behavior remain unverified. WASM is a later optional experiment.
