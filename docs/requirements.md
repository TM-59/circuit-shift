# M1 requirements

- REQ-HEALTH: GET /health returns HTTP 200 and typed JSON status ok. The scaffold
  exposes no game root or remote documentation UI. See tests/test_scaffold.py.
- REQ-CORE: domain and application import without site packages. Import Linter
  enforces inward dependencies and independent adapters. See tests/test_scaffold.py
  and pyproject.toml.

The local make test/check commands retain native pytest JUnit, a run-specific
summary and the latest summary under test-results (ignored by Git). Failure or
timeout produces a failing summary; unmeasured coverage remains null with reason.
CI runs only lint, formatting, typing, import contracts and unit tests.

M2 will implement rules and domain tests. M3 will add transactional SQLite and
restart checks. M4 will add the playable browser screen, API and input smoke.
No gameplay bench, performance claims or playable screenshot applies to M1.
