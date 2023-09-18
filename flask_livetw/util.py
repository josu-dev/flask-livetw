import dataclasses
import os
import platform
from typing import Callable, Union


STATIC_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "static"
)


@dataclasses.dataclass
class Resource:
    name: str
    content: str


def load_resource(name: str) -> Resource:
    with open(os.path.join(STATIC_PATH, name), "r") as f:
        return Resource(name, f.read())


class Term:
    if platform.system() == "Windows":
        os.system("color")

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
    def info(*values: object, end: str = "\n", sep: str = " ") -> None:
        print(f"{Term.C}[info]{Term.END}", *values, end=end, sep=sep)

    @staticmethod
    def warn(*values: object, end: str = "\n", sep: str = " ") -> None:
        print(f"{Term.Y}[warn]{Term.END}", *values, end=end, sep=sep)

    @staticmethod
    def error(*values: object, end: str = "\n", sep: str = " ") -> None:
        print(f"{Term.R}[error]{Term.END}", *values, end=end, sep=sep)

    @staticmethod
    def blank(end: str = "\n") -> None:
        print(end=end)

    @staticmethod
    def confirm(message: str) -> bool:
        response = input(f"{message} [y/N] ").strip().lower()
        while True:
            if not response or response.startswith("n"):
                return False
            if response.startswith("y"):
                return True
            print(f"{Term.R}Invalid response{Term.END}")
            response = (
                input(f"{Term.C}{message}{Term.END} [y/N] ").strip().lower()
            )

    @staticmethod
    def ask(
        message: str, validator: Union[None, Callable[[str], bool]] = None
    ) -> str:
        while True:
            response = input(message).strip()
            if not validator or validator(response):
                return response

            Term.info(f"Invalid response: {response}")

    @staticmethod
    def ask_file(message: str, base_dir: Union[str, None] = None) -> str:
        file = input(message).strip()

        while True:
            if not file:
                print("Please enter a non-empty file path")
                file = input(message).strip()
                continue

            full_path = f"{base_dir}/{file}" if base_dir else file
            if os.path.isfile(full_path):
                return file

            Term.error(f"File not found: {full_path}")
            file = input(message).strip()

    @staticmethod
    def ask_dir(
        message: str,
        base_dir: Union[str, None] = None,
        default: Union[str, None] = None,
    ) -> str:
        dir = input(message).strip()

        while True:
            if not default and not dir:
                print("Please enter a non-empty dir path")
                dir = input(message).strip()
                continue

            if default and not dir:
                full_path = f"{base_dir}/{default}" if base_dir else default

                if os.path.isdir(full_path):
                    return default
                Term.error(f"'{full_path}' is not a dir")
                dir = input(message).strip()
                continue

            full_path = f"{base_dir}/{dir}" if base_dir else dir
            if os.path.isdir(full_path):
                return dir

            Term.error(f"'{full_path}' is not a dir")
            dir = input(message).strip()
