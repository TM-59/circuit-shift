# Requirements

- REQ-HEALTH: GET /health returns HTTP 200 and typed JSON status ok. The scaffold
  exposes no game root or remote documentation UI. See tests/test_scaffold.py.
- REQ-CORE: domain and application import without site packages. Import Linter
  enforces inward dependencies and independent adapters. See tests/test_scaffold.py
  and pyproject.toml.
- REQ-USECASE: start, read and rotate are application use cases behind a repository
  port. Unknown boards and stale writes fail explicitly; invalid domain operations
  do not persist changes. See tests/test_application.py.
- REQ-PERSISTENCE: SQLite restores board identity, layout, orientations, move budget,
  moves used, derived state and ordered domain-event history after connections close
  and reopen. See tests/test_persistence.py.
- REQ-ATOMIC: a failed event write rolls back the board snapshot and leaves event
  history unchanged. See tests/test_persistence.py.

The local make test/check commands retain native pytest JUnit, a run-specific
summary and the latest summary under test-results (ignored by Git). Failure or
timeout produces a failing summary; unmeasured coverage remains null with reason.
`make test` runs unit tests; `make check` also runs SQLite integration tests. CI runs
lint, formatting, typing, import contracts and both test suites.

M2, the pure domain (standard library only; see tests/test_domain.py):

- REQ-TILE: ports turn clockwise through four orientations; tiles, cells and
  orientations are immutable values that reject malformed input.
- REQ-CONNECT: a connection needs facing ports on both tiles; borders never wrap;
  cycles and dangling ports are allowed; every lamp must be reached from the source.
- REQ-BOARD: exactly one source, at least one lamp, a positive move budget; only
  wires rotate and every rotation costs a move; solving on the last move wins;
  finished boards and invalid commands change nothing; TileRotated and BoardSolved
  are emitted at the documented transitions; the starter board needs four rotations.

M3 adds transactional SQLite and restart checks. M4 will add the playable browser
screen, API and input smoke.
No gameplay bench, performance claims or playable screenshot applies to M1.
