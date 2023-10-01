from __future__ import annotations

import argparse
import dataclasses
import shlex
import subprocess
from typing import Sequence

from flask_livetw.config import Config
from flask_livetw.util import Term, pkgprint, set_default_env

MINIFY_ON_BUILD = True


@dataclasses.dataclass
class BuildConfig:
    input: str
    output: str
    minify: bool


def minify_tailwind(config: BuildConfig) -> int:
    input_arg = f"-i {config.input}"

    output_arg = f"-o {config.output}"

    minify_arg = "--minify" if config.minify else ""

    command = f"tailwindcss {input_arg} {output_arg} {minify_arg}"

    pkgprint("Minifying tailwindcss for production...")

    build_result = subprocess.run(shlex.split(command))

    if build_result.returncode != 0:
        pkgprint(f"Tailwind build for production {Term.R}fail{Term.END}")
        return build_result.returncode

    pkgprint(f"Tailwind build for production {Term.G}ready{Term.END}")
    return build_result.returncode


def build(cli_args: argparse.Namespace) -> int:
    set_default_env("LIVETW_BUILD", "TRUE")

    config = Config.from_pyproject_toml()

    build_config = BuildConfig(
        input=cli_args.input or config.full_globalcss_file,
        output=cli_args.output or config.full_tailwind_minified_file,
        minify=cli_args.minify,
    )

    return minify_tailwind(build_config)


def add_command_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        type=str,
        help="Input path, accepts glob patterns.",
    )
    parser.add_argument(
        "-o", "--output", dest="output", type=str, help="Output path."
    )
    build_minify_group = parser.add_mutually_exclusive_group()
    build_minify_group.add_argument(
        "--minify", dest="minify", action="store_true", help="Minify output."
    )
    build_minify_group.add_argument(
        "--no-minify",
        dest="minify",
        action="store_false",
        help="Do not minify output.",
    )
    parser.set_defaults(minify=MINIFY_ON_BUILD)


def add_command(
    subparser: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparser.add_parser(
        name="build",
        description="""
        Build the tailwindcss of the project as a single minified css file.
        """,
        help="Build tailwindcss for production.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="""
        Build the tailwindcss of the project as a single css file.
        """,
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)

    parsed_args = parser.parse_args(args)

    return build(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
