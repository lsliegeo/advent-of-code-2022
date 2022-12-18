import dataclasses
import itertools
from collections import defaultdict
from enum import Enum

from src.input_util import get_input

EXAMPLE = """498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9"""

SOURCE = 500, 0


class Tile(Enum):
    AIR = '.'
    ROCK = '#'
    SOURCE = '+'
    SAND = 'o'


@dataclasses.dataclass
class Cave:
    tiles: dict[int, list[Tile]]
    sand: int = 0

    def __init__(self, max_y: int, floor: bool):
        if floor:
            self.tiles = defaultdict(lambda: [Tile.AIR] * (max_y + 2) + [Tile.ROCK])
        else:
            self.tiles = defaultdict(lambda: [Tile.AIR] * (max_y + 1))
        self.height = len(self.tiles[SOURCE[0]])

    def swap(self, co1: tuple[int, int], co2: tuple[int, int]):
        self.tiles[co1[0]][co1[1]], self.tiles[co2[0]][co2[1]] = self.tiles[co2[0]][co2[1]], self.tiles[co1[0]][co1[1]]

    def update_sand(self, co: tuple[int, int]) -> tuple[int, int] | None:
        below = co[0], co[1] + 1
        below_left = co[0] - 1, co[1] + 1
        below_right = co[0] + 1, co[1] + 1
        if self.tiles[below[0]][below[1]] == Tile.AIR:
            self.swap(co, below)
            return below
        elif self.tiles[below_left[0]][below_left[1]] == Tile.AIR:
            self.swap(co, below_left)
            return below_left
        elif self.tiles[below_right[0]][below_right[1]] == Tile.AIR:
            self.swap(co, below_right)
            return below_right
        else:
            return None

    def simulate(self):
        while True:
            # print(self.image))
            prev, head = None, SOURCE
            self.tiles[head[0]][head[1]] = Tile.SAND
            while head is not None:
                if head[1] == self.height - 1:
                    # Sand is falling off
                    self.tiles[SOURCE[0]][SOURCE[1]] = Tile.SOURCE  # reset source for the image
                    return
                prev, head = head, self.update_sand(head)

            self.sand += 1
            if prev == SOURCE and head is None:
                # Couldn't move from the source, meaning we're full
                # print(self.image)
                return

    @property
    def image(self) -> str:
        min_x, max_x = min(self.tiles), max(self.tiles)
        return '\n'.join(''.join(self.tiles[x][y].value for x in range(min_x, 1 + max_x)) for y in range(0, len(self.tiles[min_x])))


def parse_cave(input_data: str, floor: bool) -> Cave:
    rocks = [
        [eval(coordinate_str) for coordinate_str in line.split(' -> ')]
        for line in input_data.split('\n')
    ]
    max_y = max(coordinate[1] for rock in rocks for coordinate in rock)

    cave = Cave(max_y, floor)
    cave.tiles[SOURCE[0]][SOURCE[1]] = Tile.SOURCE

    for rock in rocks:
        for i in range(1, len(rock)):
            prev, current = rock[i - 1], rock[i]
            x_range = range(min(prev[0], current[0]), max(prev[0], current[0]) + 1)
            y_range = range(min(prev[1], current[1]), max(prev[1], current[1]) + 1)
            for x, y in itertools.product(x_range, y_range):
                cave.tiles[x][y] = Tile.ROCK

    return cave


def part1(input_data: str):
    cave = parse_cave(input_data, floor=False)
    cave.simulate()
    return cave.sand


def part2(input_data: str):
    cave = parse_cave(input_data, floor=True)
    cave.simulate()
    return cave.sand


if __name__ == '__main__':
    assert parse_cave(EXAMPLE, floor=False).image == """......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
........#.
........#.
#########."""
    assert part1(EXAMPLE) == 24
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert parse_cave(EXAMPLE, floor=True).image == """......+...
..........
..........
..........
....#...##
....#...#.
..###...#.
........#.
........#.
#########.
..........
##########"""
    cave2 = parse_cave(EXAMPLE, floor=True)
    cave2.simulate()
    assert cave2.image == """...........o...........
..........ooo..........
.........ooooo.........
........ooooooo........
.......oo#ooo##o.......
......ooo#ooo#ooo......
.....oo###ooo#oooo.....
....oooo.oooo#ooooo....
...oooooooooo#oooooo...
..ooo#########ooooooo..
.ooooo.......ooooooooo.
#######################"""
    assert part2(EXAMPLE) == 93
    print(f'Solution for part 2 is: {part2(get_input())}')
