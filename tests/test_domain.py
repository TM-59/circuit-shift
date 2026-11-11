"""Pure rules of Circuit Routing. No web framework is touched here."""

import copy
from itertools import product

import pytest

from circuit_shift.domain import (
    Board,
    BoardFinished,
    BoardSolved,
    BoardState,
    Cell,
    Connectivity,
    InvalidRotation,
    Orientation,
    Port,
    Role,
    Tile,
    TileRotated,
    starter_board,
    tile,
)

N, E, S, W = Port.NORTH, Port.EAST, Port.SOUTH, Port.WEST


def state_of(board: Board) -> BoardState:
    """Read the state afresh (a plain attribute read would be narrowed by the type checker)."""
    return board.state


def row_board(*tiles: Tile, budget: int = 3) -> Board:
    return Board("row", 1, len(tiles), {Cell(0, i): t for i, t in enumerate(tiles)}, budget)


def test_REQ_TILE_clockwise_and_opposite_ports() -> None:
    assert [N.clockwise, E.clockwise, S.clockwise, W.clockwise] == [E, S, W, N]
    assert [N.opposite, E.opposite, S.opposite, W.opposite] == [S, W, N, E]
    assert Cell(1, 1).towards(N) == (0, 1) and Cell(1, 1).towards(W) == (1, 0)


@pytest.mark.parametrize(
    ("turns", "expected"),
    [(0, {N, E}), (1, {E, S}), (2, {S, W}), (3, {W, N})],
)
def test_REQ_TILE_all_four_orientations(turns: int, expected: set[Port]) -> None:
    assert tile("ne", turns=turns).ports == expected


def test_REQ_TILE_rotation_gives_a_new_value_and_wraps_after_four() -> None:
    corner = tile("ne")
    turned = corner.rotated()
    assert corner.orientation == Orientation(0) and turned.orientation == Orientation(1)
    assert turned.rotated().rotated().rotated() == corner
    with pytest.raises(AttributeError):
        corner.role = Role.LAMP  # type: ignore[misc]
    assert tile("ew").rotated().rotated().ports == tile("ew").ports  # symmetric after two


@pytest.mark.parametrize("bad", [-1, 4, 1.0, "1", None])
def test_REQ_TILE_orientation_is_zero_to_three(bad: object) -> None:
    with pytest.raises(ValueError):
        Orientation(bad)  # type: ignore[arg-type]


def test_REQ_TILE_values_reject_malformed_input() -> None:
    for bad in ((-1, 0), (0, -1), (0.0, 0), ("0", 0)):
        with pytest.raises(ValueError):
            Cell(*bad)
    with pytest.raises(ValueError):
        Tile(frozenset())
    with pytest.raises(TypeError):
        Tile(frozenset({"north"}))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Tile(frozenset({N}), "wire")  # type: ignore[arg-type]


def test_REQ_CONNECT_documented_one_row_example() -> None:
    board = row_board(tile("e", Role.SOURCE), tile("ns"), tile("w", Role.LAMP))
    assert board.powered == {Cell(0, 0)} and board.state is BoardState.ACTIVE
    events = board.rotate(Cell(0, 1))
    assert board.powered == {Cell(0, 0), Cell(0, 1), Cell(0, 2)}
    assert events == (
        TileRotated("row", Cell(0, 1), Orientation(1), 1),
        BoardSolved("row", 1),
    )
    assert state_of(board) is BoardState.SOLVED


def test_REQ_CONNECT_ports_must_be_reciprocal() -> None:
    # a source opening east next to a wire opening east only: not a connection
    board = row_board(tile("e", Role.SOURCE), tile("e"), tile("w", Role.LAMP))
    assert board.powered == {Cell(0, 0)}


def test_REQ_CONNECT_borders_do_not_wrap() -> None:
    # the lamp at the far right opens east, the source at the far left opens west
    board = row_board(tile("w", Role.SOURCE), tile("ew"), tile("e", Role.LAMP))
    assert board.powered == {Cell(0, 0)}
    column = Board(
        "col", 2, 1, {Cell(0, 0): tile("n", Role.SOURCE), Cell(1, 0): tile("s", Role.LAMP)}, 1
    )
    assert column.powered == {Cell(0, 0)}


def test_REQ_CONNECT_cycles_and_dangling_ports_are_allowed() -> None:
    tiles = {
        Cell(0, 0): tile("es", Role.SOURCE),
        Cell(0, 1): tile("sw"),
        Cell(1, 0): tile("ne"),
        Cell(1, 1): tile("nesw"),  # closes the cycle and dangles east and south
        Cell(1, 2): tile("n", Role.LAMP),  # faces north: not connected to the cross
    }
    board = Board("loop", 2, 3, tiles, 2)
    assert board.powered == {Cell(0, 0), Cell(0, 1), Cell(1, 0), Cell(1, 1)}
    assert board.state is BoardState.ACTIVE
    island = {
        Cell(0, 0): tile("e", Role.SOURCE),
        Cell(0, 2): tile("e"),
        Cell(0, 3): tile("w", Role.LAMP),
    }
    assert Connectivity.powered(island) == {Cell(0, 0)}  # a connected pair away from the source


def test_REQ_CONNECT_every_lamp_must_be_reached() -> None:
    board = row_board(
        tile("e", Role.LAMP), tile("ew", Role.SOURCE), tile("ns"), tile("w", Role.LAMP)
    )
    assert board.powered == {Cell(0, 0), Cell(0, 1)} and board.state is BoardState.ACTIVE
    board.rotate(Cell(0, 2))
    assert state_of(board) is BoardState.SOLVED


