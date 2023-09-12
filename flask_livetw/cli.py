import argparse
import dataclasses
import os
import shlex
import subprocess
from typing import Union

from flask_livetw.util import Term


DEFAULT_FLASK_ROOT = 'src'

DEFAULT_STATIC_FOLDER = 'static'

DEFAULT_TEMPLATE_FOLDER = 'templates'
DEFAULT_TEMPLATE_GLOB = '**/*.html'

DEFAULT_ROOT_LAYOUT_FILE = 'layout.html'
DEFAULT_LIVE_RELOAD_FILE = '.dev/live_reload.js'
DEFAULT_TWCSS_FILE = '.dev/tailwindcss.css'
DEFAULT_MINIFIED_TWCSS_FILE = 'tailwindcss_min.css'

DEFAULT_UPDATE_GITIGNORE = False


PKG_PREFIX = f'{Term.M}[livetw]{Term.END}'


@dataclasses.dataclass
class Config:
    gitignore: bool

    flask_root: Union[str, None]

    static_folder: str
    full_static_folder: str

    templates_folder: str
    full_templates_folder: str
    templates_glob: str
    full_templates_glob: str

    root_layout_file: str
    full_root_layout_file: str
    live_reload_file: str
    full_live_reload_file: str
    twcss_file: str
    full_twcss_file: str
    minified_twcss_file: str
    full_minified_twcss_file: str


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Mods a Flask app to use TailwindCSS in a dev server like manner.',
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter
    )

    parser.add_argument(
        '-Y', '--yes', dest='all_yes', action='store_true', default=False,
        help='answer yes to all requirements checks'
    )

    parser.add_argument(
        '-D', '--default', dest='default', action='store_true', default=False,
        help='use default values for all options'
    )

    parser.add_argument(
        '--gi', '--gitignore', dest='gitignore', action='store_true', default=DEFAULT_UPDATE_GITIGNORE,
        help=f'update .gitignore to exclude dev related files (default: {DEFAULT_UPDATE_GITIGNORE})'
    )

    parser.add_argument(
        '--fr', '--flask-root', dest='flask_root', type=str,
        help=f'flask app root path (relative to cwd)'
    )

    return parser


def pkgprint(*values: object, end: str = '\n', sep: str = ' ') -> None:
    print(f'{PKG_PREFIX}', *values, end=end, sep=sep)


def check_requirements() -> int:
    pkgprint('Checking requirements...')
    cwd = os.getcwd()
    pkgprint(f'Current working directory: {Term.C}{cwd}{Term.END}')
    continue_install = Term.confirm(f'{PKG_PREFIX} Is this your project root?')

    if not continue_install:
        pkgprint('Change cwd and start again. Modding canceled')
        return 1

    python_cmd = shlex.split("python --version")
    python_cmd_result = subprocess.run(
        python_cmd, shell=True, capture_output=True
    )

    if python_cmd_result.returncode != 0:
        Term.error('python --version failed, is python installed?')
        return python_cmd_result.returncode

    version = python_cmd_result.stdout.decode('utf-8').strip()
    if version != 'Python 3.8.10':
        pkgprint(f'python --version: {Term.C}{version}{Term.END}')

        continue_install = Term.confirm(
            f'{PKG_PREFIX} Continue with this version?')
        if not continue_install:
            pkgprint('Change python version and start again. Modding canceled')
            return 1

    return 0


def get_config(args: argparse.Namespace) -> Config:
    if args.default:
        return Config(
            gitignore=DEFAULT_UPDATE_GITIGNORE,

            flask_root=DEFAULT_FLASK_ROOT,

            static_folder=DEFAULT_STATIC_FOLDER,
            full_static_folder=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_STATIC_FOLDER}',

            templates_folder=DEFAULT_TEMPLATE_FOLDER,
            full_templates_folder=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_TEMPLATE_FOLDER}',
            templates_glob=DEFAULT_TEMPLATE_GLOB,
            full_templates_glob=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_TEMPLATE_GLOB}',

            root_layout_file=DEFAULT_ROOT_LAYOUT_FILE,
            full_root_layout_file=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_ROOT_LAYOUT_FILE}',
            live_reload_file=DEFAULT_LIVE_RELOAD_FILE,
            full_live_reload_file=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_LIVE_RELOAD_FILE}',
            twcss_file=DEFAULT_TWCSS_FILE,
            full_twcss_file=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_TWCSS_FILE}',
            minified_twcss_file=DEFAULT_MINIFIED_TWCSS_FILE,
            full_minified_twcss_file=f'{DEFAULT_FLASK_ROOT}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_MINIFIED_TWCSS_FILE}',
        )

    gitignore = True if args.gitignore else False

    Term.blank()

    flask_root = args.flask_root
    if flask_root is None:
        flask_root = Term.ask_dir(
            f'{PKG_PREFIX} Flask app root (relative to {Term.C}cwd/{Term.END}) [{DEFAULT_FLASK_ROOT}] ',
            default=DEFAULT_FLASK_ROOT
        )

    static_folder = Term.ask_dir(
        f'{PKG_PREFIX} Static folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_STATIC_FOLDER}] ',
        flask_root,
        DEFAULT_STATIC_FOLDER
    )

    templates_folder = Term.ask_dir(
        f'{PKG_PREFIX} Templates folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_TEMPLATE_FOLDER}] ',
        flask_root,
        DEFAULT_TEMPLATE_FOLDER
    )

    templates_glob = Term.ask(
        f'{PKG_PREFIX} Templates glob (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_TEMPLATE_GLOB}] ',
    ) or DEFAULT_TEMPLATE_GLOB

    root_layout_file = Term.ask(
        f'{PKG_PREFIX} Root layout file (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_ROOT_LAYOUT_FILE}] ',
    ) or DEFAULT_ROOT_LAYOUT_FILE

    live_reload_file = Term.ask(
        f'{PKG_PREFIX} Live reload file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_LIVE_RELOAD_FILE}] ',
    ) or DEFAULT_LIVE_RELOAD_FILE

    twcss_file = Term.ask(
        f'{PKG_PREFIX} TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_TWCSS_FILE}] ',
    ) or DEFAULT_TWCSS_FILE

    minified_twcss_file = Term.ask(
        f'{PKG_PREFIX} Minified TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_MINIFIED_TWCSS_FILE}] ',
    ) or DEFAULT_MINIFIED_TWCSS_FILE

    if not flask_root or flask_root == '.':
        full_static_folder = static_folder
        full_templates_folder = templates_folder
    else:
        full_static_folder = f'{flask_root}/{static_folder}'
        full_templates_folder = f'{flask_root}/{templates_folder}'

    return Config(
        gitignore=gitignore,

        flask_root=flask_root,

        static_folder=static_folder,
        full_static_folder=full_static_folder,

        templates_folder=templates_folder,
        full_templates_folder=full_templates_folder,
        templates_glob=templates_glob,
        full_templates_glob=f'{full_templates_folder}/{templates_glob}',

        root_layout_file=root_layout_file,
        full_root_layout_file=f'{full_templates_folder}/{root_layout_file}',
        live_reload_file=live_reload_file,
        full_live_reload_file=f'{full_static_folder}/{live_reload_file}',
        twcss_file=twcss_file,
        full_twcss_file=f'{full_static_folder}/{twcss_file}',
        minified_twcss_file=minified_twcss_file,
        full_minified_twcss_file=f'{full_static_folder}/{minified_twcss_file}',
    )
