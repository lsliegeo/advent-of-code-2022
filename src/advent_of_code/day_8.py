from src.input_util import get_input


def parse_rows(input_data: str) -> list[list[int]]:
    rows = []
    for row in [r for r in input_data.split('\n') if r]:
        rows.append(list(map(int, row)))
    return rows


def part1(input_data: str):
    heights: list[list[int]] = parse_rows(input_data)
    visible: list[list[bool]] = [[False] * len(heights[0]) for _ in range(len(heights))]

    # Left to right
    for i, row in enumerate(heights):
        previous_highest = -1
        for j, height in enumerate(row):
            if height > previous_highest:
                visible[i][j] = True
                previous_highest = height

    # Right to left
    for i, row in enumerate(heights):
        previous_highest = -1
        for j, height in reversed(list(enumerate(row))):
            if height > previous_highest:
                visible[i][j] = True
                previous_highest = height

    # Up to down
    for j in range(len(heights[0])):
        previous_highest = -1
        for i, row in enumerate(heights):
            height = row[j]
            if height > previous_highest:
                visible[i][j] = True
                previous_highest = height

    # Down to up
    for j in range(len(heights[0])):
        previous_highest = -1
        for i, row in reversed(list(enumerate(heights))):
            height = row[j]
            if height > previous_highest:
                visible[i][j] = True
                previous_highest = height

    return sum(t for row in visible for t in row)


def part2(input_data: str):
    heights: list[list[int]] = parse_rows(input_data)
    scores: list[list[int]] = [[1] * len(heights[0]) for _ in range(len(heights))]

    # Left to right
    for i, row in enumerate(heights):
        height_to_most_recent_index = {h: None for h in range(10)}
        for j, height in enumerate(row):
            if all(index is None for index in height_to_most_recent_index.values()):
                # Near the edge
                scores[i][j] *= 0
            elif tree_indices_with_greater_or_equal_height := [
                index
                for other_height, index in height_to_most_recent_index.items()
                if index is not None and other_height >= height
            ]:
                # The view is blocked by another tree
                scores[i][j] *= j - max(tree_indices_with_greater_or_equal_height)
            else:
                # Can see from the start
                scores[i][j] *= j
            height_to_most_recent_index[heights[i][j]] = j

    # Right to left
    for i, row in enumerate(heights):
        height_to_most_recent_index = {h: None for h in range(10)}
        for j, height in reversed(list(enumerate(row))):
            if all(index is None for index in height_to_most_recent_index.values()):
                # Near the edge
                scores[i][j] *= 0
            elif tree_indices_with_greater_or_equal_height := [
                index
                for other_height, index in height_to_most_recent_index.items()
                if index is not None and other_height >= height
            ]:
                # The view is blocked by another tree
                scores[i][j] *= min(tree_indices_with_greater_or_equal_height) - j
            else:
                # Can see from the start
                scores[i][j] *= len(heights[0]) - j - 1
            height_to_most_recent_index[heights[i][j]] = j

    # Up to down
    for j in range(len(heights[0])):
        height_to_most_recent_index = {h: None for h in range(10)}
        for i, row in enumerate(heights):
            height = heights[i][j]
            if all(index is None for index in height_to_most_recent_index.values()):
                # Near the edge
                scores[i][j] *= 0
            elif tree_indices_with_greater_or_equal_height := [
                index
                for other_height, index in height_to_most_recent_index.items()
                if index is not None and other_height >= height
            ]:
                # The view is blocked by another tree
                scores[i][j] *= i - max(tree_indices_with_greater_or_equal_height)
            else:
                # Can see from the start
                scores[i][j] *= i
            height_to_most_recent_index[heights[i][j]] = i

    # Down to up
    for j in range(len(heights[0])):
        height_to_most_recent_index = {h: None for h in range(10)}
        for i, row in reversed(list(enumerate(heights))):
            height = heights[i][j]
            if all(index is None for index in height_to_most_recent_index.values()):
                # Near the edge
                scores[i][j] *= 0
            elif tree_indices_with_greater_or_equal_height := [
                index
                for other_height, index in height_to_most_recent_index.items()
                if index is not None and other_height >= height
            ]:
                # The view is blocked by another tree
                scores[i][j] *= min(tree_indices_with_greater_or_equal_height) - i
            else:
                # Can see from the start
                scores[i][j] *= len(heights) - i - 1
            height_to_most_recent_index[heights[i][j]] = i

    return max(t for row in scores for t in row)


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
