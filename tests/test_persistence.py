import sqlite3
from pathlib import Path

import pytest

from circuit_shift.application.use_cases import BoardNotFound
from circuit_shift.composition import build_board_use_cases
from circuit_shift.domain import BoardFinished, BoardSolved, BoardState, Cell, TileRotated

pytestmark = pytest.mark.integration


def test_REQ_PERSISTENCE_state_and_ordered_events_survive_reopen(tmp_path: Path) -> None:
    database = tmp_path / "boards.sqlite3"
    first = build_board_use_cases(database)
    board = first.start.execute()
    moves = (Cell(0, 1), Cell(0, 2), Cell(0, 2), Cell(1, 1))
    expected_events = tuple(
        event for cell in moves for event in first.rotate.execute(board.board_id, cell)
    )

    reopened = build_board_use_cases(database)
    stored = reopened.read.execute(board.board_id)
    assert stored.board.state is BoardState.SOLVED
    assert (stored.board.rows, stored.board.cols) == (3, 3)
    assert (stored.board.move_budget, stored.board.moves_used) == (6, 4)
    assert stored.board.tiles[Cell(0, 1)].orientation.quarter_turns == 1
    assert stored.board.tiles[Cell(0, 2)].orientation.quarter_turns == 2
    assert stored.events == expected_events
    assert sum(isinstance(event, BoardSolved) for event in stored.events) == 1
    assert all(isinstance(event, (TileRotated, BoardSolved)) for event in stored.events)


def test_REQ_PERSISTENCE_exhausted_state_survives_reopen(tmp_path: Path) -> None:
    database = tmp_path / "boards.sqlite3"
    first = build_board_use_cases(database)
    board = first.start.execute()
    for _ in range(6):
        first.rotate.execute(board.board_id, Cell(2, 2))

    reopened = build_board_use_cases(database)
    stored = reopened.read.execute(board.board_id)
    assert stored.board.state is BoardState.EXHAUSTED
    assert stored.board.moves_used == stored.board.move_budget == 6
    with pytest.raises(BoardFinished):
        reopened.rotate.execute(board.board_id, Cell(2, 2))
    assert reopened.read.execute(board.board_id) == stored


def test_REQ_ATOMIC_event_failure_rolls_back_board_state(tmp_path: Path) -> None:
    database = tmp_path / "boards.sqlite3"
    use_cases = build_board_use_cases(database)
    board = use_cases.start.execute()
    with sqlite3.connect(database) as connection:
        connection.execute(
            """CREATE TRIGGER reject_board_event BEFORE INSERT ON board_events
               BEGIN SELECT RAISE(ABORT, 'event rejected'); END"""
        )

    with pytest.raises(sqlite3.IntegrityError, match="event rejected"):
        use_cases.rotate.execute(board.board_id, Cell(0, 1))

    reopened = build_board_use_cases(database)
    stored = reopened.read.execute(board.board_id)
    assert stored.board.moves_used == 0
    assert stored.board.tiles[Cell(0, 1)].orientation.quarter_turns == 0
    assert stored.events == ()


def test_REQ_PERSISTENCE_missing_and_invalid_operations_leave_sqlite_unchanged(
    tmp_path: Path,
) -> None:
    use_cases = build_board_use_cases(tmp_path / "boards.sqlite3")
    board = use_cases.start.execute()
    before = use_cases.read.execute(board.board_id)

    with pytest.raises(BoardNotFound):
        use_cases.read.execute("missing")
    with pytest.raises(BoardNotFound):
        use_cases.rotate.execute("missing", Cell(0, 1))
    with pytest.raises(ValueError, match="fixed"):
        use_cases.rotate.execute(board.board_id, Cell(0, 0))

    assert use_cases.read.execute(board.board_id) == before
