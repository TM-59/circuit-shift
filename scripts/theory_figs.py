"""Regenerates the drawn figures and the measured-values table of docs/theory.

Run with `make theory-figs`. Everything is computed by the domain itself
(src/circuit_shift/domain); nothing here changes it. Standard library only.
"""

from __future__ import annotations

import sys
from collections import Counter, deque
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from circuit_shift.domain import (  # noqa: E402
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

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/theory/figures"
ROWS: list[str] = []
SIZE = 78
END = {Port.NORTH: (0.5, 0.0), Port.EAST: (1.0, 0.5), Port.SOUTH: (0.5, 1.0), Port.WEST: (0.0, 0.5)}


def value(key: str, what: str, measured: float, theory: float) -> None:
    """One row of the table: id | what | measured | theory | error (absolute when theory is 0)."""
    error = abs(measured / theory - 1) if theory else abs(measured - theory)
    ROWS.append(f"| `{key}` | {what} | {measured:.8g} | {theory:.8g} | {error:.2e} |")


def draw(
    tiles: dict[Cell, Tile], rows: int, cols: int, x0: float, y0: float, caption: str
) -> list[str]:
    """One board: wires as lines from the centre to each port; powered tiles in colour."""
    powered = Connectivity.powered(tiles)
    out = [f'<text x="{x0}" y="{y0 - 10}" fill="#222">{caption}</text>']
    for row in range(rows):
        for col in range(cols):
            x, y = x0 + col * SIZE, y0 + row * SIZE
            out.append(
                f'<rect x="{x}" y="{y}" width="{SIZE - 4}" height="{SIZE - 4}" fill="#f4f4f4" stroke="#cccccc"/>'
            )
            cell = Cell(row, col)
            piece = tiles.get(cell)
            if piece is None:
                continue
            colour = "#e6a800" if cell in powered else "#777777"
            cx, cy = x + (SIZE - 4) / 2, y + (SIZE - 4) / 2
            for port in piece.ports:
                ex, ey = END[port]
                out.append(
                    f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{x + ex * (SIZE - 4):.1f}" y2="{y + ey * (SIZE - 4):.1f}" stroke="{colour}" stroke-width="8" stroke-linecap="round"/>'
                )
            if piece.role is Role.SOURCE:
                out.append(
                    f'<rect x="{cx - 13:.1f}" y="{cy - 13:.1f}" width="26" height="26" fill="#1f77b4"/>'
                )
                out.append(
                    f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" fill="#ffffff" font-size="11">S</text>'
                )
            elif piece.role is Role.LAMP:
                fill = "#ffd43b" if cell in powered else "#ffffff"
                out.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="14" fill="{fill}" stroke="#333333" stroke-width="2"/>'
                )
                out.append(
                    f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" fill="#333333" font-size="11">L</text>'
                )
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="{colour}"/>')
    return out


def svg(name: str, width: float, height: float, body: list[str]) -> None:
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" font-family="sans-serif" font-size="12">'
    )
    text = "\n".join(
        [head, f'<rect width="{width:.0f}" height="{height:.0f}" fill="#ffffff"/>', *body, "</svg>"]
    )
    (OUT / name).write_text(text + "\n", encoding="utf-8")


def title(text: str) -> str:
    return f'<text x="16" y="26" font-size="16" font-weight="bold" fill="#222">{text}</text>'


def row_tiles(*pieces: Tile) -> dict[Cell, Tile]:
    return {Cell(0, i): piece for i, piece in enumerate(pieces)}


