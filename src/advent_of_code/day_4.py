from src.input_util import get_input


def parse_tasks(task: str) -> set:
    start, end = task.split('-')
    return set(range(int(start), int(end) + 1))


def parse_line(line: str) -> tuple[set, set]:
    a, b = line.split(',')
    return parse_tasks(a), parse_tasks(b)


def part1(input_data: str):
    lines = [parse_line(line) for line in input_data.split('\n') if line]
    return sum(a <= b or b <= a for a, b in lines)


def part2(input_data: str):
    lines = [parse_line(line) for line in input_data.split('\n') if line]
    return sum(bool(a & b) for a, b in lines)


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
