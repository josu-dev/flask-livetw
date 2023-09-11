#!/usr/bin/env python

import shlex
import subprocess
import os
from .util import Term, load_resource
from .cli import create_cli


DEV_DEPENDENCIES = 'pytailwindcss websockets python-dotenv'


LIVE_RELOAD_SCRIPT = load_resource('live_reload.js')
DEV_SCRIPT = load_resource('dev.py')
TAILWIND_CONFIG = load_resource('tailwind.config.js')
LAYOUT_TEMPLATE = load_resource('layout.html')


def generate_tw_config(content_glob: str) -> str:
    return TAILWIND_CONFIG.content.replace(
        '{content_glob_placeholder}',
        content_glob
    )


def generate_dev_script(twcss_file: str, minified_twcss_file: str) -> str:
    return DEV_SCRIPT.content \
        .replace(
            '{tailwind_output_placeholder}',
            twcss_file
        ).replace(
            '{minified_tailwind_output_placeholder}',
            minified_twcss_file
        )


def generate_live_reload_template(live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> str:
    return ('''
  {% if config.DEBUG %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'''' + twcss_file + '''\') }}">
    <script src="{{ url_for('static', filename=\'''' + live_reload_file + '''\') }}" defer></script>
  {% else %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'''' + minified_twcss_file + '''\') }}">
  {% endif %}
''').strip()


def generate_layout_template(live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> str:
    return LAYOUT_TEMPLATE.content.replace(
        '{live_reload_template_placeholder}',
        generate_live_reload_template(
            live_reload_file, twcss_file, minified_twcss_file)
    )


def check_installation_requirements(all_yes: bool = False) -> int:
    if all_yes:
        return 0

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


def install_dev_dependencies() -> None:
    Term.dev('Installing required dev dependencies...')

    poetry_cmd = shlex.split(f"poetry add --group=dev {DEV_DEPENDENCIES}")

    try:
        result = subprocess.run(poetry_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        Term.error(e)
        Term.info('Dev dependencies installation failed, terminating script')
        exit(1)

    if result.returncode != 0:
        Term.info('Dev dependencies installation failed, terminating script')
        exit(result.returncode)

    Term.dev('Dev dependencies installation complete')


def init_tailwindcss(content_glob: str) -> None:
    Term.dev('Initializing tailwindcss...')

    tailwind_init = "tailwindcss init"

    try:
        result = subprocess.run(tailwind_init, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        Term.error(e)
        Term.info('Tailwindcss initialization failed, terminating script')
        exit(1)

    if result.returncode != 0:
        Term.info('Tailwindcss initialization failed, terminating script')
        exit(result.returncode)

    with open('tailwind.config.js', 'w') as f:
        f.write(generate_tw_config(content_glob))

    Term.dev('Tailwindcss initialization complete')


def generate_files(live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> None:
    with open(DEV_SCRIPT.name, 'w') as f:
        f.write(generate_dev_script(twcss_file, minified_twcss_file))

    try:
        with open(live_reload_file, 'w') as f:
            f.write(LIVE_RELOAD_SCRIPT.content)

    except FileNotFoundError:
        os.makedirs(
            os.path.dirname(live_reload_file),
            exist_ok=True
        )
        with open(live_reload_file, 'w') as f:
            f.write(LIVE_RELOAD_SCRIPT.content)


def update_layout(root_layout_template: str, live_reload_file: str, twcss_file: str, minified_twcss_file: str) -> None:
    root_layout = root_layout_template

    try:
        with open(root_layout, '+r') as f:
            layout = f.read()
            if '</head>' not in layout:
                print("Error: </head> tag not found in src/web/templates/layout.html")
                exit(1)
            layout = layout.replace(
                '</head>',
                generate_live_reload_template(
                    live_reload_file,
                    twcss_file,
                    minified_twcss_file
                ) + '</head>'
            )
            f.seek(0)
            f.write(layout)
            f.truncate()
    except FileNotFoundError as e:
        Term.warn(e)
        os.makedirs(
            os.path.dirname(root_layout),
            exist_ok=True
        )
        with open(root_layout, 'w') as f:
            f.write(generate_layout_template(
                live_reload_file,
                twcss_file,
                minified_twcss_file
            ))


def update_gitignore(static_folder: str, twcss_file: str) -> None:
    content = f'''
# flask-live-twcss
{static_folder}/{twcss_file}
'''

    try:
        with open('.gitignore', 'a') as f:
            f.write(content)
    except FileNotFoundError:
        Term.info('Missing .gitignore file, creating one...')
        with open('.gitignore', 'w') as f:
            f.write(content)


def main() -> int:
    cli_args = create_cli().parse_args()

    check_code = check_installation_requirements(cli_args.all_yes)
    if check_code != 0:
        return check_code

    project_root = cli_args.project_root
    if project_root is None:
        project_root = input('Enter project directory: ')

    static_folder = f'{project_root}/{cli_args.static_folder}'
    templates_folder = f'{project_root}/{cli_args.templates_folder}'
    root_layout_template = f'{templates_folder}/{cli_args.template_root_layout}'
    live_reload_file = f'{static_folder}/{cli_args.live_reload_file}'
    twcss_file = f'{static_folder}/{cli_args.twcss_file}'
    minified_twcss_file = f'{static_folder}/{cli_args.minified_twcss_file}'
    tw_content_glob = f'{project_root}/{cli_args.templates_folder}/{cli_args.templates_glob}'

    Term.dev('Starting modding...')

    install_dev_dependencies()

    init_tailwindcss(tw_content_glob)

    generate_files(
        live_reload_file,
        twcss_file,
        minified_twcss_file
    )

    update_layout(
        root_layout_template,
        cli_args.live_reload_file,
        cli_args.twcss_file,
        cli_args.minified_twcss_file
    )

    if cli_args.gitignore:
        update_gitignore(
            static_folder,
            cli_args.twcss_file
        )

    Term.dev(f'Modding complete ✅')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
