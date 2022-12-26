import dataclasses
import math
import re
from enum import Enum

from tqdm import tqdm

from src.input_util import get_input
from src.timer_util import ContextTimer

EXAMPLE = """Blueprint 1:
  Each ore robot costs 4 ore.
  Each clay robot costs 2 ore.
  Each obsidian robot costs 3 ore and 14 clay.
  Each geode robot costs 2 ore and 7 obsidian.

Blueprint 2:
  Each ore robot costs 2 ore.
  Each clay robot costs 3 ore.
  Each obsidian robot costs 3 ore and 8 clay.
  Each geode robot costs 3 ore and 12 obsidian."""


class Item(Enum):
    ORE = 'ore'
    CLAY = 'clay'
    OBSIDIAN = 'obsidian'
    GEODE = 'geode'


@dataclasses.dataclass
class Blueprint:
    id: int
    cost: dict[Item, dict[Item, int]]


@dataclasses.dataclass(frozen=True)
class State:
    items: dict[Item, int]
    robots: dict[Item, int]
    blueprint: Blueprint

    def can_make_robots(self, item: Item) -> int:
        return max(0, min(self.items[t] // c for t, c in self.blueprint.cost[item].items()))

    def turns_to_make_robot(self, item: Item) -> int:
        return max(math.ceil(max(0, (c - self.items[t])) / self.robots[t]) for t, c in self.blueprint.cost[item].items())

    def add_ore_robot(self, item: Item, n: int = 1) -> 'State':
        return dataclasses.replace(
            self,
            items={i: self.items[i] - self.blueprint.cost[item].get(i, 0) * n for i in Item},
            robots={i: v + n if i == item else v for i, v in self.robots.items()}
        )

    def advance_resources(self, n: int = 1) -> 'State':
        return dataclasses.replace(
            self,
            items={i: self.items[i] + self.robots[i] * n for i in Item}
        )

    def __repr__(self):
        return f'Items: [{", ".join(str(self.items[i]) for i in Item)}], Robots: [{", ".join(str(self.robots[i]) for i in Item)}]'


def example_to_input(input_data: str) -> str:
    return '\n'.join([s.replace('\n', '').replace('  ', ' ') for s in input_data.split('\n\n')])


def parse_blueprints(input_data: str) -> list[Blueprint]:
    blueprints = []
    for line in input_data.split('\n'):
        match = re.match(r'Blueprint (\d+): Each ore robot costs (\d+) ore. Each clay robot costs (\d+) ore. Each obsidian robot costs (\d+) ore and (\d+) clay. Each geode robot costs (\d+) ore and (\d+) obsidian.', line)
        blueprints.append(Blueprint(
            int(match.group(1)),
            {
                Item.ORE: {Item.ORE: int(match.group(2))},
                Item.CLAY: {Item.ORE: int(match.group(3))},
                Item.OBSIDIAN: {Item.ORE: int(match.group(4)), Item.CLAY: int(match.group(5))},
                Item.GEODE: {Item.ORE: int(match.group(6)), Item.OBSIDIAN: int(match.group(7))},
            }
        ))
    return blueprints


class Backtracking:

    def __init__(self, blueprint: Blueprint):
        self.blueprint = blueprint
        self.max_geodes = 0

    def best_score(self, time: int) -> int:
        state = State({item: 0 for item in Item}, {item: 0 for item in Item} | {Item.ORE: 1}, self.blueprint)
        self.max_geodes = 0
        for i in self.robot_order(state, time):
            self._explore(state, time, 0, i)
        return self.max_geodes

    @staticmethod
    def robot_order(state: State, time: int) -> list[Item]:
        if time < 2:
            return []
        order = []

        if state.robots[Item.OBSIDIAN]:
            # We have obsidian generation -> try geode
            order.append(Item.GEODE)
        if state.robots[Item.CLAY]:
            # We have clay generation -> try obsidian
            order.append(Item.OBSIDIAN)

        if order:
            order += [Item.CLAY, Item.ORE]
        else:
            if state.robots[Item.ORE] <= min(d[Item.ORE] for d in state.blueprint.cost.values()):
                # Prioritize ore
                order += [Item.ORE, Item.CLAY]
            else:
                order += [Item.CLAY, Item.ORE]

        return order

    @classmethod
    def upper_bound(cls, state: State, time: int) -> int:
        if time < 2:
            return 0
        if state.can_make_robots(Item.GEODE):
            return sum(range(time))
        if state.advance_resources().can_make_robots(Item.GEODE):
            return sum(range(time - 1))
        return sum(range(time - 2))

    def _explore(self, state: State, time: int, score: int, item: Item):
        if score > self.max_geodes:
            self.max_geodes = score
            # print(f'{self.max_geodes}: [{state.robots[Item.ORE]}, {state.robots[Item.CLAY]}, {state.robots[Item.OBSIDIAN]}, {state.robots[Item.GEODE]}]')

        if time <= 1:
            return

        turns_needed = state.turns_to_make_robot(item)
        time -= turns_needed
        state = state.advance_resources(turns_needed + 1).add_ore_robot(item)
        if item == item.GEODE:
            score += time - 1
            if score > self.max_geodes:
                self.max_geodes = score
        if score + self.upper_bound(state, time - 1) > self.max_geodes:
            for next_item in self.robot_order(state, time - 1):
                self._explore(state, time - 1, score, next_item)


def part1(input_data: str):
    blueprints = parse_blueprints(input_data)
    return sum(b.id * Backtracking(b).best_score(24) for b in tqdm(blueprints))


def part2(input_data: str):
    blueprints = parse_blueprints(input_data)
    values = [Backtracking(b).best_score(32) for b in tqdm(blueprints[:3])]
    return values[0] * values[1] * values[2]


if __name__ == '__main__':
    with ContextTimer():
        assert Backtracking(parse_blueprints(example_to_input(EXAMPLE))[0]).best_score(24) == 9
    with ContextTimer():
        assert Backtracking(parse_blueprints(example_to_input(EXAMPLE))[1]).best_score(24) == 12  # a couple of seconds
    with ContextTimer():
        assert part1(example_to_input(EXAMPLE)) == 33  # a couple of seconds
    print(f'Solution for part 1 is: {part1(get_input())}')  # takes about a minute and a half
    with ContextTimer():
        assert Backtracking(parse_blueprints(example_to_input(EXAMPLE))[0]).best_score(32) == 56  # about 15 seconds
    # with ContextTimer():
    #     assert Backtracking(parse_blueprints(example_to_input(EXAMPLE))[1]).best_score(32) == 62  # takes long?
    print(f'Solution for part 2 is: {part2(get_input())}')  # takes about two minutes
