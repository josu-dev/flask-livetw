from __future__ import annotations

import dataclasses
import re
from typing import Any

import tomli

from flask_livetw.util import Term

PKG_PREFIX = "livetw"

DEFAULT_FLASK_ROOT = "src"

DEFAULT_FOLDER_STATIC = "static"

DEFAULT_FOLDER_TEMPLATE = "templates"
DEFAULT_TEMPLATES_GLOB = "**/*.html"

DEFAULT_FILE_ROOT_LAYOUT = "layout.html"
DEFAULT_FILE_LIVE_RELOAD = ".dev/live_reload.js"
DEFAULT_FILE_GLOBALCSS = ".dev/global.css"
DEFAULT_FILE_TAILWIND = ".dev/tailwindcss.css"
DEFAULT_FILE_MINIFIED_TAILWIND = "tailwindcss_min.css"

DEFAULT_LIVERELOAD_HOST = "127.0.0.1"
DEFAULT_LIVERELOAD_PORT = 5678


def get_pyproject_toml(base_dir: str = "") -> dict[str, Any] | None:
    path = f"{base_dir}/pyproject.toml" if base_dir else "pyproject.toml"
    try:
        with open(path, "rb") as f:
            return tomli.load(f)
    except FileNotFoundError:
        Term.info(f"Could not find pyproject.toml at '{path}'")
        return None
    except tomli.TOMLDecodeError as e:
        Term.warn(f"Malformed pyproject.toml: {e}")
        return None


@dataclasses.dataclass
class Config:
    flask_root: str

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

    globalcss_file: str
    full_globalcss_file: str
    tailwind_file: str
    full_tailwind_file: str
    tailwind_minified_file: str
    full_tailwind_minified_file: str

    live_reload_host: str
    live_reload_port: int

    flask_host: str
    flask_port: int
    flask_exclude_patterns: list[str]

    @staticmethod
    def default(base_dir: str = ""):
        return Config(
            flask_root=DEFAULT_FLASK_ROOT,
            static_folder=DEFAULT_FOLDER_STATIC,
            full_static_folder=f"{base_dir}/{DEFAULT_FOLDER_STATIC}",
            templates_folder=DEFAULT_FOLDER_TEMPLATE,
            full_templates_folder=f"{base_dir}/{DEFAULT_FOLDER_TEMPLATE}",
            templates_glob=DEFAULT_TEMPLATES_GLOB,
            live_reload_file=DEFAULT_FILE_LIVE_RELOAD,
            globalcss_file=DEFAULT_FILE_GLOBALCSS,
            tailwind_file=DEFAULT_FILE_TAILWIND,
            tailwind_minified_file=DEFAULT_FILE_MINIFIED_TAILWIND,
            root_layout_file=DEFAULT_FILE_ROOT_LAYOUT,
            full_templates_glob=f"{base_dir}/{DEFAULT_FOLDER_TEMPLATE}/{DEFAULT_TEMPLATES_GLOB}",
            full_live_reload_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_LIVE_RELOAD}",
            full_globalcss_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_GLOBALCSS}",
            full_tailwind_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_TAILWIND}",
            full_tailwind_minified_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_MINIFIED_TAILWIND}",
            full_root_layout_file=f"{base_dir}/{DEFAULT_FOLDER_TEMPLATE}/{DEFAULT_FILE_ROOT_LAYOUT}",
            # dev_server
            live_reload_host=DEFAULT_LIVERELOAD_HOST,
            live_reload_port=DEFAULT_LIVERELOAD_PORT,
            flask_host=DEFAULT_LIVERELOAD_HOST,
            flask_port=DEFAULT_LIVERELOAD_PORT,
            flask_exclude_patterns=[],
        )

    @staticmethod
    def from_pyproject_toml(base_dir: str = ""):
        """
        Reads the pyproject.toml file and returns a Config object.

        If the file does not exist, or if the flask-livetw section is missing,
        returns the default config.

        If some values are missing, they are filled with the default values.
        """
        pyproject_toml = get_pyproject_toml(base_dir)
        if (
            pyproject_toml is None
            or ("tool" not in pyproject_toml)
            or ("flask-livetw" not in pyproject_toml["tool"])
        ):
            return Config.default(base_dir)

        config: dict[str, Any] = pyproject_toml["tool"]["flask-livetw"]

        return Config(
            flask_root=config.get("flask_root", DEFAULT_FLASK_ROOT),
            static_folder=config.get("static_folder", DEFAULT_FOLDER_STATIC),
            full_static_folder=f"{base_dir}/{config.get('static_folder', DEFAULT_FOLDER_STATIC)}",
            templates_folder=config.get(
                "templates_folder", DEFAULT_FOLDER_TEMPLATE
            ),
            full_templates_folder=f"{base_dir}/{config.get('templates_folder', DEFAULT_FOLDER_TEMPLATE)}",
            templates_glob=config.get(
                "templates_glob", DEFAULT_TEMPLATES_GLOB
            ),
            live_reload_file=config.get(
                "live_reload_file", DEFAULT_FILE_LIVE_RELOAD
            ),
            globalcss_file=config.get(
                "globalcss_file", DEFAULT_FILE_GLOBALCSS
            ),
            tailwind_file=config.get("tailwind_file", DEFAULT_FILE_TAILWIND),
            tailwind_minified_file=config.get(
                "tailwind_minified_file", DEFAULT_FILE_MINIFIED_TAILWIND
            ),
            root_layout_file=config.get(
                "root_layout_file", DEFAULT_FILE_ROOT_LAYOUT
            ),
            full_templates_glob=f"{base_dir}/{DEFAULT_FOLDER_TEMPLATE}/{DEFAULT_TEMPLATES_GLOB}",
            full_live_reload_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_LIVE_RELOAD}",
            full_globalcss_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_GLOBALCSS}",
            full_tailwind_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_TAILWIND}",
            full_tailwind_minified_file=f"{base_dir}/{DEFAULT_FOLDER_STATIC}/{DEFAULT_FILE_MINIFIED_TAILWIND}",
            full_root_layout_file=f"{base_dir}/{DEFAULT_FOLDER_TEMPLATE}/{DEFAULT_FILE_ROOT_LAYOUT}",
            live_reload_host=config.get(
                "live_reload_host", DEFAULT_LIVERELOAD_HOST
            ),
            live_reload_port=config.get(
                "live_reload_port", DEFAULT_LIVERELOAD_PORT
            ),
            flask_host=config.get("flask_host", DEFAULT_LIVERELOAD_HOST),
            flask_port=config.get("flask_port", DEFAULT_LIVERELOAD_PORT),
            flask_exclude_patterns=config.get("flask_exclude_patterns", []),
        )


