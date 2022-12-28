import abc
import dataclasses
import re
from enum import Enum

from src.input_util import get_input

EXAMPLE = """        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5"""


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    def rotate(self, d: str) -> 'Direction':
        if d == 'R':
            return Direction((self.value + 1) % len(Direction))
        else:
            return Direction((self.value - 1) % len(Direction))

    def opposite(self) -> 'Direction':
        return self.rotate('R').rotate('R')

    @property
    def pretty(self) -> str:
        return {
            Direction.RIGHT: '>',
            Direction.LEFT: '<',
            Direction.UP: '^',
            Direction.DOWN: 'v',
        }[self]


"""
  0
123
  45
"""
MAPPING_EXAMPLE: dict[int, dict[Direction, tuple[int, Direction]]] = {
    # When leaving 0 while going up, you'll arrive in 1 going down
    0: {
        Direction.UP: (1, Direction.DOWN),
        Direction.DOWN: (3, Direction.DOWN),
        Direction.LEFT: (2, Direction.DOWN),
        Direction.RIGHT: (5, Direction.LEFT),
    },
    1: {
        Direction.UP: (0, Direction.DOWN),
        Direction.DOWN: (4, Direction.UP),
        Direction.LEFT: (5, Direction.UP),
        Direction.RIGHT: (2, Direction.RIGHT),
    },
    2: {
        Direction.UP: (0, Direction.RIGHT),
        Direction.DOWN: (4, Direction.RIGHT),
        Direction.LEFT: (1, Direction.LEFT),
        Direction.RIGHT: (3, Direction.RIGHT),
    },
    3: {
        Direction.UP: (0, Direction.UP),
        Direction.DOWN: (4, Direction.DOWN),
        Direction.LEFT: (2, Direction.LEFT),
        Direction.RIGHT: (5, Direction.DOWN),
    },
    4: {
        Direction.UP: (3, Direction.UP),
        Direction.DOWN: (1, Direction.UP),
        Direction.LEFT: (2, Direction.UP),
        Direction.RIGHT: (5, Direction.RIGHT),
    },
    5: {
        Direction.UP: (3, Direction.LEFT),
        Direction.DOWN: (1, Direction.RIGHT),
        Direction.LEFT: (4, Direction.LEFT),
        Direction.RIGHT: (0, Direction.LEFT),
    },
}

"""
 01
 2
34
5
"""
MAPPING_INPUT: dict[int, dict[Direction, tuple[int, Direction]]] = {
    # When leaving 0 while going up, you'll arrive in 5 going right
    0: {
        Direction.UP: (5, Direction.RIGHT),
        Direction.DOWN: (2, Direction.DOWN),
        Direction.LEFT: (3, Direction.RIGHT),
        Direction.RIGHT: (1, Direction.RIGHT),
    },
    1: {
        Direction.UP: (5, Direction.UP),
        Direction.DOWN: (2, Direction.LEFT),
        Direction.LEFT: (0, Direction.LEFT),
        Direction.RIGHT: (4, Direction.LEFT),
    },
    2: {
        Direction.UP: (0, Direction.UP),
        Direction.DOWN: (4, Direction.DOWN),
        Direction.LEFT: (3, Direction.DOWN),
        Direction.RIGHT: (1, Direction.UP),
    },
    3: {
        Direction.UP: (2, Direction.RIGHT),
        Direction.DOWN: (5, Direction.DOWN),
        Direction.LEFT: (0, Direction.RIGHT),
        Direction.RIGHT: (4, Direction.RIGHT),
    },
    4: {
        Direction.UP: (2, Direction.UP),
        Direction.DOWN: (5, Direction.LEFT),
        Direction.LEFT: (3, Direction.LEFT),
        Direction.RIGHT: (1, Direction.LEFT),
    },
    5: {
        Direction.UP: (3, Direction.UP),
        Direction.DOWN: (1, Direction.DOWN),
        Direction.LEFT: (0, Direction.DOWN),
        Direction.RIGHT: (4, Direction.UP),
    },
}


class Tile(Enum):
    GROUND = '.'
    WALL = '#'
    OUT_OF_BOUNDS = ' '


@dataclasses.dataclass
class Move:
    rotation: str | None
    steps: int


def parse(input_data: str) -> tuple[list[list[Tile]], list[Move]]:
    """Parse the input. Also adds trailing ' ' to the shorter rows"""
    tiles_str, instructions_str = input_data.split('\n\n')
    tiles = [[Tile(t) for t in row] for row in tiles_str.split('\n')]
    max_row_size = max(len(row) for row in tiles)
    for row in tiles:
        row.extend([Tile.OUT_OF_BOUNDS] * (max_row_size - len(row)))
    moves = [Move(r or None, int(v)) for r, v in re.findall(r'(^|L|R)(\d+)', instructions_str)]
    return tiles, moves


