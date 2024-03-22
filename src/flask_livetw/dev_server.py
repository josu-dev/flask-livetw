from __future__ import annotations

import argparse
import asyncio
import concurrent.futures
import dataclasses
import datetime
import json
import shlex
import subprocess
from typing import Sequence, Set

import websockets.legacy.protocol as ws_protocol
import websockets.server as ws_server

from flask_livetw.config import Config
from flask_livetw.util import Term, pkgprint, set_default_env

FLASK_BASE_EXCLUDE_PATTERNS = ("*/**/dev.py",)

LR_CONNECTIONS: Set[ws_server.WebSocketServerProtocol] = set()


async def handle_connection(websocket: ws_server.WebSocketServerProtocol):
    LR_CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        LR_CONNECTIONS.remove(websocket)


async def live_reload_server(host: str, port: int):
    async with ws_server.serve(handle_connection, host, port) as server:
        pkgprint(
            f"Live reload {Term.G}ready{Term.END} on {Term.C}ws://{host}:{Term.BOLD}{port}{Term.END}"
        )

        await server.wait_closed()

        pkgprint(f"Live reload {Term.G}closed{Term.END}")


def handle_tailwind_output(process: subprocess.Popen[bytes]):
    if process.stdout is None:
        return

    for line in iter(process.stdout.readline, b""):
        if process.poll() is not None:
            break

        if line.startswith(b"Done"):
            ws_protocol.broadcast(
                LR_CONNECTIONS,
                json.dumps(
                    {
                        "type": "TRIGGER_FULL_RELOAD",
                        "data": datetime.datetime.now().isoformat(),
                    }
                ),
            )

        print(f'{Term.C}[twcss]{Term.END} {line.decode("utf-8")}', end="")


def handle_flask_output(process: subprocess.Popen[bytes]):
    if process.stdout is None:
        return

    for line in iter(process.stdout.readline, b""):
        if process.poll() is not None:
            break

        print(f'{Term.G}[flask]{Term.END} {line.decode("utf-8")}', end="")


@dataclasses.dataclass
class DevConfig:
    no_live_reload: bool
    live_reload_host: str
    live_reload_port: int

    no_flask: bool
    flask_host: str | None
    flask_port: int | None
    flask_mode: str
    flask_exclude_patterns: Sequence[str] | None

    no_tailwind: bool
    tailwind_input: str | None
    tailwind_output: str
    tailwind_minify: bool