def bars(name: str, heading: str, labels: list[str], heights: list[int]) -> None:
    width, height, left, top, plot_w, plot_h = 720, 360, 70, 44, 630, 250
    peak = (max(heights) or 1) * 1.1
    step = plot_w / len(heights)
    out = [title(heading)]
    for i, (text, h) in enumerate(zip(labels, heights, strict=True)):
        bar_h = h / peak * plot_h
        x = left + i * step + step * 0.15
        out.append(
            f'<rect x="{x:.1f}" y="{top + plot_h - bar_h:.1f}" width="{step * 0.7:.1f}" height="{bar_h:.1f}" fill="#1f77b4"/>'
        )
        middle = left + i * step + step / 2
        out.append(
            f'<text x="{middle:.1f}" y="{top + plot_h - bar_h - 4:.1f}" text-anchor="middle" fill="#222">{h}</text>'
        )
        out.append(
            f'<text x="{middle:.1f}" y="{top + plot_h + 18}" text-anchor="middle" fill="#444">{text}</text>'
        )
    out.append(
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="none" stroke="#888"/>'
    )
    svg(name, width, height, out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # S02: the four orientations of a corner, a bar and a T
    body = [title("Clockwise quarter-turns: orientation 0, 1, 2, 3")]
    for r, (shape, name) in enumerate((("ne", "corner"), ("ns", "bar"), ("nes", "T"))):
        for turns in range(4):
            piece = tile(shape, turns=turns)
            ports = " ".join(sorted(port.value[0] for port in piece.ports))
            body += draw(
                {Cell(0, 0): piece},
                1,
                1,
                30 + turns * 150,
                70 + r * 120,
                f"{name}, {turns}: {ports}",
            )
    svg("orientations.svg", 640, 420, body)
    corner = tile("ne")
    value(
        "turn-cycle",
        "a tile after four quarter-turns equals the tile it started as (1 = equal)",
        corner.rotated().rotated().rotated().rotated() == corner,
        1,
    )
    value(
        "turn-ports",
        "ports of a north-east corner after one turn are east and south (1 = yes)",
        tile("ne", turns=1).ports == {Port.EAST, Port.SOUTH},
        1,
    )
    shapes: Counter[str] = Counter()
    for letters in ("n", "ne", "ns", "nes", "nesw"):
        shapes[letters] = len({tile(letters, turns=k).ports for k in range(4)})
    value(
        "turn-distinct-corner",
        "different port sets among the four orientations of a corner (theory 4)",
        shapes["ne"],
        4,
    )
    value(
        "turn-distinct-bar",
        "the same for a straight bar (theory 2: it repeats after two turns)",
        shapes["ns"],
        2,
    )
    value(
        "turn-distinct-cross",
        "the same for a cross (theory 1: every turn looks the same and still costs a move)",
        shapes["nesw"],
        1,
    )
    refused = 0
    for bad in (-1, 4, 1.0, "1"):
        try:
            Orientation(bad)  # type: ignore[arg-type]
        except ValueError:
            refused += 1
    value(
        "orientation-rejected",
        "of four values outside 0..3 or not whole numbers, how many are refused (theory 4)",
        refused,
        4,
    )

    # S03: connections
    examples = [
        (
            row_tiles(tile("e", Role.SOURCE), tile("ns"), tile("w", Role.LAMP)),
            "the bar faces north-south: lamp dark",
        ),
        (
            row_tiles(tile("e", Role.SOURCE), tile("ew"), tile("w", Role.LAMP)),
            "one turn later: facing ports, lamp lit",
        ),
        (
            row_tiles(tile("e", Role.SOURCE), tile("e"), tile("w", Role.LAMP)),
            "the wire has no west port: not a connection",
        ),
        (
            row_tiles(tile("w", Role.SOURCE), tile("ew"), tile("e", Role.LAMP)),
            "ports pointing off the board connect nothing",
        ),
    ]
    body = [title("A connection needs facing ports on both tiles")]
    lit = []
    for i, (tiles, caption) in enumerate(examples):
        body += draw(tiles, 1, 3, 30 + (i % 2) * 330, 70 + (i // 2) * 130, caption)
        lit.append(Cell(0, 2) in Connectivity.powered(tiles))
    svg("connections.svg", 700, 320, body)
    value(
        "connect-example-dark",
        "lamp powered in the documented one-row example before the turn (theory 0)",
        lit[0],
        0,
    )
    value("connect-example-lit", "lamp powered after one turn of the bar (theory 1)", lit[1], 1)
    value(
        "connect-one-sided",
        "lamp powered when the middle wire has no port towards the source (theory 0)",
        lit[2],
        0,
    )
    value(
        "connect-no-wrap",
        "lamp powered when source and lamp point off opposite ends of the row (theory 0)",
        lit[3],
        0,
    )
    loop = {
        Cell(0, 0): tile("es", Role.SOURCE),
        Cell(0, 1): tile("sw"),
        Cell(1, 0): tile("ne"),
        Cell(1, 1): tile("nesw"),
        Cell(1, 2): tile("n", Role.LAMP),
    }
    island = {
        Cell(0, 0): tile("e", Role.SOURCE),
        Cell(0, 2): tile("e"),
        Cell(0, 3): tile("w", Role.LAMP),
    }
    body = [title("A cycle with dangling ports, and a pair away from the source")]
    body += draw(loop, 2, 3, 30, 70, "a powered loop; the lamp faces north")
    body += draw(island, 1, 4, 340, 70, "lamp joined to a wire, not to the source")
    svg("graph.svg", 700, 250, body)
    value(
        "connect-cycle",
        "tiles powered in the 2 x 3 board with a cycle (theory 4: the loop, not the lamp)",
        len(Connectivity.powered(loop)),
        4,
    )
    value(
        "connect-island",
        "tiles powered when a connected wire-lamp pair is not joined to the source (theory 1: the source only)",
        len(Connectivity.powered(island)),
        1,
    )

    # S04, S06: the starter board
    board = starter_board()
    wires = [cell for cell, piece in board.tiles.items() if piece.role is Role.WIRE]
    body = [title("The starter board before and after its four rotations")]
    body += draw(board.tiles, 3, 3, 30, 70, "start: only the source is powered")
    solved = starter_board()
    events: list[object] = []
    for cell in (Cell(0, 1), Cell(0, 2), Cell(0, 2), Cell(1, 1)):
        events.extend(solved.rotate(cell))
    body += draw(solved.tiles, 3, 3, 330, 70, "after 4 of 6 moves: both lamps powered")
    svg("starter.svg", 600, 330, body)
    value(
        "starter-wires",
        "wire tiles on the starter board (the rest: one source, two lamps)",
        len(wires),
        6,
    )
    value(
        "starter-powered-start",
        "tiles powered at the start (theory 1: the source alone)",
        len(board.powered),
        1,
    )
    value(
        "starter-solved",
        "state after the four rotations (1 = solved)",
        solved.state is BoardState.SOLVED,
        1,
    )
    value(
        "starter-events",
        "events those four rotations returned (theory 5: four TileRotated and one BoardSolved)",
        len(events),
        5,
    )
    value(
        "starter-solved-events",
        "of them, BoardSolved events (theory 1: only on the first transition)",
        sum(isinstance(e, BoardSolved) for e in events),
        1,
    )
    value(
        "starter-moves",
        "move numbers carried by the TileRotated events run 1..4 (1 = yes)",
        [e.move for e in events if isinstance(e, TileRotated)] == [1, 2, 3, 4],
        1,
    )

    # every combination of orientations: which solve it, and at what cost
    cost: Counter[int] = Counter()
    combos = 0
    for combo in product(range(4), repeat=len(wires)):
        combos += 1
        tiles = dict(board.tiles)
        for cell, count in zip(wires, combo, strict=True):
            for _ in range(count):
                tiles[cell] = tiles[cell].rotated()
        if board.lamps <= Connectivity.powered(tiles):
            cost[sum(combo)] += 1
    value(
        "starter-combos",
        "combinations of orientations of the six wires, enumerated (theory 4^6)",
        combos,
        4**6,
    )
    value("starter-solutions", "of them, combinations that power both lamps", sum(cost.values()), 0)
    value("starter-minimum", "fewest rotations among them (the budget is 6)", min(cost), 0)
    value(
        "starter-within-budget",
        "combinations reachable within the budget of six rotations",
        sum(n for k, n in cost.items() if k <= board.move_budget),
        0,
    )
    ks = list(range(min(cost), max(cost) + 1))
    bars(
        "solutions.svg",
        "Starter board: solving combinations by number of rotations (budget 6)",
        [str(k) for k in ks],
        [cost.get(k, 0) for k in ks],
    )

    # breadth-first search over play itself: the shortest sequence of legal rotations
    start = starter_board()
    seen = {
        tuple(sorted((c.row, c.col, t.orientation.quarter_turns) for c, t in start.tiles.items()))
    }
    queue: deque[tuple[tuple[Cell, ...], int]] = deque([((), 0)])
    shortest = -1
    while queue and shortest < 0:
        path, depth = queue.popleft()
        for cell in wires:
            trial = starter_board()
            for step in path:
                trial.rotate(step)
            if trial.state is not BoardState.ACTIVE:
                continue
            result = trial.rotate(cell)
            if any(isinstance(e, BoardSolved) for e in result):
                shortest = depth + 1
                break
            key = tuple(
                sorted((c.row, c.col, t.orientation.quarter_turns) for c, t in trial.tiles.items())
            )
            if key not in seen and depth + 1 < trial.move_budget:
                seen.add(key)
                queue.append(((*path, cell), depth + 1))
    value(
        "starter-shortest-play",
        "shortest sequence of legal rotations that solves the board, by breadth-first search through the aggregate (the same as the minimum above)",
        shortest,
        min(cost),
    )

    # S05: budget and terminal states
    last = Board(
        "last", 1, 3, row_tiles(tile("e", Role.SOURCE), tile("ns"), tile("w", Role.LAMP)), 1
    )
    result = last.rotate(Cell(0, 1))
    value(
        "last-move-wins",
        "state when the only move of a budget of one solves the board (1 = solved, not exhausted)",
        last.state is BoardState.SOLVED and isinstance(result[-1], BoardSolved),
        1,
    )
    spent = Board(
        "spent", 1, 3, row_tiles(tile("e", Role.SOURCE), tile("n"), tile("w", Role.LAMP)), 2
    )
    spent.rotate(Cell(0, 1))
    spent.rotate(Cell(0, 1))
    value(
        "budget-exhausts",
        "state after two unsolving moves of a budget of two (1 = exhausted)",
        spent.state is BoardState.EXHAUSTED,
        1,
    )
    try:
        spent.rotate(Cell(0, 1))
        kept = 0
    except BoardFinished:
        kept = 1
    value(
        "terminal-refuses",
        "a rotation on an exhausted board raises BoardFinished (theory 1)",
        kept,
        1,
    )
    value(
        "terminal-moves",
        "moves used after that refusal (theory 2: nothing was added)",
        spent.moves_used,
        2,
    )
    fresh = starter_board()
    refused = 0
    for cell in (Cell(0, 0), Cell(1, 2), Cell(2, 0), Cell(7, 7)):
        try:
            fresh.rotate(cell)
        except InvalidRotation:
            refused += 1
    value(
        "invalid-refused",
        "rotations of the source, the two lamps and a cell off the board that are refused (theory 4)",
        refused,
        4,
    )
    value("invalid-free", "moves used after those four refusals (theory 0)", fresh.moves_used, 0)
    malformed = 0
    source, lamp, wire = tile("e", Role.SOURCE), tile("w", Role.LAMP), tile("ew")
    for tiles, budget in (
        ({Cell(0, 0): wire, Cell(0, 1): lamp}, 1),
        ({Cell(0, 0): source, Cell(0, 1): source}, 1),
        ({Cell(0, 0): source, Cell(0, 1): wire}, 1),
        ({Cell(0, 0): source, Cell(0, 1): lamp}, 0),
        ({Cell(0, 0): source, Cell(0, 5): lamp}, 1),
    ):
        try:
            Board("bad", 1, 2, tiles, budget)
        except ValueError:
            malformed += 1
    value(
        "board-rejected",
        "malformed boards refused: no source, two sources, no lamp, zero budget, a tile off the board (theory 5)",
        malformed,
        5,
    )

    lines = [
        "# Measured values",
        "",
        "Written by `make theory-figs` (scripts/theory_figs.py) from the domain itself. Do not edit by hand.",
        "The last column is the relative error; where the theory column is 0 it is the absolute value.",
        "",
        "| id | what is measured | measured | theory | error |",
        "|---|---|---|---|---|",
        *ROWS,
    ]
    (OUT / "values.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
