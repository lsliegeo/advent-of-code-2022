import itertools
from collections import defaultdict
from typing import Iterator

from src.input_util import get_input
from src.timer_util import ContextTimer

EXAMPLE = """....#..
..###.#
#...#.#
.#...##
#.###..
##.#.##
.#..#.."""


def parse(input_data: str) -> set[tuple[int, int]]:
    positions = set()
    for i, line in enumerate(input_data.split('\n')):
        for j, char in enumerate(line):
            if char == '#':
                positions.add((i, j))
    return positions


def neighbours(x: int, y: int) -> Iterator[tuple[int, int]]:
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i or j:
                yield x + i, y + j


def move(positions: set[tuple[int, int]], x: int, y: int, iteration: int) -> tuple[int, int] | None:
    for direction in range(iteration, iteration + 4):
        if direction % 4 == 0 and (x - 1, y - 1) not in positions and (x - 1, y) not in positions and (x - 1, y + 1) not in positions:
            # Move north
            return x - 1, y
        if direction % 4 == 1 and (x + 1, y - 1) not in positions and (x + 1, y) not in positions and (x + 1, y + 1) not in positions:
            # Move south
            return x + 1, y
        if direction % 4 == 2 and (x - 1, y - 1) not in positions and (x, y - 1) not in positions and (x + 1, y - 1) not in positions:
            # Move west
            return x, y - 1
        if direction % 4 == 3 and (x - 1, y + 1) not in positions and (x, y + 1) not in positions and (x + 1, y + 1) not in positions:
            # Move east
            return x, y + 1
    return None


def simulate(positions: set[tuple[int, int]], iterations: int | None) -> int | None:
    initial_number_positions = len(positions)
    for iteration in itertools.count() if iterations is None else range(iterations):
        moves: dict[tuple[int, int], tuple[int, int]] = {}
        targets: dict[tuple[int, int], int] = defaultdict(int)
        for position in positions:
            if any(n in positions for n in neighbours(*position)) and (target := move(positions, *position, iteration)):
                assert target not in positions
                moves[position] = target
                targets[target] += 1
        if not moves:
            return iteration
        for move_from, move_to in moves.items():
            if targets[move_to] == 1:
                positions.remove(move_from)
                positions.add(move_to)
        assert len(positions) == initial_number_positions
        # print(visualize(positions))
        # print()


def visualize(positions: set[tuple[int, int]]) -> str:
    min_x, max_x, min_y, max_y = min(p[0] for p in positions), max(p[0] for p in positions), min(p[1] for p in positions), max(p[1] for p in positions)
    s = ''
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if (x, y) in positions:
                s += '#'
            else:
                s += '.'
        s += '\n'
    return s[:-1]


def execute_part_1(input_data: str, iterations: int = 10) -> set[tuple[int, int]]:
    positions = parse(input_data)
    simulate(positions, iterations)
    return positions


def part1(input_data: str):
    positions = execute_part_1(input_data)
    # print(visualize(positions))
    min_x, max_x, min_y, max_y = min(p[0] for p in positions), max(p[0] for p in positions), min(p[1] for p in positions), max(p[1] for p in positions)
    return (max_x - min_x + 1) * (max_y - min_y + 1) - len(positions)


def part2(input_data: str):
    positions = parse(input_data)
    return simulate(positions, None) + 1


if __name__ == '__main__':
    assert visualize(execute_part_1(""".....
..##.
..#..
.....
..##.
.....""", 3)) == """..#..
....#
#....
....#
.....
..#.."""
    assert visualize(execute_part_1(EXAMPLE)) == """......#.....
..........#.
.#.#..#.....
.....#......
..#.....#..#
#......##...
....##......
.#........#.
...#.#..#...
............
...#..#..#.."""
    assert part1(EXAMPLE) == 110
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 20
    with ContextTimer():
        print(f'Solution for part 2 is: {part2(get_input())}')  # takes about 7 seconds