def update_pyproject_toml(config: Config) -> int:
    Term.blank()
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
    except FileNotFoundError:
        Term.info("Could not find pyproject.toml")
        pyproject = {}
    except tomli.TOMLDecodeError as e:
        Term.info(f"Malformed pyproject.toml: {e}")
        Term.info("Verify that the file is valid TOML")
        return 1

    ppconfig = pyproject.get("tool", {}).get("flask-livetw", {})

    new_config = f"""
[tool.flask-livetw]
flask_root = "{ppconfig.get("flask_root", config.flask_root)}"
static_folder = "{ppconfig.get("static_folder", config.static_folder)}"
templates_folder = "{ppconfig.get("templates_folder", config.templates_folder)}"
templates_glob = "{ppconfig.get("templates_glob", config.templates_glob)}"
root_layout_file = "{ppconfig.get("root_layout_file", config.root_layout_file)}"
live_reload_file = "{ppconfig.get("live_reload_file", config.live_reload_file)}"
globalcss_file = "{ppconfig.get("globalcss_file", config.globalcss_file)}"
tailwind_file = "{ppconfig.get("tailwind_file", config.tailwind_file)}"
tailwind_minified_file = "{ppconfig.get("tailwind_minified_file", config.tailwind_minified_file)}"
live_reload_host = "{ppconfig.get("live_reload_host", config.live_reload_host)}"
live_reload_port = {ppconfig.get("live_reload_port", config.live_reload_port)}
flask_host = "{ppconfig.get("flask_host", config.flask_host)}"
flask_port = {ppconfig.get("flask_port", config.flask_port)}
flask_exclude_patterns = {ppconfig.get("flask_exclude_patterns", config.flask_exclude_patterns)}
"""

    try:
        with open("pyproject.toml", "r") as f:
            pyproject_toml = f.read()
            if "[tool.flask-livetw]" in pyproject_toml:
                Term.info("Updating pyproject.toml...")
                pyproject_toml = re.sub(
                    r"\[tool\.flask-livetw\][^[]*", new_config, pyproject_toml
                )
            else:
                Term.info("Adding flask-livetw config to pyproject.toml...")
                pyproject_toml += new_config

        with open("pyproject.toml", "w") as f:
            f.write(pyproject_toml)
    except FileNotFoundError:
        Term.warn("Could not find pyproject.toml")
        Term.info("Creating pyproject.toml...")
        with open("pyproject.toml", "w") as f:
            f.write(new_config)

    return 0


