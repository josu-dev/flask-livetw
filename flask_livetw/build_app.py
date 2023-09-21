from __future__ import annotations

import argparse
import dataclasses
import shlex
import subprocess
from typing import Sequence

from flask_livetw.config import Config
from flask_livetw.util import Term, pkgprint

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


def build(cli: argparse.Namespace) -> int:
    config = Config.from_pyproject_toml()

    build_config = BuildConfig(
        input=cli.input or config.globalcss_file,
        output=cli.output or config.minified_twcss_file,
        minify=cli.minify,
    )

    return minify_tailwind(build_config)


def _add_cli_arguments(parser: argparse.ArgumentParser) -> None:
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


def add_build_command(
    subparser: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparser.add_parser(
        name="build",
        description="""
            Build the tailwindcss of the provided input as a single css file.
        """,
        help="Build tailwindcss for production.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    _add_cli_arguments(parser)


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the tailwindcss of the provided input as a single css file.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    _add_cli_arguments(parser)

    parsed_args = parser.parse_args(args)

    return build(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
