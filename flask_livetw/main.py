#!/usr/bin/env python
from __future__ import annotations

import argparse
from typing import Sequence

from flask_livetw import build_app, dev_server, initialize, local_install


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mods a Flask app to use TailwindCSS in a dev server like manner.",
        allow_abbrev=True,
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    build_app.add_build_command(subparsers)
    dev_server.add_dev_command(subparsers)
    initialize.add_init_command(subparsers)
    local_install.add_local_install_command(subparsers)

    return parser


def main(args: Sequence[str] | None = None) -> int:
    parsed_args = create_cli().parse_args(args)

    if parsed_args.command == "dev":
        dev_server.dev(parsed_args)
        return 0

    if parsed_args.command == "build":
        return build_app.build(parsed_args)

    if parsed_args.commad == "init":
        return initialize.init(parsed_args)

    if parsed_args.command == "local_install":
        return local_install.local_install(parsed_args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