def ask_project_layout(app_source: str | None = None) -> Config:
    Term.blank()

    flask_root = app_source
    if flask_root is None or flask_root == "":
        flask_root = Term.ask_dir(
            f"{PKG_PREFIX} Flask app root (relative to {Term.C}cwd/{Term.END}) [{DEFAULT_FLASK_ROOT}] ",
            default=DEFAULT_FLASK_ROOT,
        )

    static_folder = Term.ask_dir(
        f"{PKG_PREFIX} Static folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_FOLDER_STATIC}] ",
        flask_root,
        DEFAULT_FOLDER_STATIC,
    )

    templates_folder = Term.ask_dir(
        f"{PKG_PREFIX} Templates folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_FOLDER_TEMPLATE}] ",
        flask_root,
        DEFAULT_FOLDER_TEMPLATE,
    )

    templates_glob = (
        Term.ask(
            f"{PKG_PREFIX} Templates glob (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_TEMPLATES_GLOB}] ",
        )
        or DEFAULT_TEMPLATES_GLOB
    )

    root_layout_file = (
        Term.ask(
            f"{PKG_PREFIX} Root layout file (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_FILE_ROOT_LAYOUT}] ",
        )
        or DEFAULT_FILE_ROOT_LAYOUT
    )

    live_reload_file = (
        Term.ask(
            f"{PKG_PREFIX} Live reload file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_LIVE_RELOAD}] ",
        )
        or DEFAULT_FILE_LIVE_RELOAD
    )

    globalcss_file = (
        Term.ask(
            f"{PKG_PREFIX} Global css file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_GLOBALCSS}] ",
        )
        or DEFAULT_FILE_GLOBALCSS
    )

    tailwind_file = (
        Term.ask(
            f"{PKG_PREFIX} TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_TAILWIND}] ",
        )
        or DEFAULT_FILE_TAILWIND
    )

    tailwind_minified_file = (
        Term.ask(
            f"{PKG_PREFIX} Minified TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_MINIFIED_TAILWIND}] ",
        )
        or DEFAULT_FILE_MINIFIED_TAILWIND
    )

    if not flask_root or flask_root == ".":
        full_static_folder = static_folder
        full_templates_folder = templates_folder
    else:
        full_static_folder = f"{flask_root}/{static_folder}"
        full_templates_folder = f"{flask_root}/{templates_folder}"

    return Config(
        flask_root=flask_root,
        static_folder=static_folder,
        full_static_folder=full_static_folder,
        templates_folder=templates_folder,
        full_templates_folder=full_templates_folder,
        templates_glob=templates_glob,
        full_templates_glob=f"{full_templates_folder}/{templates_glob}",
        root_layout_file=root_layout_file,
        full_root_layout_file=f"{full_templates_folder}/{root_layout_file}",
        live_reload_file=live_reload_file,
        full_live_reload_file=f"{full_static_folder}/{live_reload_file}",
        globalcss_file=globalcss_file,
        full_globalcss_file=f"{full_static_folder}/{globalcss_file}",
        tailwind_file=tailwind_file,
        full_tailwind_file=f"{full_static_folder}/{tailwind_file}",
        tailwind_minified_file=tailwind_minified_file,
        full_tailwind_minified_file=f"{full_static_folder}/{tailwind_minified_file}",
        live_reload_host=DEFAULT_LIVERELOAD_HOST,
        live_reload_port=DEFAULT_LIVERELOAD_PORT,
        flask_host=DEFAULT_LIVERELOAD_HOST,
        flask_port=DEFAULT_LIVERELOAD_PORT,
        flask_exclude_patterns=[],
    )


def main() -> int:
    config = Config.from_pyproject_toml()
    print(config)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
