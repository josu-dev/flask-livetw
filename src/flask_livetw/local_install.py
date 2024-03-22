from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
from typing import Sequence

from flask_livetw.config import Config, ask_project_layout
from flask_livetw.util import PKG_PP, Term, load_resource, pkgprint

DEV_DEPENDENCIES = "pytailwindcss python-dotenv websockets"


LIVE_RELOAD_SCRIPT = load_resource("live_reload.js")
DEV_SCRIPT = load_resource("dev.py")
TAILWIND_CONFIG = load_resource("tailwind.config.js")
GLOBAL_CSS = load_resource("global.css")
LAYOUT_TEMPLATE = load_resource("layout.html")


def generate_tw_config(content_glob: str) -> str:
    return TAILWIND_CONFIG.content.replace(
        "{content_glob_placeholder}", content_glob
    )


def generate_dev_script(
    globalcss_file: str, twcss_file: str, minified_twcss_file: str
) -> str:
    return (
        DEV_SCRIPT.content.replace(
            "{tailwind_input_placeholder}", globalcss_file
        )
        .replace("{tailwind_output_placeholder}", twcss_file)
        .replace("{minified_tailwind_output_placeholder}", minified_twcss_file)
    )


def generate_live_reload_template(
    live_reload_file: str, twcss_file: str, minified_twcss_file: str
) -> str:
    return (
        """
  {% if config.DEBUG %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + twcss_file
        + """\') }}">
    <script src="{{ url_for('static', filename=\'"""
        + live_reload_file
        + """\') }}" defer></script>
  {% else %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + minified_twcss_file
        + """\') }}">
  {% endif %}
"""
    ).strip("\n")


def generate_layout_template(
    live_reload_file: str, twcss_file: str, minified_twcss_file: str
) -> str:
    return LAYOUT_TEMPLATE.content.replace(
        "{live_reload_template_placeholder}",
        generate_live_reload_template(
            live_reload_file, twcss_file, minified_twcss_file
        ),
    )


def install_dev_dependencies() -> int:
    Term.blank()
    pkgprint("Installing required dev dependencies...")

    poetry_cmd = shlex.split(f"poetry add --group=dev {DEV_DEPENDENCIES}")

    try:
        _ = subprocess.run(poetry_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        Term.error(e)
        Term.info(
            "Dev dependencies installation failed, please install them manually"  # noqa: E501
        )
        return -1

    pkgprint("Dev dependencies installed")
    return 0


def configure_tailwind(content_glob: str) -> int:
    Term.blank()
    pkgprint("Configuring tailwindcss...")

    if os.path.exists(TAILWIND_CONFIG.name):
        Term.info("Detected existing configuration file")
        Term.info("Updating tailwindcss configuration file...")

        with open(TAILWIND_CONFIG.name, "r+t") as f:
            config = f.read()
            content_glob_re = re.compile(r"content:\s*\[([^\]]*)\]")
            re_match = content_glob_re.search(config)
            if re_match is None:
                Term.info(
                    "No content config found in existing tailwind.config.js"
                )
                Term.info("Add the following glob to the content config:")
                Term.info(f"'{content_glob}',")
                return -1

            existing_globs = re_match.group(1)
            content_start, content_end = re_match.span(1)
            prev = config[:content_start]
            next = config[content_end:]
            if existing_globs.strip() == "":
                new_globs = f"'{content_glob}',"
            else:
                no_new_line = existing_globs.lstrip("\n")
                space = " " * (len(no_new_line) - len(no_new_line.lstrip()))
                existing_globs = no_new_line.rstrip(", \t\n")
                if space == "":
                    new_globs = (
                        f"\n    {existing_globs},\n    '{content_glob}',\n  "
                    )
                else:
                    new_globs = (
                        f"\n{existing_globs},\n{space}'{content_glob}',\n  "
                    )

            config = f"{prev}{new_globs}{next}"
            config = config.rstrip() + "\n"
            f.seek(0)
            f.write(config)
            f.truncate()

        Term.info("Tailwindcss configuration file updated")
        pkgprint("Tailwindcss configured")
        return 0

    with open(TAILWIND_CONFIG.name, "w") as f:
        f.write(generate_tw_config(content_glob))

    Term.info("Tailwindcss configuration file created")
    pkgprint("Tailwindcss configuration complete")
    return 0


def generate_files(
    live_reload_file: str,
    globalcss_file: str,
    twcss_file: str,
    minified_twcss_file: str,
) -> None:
    with open(DEV_SCRIPT.name, "w") as f:
        f.write(
            generate_dev_script(
                globalcss_file, twcss_file, minified_twcss_file
            )
        )

    try:
        with open(live_reload_file, "w") as f:
            f.write(LIVE_RELOAD_SCRIPT.content)
    except FileNotFoundError:
        os.makedirs(os.path.dirname(live_reload_file), exist_ok=True)
        with open(live_reload_file, "w") as f:
            f.write(LIVE_RELOAD_SCRIPT.content)

    with open(globalcss_file, "w") as f:
        f.write(GLOBAL_CSS.content)


def update_layout(
    root_layout_file: str,
    live_reload_file: str,
    twcss_file: str,
    minified_twcss_file: str,
) -> int:
    try:
        with open(root_layout_file, "+r") as f:
            layout = f.read()
            if "</head>" not in layout:
                Term.error(
                    "Root layour is malformed, the </head> tag is missing. \
                        Please check your root layout file."
                )
                return 1

            layout = layout.replace(
                "</head>",
                generate_live_reload_template(
                    live_reload_file, twcss_file, minified_twcss_file
                )
                + "\n</head>",
            )
            f.seek(0)
            f.write(layout)
            f.truncate()
            return 0
    except FileNotFoundError as e:
        Term.warn(e)
        os.makedirs(os.path.dirname(root_layout_file), exist_ok=True)
        with open(root_layout_file, "w") as f:
            f.write(
                generate_layout_template(
                    live_reload_file, twcss_file, minified_twcss_file
                )
            )

    return 0


def update_gitignore(static_folder: str, twcss_file: str) -> None:
    content = f"""
# flask-livetw
{static_folder}/{twcss_file}
"""
    try:
        with open(".gitignore", "a") as f:
            f.write(content)
    except FileNotFoundError:
        Term.info("Missing .gitignore file, creating one...")
        with open(".gitignore", "w") as f:
            f.write(content)


def check_requirements() -> int:
    pkgprint("Checking requirements...")
    cwd = os.getcwd()
    pkgprint(f"Current working directory: {Term.C}{cwd}{Term.END}")
    continue_install = Term.confirm(f"{PKG_PP} Is this your project root?")

    if not continue_install:
        pkgprint("Change cwd and start again. Modding canceled")
        return 1

    python_cmd = shlex.split("python --version")
    python_cmd_result = subprocess.run(
        python_cmd, shell=True, capture_output=True
    )

    if python_cmd_result.returncode != 0:
        Term.error("python --version failed, is python installed?")
        return python_cmd_result.returncode

    version = python_cmd_result.stdout.decode("utf-8").strip()
    if version != "Python 3.8.10":
        pkgprint(f"python --version: {Term.C}{version}{Term.END}")

        continue_install = Term.confirm(
            f"{PKG_PP} Continue with this version?"
        )
        if not continue_install:
            pkgprint("Change python version and start again. Modding canceled")
            return 1

    return 0


def local_install(args: argparse.Namespace) -> int:
    if not args.all_yes:
        code = check_requirements()
        if code != 0:
            return code

    config = Config.try_from_pyproject_toml()
    if config is None:
        config = ask_project_layout()

    Term.blank()
    pkgprint("Installing flask-livetw as local script 🚀...")

    dependancies_code = install_dev_dependencies()
    if dependancies_code > 0:
        return dependancies_code

    tailwind_code = configure_tailwind(config.full_templates_glob)
    if tailwind_code > 0:
        return tailwind_code

    generate_files(
        config.full_live_reload_file,
        config.full_globalcss_file,
        config.full_tailwind_file,
        config.full_tailwind_minified_file,
    )

    code = update_layout(
        config.full_root_layout_file,
        config.live_reload_file,
        config.full_tailwind_file,
        config.full_tailwind_minified_file,
    )
    if code != 0:
        return code

    if args.gitignore:
        update_gitignore(config.full_static_folder, config.tailwind_file)

    Term.blank()

    if dependancies_code == 0 and tailwind_code == 0:
        pkgprint("Local install completed 🎉")
        return 0

    pkgprint("Local install almost completed")

    if dependancies_code != 0:
        pkgprint("Remember to install the missing dev dependencies manually")
        pkgprint(f"Dependancies: {DEV_DEPENDENCIES}")

    if tailwind_code != 0:
        pkgprint(
            "Remember to add the content glob to your tailwind.config.js manually"
        )
        pkgprint(f"Glob: '{config.full_templates_glob}'")

    return 0


def add_command_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-Y",
        "--yes",
        dest="all_yes",
        action="store_true",
        default=False,
        help="answer yes to all requirements checks",
    )

    parser.add_argument(
        "-D",
        "--default",
        dest="default",
        action="store_true",
        default=False,
        help="use default values for all options",
    )

    parser.add_argument(
        "--gi",
        "--gitignore",
        dest="gitignore",
        action="store_true",
        default=False,
        help="update .gitignore to exclude dev related files",
    )


def add_command(
    subparser: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparser.add_parser(
        name="local-install",
        description="""
        Install flask-livetw as a local script
        (adds dev dependencies, configures tailwindcss,
        adds dev script and updates root layout file).
        """,
        help="Install flask-livetw as a local script.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="""
        Install flask-livetw as a local script
        (adds dev dependencies, configures tailwindcss,
        adds dev script and updates root layout file).
        """,
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    add_command_args(parser)

    parsed_args = parser.parse_args(args)

    return local_install(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