def test_REQ_BOARD_creation_rejects_malformed_boards() -> None:
    source, lamp, wire = tile("e", Role.SOURCE), tile("w", Role.LAMP), tile("ew")
    good = {Cell(0, 0): source, Cell(0, 1): lamp}
    for kwargs in (
        dict(board_id="", rows=1, cols=2, tiles=good, move_budget=1),
        dict(board_id="b", rows=0, cols=2, tiles=good, move_budget=1),
        dict(board_id="b", rows=1, cols=2, tiles=good, move_budget=0),
        dict(board_id="b", rows=1, cols=2, tiles=good, move_budget=-3),
        dict(board_id="b", rows=1, cols=1, tiles=good, move_budget=1),  # lamp off the board
        dict(
            board_id="b", rows=1, cols=2, tiles={Cell(0, 0): wire, Cell(0, 1): lamp}, move_budget=1
        ),
        dict(
            board_id="b",
            rows=1,
            cols=2,
            tiles={Cell(0, 0): source, Cell(0, 1): source},
            move_budget=1,
        ),
        dict(
            board_id="b",
            rows=1,
            cols=2,
            tiles={Cell(0, 0): source, Cell(0, 1): wire},
            move_budget=1,
        ),
        dict(board_id="b", rows=1, cols=2, tiles=good, move_budget=1, moves_used=2),
    ):
        with pytest.raises(ValueError):
            Board(**kwargs)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Board("b", 1, 2, {(0, 0): source, Cell(0, 1): lamp}, 1)  # type: ignore[dict-item]


def test_REQ_BOARD_a_board_can_start_solved_and_then_rejects_rotation() -> None:
    board = row_board(tile("e", Role.SOURCE), tile("ew"), tile("w", Role.LAMP))
    assert state_of(board) is BoardState.SOLVED
    with pytest.raises(BoardFinished):
        board.rotate(Cell(0, 1))
    assert board.moves_used == 0


def test_REQ_BOARD_symmetric_rotation_still_costs_a_move() -> None:
    board = row_board(tile("e", Role.SOURCE), tile("nesw"), tile("n", Role.LAMP), budget=2)
    (event,) = board.rotate(Cell(0, 1))
    assert isinstance(event, TileRotated) and event.move == 1
    assert board.moves_used == 1 and board.tiles[Cell(0, 1)].ports == {N, E, S, W}


def test_REQ_BOARD_solving_on_the_last_move_wins() -> None:
    board = row_board(tile("e", Role.SOURCE), tile("ns"), tile("w", Role.LAMP), budget=1)
    events = board.rotate(Cell(0, 1))
    assert board.moves_used == board.move_budget
    assert state_of(board) is BoardState.SOLVED and isinstance(events[-1], BoardSolved)


def test_REQ_BOARD_running_out_of_moves_exhausts_and_rejects() -> None:
    board = row_board(tile("e", Role.SOURCE), tile("n"), tile("w", Role.LAMP), budget=2)
    assert len(board.rotate(Cell(0, 1))) == 1  # one event: not solved
    board.rotate(Cell(0, 1))
    assert board.state is BoardState.EXHAUSTED
    before = copy.deepcopy(board)
    with pytest.raises(BoardFinished):
        board.rotate(Cell(0, 1))
    assert board == before


def test_REQ_BOARD_invalid_commands_cost_nothing() -> None:
    board = starter_board()
    before = copy.deepcopy(board)
    for cell in (Cell(0, 0), Cell(1, 2), Cell(2, 0), Cell(5, 5)):  # source, lamps, off the board
        with pytest.raises(InvalidRotation):
            board.rotate(cell)
    sparse = Board(
        "sparse", 1, 3, {Cell(0, 0): tile("e", Role.SOURCE), Cell(0, 2): tile("w", Role.LAMP)}, 2
    )
    with pytest.raises(InvalidRotation):
        sparse.rotate(Cell(0, 1))  # an empty cell
    with pytest.raises(InvalidRotation):
        board.rotate((0, 1))  # type: ignore[arg-type]
    assert board == before and sparse.moves_used == 0


def test_REQ_BOARD_solved_event_only_on_the_first_transition() -> None:
    board = starter_board()
    seen: list[object] = []
    for cell in (Cell(0, 1), Cell(0, 2), Cell(0, 2), Cell(1, 1)):
        seen.extend(board.rotate(cell))
    assert [type(event) for event in seen].count(BoardSolved) == 1
    assert seen[-1] == BoardSolved("starter", 4) and board.state is BoardState.SOLVED
    assert [event.move for event in seen if isinstance(event, TileRotated)] == [1, 2, 3, 4]


def test_REQ_BOARD_starter_needs_four_rotations_found_by_search() -> None:
    board = starter_board()
    assert board.state is BoardState.ACTIVE and board.powered == {Cell(0, 0)}
    assert (board.rows, board.cols, board.move_budget, len(board.lamps)) == (3, 3, 6, 2)
    wires = [cell for cell, t in board.tiles.items() if t.role is Role.WIRE]
    costs = []
    for turns in product(range(4), repeat=len(wires)):
        tiles = dict(board.tiles)
        for cell, count in zip(wires, turns, strict=True):
            for _ in range(count):
                tiles[cell] = tiles[cell].rotated()
        if board.lamps <= Connectivity.powered(tiles):
            costs.append(sum(turns))
    assert min(costs) == 4
    assert sum(cost <= board.move_budget for cost in costs) == 7  # ways to win within the budget
    assert starter_board("other").board_id == "other"


def test_REQ_BOARD_same_commands_give_the_same_board() -> None:
    plays = []
    for _ in range(2):
        board = starter_board()
        for cell in (Cell(2, 2), Cell(0, 1), Cell(1, 0)):
            board.rotate(cell)
        plays.append((board.moves_used, board.state, board.tiles, board.powered))
    assert plays[0] == plays[1]
