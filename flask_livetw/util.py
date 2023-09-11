import platform
import os
import dataclasses


STATIC_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'static'
)


@dataclasses.dataclass
class Resource:
    name: str
    content: str


def load_resource(name: str) -> Resource:
    with open(os.path.join(STATIC_PATH, name), 'r') as f:
        return Resource(name, f.read())


class Term:
    if platform.system() == 'Windows':
        os.system('color')

    BLACK = "\033[30m"
    R = "\033[31m"
    G = "\033[32m"
    BG = "\033[1;32m"
    Y = "\033[33m"
    B = "\033[34m"
    M = "\033[35m"
    C = "\033[36m"
    W = "\033[37m"
    END = "\033[0;0m"
    NORM = "\033[1m"
    BOLD = "\033[1m"

    @staticmethod
    def dev(*values: object, end: str = '\n', sep: str = ' '):
        print(f'{Term.M}[dev]{Term.END}', *values, end=end, sep=sep)

    @staticmethod
    def info(*values: object, end: str = '\n', sep: str = ' '):
        print(f'{Term.C}[info]{Term.END}', *values, end=end, sep=sep)

    @staticmethod
    def warn(*values: object, end: str = '\n', sep: str = ' '):
        print(f'{Term.Y}[warn]{Term.END}', *values, end=end, sep=sep)

    @staticmethod
    def error(*values: object, end: str = '\n', sep: str = ' '):
        print(f'{Term.R}[error]{Term.END}', *values, end=end, sep=sep)

    @staticmethod
    def confirm(message: str) -> bool:
        response = input(
            f'{Term.C}{message}{Term.END} [y/N] ').strip().lower()
        while True:
            if not response or response.startswith('n'):
                return False
            if response.startswith('y'):
                return True
            print(f'{Term.R}Invalid response{Term.END}')
            response = input(
                f'{Term.C}{message}{Term.END} [y/N] ').strip().lower()

    @staticmethod
    def ask_fs_entry(message: str, entry_type: str = 'file'):
        if entry_type not in ('file', 'dir'):
            raise ValueError(f'Invalid entry type: {entry_type}')

        response = input(f'{Term.C}{message}{Term.END} ').strip()

        while True:
            if not response:
                print(f'{Term.R}Invalid response{Term.END}')
                response = input(f'{Term.C}{message}{Term.END} ').strip()
                continue

            if entry_type == 'file':
                if os.path.isfile(response):
                    return response
                print(f'{Term.R}File not found{Term.END}')
                response = input(f'{Term.C}{message}{Term.END} ').strip()
                continue

            if os.path.isdir(response):
                return response
            print(f'{Term.R}Directory not found{Term.END}')
            response = input(f'{Term.C}{message}{Term.END} ').strip()
