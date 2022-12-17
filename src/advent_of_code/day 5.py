import dataclasses
import re
from collections import defaultdict
from src.input_util import get_input


@dataclasses.dataclass
class Move:
    number: int
    source: int
    destination: int


def parse_input(input_data: str) -> tuple[dict[int, str], list[Move]]:
    crates_str, moves_str = input_data.split('\n\n')

    # parse crates
    crates = defaultdict(str)
    crates_str_list = crates_str.split('\n')
    num_crates = max(int(i) for i in crates_str_list[-1].strip().split('   '))
    for row in reversed(crates_str_list[:-1]):
        for i in range(num_crates):
            item_index = 1 + 4 * i
            if item_index >= len(row):
                continue
            item = row[item_index]
            if item != ' ':
                crates[i + 1] += item

    # parse moves
    moves = []
    for s in moves_str.split('\n'):
        if s:
            match = re.match('move (\d+) from (\d+) to (\d+)', s)
            if not match:
                pass
            moves.append(Move(int(match.group(1)), int(match.group(2)), int(match.group(3))))

    return crates, moves


def execute_move_multiples(crates: dict[int, str], move):
    crates[move.destination] += crates[move.source][-move.number:]
    crates[move.source] = crates[move.source][:-move.number]


def execute_move_one_by_one(crates: dict[int, str], move):
    for _ in range(move.number):
        crates[move.destination] += crates[move.source][-1]
        crates[move.source] = crates[move.source][:-1]


def part1(input_data: str):
    crates, moves = parse_input(input_data)
    for move in moves:
        execute_move_one_by_one(crates, move)
    return ''.join(crates[k][-1] for k in sorted(crates))


def part2(input_data: str):
    crates, moves = parse_input(input_data)
    for move in moves:
        execute_move_multiples(crates, move)
    return ''.join(crates[k][-1] for k in sorted(crates))


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