async def dev_server(config: DevConfig):
    def live_reload_coroutine():
        if config.no_live_reload or config.no_tailwind:
            return None

        host = config.live_reload_host
        port = config.live_reload_port

        return live_reload_server(host, port)

    def tailwind_cli_executor(
        loop: asyncio.AbstractEventLoop,
        pool: concurrent.futures.ThreadPoolExecutor,
    ):
        if config.no_tailwind:
            return None

        input_arg = ""
        if config.tailwind_input is not None:
            input_arg = f"-i {config.tailwind_input}"

        output_arg = f"-o {config.tailwind_output}"

        minify_arg = "--minify" if config.tailwind_minify else ""

        cmd = f"tailwindcss --watch {input_arg} {output_arg} {minify_arg}"

        process = subprocess.Popen(
            shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        return loop.run_in_executor(pool, handle_tailwind_output, process)

    def flask_server_executor(
        loop: asyncio.AbstractEventLoop,
        pool: concurrent.futures.ThreadPoolExecutor,
    ):
        if config.no_flask:
            return None

        host_arg = ""
        if config.flask_host is not None:
            host_arg = f"--host {config.flask_host}"

        port_arg = ""
        if config.flask_port is not None:
            port_arg = f"--port {config.flask_port}"

        debug_arg = "--debug" if config.flask_mode == "debug" else ""

        exclude_patterns: list[str] = list(FLASK_BASE_EXCLUDE_PATTERNS)
        if config.flask_exclude_patterns is not None:
            exclude_patterns.extend(config.flask_exclude_patterns)

        exclude_patterns_arg = (
            f"--exclude-patterns {';'.join(exclude_patterns)}"
        )

        cmd = f"\
            flask run {host_arg} {port_arg} {debug_arg} {exclude_patterns_arg}"

        process = subprocess.Popen(
            shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        return loop.run_in_executor(pool, handle_flask_output, process)

    loop = asyncio.get_running_loop()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        maybe_future_like = (
            live_reload_coroutine(),
            tailwind_cli_executor(loop, pool),
            flask_server_executor(loop, pool),
        )

        futures = (
            future for future in maybe_future_like if future is not None
        )

        pkgprint("Starting dev server...")

        _ = await asyncio.gather(*futures, return_exceptions=True)


def dev(cli_args: argparse.Namespace) -> int:
    set_default_env("LIVETW_DEV", "TRUE")

    project_config = Config.try_from_pyproject_toml()
    if project_config is None:
        pkgprint(
            "Project config not found. Dev server not started.",
        )
        pkgprint(
            "Try checking your current working directory or running 'flask-livetw init' to configure the project."
        )
        return 1

    no_live_reload = cli_args.no_live_reload
    live_reload_host = (
        cli_args.live_reload_host or project_config.live_reload_host
    )
    live_reload_port = (
        cli_args.live_reload_port or project_config.live_reload_port
    )

    no_flask = cli_args.no_flask
    flask_host = cli_args.flask_host or project_config.flask_host
    flask_port = cli_args.flask_port or project_config.flask_port
    flask_mode = cli_args.flask_mode
    flask_exclude_patterns = (
        cli_args.flask_exclude_patterns
        or project_config.flask_exclude_patterns
    )

    no_tailwind = cli_args.no_tailwind
    tailwind_input = (
        cli_args.tailwind_input or project_config.full_globalcss_file
    )
    tailwind_output = (
        cli_args.tailwind_output or project_config.full_tailwind_file
    )
    tailwind_minify = cli_args.tailwind_minify

    dev_config = DevConfig(
        no_live_reload=no_live_reload,
        live_reload_host=live_reload_host,
        live_reload_port=live_reload_port,
        no_flask=no_flask,
        flask_host=flask_host,
        flask_port=flask_port,
        flask_mode=flask_mode,
        flask_exclude_patterns=flask_exclude_patterns,
        no_tailwind=no_tailwind,
        tailwind_input=tailwind_input,
        tailwind_output=tailwind_output,
        tailwind_minify=tailwind_minify,
    )

    asyncio.run(dev_server(dev_config))
    return 0


def add_command_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--no-live-reload",
        dest="no_live_reload",
        action="store_true",
        default=False,
        help="Disable live reload server.",
    )
    parser.add_argument(
        "-lrh",
        "--live-reload-host",
        dest="live_reload_host",
        type=str,
        help="Hostname for live reload server.",
    )
    parser.add_argument(
        "-lrp",
        "--live-reload-port",
        dest="live_reload_port",
        type=int,
        help="Port for live reload server.",
    )

    parser.add_argument(
        "--no-flask",
        dest="no_flask",
        action="store_true",
        default=False,
        help="Disable flask server.",
    )
    parser.add_argument(
        "-fh",
        "--flask-host",
        dest="flask_host",
        type=str,
        help="Hostname for flask server.",
    )
    parser.add_argument(
        "-fp",
        "--flask-port",
        dest="flask_port",
        type=int,
        help="Port for flask server.",
    )
    parser.add_argument(
        "-fm",
        "--flask-mode",
        dest="flask_mode",
        choices=("debug", "no-debug"),
        default="debug",
        help="If debug mode is enabled, the flask server will be started with --debug flag. Default: debug.",
    )
    parser.add_argument(
        "--flask-exclude-patterns",
        dest="flask_exclude_patterns",
        type=str,
        nargs="+",
        help="File exclude patterns for flask server. Base: */**/dev.py",
    )

    parser.add_argument(
        "--no-tailwind",
        dest="no_tailwind",
        action="store_true",
        default=False,
        help="Disable tailwindcss generation. If tailwindcss is disabled the live reload server will not be started.",
    )
    parser.add_argument(
        "-ti",
        "--tailwind-input",
        dest="tailwind_input",
        type=str,
        help="Input path for global css file. Includes glob patterns.",
    )
    parser.add_argument(
        "-to",
        "--tailwind-output",
        dest="tailwind_output",
        type=str,
        help="Output path for the generated css file.",
    )
    parser.add_argument(
        "-tm",
        "--tailwind-minify",
        dest="tailwind_minify",
        action="store_true",
        default=False,
        help="Enables minification of the generated css file.",
    )


def add_command(
    subparser: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparser.add_parser(
        name="dev",
        description="""
        Extended dev mode for flask apps.
        By default runs the flask app in debug mode,
        tailwindcss in watch mode and live reload server.
        """,
        help="Run a development server.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="""
        Extended dev mode for flask apps.
        By default runs the flask app in debug mode,
        tailwindcss in watch mode and live reload server.
        """,
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)

    parsed_args = parser.parse_args(args)

    return dev(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
