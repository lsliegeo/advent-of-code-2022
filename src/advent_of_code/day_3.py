import string

from src.input_util import get_input


def priority(char: str) -> int:
    return string.ascii_letters.index(char) + 1


def part1(input_data: str):
    score = 0
    for line in input_data.split('\n'):
        if line:
            a, b = set(line[:len(line) // 2]), set(line[len(line) // 2:])
            for c in a & b:
                score += priority(c)
    return score


def part2(input_data: str):
    score = 0
    lines = [line for line in input_data.split('\n') if line]
    for group_index in range(0, len(lines), 3):
        group = lines[group_index:group_index + 3]
        common_item = set(group[0]) & set(group[1]) & set(group[2])
        if len(common_item) != 1:
            raise ValueError()
        score += priority(list(common_item)[0])
    return score


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
