from collections.abc import Callable
from uuid import uuid4

from circuit_shift.application.ports import BoardRecord, BoardRepository
from circuit_shift.domain import Board, Cell, Event, starter_board


class BoardNotFound(LookupError):
    """No board exists with the requested identity."""


class BoardConflict(RuntimeError):
    """The board changed after it was read."""


class StartBoard:
    def __init__(
        self, repository: BoardRepository, board_id_factory: Callable[[], str] | None = None
    ) -> None:
        self._repository = repository
        self._board_id_factory = board_id_factory or (lambda: str(uuid4()))

    def execute(self) -> Board:
        board = starter_board(self._board_id_factory())
        self._repository.add(board)
        return board


class ReadBoard:
    def __init__(self, repository: BoardRepository) -> None:
        self._repository = repository

    def execute(self, board_id: str) -> BoardRecord:
        record = self._repository.get(board_id)
        if record is None:
            raise BoardNotFound(board_id)
        return record


class RotateBoard:
    def __init__(self, repository: BoardRepository) -> None:
        self._repository = repository

    def execute(self, board_id: str, cell: Cell) -> tuple[Event, ...]:
        record = self._repository.get(board_id)
        if record is None:
            raise BoardNotFound(board_id)
        expected_moves = record.board.moves_used
        events = record.board.rotate(cell)
        if not self._repository.save(record.board, events, expected_moves):
            raise BoardConflict(board_id)
        return events
