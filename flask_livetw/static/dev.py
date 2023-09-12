#!/usr/bin/env python

import argparse
import asyncio
import concurrent.futures
import datetime
import json
import os
import platform
import shlex
import subprocess
from typing import Set, Union

import dotenv
import websockets.legacy.protocol as ws_protocol
import websockets.server as ws_server


# docs:
# - https://websockets.readthedocs.io/en/stable/intro/tutorial2.html
# - https://websockets.readthedocs.io/en/stable/reference/asyncio/server.html

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
    NORMAL = "\033[1m"
    BOLD = "\033[1m"


def dev_print(*values: object):
    print(f'{Term.M}[dev]{Term.END}', *values)


def int_or_default(value: Union[str, None], default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


dotenv.load_dotenv()

LRWS_HOST = os.getenv('LIVE_RELOAD_WS_HOST', '127.0.0.1')
LRWS_PORT = int_or_default(os.getenv('LIVE_RELOAD_WS_PORT'), 5678)
TW_WATCH_PATH = os.getenv('TW_WATCH_PATH')
TW_OUTPUT_PATH = os.getenv(
    'TW_OUTPUT_PATH', '{tailwind_output_placeholder}'
)
TW_OUTPUT_PATH_BUILD = os.getenv(
    'TW_OUTPUT_PATH_BUILD', '{minified_tailwind_output_placeholder}'
)


LR_CONNECTIONS: Set[ws_server.WebSocketServerProtocol] = set()


async def handle_connection(websocket: ws_server.WebSocketServerProtocol):
    LR_CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        LR_CONNECTIONS.remove(websocket)


async def live_reload_server(host: str, port: int):
    async with ws_server.serve(handle_connection, host, port) as server:
        dev_print(
            f'Live reload {Term.G}ready{Term.END} on {Term.C}ws://{host}:{Term.BOLD}{port}{Term.END}')

        await server.wait_closed()

        dev_print(f'Live reload {Term.G}closed{Term.END}')


def handle_tw_output(process: 'subprocess.Popen[bytes]'):
    if process.stdout is None:
        return

    for line in iter(process.stdout.readline, b''):
        if process.poll() is not None:
            break

        if (line.startswith(b'Done')):
            ws_protocol.broadcast(LR_CONNECTIONS, json.dumps({
                "type": "TRIGGER_FULL_RELOAD",
                "data": datetime.datetime.now().isoformat()
            }))

        print(f'{Term.C}[twcss]{Term.END} {line.decode("utf-8")}', end='')


def handle_flask_output(process: 'subprocess.Popen[bytes]'):
    if process.stdout is None:
        return

    for line in iter(process.stdout.readline, b''):
        if process.poll() is not None:
            break

        print(f'{Term.G}[flask]{Term.END} {line.decode("utf-8")}', end='')


async def dev_server(cli: argparse.Namespace):
    def live_reload_coroutine():
        if cli.no_live_reload or cli.no_tailwind:
            return None

        host = LRWS_HOST if cli.live_reload_host is None else cli.live_reload_host
        port = LRWS_PORT if cli.live_reload_port is None else cli.live_reload_port

        return live_reload_server(host, port)

    def tw_cli_executor(loop: asyncio.AbstractEventLoop, pool: concurrent.futures.ThreadPoolExecutor):
        if cli.no_tailwind:
            return None

        input_arg = f''
        if cli.tailwind_input is not None:
            input_arg = f'-i {cli.tailwind_input}'
        elif TW_WATCH_PATH is not None:
            input_arg = f'-i {TW_WATCH_PATH}'

        output_arg = f'-o {TW_OUTPUT_PATH}'
        if cli.tailwind_output is not None:
            output_arg = f'-o {cli.tailwind_output}'

        minify_arg = '--minify' if cli.tailwind_minify else ''

        cmd = f'tailwindcss --watch {input_arg} {output_arg} {minify_arg}'

        process = subprocess.Popen(
            shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        return loop.run_in_executor(pool, handle_tw_output, process)

    def flask_server_executor(loop: asyncio.AbstractEventLoop, pool: concurrent.futures.ThreadPoolExecutor):
        if cli.no_flask:
            return None

        host_arg = '--host' + cli.flask_host if cli.flask_host is not None else ''

        port_arg = '--port' + cli.flask_port if cli.flask_port is not None else ''

        debug_arg = '--debug' if cli.flask_mode == 'debug' else ''

        exclude_patterns = ['*/**/dev.py', '*/**/install_dev_mode.py']
        if cli.flask_exclude_patterns is not None:
            exclude_patterns.extend(cli.flask_exclude_patterns)
        exclude_patterns_arg = f'--exclude-patterns {";".join(exclude_patterns)}'

        cmd = f'flask run {host_arg} {port_arg} {debug_arg} {exclude_patterns_arg}'

        process = subprocess.Popen(
            shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        return loop.run_in_executor(pool, handle_flask_output, process)

    loop = asyncio.get_running_loop()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        maybe_future_like = (
            live_reload_coroutine(),
            tw_cli_executor(loop, pool),
            flask_server_executor(loop, pool)
        )

        futures = (
            future
            for future in maybe_future_like
            if future is not None
        )

        _ = await asyncio.gather(*futures, return_exceptions=True)


def minify_tailwindcss(cli: argparse.Namespace):
    input_arg = f''
    if cli.input is not None:
        input_arg = f'-i {cli.input}'

    output_arg = f'-o {TW_OUTPUT_PATH_BUILD}'
    if cli.output is not None:
        output_arg = f'-o {cli.output}'

    minify_arg = '--minify' if cli.minify else ''

    command = f'tailwindcss {input_arg} {output_arg} {minify_arg}'

    dev_print(f'Minifying tailwindcss for production...')

    build_result = subprocess.run(shlex.split(command))

    if build_result.returncode != 0:
        dev_print(f'Tailwind build for production {Term.R}fail{Term.END}')
        return build_result.returncode

    dev_print(f'Tailwind build for production {Term.G}ready{Term.END}')
    return build_result.returncode


def main():
    cli_args = cli().parse_args()

    if cli_args.command == 'build':
        return minify_tailwindcss(cli_args)

    if cli_args.command == 'dev':
        asyncio.run(dev_server(cli_args))
        return 0

    dev_print(f'Unknown command {Term.BOLD}{cli_args.command}{Term.END}')
    dev_print(f'Use {Term.BOLD}dev.py [-h | --help]{Term.END} for help.')
    return 1


def cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Enhanced dev environment for flask apps.',
        allow_abbrev=True,
    )

    subparsers = parser.add_subparsers(
        title='commands', dest='command',
        help='availible commands',
        required=True
    )

    parser_build = subparsers.add_parser(
        name='build',
        description='Build the tailwindcss of the provided input as a single css file.',
        help='Build tailwindcss for production.',
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser_build.add_argument(
        '-i', '--input', dest='input', type=str,
        help='Input path, accepts glob patterns.'
    )
    parser_build.add_argument(
        '-o', '--output', dest='output', type=str,
        help='Output path.'
    )
    build_minify_group = parser_build.add_mutually_exclusive_group()
    build_minify_group.add_argument(
        '--minify', dest='minify', action='store_true',
        help='Minify output.'
    )
    build_minify_group.add_argument(
        '--no-minify', dest='minify', action='store_false',
        help='Do not minify output.'
    )
    parser_build.set_defaults(minify=True)

    parser_dev = subparsers.add_parser(
        name='dev',
        description='''
            Extended dev mode for flask apps.
            By default runs the flask app in debug mode,
            tailwindcss in watch mode and live reload server.
        ''',
        help='Run a development server.',
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser_dev.add_argument(
        '--no-live-reload', dest='no_live_reload', action='store_true', default=False,
        help='Disable live reload server.'
    )
    parser_dev.add_argument(
        '-lrh', '--live-reload-host', dest='live_reload_host', type=str,
        help='Hostname for live reload server.'
    )
    parser_dev.add_argument(
        '-lrp', '--live-reload-port', dest='live_reload_port', type=int,
        help='Port for live reload server.'
    )

    parser_dev.add_argument(
        '--no-flask', dest='no_flask', action='store_true', default=False,
        help='Disable flask server.'
    )
    parser_dev.add_argument(
        '-fh', '--flask-host', dest='flask_host', type=str,
        help='Hostname for flask server.'
    )
    parser_dev.add_argument(
        '-fp', '--flask-port', dest='flask_port', type=int,
        help='Port for flask server.'
    )
    parser_dev.add_argument(
        '-fm', '--flask-mode',  dest='flask_mode', choices=('debug', 'no-debug'), default='debug',
        help='If debug mode is enabled, the flask server will be started with --debug flag. Default: debug.'
    )
    parser_dev.add_argument(
        '--flask-exclude-patterns', dest='flask_exclude_patterns', type=str, nargs='+',
        help='File exclude patterns for flask server. Base: */**/dev.py */**/install_dev_mode.py'
    )

    parser_dev.add_argument(
        '-nt', '--no-tailwind', dest='no_tailwind', action='store_true', default=False,
        help='Disable tailwindcss generation. If tailwindcss is disabled the live reload server will not be started.'
    )
    parser_dev.add_argument(
        '-ti', '--tailwind-input', dest='tailwind_input', type=str,
        help='Input path to watch for changes. Includes glob patterns.'
    )
    parser_dev.add_argument(
        '-to', '--tailwind-output', dest='tailwind_output', type=str,
        help='Output path for the generated css file.'
    )
    parser_dev.add_argument(
        '-tm', '--tailwind-minify', dest='tailwind_minify', action='store_true', default=False,
        help='Enables minification of the generated css file.'
    )

    return parser


if __name__ == "__main__":
    raise SystemExit(main())
