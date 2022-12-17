from src.input_util import get_input


def part1(input_data: str):
    return 4 + next(i for i in range(len(input_data)) if len(set(input_data[i:i + 4])) == 4)


def part2(input_data: str):
    return 14 + next(i for i in range(len(input_data)) if len(set(input_data[i:i + 14])) == 14)


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
