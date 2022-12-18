import dataclasses
import string
from enum import Enum

from src.input_util import get_input

EXAMPLE = """Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi"""

MAX_SCORE = 10 ** 6


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

    def reverse(self) -> 'Direction':
        match self:
            case Direction.UP:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.UP
            case Direction.LEFT:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.LEFT
            case _:
                raise ValueError()

    @property
    def char(self) -> str:
        match self:
            case Direction.UP:
                return '^'
            case Direction.DOWN:
                return 'v'
            case Direction.LEFT:
                return '<'
            case Direction.RIGHT:
                return '>'
            case _:
                raise ValueError()


@dataclasses.dataclass
class Position:
    height: int
    row: int
    column: int
    score: int = MAX_SCORE
    best_direction: Direction | None = None

    def __lt__(self, other: 'Position'):
        return self.score.__lt__(other.score)

    def step(self, direction: Direction) -> tuple[int, int]:
        match direction:
            case Direction.UP:
                return self.row - 1, self.column
            case Direction.DOWN:
                return self.row + 1, self.column
            case Direction.LEFT:
                return self.row, self.column - 1
            case Direction.RIGHT:
                return self.row, self.column + 1
            case _:
                raise ValueError()


@dataclasses.dataclass
class Area:
    positions: list[list[Position]]
    start: tuple[int, int]
    goal: tuple[int, int]
    exploration: list[list[int]] = None

    def is_out_of_bounds(self, row: int, column: int) -> bool:
        return row < 0 or row >= len(self.positions) or column < 0 or column >= len(self.positions[0])

    def get_height(self, position: Position, direction: Direction | None = None) -> int:
        row, column = position.step(direction) if direction else (position.row, position.column)
        if self.is_out_of_bounds(row, column):
            return MAX_SCORE
        return self.positions[row][column].height

    def can_move(self, position: Position, direction: Direction) -> bool:
        return self.get_height(position) + 1 >= self.get_height(position, direction)

    def get_position(self, row: int, column: int) -> Position:
        return self.positions[row][column]

    def step(self, position: Position, direction: Direction) -> Position | None:
        new_position = position.step(direction)
        if self.is_out_of_bounds(*new_position):
            return None
        return self.get_position(*new_position)

    @staticmethod
    def parse(input_data: str) -> 'Area':
        char_to_height = lambda c: string.ascii_lowercase.index(c)
        heights = []
        start = goal = None
        for i, row in enumerate(input_data.split('\n')):
            heights.append([])
            for j, char in enumerate(row):
                if char == 'S':
                    start = i, j
                    height = char_to_height('a')
                elif char == 'E':
                    goal = i, j
                    height = char_to_height('z')
                else:
                    height = char_to_height(char)
                heights[-1].append(Position(height, i, j))
        return Area(heights, start, goal)

    @property
    def image(self) -> str:
        result: list[list[str]] = []
        for row in self.positions:
            result.append([])
            for position in row:
                result[-1] += '.' if position.best_direction is None else position.best_direction.char
        result[self.goal[0]][self.goal[1]] = 'E'
        result[self.start[0]][self.start[1]] = 'S'
        return '\n'.join(''.join(row) for row in result)

    def explore(self):
        self.get_position(self.goal[0], self.goal[1]).score = 0
        positions = [position for row in self.positions for position in row]
        self._explore(positions)

    def _explore(self, to_consider: list[Position]):
        if not to_consider:
            return

        best_score = min(position.score for position in to_consider)
        to_consider_now = [position for position in to_consider if position.score == best_score and position.score != MAX_SCORE]
        to_consider_later = [position for position in to_consider if position.score != best_score]

        for current in to_consider_now:
            for direction in Direction:
                neighbour = self.step(current, direction)
                if neighbour is None or self.is_out_of_bounds(neighbour.row, neighbour.column):
                    continue

                if self.can_move(neighbour, direction.reverse()):
                    if current.score + 1 < neighbour.score:
                        neighbour.score = current.score + 1
                        neighbour.best_direction = direction.reverse()

        return self._explore(to_consider_later)


def part1(input_data: str):
    area = Area.parse(input_data)
    area.explore()
    # print(area.plot)
    return area.get_position(*area.start).score


def part2(input_data: str):
    area = Area.parse(input_data)
    area.explore()
    # print(area.plot)
    return min(position.score for row in area.positions for position in row if position.height == 0)


if __name__ == '__main__':
    assert part1(EXAMPLE) == 31
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 29
    print(f'Solution for part 2 is: {part2(get_input())}')
