import re
from collections import defaultdict
from typing import Iterable

from tqdm import tqdm

from src.input_util import get_input

EXAMPLE = """Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3"""


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


def calculate_overlap(x1: int, y1: int, d1: int, x2: int, y2: int, d2: int) -> int:
    overlap = 0

    # order so 1 is the smallest
    if d1 > d2:
        x1, y1, d1, x2, y2, d2 = x2, y2, d2, x1, y1, d1

    for x_offset in range(-d1, d1 + 1):
        has_match = False
        for y_offset in range(-d1 + abs(x_offset), d1 - abs(x_offset) + 1):
            x, y = x1 + x_offset, y1 + y_offset
            if manhattan_distance(x, y, x2, y2) <= d2:
                has_match = True
                overlap += 1
            elif has_match:
                break

    return overlap


def total_unavailable_spots(input_data: str) -> int:
    sensors_and_distances: list[tuple[int, int, int]] = []
    for line in input_data.split('\n'):
        match = re.match(r'Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)', line)
        sensor_x, sensor_y, beacon_x, beacon_y = map(int, match.groups())
        sensors_and_distances.append((sensor_x, sensor_y, manhattan_distance(sensor_x, sensor_y, beacon_x, beacon_y)))

    unavailable_spots = sum(sum(range(n + 1)) * n for _, _, n in sensors_and_distances)
    for i in range(len(sensors_and_distances)):
        for j in range(len(sensors_and_distances)):
            if i != j:
                unavailable_spots -= calculate_overlap(*sensors_and_distances[i], *sensors_and_distances[j])

    return unavailable_spots


def part1(input_data: str, y: int) -> int:
    unavailable_spots = 0

    # Parse
    sensors_and_distances: list[tuple[int, int, int]] = []
    beacon_xs = set()
    for line in input_data.split('\n'):
        match = re.match(r'Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)', line)
        sensor_x, sensor_y, beacon_x, beacon_y = map(int, match.groups())
        sensors_and_distances.append((sensor_x, sensor_y, manhattan_distance(sensor_x, sensor_y, beacon_x, beacon_y)))
        if beacon_y == y:
            beacon_xs.add(beacon_x)

    # Loop over the line
    # Starting from min(sensor x - sensor distance) to max(sensor x + sensor distance)
    min_x, max_x = min(t[0] - t[2] for t in sensors_and_distances), max(t[0] + t[2] for t in sensors_and_distances)
    for x in tqdm(range(min_x, max_x + 1), desc=f'Iterating y={y}'):
        if x in beacon_xs:
            # Could be there's already a beacon from the input data on the line
            continue
        for sensor_x, sensor_y, sensor_distance in sensors_and_distances:
            if sensor_y == y or manhattan_distance(x, y, sensor_x, sensor_y) <= sensor_distance:
                # Check for overlap with all sensors
                # Could be a sensor is on this point
                # Could be a sensor's range overlaps with this point
                unavailable_spots += 1
                break

    return unavailable_spots


def tuning_frequency(x: int, y: int) -> int:
    return 4000000 * x + y


def sensor_boundaries(x: int, y: int, d: int) -> Iterable[tuple[int, int]]:
    yield x - d - 1, y
    yield x + d + 1, y
    for offset in range(-d, d + 1):
        yield x + offset, y + d - abs(offset) + 1
        yield x + offset, y - d + abs(offset) - 1


def part2(input_data: str, max_co: int) -> int:
    # Parse
    sensors_and_distances: list[tuple[int, int, int]] = []
    for line in input_data.split('\n'):
        match = re.match(r'Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)', line)
        sensor_x, sensor_y, beacon_x, beacon_y = map(int, match.groups())
        distance = manhattan_distance(sensor_x, sensor_y, beacon_x, beacon_y)
        sensors_and_distances.append((sensor_x, sensor_y, distance))

    # Positions that lie just outside a sensor's range + how many times that position occurs
    relevant_positions: dict[tuple[int, int], int] = defaultdict(int)
    for sensor_x, sensor_y, distance in tqdm(sensors_and_distances, desc='Processing signals'):
        for x, y in sensor_boundaries(sensor_x, sensor_y, distance):
            if 0 <= x <= max_co and 0 <= y <= max_co:
                relevant_positions[x, y] += 1

    # For every relevant position, check whether the beacon could lie there
    for (x, y), c in tqdm(relevant_positions.items(), desc='Checking positions'):
        # Since there's only one beacon, it has to be adjacent to the border of a sensor from all sides
        if c >= 4 and all(manhattan_distance(x, y, sensor_x, sensor_y) > sensor_distance for sensor_x, sensor_y, sensor_distance in sensors_and_distances):
            return tuning_frequency(x, y)

    raise Exception("Couldn't find a possible position for the beacon")


if __name__ == '__main__':
    assert calculate_overlap(2, -5, 5, 0, 0, 4) == 11
    assert part1(EXAMPLE, 10) == 26
    print(f'Solution for part 1 is: {part1(get_input(), 2000000)}')
    assert set(sensor_boundaries(2, 0, 2)) == {(-1, 0), (0, -1), (1, -2), (2, -3), (3, -2), (4, -1), (5, 0), (4, 1), (3, 2), (2, 3), (1, 2), (0, 1)}
    assert part2(EXAMPLE, 20) == 56000011
    print(f'Solution for part 2 is: {part2(get_input(), 4000000)}')
