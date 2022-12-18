from enum import Enum

from src.input_util import get_input

EXAMPLE_PART_1 = """R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
"""

EXAMPLE_PART_2 = """R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""


class Direction(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'


Position = tuple[int, int]


def move(head: Position, direction: Direction) -> Position:
    match direction:
        case Direction.UP:
            return head[0] + 1, head[1]
        case Direction.DOWN:
            return head[0] - 1, head[1]
        case Direction.LEFT:
            return head[0], head[1] - 1
        case Direction.RIGHT:
            return head[0], head[1] + 1
        case _:
            raise ValueError()


def update_tail(head: Position, tail: Position) -> Position:
    if abs(head[0] - tail[0]) < 2 and abs(head[1] - tail[1]) < 2:
        # No need to move
        return tail
    for direction in Direction:
        # Head is on the same line, 2 tiles away
        if move(move(tail, direction), direction) == head:
            return move(tail, direction)
    if head[0] > tail[0] and head[1] > tail[1]:
        # Head is upper right
        return tail[0] + 1, tail[1] + 1
    elif head[0] > tail[0] and head[1] < tail[1]:
        # Head is lower right
        return tail[0] + 1, tail[1] - 1
    elif head[0] < tail[0] and head[1] > tail[1]:
        # Head is upper left
        return tail[0] - 1, tail[1] + 1
    elif head[0] < tail[0] and head[1] < tail[1]:
        # Head is lower left
        return tail[0] - 1, tail[1] - 1
    else:
        raise Exception()


def execute_move_simple(head: Position, tail: Position, direction: Direction) -> tuple[Position, Position]:
    head = move(head, direction)
    tail = update_tail(head, tail)
    return head, tail


def execute_move_long_rope(knots: list[Position], direction: Direction) -> list[Position]:
    knots[0] = move(knots[0], direction)
    for i in range(1, len(knots)):
        knots[i] = update_tail(knots[i - 1], knots[i])
    return knots


def part1(input_data: str):
    head, tail = (0, 0), (0, 0)
    visited_positions = {tail}
    for direction_str, times_str in [line.split(' ') for line in input_data.split('\n') if line]:
        for _ in range(int(times_str)):
            head, tail = execute_move_simple(head, tail, Direction(direction_str))
            visited_positions.add(tail)
    return len(visited_positions)


def part2(input_data: str):
    knots = [(0, 0)] * 10
    visited_positions = {knots[-1]}
    for direction_str, times_str in [line.split(' ') for line in input_data.split('\n') if line]:
        for _ in range(int(times_str)):
            knots = execute_move_long_rope(knots, Direction(direction_str))
            visited_positions.add(knots[-1])
    return len(visited_positions)


if __name__ == '__main__':
    assert part1(EXAMPLE_PART_1) == 13
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE_PART_1) == 1
    assert part2(EXAMPLE_PART_2) == 36
    print(f'Solution for part 2 is: {part2(get_input())}')
