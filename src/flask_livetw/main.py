from __future__ import annotations

import argparse
from typing import Sequence

from flask_livetw import cmd_build, cmd_dev, cmd_init


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="livetw",
        description="CLI for flask-livetw commands.",
        allow_abbrev=True,
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    cmd_build.add_command(subparsers)

    cmd_dev.add_command(subparsers)

    cmd_init.add_command(subparsers)

    return parser


def main(args: Sequence[str] | None = None) -> int:
    parsed_args = create_cli().parse_args(args)

    if parsed_args.command == "dev":
        return cmd_dev.dev(parsed_args)

    if parsed_args.command == "build":
        return cmd_build.build(parsed_args)

    if parsed_args.command == "init":
        return cmd_init.init(parsed_args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
