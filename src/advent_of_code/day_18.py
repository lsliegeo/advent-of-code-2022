from src.input_util import get_input

EXAMPLE = """2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5"""


def parse(input_data: str, shift: bool) -> tuple[set[tuple[int, int, int]], int, int, int]:
    # Parse
    positions = {tuple(int(i) for i in line.split(',')) for line in input_data.split('\n')}
    min_x, max_x = min(p[0] for p in positions), max(p[0] for p in positions)
    min_y, max_y = min(p[1] for p in positions), max(p[1] for p in positions)
    min_z, max_z = min(p[2] for p in positions), max(p[2] for p in positions)

    if shift:
        # Shift to O ... n
        positions = {(x - min_x, y - min_y, z - min_z) for x, y, z in positions}
        min_x, max_x = min(p[0] for p in positions), max(p[0] for p in positions)
        min_y, max_y = min(p[1] for p in positions), max(p[1] for p in positions)
        min_z, max_z = min(p[2] for p in positions), max(p[2] for p in positions)

    return positions, max_x, max_y, max_z


def part1(input_data: str):
    positions, max_x, max_y, max_z = parse(input_data, shift=True)

    surfaces = [[[0] * (max_z + 1) for _ in range(max_y + 1)] for _ in range(max_x + 1)]
    for x, y, z in positions:
        surfaces[x][y][z] += 6
        if x > 0:
            surfaces[x - 1][y][z] -= 1
        if y > 0:
            surfaces[x][y - 1][z] -= 1
        if z > 0:
            surfaces[x][y][z - 1] -= 1
        if x < max_x:
            surfaces[x + 1][y][z] -= 1
        if y < max_y:
            surfaces[x][y + 1][z] -= 1
        if z < max_z:
            surfaces[x][y][z + 1] -= 1

    return sum(s for rows in surfaces for columns in rows for s in columns if s > 0)


def part2(input_data: str):
    positions, max_x, max_y, max_z = parse(input_data, shift=False)

    # Check what the fresh air can reach
    can_reach_fresh_air = set()
    to_check = [(x, y, max_z) for x in range(max_x + 1) for y in range(max_y + 1)]
    while to_check:
        x, y, z = to_check.pop()
        if (x, y, z) in can_reach_fresh_air:
            continue
        can_reach_fresh_air.add((x, y, z))

        if (x, y, z) not in positions:
            if x > 0:
                to_check.append((x - 1, y, z))
            if y > 0:
                to_check.append((x, y - 1, z))
            if z > 0:
                to_check.append((x, y, z - 1))
            if x < max_x:
                to_check.append((x + 1, y, z))
            if y < max_y:
                to_check.append((x, y + 1, z))
            if z < max_z:
                to_check.append((x, y, z + 1))

    # Regular
    surfaces = [[[0] * (max_z + 1) for _ in range(max_y + 1)] for _ in range(max_x + 1)]
    for x, y, z in positions:
        surfaces[x][y][z] += 6
        if x > 0:
            surfaces[x - 1][y][z] -= 1
        if y > 0:
            surfaces[x][y - 1][z] -= 1
        if z > 0:
            surfaces[x][y][z - 1] -= 1
        if x < max_x:
            surfaces[x + 1][y][z] -= 1
        if y < max_y:
            surfaces[x][y + 1][z] -= 1
        if z < max_z:
            surfaces[x][y][z + 1] -= 1

    # For every isolated piece of air, subtract 1 of each of its neighbours
    for x, y, z in {(x, y, z) for x in range(max_x + 1) for y in range(max_y + 1) for z in range(max_z + 1)} - can_reach_fresh_air - positions:
        if x > 0:
            surfaces[x - 1][y][z] -= 1
        if y > 0:
            surfaces[x][y - 1][z] -= 1
        if z > 0:
            surfaces[x][y][z - 1] -= 1
        if x < max_x:
            surfaces[x + 1][y][z] -= 1
        if y < max_y:
            surfaces[x][y + 1][z] -= 1
        if z < max_z:
            surfaces[x][y][z + 1] -= 1

    return sum(s for rows in surfaces for columns in rows for s in columns if s > 0)


if __name__ == '__main__':
    assert part1(EXAMPLE) == 64
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 58
    print(f'Solution for part 2 is: {part2(get_input())}')
