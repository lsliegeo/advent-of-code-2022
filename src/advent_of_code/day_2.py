from enum import IntEnum

from src.input_util import get_input


class Result(IntEnum):
    WIN = 6
    DRAW = 3
    LOSS = 0

    @staticmethod
    def from_char(v: str) -> 'Result':
        match v:
            case 'X':
                return Result.LOSS
            case 'Y':
                return Result.DRAW
            case 'Z':
                return Result.WIN
            case _:
                raise ValueError()


class RPC(IntEnum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @staticmethod
    def from_char(v: str) -> 'RPC':
        match v:
            case 'A' | 'X':
                return RPC.ROCK
            case 'B' | 'Y':
                return RPC.PAPER
            case 'C' | 'Z':
                return RPC.SCISSORS
            case _:
                raise ValueError()


def this_beats_that(this: RPC) -> RPC:
    """input: this, output: that"""
    if this == RPC.ROCK:
        return RPC.SCISSORS
    elif this == RPC.SCISSORS:
        return RPC.PAPER
    else:
        return RPC.ROCK


def round_result(me: RPC, other: RPC) -> Result:
    if this_beats_that(me) == other:
        return Result.WIN
    elif me == other:
        return Result.DRAW
    else:
        return Result.LOSS


def score_for_round(me: RPC, other: RPC) -> int:
    return me.value + round_result(me, other).value


def what_should_i_pick(other: RPC, result: Result) -> RPC:
    if result == Result.DRAW:
        return other
    move_that_looses = this_beats_that(other)
    if result == Result.LOSS:
        return move_that_looses
    else:
        return this_beats_that(move_that_looses)


def part1(input_data: str) -> int:
    total_score = 0
    for line in input_data.split('\n'):
        if line:
            other, me = RPC.from_char(line[0]), RPC.from_char(line[2])
            total_score += score_for_round(me, other)
    return total_score


def part2(input_data: str) -> int:
    total_score = 0
    for line in input_data.split('\n'):
        if line:
            other, result = RPC.from_char(line[0]), Result.from_char(line[2])
            me = what_should_i_pick(other, result)
            total_score += score_for_round(me, other)
    return total_score


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
