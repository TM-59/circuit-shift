import json
import sqlite3
from pathlib import Path
from typing import cast

from circuit_shift.application.ports import BoardRecord
from circuit_shift.domain import (
    Board,
    BoardSolved,
    Cell,
    Event,
    Orientation,
    Port,
    Role,
    Tile,
    TileRotated,
)

_PORT_CODES = {
    Port.NORTH: "n",
    Port.EAST: "e",
    Port.SOUTH: "s",
    Port.WEST: "w",
}
_CODE_PORTS = {code: port for port, code in _PORT_CODES.items()}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS boards (
    board_id TEXT PRIMARY KEY,
    rows INTEGER NOT NULL,
    cols INTEGER NOT NULL,
    move_budget INTEGER NOT NULL,
    moves_used INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS tiles (
    board_id TEXT NOT NULL REFERENCES boards(board_id) ON DELETE CASCADE,
    row INTEGER NOT NULL,
    col INTEGER NOT NULL,
    role TEXT NOT NULL,
    base_ports TEXT NOT NULL,
    orientation INTEGER NOT NULL,
    PRIMARY KEY (board_id, row, col)
);
CREATE TABLE IF NOT EXISTS board_events (
    board_id TEXT NOT NULL REFERENCES boards(board_id) ON DELETE CASCADE,
    event_number INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (board_id, event_number)
);
"""


class SQLiteBoardRepository:
    """A file-backed repository; each operation opens and closes its own connection."""

    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        if self._path == ":memory:":
            raise ValueError("SQLiteBoardRepository requires a file-backed database")
        Path(self._path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(_SCHEMA)

    def add(self, board: Board) -> None:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """INSERT INTO boards (board_id, rows, cols, move_budget, moves_used)
                   VALUES (?, ?, ?, ?, ?)""",
                (board.board_id, board.rows, board.cols, board.move_budget, board.moves_used),
            )
            self._insert_tiles(connection, board)

    def get(self, board_id: str) -> BoardRecord | None:
        with self._connect() as connection:
            connection.execute("BEGIN")
            row = connection.execute(
                """SELECT board_id, rows, cols, move_budget, moves_used
                   FROM boards WHERE board_id = ?""",
                (board_id,),
            ).fetchone()
            if row is None:
                return None
            tiles = {
                Cell(cast(int, tile_row["row"]), cast(int, tile_row["col"])): self._decode_tile(
                    tile_row
                )
                for tile_row in connection.execute(
                    """SELECT row, col, role, base_ports, orientation
                       FROM tiles WHERE board_id = ? ORDER BY row, col""",
                    (board_id,),
                )
            }
            board = Board(
                cast(str, row["board_id"]),
                cast(int, row["rows"]),
                cast(int, row["cols"]),
                tiles,
                cast(int, row["move_budget"]),
                cast(int, row["moves_used"]),
            )
            events = tuple(
                self._decode_event(cast(str, event["event_type"]), cast(str, event["payload"]))
                for event in connection.execute(
                    """SELECT event_type, payload FROM board_events
                       WHERE board_id = ? ORDER BY event_number""",
                    (board_id,),
                )
            )
            return BoardRecord(board, events)

    def save(self, board: Board, events: tuple[Event, ...], expected_moves: int) -> bool:
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            changed = connection.execute(
                """UPDATE boards SET rows = ?, cols = ?, move_budget = ?, moves_used = ?
                   WHERE board_id = ? AND moves_used = ?""",
                (
                    board.rows,
                    board.cols,
                    board.move_budget,
                    board.moves_used,
                    board.board_id,
                    expected_moves,
                ),
            ).rowcount
            if changed == 0:
                return False
            connection.execute("DELETE FROM tiles WHERE board_id = ?", (board.board_id,))
            self._insert_tiles(connection, board)
            next_number = cast(
                int,
                connection.execute(
                    "SELECT COALESCE(MAX(event_number), 0) + 1 FROM board_events "
                    "WHERE board_id = ?",
                    (board.board_id,),
                ).fetchone()[0],
            )
            for offset, event in enumerate(events):
                event_type, payload = self._encode_event(event)
                connection.execute(
                    """INSERT INTO board_events (board_id, event_number, event_type, payload)
                       VALUES (?, ?, ?, ?)""",
                    (board.board_id, next_number + offset, event_type, payload),
                )
        return True

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _insert_tiles(connection: sqlite3.Connection, board: Board) -> None:
        connection.executemany(
            """INSERT INTO tiles (board_id, row, col, role, base_ports, orientation)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    board.board_id,
                    cell.row,
                    cell.col,
                    tile.role.value,
                    "".join(_PORT_CODES[port] for port in Port if port in tile.base_ports),
                    tile.orientation.quarter_turns,
                )
                for cell, tile in board.tiles.items()
            ],
        )

    @staticmethod
    def _decode_tile(row: sqlite3.Row) -> Tile:
        codes = cast(str, row["base_ports"])
        if any(code not in _CODE_PORTS for code in codes):
            raise ValueError("database contains an unknown port code")
        return Tile(
            frozenset(_CODE_PORTS[code] for code in codes),
            Role(cast(str, row["role"])),
            Orientation(cast(int, row["orientation"])),
        )

    @staticmethod
    def _encode_event(event: Event) -> tuple[str, str]:
        if isinstance(event, TileRotated):
            payload = dict(
                board_id=event.board_id,
                row=event.cell.row,
                col=event.cell.col,
                orientation=event.orientation.quarter_turns,
                move=event.move,
            )
            return "tile_rotated", json.dumps(payload, sort_keys=True)
        payload = dict(board_id=event.board_id, moves_used=event.moves_used)
        return "board_solved", json.dumps(payload, sort_keys=True)

    @staticmethod
    def _decode_event(event_type: str, payload: str) -> Event:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("database contains an invalid event payload")
        if event_type == "tile_rotated":
            return TileRotated(
                str(data["board_id"]),
                Cell(data["row"], data["col"]),
                Orientation(data["orientation"]),
                data["move"],
            )
        if event_type == "board_solved":
            return BoardSolved(str(data["board_id"]), data["moves_used"])
        raise ValueError(f"database contains unknown event type: {event_type}")
