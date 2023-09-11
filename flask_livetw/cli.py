import argparse


DEFAULT_STATIC_FOLDER = 'static'

DEFAULT_TEMPLATE_FOLDER = 'templates'
DEFAULT_TEMPLATE_GLOB = '**/*.html'
DEFAULT_TEMPLATE_ROOT_LAYOUT = 'layout.html'

DEFAULT_LIVE_RELOAD_FILE = '.dev/live_reload.js'

DEFAULT_TWCSS_FILE = '.dev/tailwindcss.css'

DEFAULT_MINIFIED_TWCSS_FILE = 'tailwindcss_min.css'

DEFAULT_UPDATE_GITIGNORE = False


def create_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Mods a Flask app to use TailwindCSS in a dev server like manner.',
        allow_abbrev=True
    )

    parser.add_argument(
        '-y', '--yes', dest='all_yes', action='store_true', default=False,
        help='Answer yes to all questions.'
    )

    parser.add_argument(
        '-gi', '--gitignore', dest='gitignore', action='store_true', default=DEFAULT_UPDATE_GITIGNORE,
        help=f'Update .gitignore to exclude dev mode related files. Default: {DEFAULT_UPDATE_GITIGNORE}'
    )

    parser.add_argument(
        '-pr', '--project-root', dest='project_root', type=str,
        help=f'Project root path.'
    )

    parser.add_argument(
        '-sf', '--static-folder', dest='static_folder', type=str, default=DEFAULT_STATIC_FOLDER,
        help=f'Static folder path. Default: <your project>/{DEFAULT_STATIC_FOLDER}'
    )

    parser.add_argument(
        '-tf', '--templates-folder', dest='templates_folder', type=str, default=DEFAULT_TEMPLATE_FOLDER,
        help=f'Templates folder path. Default: <your project>/{DEFAULT_TEMPLATE_FOLDER}'
    )
    parser.add_argument(
        '-tg', '--templates-glob', dest='templates_glob', type=str, default=DEFAULT_TEMPLATE_GLOB,
        help=f'Templates glob pattern. Default: {DEFAULT_TEMPLATE_GLOB}'
    )
    parser.add_argument(
        '-trl', '--template-root-layout', dest='template_root_layout', type=str, default=DEFAULT_TEMPLATE_ROOT_LAYOUT,
        help=f'Template root layout file. Default: <templates folder>/{DEFAULT_TEMPLATE_ROOT_LAYOUT}'
    )

    parser.add_argument(
        '-lrf', '--live-reload-file', dest='live_reload_file', type=str, default=DEFAULT_LIVE_RELOAD_FILE,
        help=f'Live reload js file, relative to static folder. Default: <static folder>/{DEFAULT_LIVE_RELOAD_FILE}'
    )
    parser.add_argument(
        '-twf', '--twcss-file', dest='twcss_file', type=str, default=DEFAULT_TWCSS_FILE,
        help=f'Generated css file, relative to static folder. Default: <static folder>/{DEFAULT_TWCSS_FILE}'
    )
    parser.add_argument(
        '-mtwf', '--minified-twcss-file', dest='minified_twcss_file', type=str, default=DEFAULT_MINIFIED_TWCSS_FILE,
        help=f'Minified css file, relative to static folder. Default: <static folder>/{DEFAULT_MINIFIED_TWCSS_FILE}'
    )

    return parser
