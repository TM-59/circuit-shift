from dataclasses import dataclass
from typing import Protocol

from circuit_shift.domain import Board, Event


@dataclass(frozen=True, slots=True)
class BoardRecord:
    board: Board
    events: tuple[Event, ...]


class BoardRepository(Protocol):
    def add(self, board: Board) -> None: ...

    def get(self, board_id: str) -> BoardRecord | None: ...

    def save(self, board: Board, events: tuple[Event, ...], expected_moves: int) -> bool: ...
