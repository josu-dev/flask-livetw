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
from flask_livetw.util import Term, load_resource, pkgprint

LIVE_RELOAD_SCRIPT = load_resource("live_reload.js")
TAILWIND_CONFIG = load_resource("tailwind.config.js")
GLOBAL_CSS = load_resource("global.css")
LAYOUT_TEMPLATE = load_resource("layout.html")


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
    live_reload_file: str, tailwind_file: str, tailwind_min_file: str
) -> str:
    return (
        """
  {% if config.DEBUG %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + tailwind_file
        + """\') }}">
    <script src="{{ url_for('static', filename=\'"""
        + live_reload_file
        + """\') }}" defer></script>
  {% else %}
    <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename=\'"""  # noqa: E501
        + tailwind_min_file
        + """\') }}">
  {% endif %}
"""
    ).strip("\n")


def generate_layout_template(
    live_reload_file: str, tailwind_file: str, tailwind_min_file: str
) -> str:
    return LAYOUT_TEMPLATE.content.replace(
        "{live_reload_template_placeholder}",
        generate_live_reload_template(
            live_reload_file, tailwind_file, tailwind_min_file
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

        Term.info("Tailwindcss configuration file updated")
        pkgprint("Tailwindcss configured")
        return 0

    config = generate_tailwind_config(content_glob)

    with open(TAILWIND_CONFIG.name, "w") as f:
        f.write(config)

    Term.info("Tailwindcss configuration file created")
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
                    "Root layour is malformed, the </head> tag is missing. \
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

            pkgprint("Root layout file updated")
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

    pkgprint("Root layout file created")
    return 0


def update_gitignore(static_folder: str, tailwind_file: str) -> None:
    Term.blank()
    pkgprint("Updating .gitignore...")

    content = f"""
# flask-livetw
{static_folder}/{tailwind_file}
"""
    try:
        with open(".gitignore", "a") as f:
            f.write(content)
    except FileNotFoundError:
        Term.info("Missing .gitignore file, creating one...")
        with open(".gitignore", "w") as f:
            f.write(content)

    pkgprint(".gitignore updated")


def initialize(config: Config, gitignore: bool) -> int:
    pkgprint("Initializing flask-livetw...")

    code = update_pyproject_toml(config)
    if code != 0:
        return code

    tailwind_code = configure_tailwind(config.full_templates_glob)
    if tailwind_code > 0:
        return tailwind_code

    generate_files(
        config.full_live_reload_file,
        config.full_globalcss_file,
    )

    code = update_layout(
        config.full_root_layout_file,
        config.live_reload_file,
        config.tailwind_file,
        config.tailwind_minified_file,
    )
    if code != 0:
        return code

    if gitignore:
        update_gitignore(config.full_static_folder, config.tailwind_file)

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
    # project_config = Config.from_pyproject_toml()

    if cli.default:
        init_config = Config.default()
    else:
        init_config = ask_project_layout(app_source=cli.flask_root)

    return initialize(init_config, gitignore=cli.gitignore)


def add_command_args(parser: argparse.ArgumentParser) -> None:
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