@dataclasses.dataclass
class Area(abc.ABC):
    """
    Class to keep track of the whole area.

    tiles: full grid
    history: the way we've traversed through the area

    Provides the advance() method, to execute a single method.
    Subclasses have to implement next_position()
    """

    tiles: list[list[Tile]]
    history: dict[tuple[int, int], Direction] = dataclasses.field(default_factory=dict)
    current_position: tuple[int, int] = dataclasses.field(init=False)
    current_direction: Direction = dataclasses.field(init=False)

    def __post_init__(self):
        self.current_position = next(iter((i, j) for i, row in enumerate(self.tiles) for j, tile in enumerate(row) if tile == Tile.GROUND))
        self.current_direction = Direction.RIGHT
        self.update_history()

    def visualize(self) -> str:
        s = ''
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                if direction := self.history.get((i, j)):
                    s += direction.pretty
                else:
                    s += tile.value
            s += '\n'
        return s

    def print(self):
        print(self.visualize())

    def update_history(self):
        self.history[self.current_position] = self.current_direction

    def next_position(self) -> tuple[int, int, Direction]:
        raise NotImplementedError()

    def advance(self, move: Move):
        if move.rotation:
            self.current_direction = self.current_direction.rotate(move.rotation)
            self.update_history()
        for _ in range(move.steps):
            next_x, next_y, next_direction = self.next_position()
            if self.tiles[next_x][next_y] == Tile.OUT_OF_BOUNDS:
                raise Exception()
            if self.tiles[next_x][next_y] == Tile.WALL:
                break
            self.current_position = next_x, next_y
            self.current_direction = next_direction
            self.update_history()
            # self.print()
        # self.print()


@dataclasses.dataclass
class Area1(Area):
    """
    next_position() will wrap to the other side of the row/column
    """

    row_to_boundaries: dict[int, tuple[int, int]] = dataclasses.field(init=False)
    column_to_boundaries: dict[int, tuple[int, int]] = dataclasses.field(init=False)

    def __post_init__(self):
        super().__post_init__()
        # Calculate boundaries
        self.row_to_boundaries = {
            i: (
                min(j for j, tile in enumerate(row) if tile != Tile.OUT_OF_BOUNDS),
                max(j for j, tile in enumerate(row) if tile != Tile.OUT_OF_BOUNDS)
            )
            for i, row in enumerate(self.tiles)
        }
        self.column_to_boundaries = {
            j: (
                min(i for i, row in enumerate(self.tiles) if row[j] != Tile.OUT_OF_BOUNDS),
                max(i for i, row in enumerate(self.tiles) if row[j] != Tile.OUT_OF_BOUNDS),
            )
            for j in range(len(self.tiles[0]))
        }

    def next_position(self) -> tuple[int, int, Direction]:
        match self.current_direction:
            case Direction.RIGHT:
                next_x, next_y = self.current_position[0], self.current_position[1] + 1
                if next_y > self.row_to_boundaries[next_x][1]:
                    next_y = self.row_to_boundaries[next_x][0]
            case Direction.LEFT:
                next_x, next_y = self.current_position[0], self.current_position[1] - 1
                if next_y < self.row_to_boundaries[next_x][0]:
                    next_y = self.row_to_boundaries[next_x][1]
            case Direction.UP:
                next_x, next_y = self.current_position[0] - 1, self.current_position[1]
                if next_x < self.column_to_boundaries[next_y][0]:
                    next_x = self.column_to_boundaries[next_y][1]
            case Direction.DOWN:
                next_x, next_y = self.current_position[0] + 1, self.current_position[1]
                if next_x > self.column_to_boundaries[next_y][1]:
                    next_x = self.column_to_boundaries[next_y][0]
            case _:
                raise ValueError()
        return next_x, next_y, self.current_direction


