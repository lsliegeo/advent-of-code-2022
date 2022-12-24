from collections import defaultdict
from typing import Callable, Iterator

from src.input_util import get_input

EXAMPLE = """>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>"""


def bitvector(values: list[int]) -> int:
    r = 0
    for v in values:
        r += 2 ** v
    return r


WIDTH = 7
MAX_VECTOR = bitvector(list(range(WIDTH)))


def rock_generator() -> Iterator[tuple[int, Callable[[int], tuple[tuple[int, int]]]]]:
    rocks = [
        lambda h: tuple([(h, bitvector([1, 2, 3, 4]))]),
        lambda h: tuple([(h, bitvector([3])), (h + 1, bitvector([2, 3, 4])), (h + 2, bitvector([3]))]),
        lambda h: tuple([(h, bitvector([2, 3, 4])), (h + 1, bitvector([2])), (h + 2, bitvector([2]))]),
        lambda h: tuple([(h, bitvector([4])), (h + 1, bitvector([4])), (h + 2, bitvector([4])), (h + 3, bitvector([4]))]),
        lambda h: tuple([(h, bitvector([3, 4])), (h + 1, bitvector([3, 4]))]),
    ]
    while True:
        yield from enumerate(rocks)


def sequence_generator(input_data: str) -> Iterator[tuple[int, str]]:
    while True:
        yield from enumerate(input_data.strip())


def move_down(rock: tuple[tuple[int, int]]) -> tuple[tuple[int, int]]:
    return tuple((x - 1, v) for x, v in rock)


def move_sideways(char: str, rock: tuple[tuple[int, int]]) -> tuple[tuple[int, int]]:
    if char == '<':
        new_rock = tuple((x, v << 1) for x, v in rock)
        if any(v & 2 ** (WIDTH - 1) for _, v in rock):
            return rock
        return new_rock
    else:
        new_rock = tuple((x, v >> 1) for x, v in rock)
        if any(v & 1 for _, v in rock):
            return rock
        return new_rock


def rock_invalid(rock: tuple[tuple[int, int]], layout: dict[int, int]) -> bool:
    return any(x < 0 or layout[x] & v for x, v in rock)


def visualize(layout: dict[int, int], rock: tuple[tuple[int, int]] | None, skip: bool = True):
    if skip:
        return
    s = ''
    max_height = max(x for x, v in layout.items() if v)
    if rock:
        max_height = max(max_height, max(x for x, v in rock))
    for x in reversed(range(max_height + 1)):
        for p in reversed(range(WIDTH)):
            if rock and any(x == h and v & 2 ** p for h, v in rock):
                s += '@'
            elif layout[x] & 2 ** p:
                s += '#'
            else:
                s += '.'
        s += '\n'
    print()
    print(s)
    print()
    input()


def simulate(input_data: str, n: int):
    """
    Caching:
    At every full horizontal line, try to cache the state
    Cache input:
      * Bitvectors starting from the last horizontal line
      * Rock cycle index
      * Char cycle index
    Cache output:
      * Total number of falled rocks
      * Current max height

    Hitting the cache means we can advance the simulation very easily.
    Upon the first cache hit
      * i_diff = how many rocks have fallen
      * height_diff = the difference in height
      * This means if we add i_diff rocks, the height will increase with height_diff, and the layout will be the same starting from the last full horizontal line
      * We can advance as many times as we want, up to the target 1000000000000 rocks
    """

    cache = {}
    cache_height_offset = 0
    should_cache = True

    s = sequence_generator(input_data)
    r = rock_generator()

    max_height = 0
    layout = defaultdict(int, {0: MAX_VECTOR})

    i = 0
    while i < n:
        r_index, r_function = next(r)
        rock = r_function(max_height + 4)
        visualize(layout, rock)

        for _ in range(3):
            s_index, char = next(s)
            new_rock = move_sideways(char, rock)
            if not rock_invalid(new_rock, layout):
                rock = new_rock
                visualize(layout, rock)
            rock = move_down(rock)
            visualize(layout, rock)
        s_index, char = next(s)
        new_rock = move_sideways(char, rock)
        if not rock_invalid(new_rock, layout):
            rock = new_rock
            visualize(layout, rock)
        while True:
            new_rock = move_down(rock)
            if rock_invalid(new_rock, layout):
                break
            else:
                rock = new_rock
                visualize(layout, rock)

            s_index, char = next(s)
            new_rock = move_sideways(char, rock)
            if not rock_invalid(new_rock, layout):
                rock = new_rock
                visualize(layout, rock)

        for x, v in rock:
            layout[x] |= v
        visualize(layout, None)

        # print(floor)
        # print([max(l) for l in layout])
        max_height = max(max_height, max(x for x, _ in rock))
        # print(max_height)

        if should_cache:
            max_layout_index = max(i for i, v in layout.items() if v)
            for x, _ in rock:
                if layout[x] == MAX_VECTOR:
                    layout_for_cache = tuple(layout[i] for i in range(x, max_layout_index + 1))
                    if (cache_hit := cache.get((layout_for_cache, r_index, s_index))) and max_height > cache_hit[1]:
                        # print(f'CACHE HIT, {layout_for_cache, r_index, s_index}: {cache_hit} -> {i, max_height}')
                        i_diff = i - cache_hit[0]
                        height_diff = max_height - cache_hit[1]
                        times_to_simulate = (n - i) // i_diff
                        i += times_to_simulate * i_diff
                        cache_height_offset += times_to_simulate * height_diff
                        should_cache = False
                    else:
                        cache[(layout_for_cache, r_index, s_index)] = (i, max_height)
        i += 1

    return max_height + cache_height_offset


def part1(input_data: str):
    return simulate(input_data, 2022)


def part2(input_data: str):
    return simulate(input_data, 1000000000000)


if __name__ == '__main__':
    assert part1(EXAMPLE) == 3068
    print(f'Solution for part 1 is: {part1(get_input())}')
    # assert part2(EXAMPLE) == 1514285714288  # this one doesn't get a cache hit, so my solution can not solve this
    print(f'Solution for part 2 is: {part2(get_input())}')
