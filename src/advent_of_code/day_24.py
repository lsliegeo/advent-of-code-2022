import dataclasses
import math
from collections import defaultdict
from enum import Enum

from tqdm import tqdm

from src.input_util import get_input
from src.timer_util import ContextTimer

EXAMPLE = """#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#"""


class Direction(Enum):
    UP = '^'
    DOWN = 'v'
    LEFT = '<'
    RIGHT = '>'


@dataclasses.dataclass
class Blizzard:
    direction: Direction
    position: tuple[int, int]


class Tile(Enum):
    WALL = '#'
    GROUND = '.'
    BLIZZARD = 'x'


def advance(x: int, y: int, direction: Direction) -> tuple[int, int]:
    match direction:
        case Direction.UP:
            return x - 1, y
        case Direction.DOWN:
            return x + 1, y
        case Direction.LEFT:
            return x, y - 1
        case Direction.RIGHT:
            return x, y + 1
        case _:
            raise ValueError()


@dataclasses.dataclass
class Area:
    """
    A representation of the field at a given moment.
    tiles: the whole grid
    blizzards: specific information about every individual blizzard. Its direction and coordinates
    """

    tiles: list[list[Tile]]
    blizzards: list[Blizzard]

    def advance(self) -> 'Area':
        """Advance the whole area to the next state. Move all blizzards."""
        new_tiles = [[Tile.WALL if tile == Tile.WALL else Tile.GROUND for tile in row] for row in self.tiles]
        new_blizzards = []
        for blizzard in self.blizzards:
            new_blizzard = self._advance_blizzard(blizzard)
            new_blizzards.append(new_blizzard)
            new_tiles[new_blizzard.position[0]][new_blizzard.position[1]] = Tile.BLIZZARD
        return Area(new_tiles, new_blizzards)

    def _advance_blizzard(self, blizzard: Blizzard) -> Blizzard:
        """Move a single blizzard. Returns a new object."""
        next_x, next_y = advance(*blizzard.position, blizzard.direction)
        if self.tiles[next_x][next_y] == Tile.WALL:
            next_x, next_y = advance(next_x, next_y, blizzard.direction)
            next_x, next_y = advance(next_x, next_y, blizzard.direction)
        next_x %= len(self.tiles)
        next_y %= len(self.tiles[0])
        return Blizzard(blizzard.direction, (next_x, next_y))

    def visualize(self, current_position: tuple[int, int] | None = None) -> str:
        s = ''
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if current_position and current_position == (i, j):
                    s += 'E'
                elif tile == Tile.BLIZZARD:
                    blizzards = [b for b in self.blizzards if b.position == (i, j)]
                    if len(blizzards) == 1:
                        s += blizzards[0].direction.value
                    else:
                        s += str(min(len(blizzards), 9))
                else:
                    s += tile.value
            s += '\n'
        return s[:-1]


class Backtracking:

    def __init__(self, init_area: Area):
        # Least common multiple of the width and length (excluding the walls)
        # All areas modulo `lcm` are identical. We only need to calculate the `lcm` distinct areas
        self.lcm = math.lcm(len(init_area.tiles) - 2, len(init_area.tiles[0]) - 2)
        self._areas = [init_area]
        for _ in tqdm(range(self.lcm - 1), desc='Generating areas') if self.lcm > 100 else range(self.lcm - 1):
            self._areas.append(self._areas[-1].advance())

        self.start = (0, 1)
        self.finish = (-1 % len(init_area.tiles), -2 % len(init_area.tiles[0]))
        self.best_case = manhattan_distance(*self.start, *self.finish)

        self.stages: int = None
        self.stage_to_modulo_to_time_to_explored: dict[int, dict[int, dict[int, set]]] = None
        self.best_time: int = None

    def areas(self, time: int) -> Area:
        # All areas modulo `lcm` are identical
        return self._areas[time % self.lcm]

    def fastest_route(self, stages: int = 1) -> int:
        self.stages = stages
        self.best_time = 10 ** 10
        self.stage_to_modulo_to_time_to_explored = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        self._backtrack(0, 0, self.start)
        return self.best_time

    def _backtrack(self, time: int, stage: int, position: tuple[int, int]):
        """
        stage: indicating which part of the adventure we are in
          * even: going from start to finish
          * odd going from finish back to the start

        stage_to_modulo_to_time_to_explored: in order to avoid exploring a specific position on the same time more than once
        """

        goal = self.finish if stage % 2 == 0 else self.start

        if position == goal:
            # Current stage is finished
            stage += 1
            if stage == self.stages:
                # Done with all stages
                if time < self.best_time:
                    # New best
                    # print(time)
                    self.best_time = time
                return
            goal = self.finish if stage % 2 == 0 else self.start

        # if
        #  * current stage
        #  * current position
        #  * same state of the area (same time % lcm)
        #  * already explored this with current time (literal exact state)
        #      or alreadt explored with lower time (literal exact state, but a lcm cycle earlier)
        # then: skip
        # else: register this
        if any(position in v for k, v in self.stage_to_modulo_to_time_to_explored[stage][time % self.lcm].items() if time >= k):
            return
        else:
            self.stage_to_modulo_to_time_to_explored[stage][time % self.lcm][time].add(position)

        # Upper bound using manhattan distance
        if time + manhattan_distance(*position, *goal) + self.best_case * (self.stages - 1 - stage) > self.best_time:
            return

        next_area = self.areas(time + 1)
        order = (
            [Direction.DOWN, Direction.RIGHT, Direction.UP, Direction.LEFT],  # going to finish: down right first
            [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT],  # going to start: up left first
        )[stage % 2]
        for d in order:
            next_x, next_y = advance(*position, d)
            if 0 <= next_x < len(next_area.tiles) and 0 <= next_y < len(next_area.tiles[0]):
                # If is not out of bounds
                if next_area.tiles[next_x][next_y] == Tile.GROUND:
                    # If it's possible to walk to that tile
                    self._backtrack(time + 1, stage, (next_x, next_y))
        if next_area.tiles[position[0]][position[1]] == Tile.GROUND:
            # Stand still
            self._backtrack(time + 1, stage, position)


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


def parse(input_data: str) -> Area:
    tiles = []
    blizzards = []
    for i, row in enumerate(input_data.split('\n')):
        tiles.append([])
        for j, char in enumerate(row):
            try:
                direction = Direction(char)
                tile = Tile.BLIZZARD
                blizzards.append(Blizzard(direction, (i, j)))
            except ValueError:
                tile = Tile(char)
            tiles[-1].append(tile)
    return Area(tiles, blizzards)


def part1(input_data: str):
    area = parse(input_data)
    return Backtracking(area).fastest_route()


def part2(input_data: str):
    area = parse(input_data)
    return Backtracking(area).fastest_route(stages=3)


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(10000)

    assert Backtracking(parse("""#.#####
#.....#
#>....#
#.....#
#...v.#
#.....#
#####.#"""))._areas[3].visualize() == """#.#####
#.....#
#...2.#
#.....#
#.....#
#.....#
#####.#"""
    assert Backtracking(parse(EXAMPLE))._areas[0].visualize() == Backtracking(parse(EXAMPLE)).areas(Backtracking(parse(EXAMPLE)).lcm).visualize()
    with ContextTimer():
        assert part1(EXAMPLE) == 18
    with ContextTimer():
        print(f'Solution for part 1 is: {part1(get_input())}')  # takes about 10 seconds
    with ContextTimer():
        assert part2(EXAMPLE) == 54
    with ContextTimer():
        print(f'Solution for part 2 is: {part2(get_input())}')  # takes about 40 seconds
