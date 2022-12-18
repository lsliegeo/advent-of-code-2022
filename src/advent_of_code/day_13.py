import random
from typing import Callable, TypeVar

from src.input_util import get_input

EXAMPLE_PART_1 = """[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]"""

EXAMPLE_PART_2 = """[]
[[]]
[[[]]]
[1,1,3,1,1]
[1,1,5,1,1]
[[1],[2,3,4]]
[1,[2,[3,[4,[5,6,0]]]],8,9]
[1,[2,[3,[4,[5,6,7]]]],8,9]
[[1],4]
[[2]]
[3]
[[4,4],4,4]
[[4,4],4,4,4]
[[6]]
[7,7,7]
[7,7,7,7]
[[8,7,6]]
[9]"""

Value = int | list[int]
Packet = list[Value]


def parse_pairs(input_data: str) -> list[tuple[Packet, Packet]]:
    packets = []
    for lines in input_data.split('\n\n'):
        line_one, line_two = lines.split('\n')
        packets.append((eval(line_one), eval(line_two)))
    return packets


def parse_all(input_data: str) -> list[Packet]:
    return [eval(line) for line in input_data.split('\n') if line]


def compare(one: Packet | Value, other: Packet | Value) -> bool | None:
    # If possible, compare ints
    if isinstance(one, int) and isinstance(other, int):
        if one != other:
            return one < other
        return None

    # Covert to lists
    if isinstance(one, int):
        one = [one]
    elif isinstance(other, int):
        other = [other]

    # Compare lists, piecewise
    for a, b in zip(one, other):
        tmp_result = compare(a, b)
        if tmp_result is not None:
            return tmp_result

    # Compare list, length
    if len(one) < len(other):
        return True
    elif len(one) > len(other):
        return False
    else:
        return None


T = TypeVar('T')


def merge_sort(values: list[T], comp: Callable[[T, T], bool]) -> list[T]:
    if len(values) < 2:
        return values

    left, right = merge_sort(values[:len(values) // 2], comp), merge_sort(values[len(values) // 2:], comp)
    result = []
    left_i = right_i = 0
    while left_i < len(left) and right_i < len(right):
        if comp(left[left_i], right[right_i]):
            result.append(left[left_i])
            left_i += 1
        else:
            result.append(right[right_i])
            right_i += 1

    result += left[left_i:] + right[right_i:]

    return result


def add_2_6_sort(packets: list[Packet]) -> list[Packet]:
    packets.append([[2]])
    packets.append([[6]])
    return merge_sort(packets, compare)


def get_decoder_key(packets: list[Packet]) -> int:
    return (packets.index([[2]]) + 1) * (packets.index([[6]]) + 1)


def part1(input_data: str):
    return sum(
        i + 1
        for i, pair in enumerate(parse_pairs(input_data))
        if compare(*pair)
    )


def part2(input_data: str):
    return get_decoder_key(add_2_6_sort(parse_all(input_data)))


if __name__ == '__main__':
    assert compare([1, 1, 3, 1, 1], [1, 1, 5, 1, 1]) == True
    assert compare([[1], [2, 3, 4]], [[1], 4]) == True
    assert compare([9], [[8, 7, 6]]) == False
    assert compare([[4, 4], 4, 4], [[4, 4], 4, 4, 4]) == True
    assert compare([7, 7, 7, 7], [7, 7, 7]) == False
    assert compare([], [3]) == True
    assert compare([[[]]], [[]]) == False
    assert compare([1, [2, [3, [4, [5, 6, 7]]]], 8, 9], [1, [2, [3, [4, [5, 6, 0]]]], 8, 9]) == False
    assert part1(EXAMPLE_PART_1) == 13
    print(f'Solution for part 1 is: {part1(get_input())}')

    random_list = [random.randint(0, 2 ** 10) for _ in range(2 ** 14)]
    assert merge_sort(random_list, int.__lt__) == sorted(random_list)
    assert add_2_6_sort(parse_all(EXAMPLE_PART_1)) == parse_all(EXAMPLE_PART_2)
    print(f'Solution for part 2 is: {part2(get_input())}')
