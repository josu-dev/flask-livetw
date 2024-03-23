from __future__ import annotations

import argparse
import os
import re
from typing import Sequence

from flask_livetw.config import (
    Config,
    ask_project_layout,
    update_pyproject_toml,
)
from flask_livetw.util import PKG_PP, Term, load_resource, pkgprint

GLOBAL_CSS = load_resource("global.css")
LAYOUT_TEMPLATE = load_resource("layout.html")
LIVE_RELOAD_SCRIPT = load_resource("live_reload.js")
TAILWIND_CONFIG = load_resource("tailwind.config.js")


def generate_tailwind_config(content_glob: str) -> str:
    return TAILWIND_CONFIG.content.replace(
        "{content_glob_placeholder}", content_glob
    )


def add_content_glob(config: str, content_glob: str) -> str | None:
    content_glob_re = re.compile(r"content:\s*\[([^\]]*)\]")
    re_match = content_glob_re.search(config)
    if re_match is None:
        return None

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
            new_globs = f"\n    {existing_globs},\n    '{content_glob}',\n  "
        else:
            new_globs = f"\n{existing_globs},\n{space}'{content_glob}',\n  "

    config = f"{prev}{new_globs}{next}"
    config = config.rstrip() + "\n"
    return config


def generate_live_reload_template(
    live_reload_file: str, tailwind_dev_file: str, tailwind_prod_file: str
) -> str:
    return (
        """
  {% if config.LIVETW_DEV %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + tailwind_dev_file
        + """\') }}">
    <script src="{{ url_for('static', filename=\'"""
        + live_reload_file
        + """\') }}" defer></script>
  {% else %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + tailwind_prod_file
        + """\') }}">
  {% endif %}
"""
    ).strip("\n")


def generate_layout_template(
    live_reload_file: str, tailwind_dev_file: str, tailwind_prod_file: str
) -> str:
    return LAYOUT_TEMPLATE.content.replace(
        "{live_reload_template_placeholder}",
        generate_live_reload_template(
            live_reload_file, tailwind_dev_file, tailwind_prod_file
        ),
    )


def configure_tailwind(content_glob: str) -> int:
    Term.blank()
    pkgprint("Configuring tailwindcss...")

    if os.path.exists(TAILWIND_CONFIG.name):
        Term.info("Detected existing configuration file")
        Term.info("Updating tailwindcss configuration file...")

        with open(TAILWIND_CONFIG.name, "r") as f:
            existing_config = f.read()

        config = add_content_glob(existing_config, content_glob)
        if config is None:
            Term.info("No content config found in existing tailwind.config.js")
            Term.info(f"Manually add '{content_glob}' to your content config.")
            return -1

        with open(TAILWIND_CONFIG.name, "w") as f:
            f.write(config)

        pkgprint("Tailwindcss configured")
        return 0

    config = generate_tailwind_config(content_glob)

    with open(TAILWIND_CONFIG.name, "w") as f:
        f.write(config)

    pkgprint("Tailwindcss configured")
    return 0


def generate_files(
    live_reload_file: str,
    globalcss_file: str,
) -> None:
    Term.blank()
    pkgprint("Generating files...")

    try:
        with open(live_reload_file, "w") as f:
            f.write(LIVE_RELOAD_SCRIPT.content)
    except FileNotFoundError:
        os.makedirs(os.path.dirname(live_reload_file), exist_ok=True)
        with open(live_reload_file, "w") as f:
            f.write(LIVE_RELOAD_SCRIPT.content)

    try:
        with open(globalcss_file, "w") as f:
            f.write(GLOBAL_CSS.content)
    except FileNotFoundError:
        os.makedirs(os.path.dirname(globalcss_file), exist_ok=True)
        with open(globalcss_file, "w") as f:
            f.write(GLOBAL_CSS.content)

    pkgprint("Files generated")


def update_layout(
    root_layout_file: str,
    live_reload_file: str,
    tailwind_file: str,
    tailwind_min_file: str,
) -> int:
    Term.blank()
    pkgprint("Updating layout...")

    try:
        with open(root_layout_file, "+r") as f:
            layout = f.read()
            if "</head>" not in layout:
                Term.error(
                    "Base layout is malformed, the </head> tag is missing. \
                        Please check your root layout file."
                )
                return 1

            layout = layout.replace(
                "</head>",
                generate_live_reload_template(
                    live_reload_file, tailwind_file, tailwind_min_file
                )
                + "\n</head>",
            )
            f.seek(0)
            f.write(layout)
            f.truncate()

            pkgprint("Base layout file updated")
            return 0
    except FileNotFoundError as e:
        Term.warn(e)
        os.makedirs(os.path.dirname(root_layout_file), exist_ok=True)
        with open(root_layout_file, "w") as f:
            f.write(
                generate_layout_template(
                    live_reload_file, tailwind_file, tailwind_min_file
                )
            )

    pkgprint("Base layout file created")
    return 0


def initialize(config: Config) -> int:
    Term.blank()
    pkgprint("Initializing flask-livetw 😎")

    Term.blank()
    pkgprint("Updating pyproject.toml...")
    code = update_pyproject_toml(
        config,
        keys=[
            "flask_root",
            "static_folder",
            "templates_folder",
            "templates_glob",
            "base_layout",
            "livetw_folder",
            "flask_app",
        ],
    )
    if code != 0:
        return code
    pkgprint("pyproject.toml updated")

    tailwind_code = configure_tailwind(config.full_templates_glob)
    if tailwind_code > 0:
        return tailwind_code

    generate_files(
        config.full_live_reload,
        config.full_global_css,
    )

    code = update_layout(
        config.full_base_layout,
        config.livetw_folder + "/" + config.live_reload,
        config.livetw_folder + "/" + config.tailwind_dev,
        config.tailwind_prod,
    )
    if code != 0:
        return code

    Term.blank()

    if tailwind_code == 0:
        pkgprint("Initialization completed ✅")
        return 0

    pkgprint("Initialization almost completed")
    pkgprint(
        "Remember to add the content glob to your tailwind.config.js manually"
    )
    pkgprint(f"Glob: '{config.full_templates_glob}'")

    return 0


def init(cli: argparse.Namespace) -> int:
    project_config = Config.try_from_pyproject_toml()
    if project_config is not None:
        pkgprint("flask-livetw is already initialized in this project")
        overwite = Term.confirm(
            f"{PKG_PP} Do you want to overwrite the existing configuration?",
        )
        if not overwite:
            pkgprint("Initialization cancelled")
            return 0

    if cli.default:
        init_config = Config.default()
    else:
        pkgprint("Describe your project layout:")
        init_config = ask_project_layout()

    return initialize(init_config)


def add_command_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--default",
        dest="default",
        action="store_true",
        default=False,
        help="use default values for all options",
    )


def add_command(
    subparser: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    parser = subparser.add_parser(
        name="init",
        description="""
        Initialize flask-livetw for the project.
        Adds the configuration to pyproject.toml and creates the necessary files.
        """,
        help="Initialize flask-livetw for the project.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)


def main(args: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Initialize flask-livetw in the current working directory.",
        allow_abbrev=True,
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )

    add_command_args(parser)

    parsed_args = parser.parse_args(args)

    return init(parsed_args)


if __name__ == "__main__":
    raise SystemExit(main())
