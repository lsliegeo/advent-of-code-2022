import dataclasses
import re
from typing import Callable

from tqdm import tqdm

from src.input_util import get_input

EXAMPLE = """Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1"""


@dataclasses.dataclass
class Item:
    """
    value: stores the total value. Only used by part 1
    modulo_counters: tracks the remainder after every relevant modulo divisible. Only used by part 2
    """
    value: int
    modulo_counters: dict[int, int]

    def __init__(self, value: int, relevant_modulos: list[int]):
        self.value = value
        self.modulo_counters = {modulo: self.value % modulo for modulo in relevant_modulos}

    def __add__(self, value: int | None):
        for k in self.modulo_counters:
            if value is None:
                # None: + self, aka, * 2
                self.modulo_counters[k] *= 2
            else:
                # int: + value
                self.modulo_counters[k] += value
            self.modulo_counters[k] %= k

    def __mul__(self, value: int | None):
        for k in self.modulo_counters:
            if value is None:
                # None: * self, aka, **2
                self.modulo_counters[k] **= 2
            else:
                # int: * value
                self.modulo_counters[k] *= value
            self.modulo_counters[k] %= k

    def is_divisible(self, modulo: int) -> bool:
        # self.modulo_counters[modulo] %= modulo
        return self.modulo_counters[modulo] == 0


@dataclasses.dataclass
class Monkey:
    items: list[Item]
    simple_operation: Callable[[int, int], int]
    item_operation: Callable[[Item, int | None], None]
    operation_argument: int | None
    test: int
    targets: tuple[int, int]
    number_inspects: int = 0


def parse_monkey(lines: list[str], relevant_modulos: list[int]) -> Monkey:
    # Parse items
    items = [
        Item(int(value), relevant_modulos)
        for value in re.match(r'.*: (.*)', lines[1]).group(1).split(', ')
    ]

    # Parse operation
    operation_str, arg_str = re.match(r'.* = old (.*)', lines[2]).group(1).split(' ')
    simple_operation, item_operation = {
        '+': (int.__add__, Item.__add__),
        '*': (int.__mul__, Item.__mul__),
    }[operation_str]
    operation_argument = None if arg_str == 'old' else int(arg_str)

    # Parse test
    test_number = int(re.match(r'.* divisible by (.*)', lines[3]).group(1))

    # Parse targets
    target_true = int(re.match(r'.* to monkey (.*)', lines[4]).group(1))
    target_false = int(re.match(r'.* to monkey (.*)', lines[5]).group(1))
    targets = (target_false, target_true)

    return Monkey(items, simple_operation, item_operation, operation_argument, test_number, targets)


def parse_monkeys(input_data: str) -> list[Monkey]:
    monkey_lines: list[list[str]] = [lines.split('\n') for lines in input_data.split('\n\n')]
    relevant_modulos = [int(re.match(r'.* divisible by (.*)', lines[3]).group(1)) for lines in monkey_lines]
    return [parse_monkey(lines, relevant_modulos) for lines in monkey_lines]


def execute_round(monkeys: list[Monkey], divide_by_3: bool):
    for monkey in monkeys:
        for item in monkey.items:
            if divide_by_3:
                # Work with the total value. Disregards the Item container
                item.value = monkey.simple_operation(item.value, monkey.operation_argument or item.value) // 3
                target = monkey.targets[item.value % monkey.test == 0]
            else:
                # Work with the modulo remainder. Disregards the Item.value
                monkey.item_operation(item, monkey.operation_argument)
                target = monkey.targets[item.is_divisible(monkey.test)]
            monkeys[target].items.append(item)
        monkey.number_inspects += len(monkey.items)
        monkey.items.clear()


def example_single_round(input_data: str):
    monkeys = parse_monkeys(input_data)
    execute_round(monkeys, divide_by_3=True)
    return [[item.value for item in monkey.items] for monkey in monkeys]


def part1(input_data: str):
    monkeys = parse_monkeys(input_data)
    for _ in range(20):
        execute_round(monkeys, divide_by_3=True)
    monkeys.sort(key=lambda m: m.number_inspects, reverse=True)
    return monkeys[0].number_inspects * monkeys[1].number_inspects


def part2(input_data: str):
    monkeys = parse_monkeys(input_data)
    for i in tqdm(range(10000)):
        execute_round(monkeys, divide_by_3=False)
        # if i + 1 in [1, 20] or (i + 1) % 1000 == 0:
        #     print([m.number_inspects for m in monkeys])
    monkeys.sort(key=lambda m: m.number_inspects, reverse=True)
    return monkeys[0].number_inspects * monkeys[1].number_inspects


if __name__ == '__main__':
    assert example_single_round(EXAMPLE) == [[20, 23, 27, 26], [2080, 25, 167, 207, 401, 1046], [], []]
    assert part1(EXAMPLE) == 10605
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 2713310158
    print(f'Solution for part 2 is: {part2(get_input())}')
