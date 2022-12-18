import dataclasses

from src.input_util import get_input

EXAMPLE = """addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop"""

EXAMPLE_PART_2 = """
"""


@dataclasses.dataclass
class CPU:
    instructions: list[str]
    X: int = 1
    cycle: int = 0
    signal_strength: int = 0
    _instruction_index: int = 0
    _instruction_cycle: int = 0
    _pixels: list[str] = dataclasses.field(default_factory=list)
    line_width: int = 40

    def run(self):
        while self.can_advance():
            self.advance()

    def can_advance(self) -> bool:
        return self._instruction_index < len(self.instructions)

    def advance(self):
        self.update_crt()
        self.cycle += 1
        self.update_signal_strength()

        match self.instructions[self._instruction_index].split(' '):
            case ['noop']:
                self.current_instruction_finished()
            case ['addx', number_str]:
                if self._instruction_cycle == 0:
                    self._instruction_cycle += 1
                else:
                    self.X += int(number_str)
                    self.current_instruction_finished()
            case _:
                raise ValueError()

    def current_instruction_finished(self):
        self._instruction_index += 1
        self._instruction_cycle = 0

    def update_signal_strength(self):
        if (self.cycle - 20) % 40 == 0:
            self.signal_strength += self.X * self.cycle

    def update_crt(self):
        self._pixels.append('#' if abs(self.X - self.cycle % self.line_width) < 2 else '.')

    @property
    def picture(self) -> str:
        return '\n'.join(''.join(self._pixels[batch_start:batch_start + self.line_width]) for batch_start in range(0, len(self._pixels), self.line_width))


def mini_example() -> int:
    cpu = CPU(['noop', 'addx 3', 'addx -5', ])
    cpu.run()
    return cpu.X


def part1(input_data: str):
    cpu = CPU(input_data.split('\n'))
    cpu.run()
    return cpu.signal_strength


def part2(input_data: str):
    cpu = CPU(input_data.split('\n'))
    cpu.run()
    return cpu.picture


if __name__ == '__main__':
    assert mini_example() == -1
    assert part1(EXAMPLE) == 13140
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == """##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######....."""
    print(f'Solution for part 2 is:\n{part2(get_input())}')
