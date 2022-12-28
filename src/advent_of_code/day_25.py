import math

from src.input_util import get_input

EXAMPLE = """1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122"""

_snafu_char_to_int = {
    '2': 2,
    '1': 1,
    '0': 0,
    '-': -1,
    '=': -2,
}


def int_to_snafu(value: int) -> str:
    result = ''
    remaining_value = value
    leftmost_position_index = round(math.log(remaining_value, 5))
    for i in reversed(range(leftmost_position_index + 1)):
        _, best_char = min((abs(remaining_value - v * 5 ** i), c) for c, v in _snafu_char_to_int.items())
        result += best_char
        remaining_value -= _snafu_char_to_int[best_char] * 5 ** i
    return result


def snafu_to_int(value: str) -> int:
    result = 0
    for i, c in enumerate(reversed(value)):
        result += _snafu_char_to_int[c] * 5 ** i
    return result


def verify_table(table: str):
    header_a, header_b = [h.lower() for h in table.split('\n')[0].strip().split(' ') if h]
    for line in table.split('\n')[1:]:
        a, b = [v for v in line.strip().split(' ') if v]
        snafu, decimal = (a, b) if header_a == 'snafu' else (b, a)
        decimal = int(decimal)
        assert int_to_snafu(decimal) == snafu
        assert snafu_to_int(snafu) == decimal


def part1(input_data: str):
    return int_to_snafu(sum(snafu_to_int(line) for line in input_data.split('\n')))


def part2(input_data: str):
    pass


if __name__ == '__main__':
    verify_table("""  Decimal          SNAFU
        1              1
        2              2
        3             1=
        4             1-
        5             10
        6             11
        7             12
        8             2=
        9             2-
       10             20
       15            1=0
       20            1-0
     2022         1=11-2
    12345        1-0---0
314159265  1121-1110-1=0""")
    verify_table(""" SNAFU  Decimal
1=-0-2     1747
 12111      906
  2=0=      198
    21       11
  2=01      201
   111       31
 20012     1257
   112       32
 1=-1=      353
  1-12      107
    12        7
    1=        3
   122       37""")
    assert snafu_to_int('2=-1=0') == 4890
    assert int_to_snafu(8) == '2='
    assert int_to_snafu(10) == '20'
    assert int_to_snafu(4890) == '2=-1=0'
    assert part1(EXAMPLE) == '2=-1=0'
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == None
    print(f'Solution for part 2 is: {part2(get_input())}')
