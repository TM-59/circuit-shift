from copy import deepcopy

import pytest

from circuit_shift.application.ports import BoardRecord, BoardRepository
from circuit_shift.application.use_cases import (
    BoardConflict,
    BoardNotFound,
    ReadBoard,
    RotateBoard,
    StartBoard,
)
from circuit_shift.domain import Board, Cell, Event, TileRotated


class MemoryBoardRepository:
    def __init__(self) -> None:
        self.records: dict[str, BoardRecord] = {}
        self.conflict = False

    def add(self, board: Board) -> None:
        self.records[board.board_id] = BoardRecord(deepcopy(board), ())

    def get(self, board_id: str) -> BoardRecord | None:
        record = self.records.get(board_id)
        return deepcopy(record) if record is not None else None

    def save(self, board: Board, events: tuple[Event, ...], expected_moves: int) -> bool:
        record = self.records[board.board_id]
        if self.conflict or record.board.moves_used != expected_moves:
            return False
        self.records[board.board_id] = BoardRecord(deepcopy(board), (*record.events, *events))
        return True


def test_REQ_USECASE_start_read_and_rotate_preserve_event_history() -> None:
    repository: BoardRepository = MemoryBoardRepository()
    board = StartBoard(repository, lambda: "board-1").execute()
    rotation = RotateBoard(repository).execute(board.board_id, Cell(0, 1))

    stored = ReadBoard(repository).execute(board.board_id)
    assert stored.board.board_id == "board-1"
    assert stored.board.moves_used == 1
    assert stored.board.tiles[Cell(0, 1)].orientation.quarter_turns == 1
    assert stored.events == rotation
    assert isinstance(stored.events[0], TileRotated)


def test_REQ_USECASE_unknown_board_and_invalid_rotation_do_not_save() -> None:
    repository = MemoryBoardRepository()
    board = StartBoard(repository, lambda: "board-1").execute()
    rotate = RotateBoard(repository)

    with pytest.raises(BoardNotFound):
        rotate.execute("missing", Cell(0, 1))
    with pytest.raises(BoardNotFound):
        ReadBoard(repository).execute("missing")
    with pytest.raises(ValueError, match="fixed"):
        rotate.execute(board.board_id, Cell(0, 0))

    stored = ReadBoard(repository).execute(board.board_id)
    assert stored.board.moves_used == 0
    assert stored.events == ()


def test_REQ_USECASE_stale_write_is_reported_as_a_conflict() -> None:
    repository = MemoryBoardRepository()
    board = StartBoard(repository, lambda: "board-1").execute()
    repository.conflict = True

    with pytest.raises(BoardConflict):
        RotateBoard(repository).execute(board.board_id, Cell(0, 1))

    stored = ReadBoard(repository).execute(board.board_id)
    assert stored.board.moves_used == 0
    assert stored.events == ()
