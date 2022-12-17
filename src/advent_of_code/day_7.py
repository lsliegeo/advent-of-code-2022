import dataclasses
from typing import Iterator

from src.input_util import get_input


@dataclasses.dataclass
class File:
    name: str
    size: int


@dataclasses.dataclass
class Folder:
    name: str
    parent: 'Folder'
    files: dict[str, File] = dataclasses.field(default_factory=dict)
    folders: dict[str, 'Folder'] = dataclasses.field(default_factory=dict)
    explored: bool = False
    size: int = 0

    def add_file(self, name: str, size: int):
        self.files[name] = File(name, size)
        self.size += size
        p = self
        while p := p.parent:
            p.size += size

    def add_folder(self, name: str):
        self.folders[name] = Folder(name, self)


def parse(input_data: str) -> Folder:
    root = Folder('/', None)
    head = root

    lines = [l for l in input_data.split('\n') if l]
    line_index = 1  # skipping the `cd /`

    while line_index < len(lines):
        match lines[line_index].split(' '):
            case ['$', 'ls']:
                head.explored = True
                while line_index + 1 < len(lines) and lines[line_index + 1][0] != '$':
                    line_index += 1
                    match lines[line_index].split(' '):
                        case ['dir', dir_name]:
                            head.add_folder(dir_name)
                        case [file_size, file_name]:
                            head.add_file(file_name, int(file_size))
                        case _:
                            raise Exception()

            case ['$', 'cd', '..']:
                head = head.parent

            case ['$', 'cd', dir_name]:
                head = head.folders[dir_name]

        line_index += 1

    return root


def iterate_folders(folder: Folder) -> Iterator[Folder]:
    yield folder
    for sub_folder in folder.folders.values():
        yield from iterate_folders(sub_folder)


def part1(input_data: str):
    root = parse(input_data)
    return sum(f.size for f in iterate_folders(root) if f.size <= 100000)


def part2(input_data: str):
    root = parse(input_data)
    current_free_space = 70000000 - root.size
    additional_size_needed = 30000000 - current_free_space
    return sorted([f for f in iterate_folders(root) if f.size >= additional_size_needed], key=lambda f: f.size)[0].size


if __name__ == '__main__':
    print(f'Solution for part 1 is: {part1(get_input())}')
    print(f'Solution for part 2 is: {part2(get_input())}')
