from src.input_util import get_input


def part1(input_data: str):
    best = current = 0
    for line in input_data.split('\n'):
        if line:
            current += int(line)
        else:
            best = max(current, best)
            current = 0

    return best


def part2(input_data: str):
    totals = []
    current = 0
    for line in input_data.split('\n'):
        if line:
            current += int(line)
        else:
            totals.append(current)
            current = 0

    return sum(sorted(totals)[-3:])


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
