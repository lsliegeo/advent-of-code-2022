import abc
import dataclasses
import re

from src.input_util import get_input

EXAMPLE = """Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II"""


@dataclasses.dataclass
class Valve:
    name: str
    pressure: int
    neighbours: list[str]


def parse_valves(input_data: str) -> dict[str, Valve]:
    """name to (pressure, [neighbours])"""
    valves = {}
    for line in input_data.split('\n'):
        match = re.match(r'Valve ([A-Z]+) has flow rate=(\d+); tunnels? leads? to valves? (.*)', line)
        name, rate, neighbours = match.groups()
        valve = Valve(name, int(rate), neighbours.split(', '))
        valves[valve.name] = valve
    return valves


class Backtracking(abc.ABC):

    def __init__(self, valves: dict[str, Valve]):
        self.best_score = None
        self.valves = valves
        self.valve_order = sorted({valve.name for valve in valves.values() if valve.pressure > 0}, reverse=True, key=lambda v: valves[v].pressure)

    def most_pressure(self, time: int, start_position: str, hint: int = 0) -> int:
        raise NotImplemented()


class SingleBacktracking(Backtracking):
    _upper_bound_score_calc = {
        t: [2 * n + 1 + (0 if t % 2 == 0 else 1) for n in reversed(range(t // 2))]
        for t in range(100)
    }

    def upper_bound(self, time: int, open_valves: set[str]) -> int:
        remaining_scores = [self.valves[valve].pressure for valve in self.valve_order if valve not in open_valves]
        return sum(f * s for f, s in zip(self._upper_bound_score_calc[time], remaining_scores))

    def most_pressure(self, time: int, start_position: str, hint: int = 0) -> int:
        self.best_score = hint
        open_valves = {valve.name for valve in self.valves.values() if valve.pressure == 0}
        self.backtracking(time, start_position, 0, open_valves, set())
        return self.best_score

    def backtracking(self, time: int, current_valve: str, score: int, open_valves: set[str], circling: set[str]):
        if score > self.best_score:
            self.best_score = score

        if score + self.upper_bound(time, open_valves) < self.best_score:
            return
        if time <= 0:
            return
        if current_valve in circling:
            return

        time -= 1

        # Explore
        for valve in self.valves[current_valve].neighbours:
            self.backtracking(time, valve, score, open_valves, circling | {current_valve})

        # Open
        if current_valve not in open_valves:
            # Open valve
            score += self.valves[current_valve].pressure * time
            self.backtracking(time, current_valve, score, open_valves | {current_valve}, set())


class DoubleBacktracking(Backtracking):
    _upper_bound_score_calc = {
        t: [2 * n + 1 + (0 if t % 2 == 0 else 1) for n in reversed(range(t // 2)) for _ in range(2)]
        for t in range(100)
    }

    def upper_bound(self, time: int, open_valves: set[str]) -> int:
        remaining_scores = [self.valves[valve].pressure for valve in self.valve_order if valve not in open_valves]
        return sum(f * s for f, s in zip(self._upper_bound_score_calc[time], remaining_scores))

    def most_pressure(self, time: int, start_position: str, hint: int = 0) -> int:
        self.best_score = hint
        open_valves = {valve.name for valve in self.valves.values() if valve.pressure == 0}
        self.backtracking(time, start_position, start_position, 0, open_valves, set(), set())
        return self.best_score

    def backtracking(self, time: int, current_valve_1: str, current_valve_2: str, score: int, open_valves: set[str], circling_1: set[str], circling_2: set[str]):
        if score > self.best_score:
            self.best_score = score

        if score + self.upper_bound(time, open_valves) < self.best_score:
            return
        if time <= 0:
            return
        if current_valve_1 in circling_1 or current_valve_2 in circling_2:
            return

        time -= 1

        # Explore both
        for neighbour_1 in self.valves[current_valve_1].neighbours:
            for neighbour_2 in self.valves[current_valve_2].neighbours:
                self.backtracking(time, neighbour_1, neighbour_2, score, open_valves, circling_1 | {current_valve_1}, circling_2 | {current_valve_2})

        # Open both
        if current_valve_1 != current_valve_2 and current_valve_1 not in open_valves and current_valve_2 not in open_valves:
            score_1_2 = score + time * (self.valves[current_valve_1].pressure + self.valves[current_valve_2].pressure)
            self.backtracking(time, current_valve_1, current_valve_2, score_1_2, open_valves | {current_valve_1, current_valve_2}, set(), set())

        # Open 1
        if current_valve_1 not in open_valves:
            score_1 = score + time * self.valves[current_valve_1].pressure
            for neighbour_2 in self.valves[current_valve_2].neighbours:
                self.backtracking(time, current_valve_1, neighbour_2, score_1, open_valves | {current_valve_1}, set(), circling_2 | {current_valve_2})

        # Open 2
        if current_valve_1 != current_valve_2 and current_valve_2 not in open_valves:
            score_2 = score + time * self.valves[current_valve_2].pressure
            for neighbour_1 in self.valves[current_valve_1].neighbours:
                self.backtracking(time, neighbour_1, current_valve_2, score_2, open_valves | {current_valve_2}, circling_1 | {current_valve_1}, set())


def part1(input_data: str):
    valves = parse_valves(input_data)
    return SingleBacktracking(valves).most_pressure(30, 'AA')


def part2(input_data: str):
    valves = parse_valves(input_data)
    return DoubleBacktracking(valves).most_pressure(26, 'AA')


if __name__ == '__main__':
    assert part1(EXAMPLE) == 1651
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 1707
    print(f'Solution for part 2 is: {part2(get_input())}')
