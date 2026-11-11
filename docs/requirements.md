# Requirements (M1 and M2)

- REQ-HEALTH: GET /health returns HTTP 200 and typed JSON status ok. The scaffold
  exposes no game root or remote documentation UI. See tests/test_scaffold.py.
- REQ-CORE: domain and application import without site packages. Import Linter
  enforces inward dependencies and independent adapters. See tests/test_scaffold.py
  and pyproject.toml.

The local make test/check commands retain native pytest JUnit, a run-specific
summary and the latest summary under test-results (ignored by Git). Failure or
timeout produces a failing summary; unmeasured coverage remains null with reason.
CI runs only lint, formatting, typing, import contracts and unit tests.

M2, the pure domain (standard library only; see tests/test_domain.py):

- REQ-TILE: ports turn clockwise through four orientations; tiles, cells and
  orientations are immutable values that reject malformed input.
- REQ-CONNECT: a connection needs facing ports on both tiles; borders never wrap;
  cycles and dangling ports are allowed; every lamp must be reached from the source.
- REQ-BOARD: exactly one source, at least one lamp, a positive move budget; only
  wires rotate and every rotation costs a move; solving on the last move wins;
  finished boards and invalid commands change nothing; TileRotated and BoardSolved
  are emitted at the documented transitions; the starter board needs four rotations.

M3 will add transactional SQLite and
restart checks. M4 will add the playable browser screen, API and input smoke.
No gameplay bench, performance claims or playable screenshot applies to M1.
