import re
from collections import defaultdict
from typing import Callable

from src.input_util import get_input

EXAMPLE = """root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32"""


def parse(input_data: str) -> tuple[dict[str, set[str]], dict[str, int], dict[str, list[tuple[Callable[[int, int], int], str, str]]]]:
    dependencies, values, operations = defaultdict(set), {}, defaultdict(list)
    for line in input_data.split('\n'):
        if match := re.match(r'(.*): (\d+)', line):
            values[match.group(1)] = int(match.group(2))
        elif match := re.match(r'(.*): (.*) (.) (.*)', line):
            derived_lines = [line]
            match match.groups():
                case [name, a, '+', b]:
                    derived_lines.append(f'{a}: {name} - {b}')
                    derived_lines.append(f'{b}: {name} - {a}')
                case [name, a, '-', b]:
                    derived_lines.append(f'{a}: {name} + {b}')
                    derived_lines.append(f'{b}: {a} - {name}')
                case [name, a, '*', b]:
                    derived_lines.append(f'{a}: {name} / {b}')
                    derived_lines.append(f'{b}: {name} / {a}')
                case [name, a, '/', b]:
                    derived_lines.append(f'{a}: {name} * {b}')
                    derived_lines.append(f'{b}: {a} / {name}')
            for derived_line in derived_lines:
                match = re.match(r'(.*): (.*) (.) (.*)', derived_line)
                dependencies[match.group(2)].add(match.group(1))
                dependencies[match.group(4)].add(match.group(1))
                operations[match.group(1)].append((
                    {
                        '+': int.__add__,
                        '-': int.__sub__,
                        '*': int.__mul__,
                        '/': int.__floordiv__,
                    }[match.group(3)],
                    match.group(2),
                    match.group(4),
                ))
        else:
            raise Exception()
    return dependencies, values, operations


def solve(dependencies: dict[str, set[str]], values: dict[str, int], operations: dict[str, list[tuple[Callable[[int, int], int], str, str]]]):
    ready_to_action = set(dependency for value in values for dependency in dependencies[value])
    while ready_to_action:
        name = ready_to_action.pop()
        if name in values:
            continue
        for operation in operations[name]:
            if isinstance(operation, tuple):
                op, one, two = operation
                if one not in values or two not in values:
                    continue
                values[name] = op(values[one], values[two])
            else:
                other_name = operation
                if other_name not in values:
                    continue
                values[name] = values[other_name]
            ready_to_action |= dependencies[name]
            break


def part1(input_data: str):
    dependencies, values, operations = parse(input_data)
    solve(dependencies, values, operations)
    return values['root']


def part2(input_data: str):
    dependencies, values, operations = parse(input_data)
    del values['humn']
    solve(dependencies, values, operations)
    root_1, root_2 = operations['root'][0][1], operations['root'][0][2]
    values[root_1] = values[root_2] = values.get(root_1) or values.get(root_2)
    solve(dependencies, values, operations)
    return values['humn']


if __name__ == '__main__':
    assert part1(EXAMPLE) == 152
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 301
    print(f'Solution for part 2 is: {part2(get_input())}')