class Area2(Area):
    """
    The Area is divided in 6 tiles
    * Tiles are indexed 0..5
    * Tiles have width = height = tile_size

    When moving outside the current tile, the mapping will indicate which tile will be entered, and with which direction
    """

    mapping: dict[int, dict[Direction, tuple[int, Direction]]]
    tile_size: int
    index_to_tiles: dict[int, list[list[Tile]]] = dataclasses.field(init=False)  # tile index to the subset of the tiles
    index_to_position: dict[int, tuple[int, int]] = dataclasses.field(init=False)  # tile index to coordinate of the top left corner
    tile_map: list[list[int | None]] = dataclasses.field(init=False)  # grid with tile indices. E.g. [[None, None, 0, None], [1, 2, 3, None], [None, None, 4, 5]]

    def __init__(self, tiles: list[list[Tile]], mapping: dict[int, dict[Direction, tuple[int, Direction]]], face_size: int):
        super().__init__(tiles)

        self.mapping = mapping
        self.tile_size = face_size

        self.tile_map = []
        self.index_to_tiles = {}
        self.index_to_position = {}
        index = 0
        for i in range(len(self.tiles) // self.tile_size):
            self.tile_map.append([])
            for j in range(len(self.tiles[0]) // self.tile_size):
                if self.tiles[i * self.tile_size][j * self.tile_size] != Tile.OUT_OF_BOUNDS:
                    self.index_to_tiles[index] = [row[j * self.tile_size:(j + 1) * self.tile_size] for row in self.tiles[i * self.tile_size:(i + 1) * self.tile_size]]
                    self.tile_map[-1].append(index)
                    self.index_to_position[index] = i, j
                    index += 1
                else:
                    self.tile_map[-1].append(None)

    def next_position(self) -> tuple[int, int, Direction]:
        current_tile_index = self.tile_map[self.current_position[0] // self.tile_size][self.current_position[1] // self.tile_size]
        match self.current_direction:
            case Direction.RIGHT:
                next_x, next_y = self.current_position[0], self.current_position[1] + 1
            case Direction.LEFT:
                next_x, next_y = self.current_position[0], self.current_position[1] - 1
            case Direction.UP:
                next_x, next_y = self.current_position[0] - 1, self.current_position[1]
            case Direction.DOWN:
                next_x, next_y = self.current_position[0] + 1, self.current_position[1]
            case _:
                raise ValueError()
        next_x %= len(self.tiles)
        next_y %= len(self.tiles[0])
        next_direction = self.current_direction

        new_tile_index = self.tile_map[next_x // self.tile_size][next_y // self.tile_size]  # Tile index if we would execute this move, disregarding the cube
        if current_tile_index != new_tile_index:
            # Moving to a different tile
            next_tile_index, next_direction = self.mapping[current_tile_index][self.current_direction]
            next_x_rel = next_x % self.tile_size
            next_y_rel = next_y % self.tile_size
            tmp = self.current_direction
            while tmp != next_direction:
                # When entering the next tile with different direction, need to rotate the coordinates as well
                tmp = tmp.rotate('R')
                next_x_rel, next_y_rel = next_y_rel, self.tile_size - next_x_rel - 1
            next_x = next_x_rel + self.index_to_position[next_tile_index][0] * self.tile_size
            next_y = next_y_rel + self.index_to_position[next_tile_index][1] * self.tile_size

        return next_x, next_y, next_direction


def part1_area(input_data: str) -> Area1:
    # Small in between function that returns the Area object
    tiles, moves = parse(input_data)
    area = Area1(tiles)
    for move in moves:
        area.advance(move)
    # area.print()
    return area


def part1(input_data: str):
    area = part1_area(input_data)
    x, y = area.current_position
    return (x + 1) * 1000 + (y + 1) * 4 + area.current_direction.value


def part2_area(input_data: str, face_size: int, mapping: dict[int, dict[Direction, tuple[int, Direction]]]) -> Area2:
    # Small in between function that returns the Area object
    tiles, moves = parse(input_data)
    area = Area2(tiles, mapping, face_size)
    for move in moves:
        area.advance(move)
    # area.print()
    return area


def part2(input_data: str, face_size: int = 50, mapping: dict[int, dict[Direction, tuple[int, Direction]]] = MAPPING_INPUT):
    area = part2_area(input_data, face_size, mapping)
    x, y = area.current_position
    return (x + 1) * 1000 + (y + 1) * 4 + area.current_direction.value


if __name__ == '__main__':
    assert Direction.RIGHT.rotate('R') == Direction.DOWN
    assert Direction.RIGHT.rotate('L') == Direction.UP
    assert part1_area(EXAMPLE).visualize() == """        >>v#    
        .#v.    
        #.v.    
        ..v.    
...#...v..v#    
>>>v...>#.>>    
..#v...#....    
...>>>>v..#.    
        ...#....
        .....#..
        .#......
        ......#.
"""
    assert part1(EXAMPLE) == 6032
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert len(set(j for i in MAPPING_EXAMPLE.values() for j in i.values())) == 24
    assert part2_area(EXAMPLE, 4, MAPPING_EXAMPLE).visualize() == """        >>v#    
        .#v.    
        #.v.    
        ..v.    
...#..^...v#    
.>>>>>^.#.>>    
.^#....#....    
.^........#.    
        ...#..v.
        .....#v.
        .#v<<<<.
        ..v...#.
"""
    assert part2(EXAMPLE, 4, MAPPING_EXAMPLE) == 5031
    assert len(set(j for i in MAPPING_INPUT.values() for j in i.values())) == 24
    print(f'Solution for part 2 is: {part2(get_input())}')
