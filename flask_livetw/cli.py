import argparse
import dataclasses
import os
import shlex
import subprocess
from typing import Union

from flask_livetw.util import Term


DEFAULT_STATIC_FOLDER = 'static'

DEFAULT_TEMPLATE_FOLDER = 'templates'
DEFAULT_TEMPLATE_GLOB = '**/*.html'
DEFAULT_TEMPLATE_ROOT_LAYOUT = 'layout.html'

DEFAULT_LIVE_RELOAD_FILE = '.dev/live_reload.js'

DEFAULT_TWCSS_FILE = '.dev/tailwindcss.css'

DEFAULT_MINIFIED_TWCSS_FILE = 'tailwindcss_min.css'

DEFAULT_UPDATE_GITIGNORE = False


@dataclasses.dataclass
class Config:
    gitignore: bool

    flask_root: Union[str, None]

    static_folder: str

    templates_folder: str
    templates_glob: str

    root_layout_file: str
    live_reload_file: str
    twcss_file: str
    minified_twcss_file: str


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Mods a Flask app to use TailwindCSS in a dev server like manner.',
        allow_abbrev=True
    )

    parser.add_argument(
        '-Y', '--yes', dest='all_yes', action='store_true', default=False,
        help='Answer yes to all questions.'
    )

    parser.add_argument(
        '-D', '--default', dest='default', action='store_true', default=False,
        help='Use default values for all options.'
    )

    parser.add_argument(
        '--gi', '--gitignore', dest='gitignore', action='store_true',
        help=f'Update .gitignore to exclude dev mode related files. Default: {DEFAULT_UPDATE_GITIGNORE}'
    )

    parser.add_argument(
        '--fr', '--flask-root', dest='flask_root', type=str,
        help=f'Flask app root path (relative to cwd).'
    )

    parser.add_argument(
        '--sf', '--static-folder', dest='static_folder', type=str,
        help=f'Static folder path. Default: <your project>/{DEFAULT_STATIC_FOLDER}'
    )

    parser.add_argument(
        '--tf', '--templates-folder', dest='templates_folder', type=str,
        help=f'Templates folder path. Default: <your project>/{DEFAULT_TEMPLATE_FOLDER}'
    )
    parser.add_argument(
        '--tg', '--templates-glob', dest='templates_glob', type=str,
        help=f'Templates glob pattern. Default: {DEFAULT_TEMPLATE_GLOB}'
    )
    parser.add_argument(
        '--rlf', '--root-layout-file', dest='root_layout_file', type=str,
        help=f'Template root layout file. Default: <templates folder>/{DEFAULT_TEMPLATE_ROOT_LAYOUT}'
    )

    parser.add_argument(
        '--lrf', '--live-reload-file', dest='live_reload_file', type=str,
        help=f'Live reload js file, relative to static folder. Default: <static folder>/{DEFAULT_LIVE_RELOAD_FILE}'
    )
    parser.add_argument(
        '--twf', '--twcss-file', dest='twcss_file', type=str,
        help=f'Generated css file, relative to static folder. Default: <static folder>/{DEFAULT_TWCSS_FILE}'
    )
    parser.add_argument(
        '--mtwf', '--minified-twcss-file', dest='minified_twcss_file', type=str,
        help=f'Minified css file, relative to static folder. Default: <static folder>/{DEFAULT_MINIFIED_TWCSS_FILE}'
    )

    return parser


def check_requirements() -> int:
    cwd = os.getcwd()
    print(
        f'The modding will continue on the current working directory:\n> {Term.BOLD}{cwd}{Term.END} ')
    continue_install = Term.confirm("Continue?")

    if not continue_install:
        Term.dev("modding canceled")
        return 1

    python_cmd = shlex.split("python --version")
    python_cmd_result = subprocess.run(
        python_cmd, shell=True, check=True, capture_output=True
    )

    if python_cmd_result.returncode != 0:
        Term.error('python --version failed, terminating script')
        return python_cmd_result.returncode

    version = python_cmd_result.stdout.decode('utf-8')
    if version != 'Python 3.8.10':
        Term.warn("Current python version is 3.8.10")
        continue_install = Term.confirm("Continue?")
        if not continue_install:
            Term.dev("modding canceled")
            return 1

    return 0


def get_config(args: argparse.Namespace) -> Config:
    if args.default:
        return Config(
            gitignore=DEFAULT_UPDATE_GITIGNORE,

            flask_root=None,

            static_folder=DEFAULT_STATIC_FOLDER,

            templates_folder=DEFAULT_TEMPLATE_FOLDER,
            templates_glob=DEFAULT_TEMPLATE_GLOB,

            root_layout_file=DEFAULT_TEMPLATE_ROOT_LAYOUT,
            live_reload_file=DEFAULT_LIVE_RELOAD_FILE,
            twcss_file=DEFAULT_TWCSS_FILE,
            minified_twcss_file=DEFAULT_MINIFIED_TWCSS_FILE
        )

    gitignore = True if args.gitignore else False

    flask_root = args.flask_root
    if flask_root is None:
        flask_root = Term.ask_dir('Flask app root path (relative to cwd): ')

    static_folder = args.static_folder
    if static_folder is None:
        static_folder = Term.ask_dir(
            f'Static folder (relative to \'cwd/{flask_root}\'): ',
            flask_root
        )

    templates_folder = args.templates_folder
    if templates_folder is None:
        templates_folder = Term.ask_dir(
            f'Templates folder (relative to \'cwd/{flask_root}\'): ',
            flask_root
        )

    templates_glob = args.templates_glob
    if templates_glob is None:
        templates_glob = Term.ask(
            f'Templates glob pattern (default: {templates_folder}/{DEFAULT_TEMPLATE_GLOB}): ',
            lambda glob: not glob
        )

    root_layout_file = args.root_layout_file
    if root_layout_file is None:
        root_layout_file = Term.ask(
            f'Template root layout file (default: {templates_folder}/{DEFAULT_TEMPLATE_ROOT_LAYOUT}): ',
            lambda glob: not glob
        )

    live_reload_file = args.live_reload_file
    if live_reload_file is None:
        live_reload_file = Term.ask(
            f'Live reload js file (default: {static_folder}/{DEFAULT_LIVE_RELOAD_FILE}): ',
            lambda glob: not glob
        )

    twcss_file = args.twcss_file
    if twcss_file is None:
        twcss_file = Term.ask(
            f'Generated css file (default: {static_folder}/{DEFAULT_TWCSS_FILE}): ',
            lambda glob: not glob
        )

    minified_twcss_file = args.minified_twcss_file
    if minified_twcss_file is None:
        minified_twcss_file = Term.ask(
            f'Minified css file (default: {static_folder}/{DEFAULT_MINIFIED_TWCSS_FILE}): ',
            lambda glob: not glob
        )

    full_static_folder = f'{flask_root}/{static_folder}'
    full_templates_folder = f'{flask_root}/{templates_folder}'

    return Config(
        gitignore=gitignore,

        flask_root=flask_root,

        static_folder=full_static_folder,

        templates_folder=full_templates_folder,
        templates_glob=f'{full_templates_folder}/{templates_glob}',

        root_layout_file=f'{full_templates_folder}/{root_layout_file}',
        live_reload_file=live_reload_file,
        twcss_file=twcss_file,
        minified_twcss_file=minified_twcss_file,
    )
