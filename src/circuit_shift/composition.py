import os
from pathlib import Path

from fastapi import FastAPI

from circuit_shift.application.ports import BoardRepository
from circuit_shift.application.use_cases import ReadBoard, RotateBoard, StartBoard
from circuit_shift.infrastructure.repository import SQLiteBoardRepository
from circuit_shift.presentation.health import router


class BoardUseCases:
    def __init__(self, repository: BoardRepository) -> None:
        self.start = StartBoard(repository)
        self.read = ReadBoard(repository)
        self.rotate = RotateBoard(repository)


def build_board_use_cases(path: str | Path | None = None) -> BoardUseCases:
    database_path = path or os.environ.get(
        "CIRCUIT_SHIFT_DB_PATH", "test-results/circuit-shift.sqlite3"
    )
    return BoardUseCases(SQLiteBoardRepository(database_path))


def create_app() -> FastAPI:
    app = FastAPI(title="Circuit Shift", docs_url=None, redoc_url=None)
    app.state.board_use_cases = build_board_use_cases()
    app.include_router(router)
    return app
