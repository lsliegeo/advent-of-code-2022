import dataclasses

from tqdm import tqdm

from src.input_util import get_input

EXAMPLE = """1
2
-3
3
-2
0
4"""


@dataclasses.dataclass
class Node:
    value: int
    next: 'Node' = None
    prev: 'Node' = None

    def remove(self):
        self.prev.next = self.next
        self.next.prev = self.prev

    def insert_after(self, after: 'Node'):
        self.prev = after
        self.next = after.next
        self.next.prev = self
        after.next = self


@dataclasses.dataclass
class LinkedList:
    original_order: list[Node]

    def __init__(self, values: list[int]):
        self.original_order = [Node(v) for v in values]
        for i in range(self.size):
            self.original_order[i].prev = self.original_order[(i - 1) % self.size]
            self.original_order[i].next = self.original_order[(i + 1) % self.size]

    @property
    def size(self) -> int:
        return len(self.original_order)

    def move(self, node: Node, amount: int):
        to_node = node.prev
        node.remove()
        amount = amount % (self.size - 1)
        if amount < self.size // 2:
            for _ in range(amount):
                to_node = to_node.next
        else:
            amount = self.size - 1 - amount
            for _ in range(amount):
                to_node = to_node.prev
        node.insert_after(to_node)


def part1(input_data: str):
    values = [int(i) for i in input_data.split('\n')]
    ll = LinkedList(values)
    for node in tqdm(ll.original_order):
        ll.move(node, node.value)
    node = next(iter(node for node in ll.original_order if node.value == 0))
    s = 0
    for _ in range(3):
        for _ in range(1000):
            node = node.next
        s += node.value
    return s


def part2(input_data: str, decryption_key: int = 811589153, times: int = 10):
    values = [int(i) * decryption_key for i in input_data.split('\n')]
    ll = LinkedList(values)
    for _ in tqdm(range(times)):
        for node in ll.original_order:
            ll.move(node, node.value)
    node = next(iter(node for node in ll.original_order if node.value == 0))
    s = 0
    for _ in range(3):
        for _ in range(1000):
            node = node.next
        s += node.value
    return s


if __name__ == '__main__':
    assert part1(EXAMPLE) == 3
    print(f'Solution for part 1 is: {part1(get_input())}')
    assert part2(EXAMPLE) == 1623178306
    print(f'Solution for part 2 is: {part2(get_input())}')
