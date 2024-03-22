from __future__ import annotations

import dataclasses
import re
from typing import Any

import tomli

from flask_livetw.util import PKG_PP, Term

DEFAULT_FLASK_ROOT = "src"

DEFAULT_FOLDER_STATIC = "static"

DEFAULT_FOLDER_TEMPLATE = "templates"
DEFAULT_TEMPLATES_GLOB = "**/*.html"

DEFAULT_FILE_ROOT_LAYOUT = "layout.html"
DEFAULT_FILE_LIVE_RELOAD = ".dev/live_reload.js"
DEFAULT_FILE_GLOBALCSS = ".dev/global.css"
DEFAULT_FILE_TAILWIND = ".dev/tailwind.css"
DEFAULT_FILE_MINIFIED_TAILWIND = "tailwind_min.css"

DEFAULT_LIVERELOAD_HOST = "127.0.0.1"
DEFAULT_LIVERELOAD_PORT = 5678

DEFAULT_FLASK_HOST = None
DEFAULT_FLASK_PORT = None
DEFAULT_FLASK_EXCLUDE_PATTERNS = []


def get_pyproject_toml(base_dir: str | None = None) -> dict[str, Any] | None:
    path = (
        f"{base_dir.strip()}/pyproject.toml"
        if base_dir and base_dir.strip()
        else "pyproject.toml"
    )
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

    flask_host: str | None
    flask_port: int | None
    flask_exclude_patterns: list[str] | None

    @staticmethod
    def from_dict_with_defaults(
        src_dict: dict[str, Any], base_dir: str | None = None
    ) -> Config:
        flask_root = src_dict.get("flask_root", DEFAULT_FLASK_ROOT)
        static_folder = src_dict.get("static_folder", DEFAULT_FOLDER_STATIC)
        templates_folder = src_dict.get(
            "templates_folder", DEFAULT_FOLDER_TEMPLATE
        )

        if isinstance(base_dir, str) and base_dir != "":
            base_dir = base_dir.rstrip("/")
            full_static_folder = f"{base_dir}/{flask_root}/{static_folder}"
            full_templates_folder = (
                f"{base_dir}/{flask_root}/{templates_folder}"
            )
        else:
            full_static_folder = f"{flask_root}/{static_folder}"
            full_templates_folder = f"{flask_root}/{templates_folder}"

        templates_glob = src_dict.get("templates_glob", DEFAULT_TEMPLATES_GLOB)
        root_layout_file = src_dict.get(
            "root_layout_file", DEFAULT_FILE_ROOT_LAYOUT
        )
        live_reload_file = src_dict.get(
            "live_reload_file", DEFAULT_FILE_LIVE_RELOAD
        )
        globalcss_file = src_dict.get("globalcss_file", DEFAULT_FILE_GLOBALCSS)
        tailwind_file = src_dict.get("tailwind_file", DEFAULT_FILE_TAILWIND)
        tailwind_minified_file = src_dict.get(
            "tailwind_minified_file", DEFAULT_FILE_MINIFIED_TAILWIND
        )
        live_reload_host = src_dict.get(
            "live_reload_host", DEFAULT_LIVERELOAD_HOST
        )
        live_reload_port = src_dict.get(
            "live_reload_port", DEFAULT_LIVERELOAD_PORT
        )
        flask_host = src_dict.get("flask_host", DEFAULT_FLASK_HOST)
        flask_port = src_dict.get("flask_port", DEFAULT_FLASK_PORT)
        flask_exclude_patterns = src_dict.get(
            "flask_exclude_patterns", DEFAULT_FLASK_EXCLUDE_PATTERNS
        )

        config_dict: dict[str, Any] = {
            "flask_root": flask_root,
            "static_folder": static_folder,
            "full_static_folder": full_static_folder,
            "templates_folder": templates_folder,
            "full_templates_folder": full_templates_folder,
            "templates_glob": templates_glob,
            "full_templates_glob": f"{full_templates_folder}/{templates_glob}",
            "root_layout_file": root_layout_file,
            "full_root_layout_file": f"{full_templates_folder}/{root_layout_file}",
            "live_reload_file": live_reload_file,
            "full_live_reload_file": f"{full_static_folder}/{live_reload_file}",
            "globalcss_file": globalcss_file,
            "full_globalcss_file": f"{full_static_folder}/{globalcss_file}",
            "tailwind_file": tailwind_file,
            "full_tailwind_file": f"{full_static_folder}/{tailwind_file}",
            "tailwind_minified_file": tailwind_minified_file,
            "full_tailwind_minified_file": f"{full_static_folder}/{tailwind_minified_file}",
            "live_reload_host": live_reload_host,
            "live_reload_port": live_reload_port,
            "flask_host": flask_host,
            "flask_port": flask_port,
            "flask_exclude_patterns": flask_exclude_patterns,
        }

        return Config(**config_dict)

    @staticmethod
    def default(base_dir: str | None = None) -> Config:
        return Config.from_dict_with_defaults({}, base_dir)

    @staticmethod
    def try_from_pyproject_toml(base_dir: str | None = None) -> Config | None:
        if base_dir is None or base_dir == "":
            base_dir = "."
        else:
            base_dir = base_dir.rstrip("/")

        pyproject = get_pyproject_toml(base_dir)
        if pyproject is None:
            return None

        tool_config = pyproject.get("tool")
        if tool_config is None:
            return None

        flask_livetw_config = tool_config.get("flask-livetw")
        if flask_livetw_config is None:
            return None

        return Config.from_dict_with_defaults(flask_livetw_config, base_dir)

    @staticmethod
    def from_pyproject_toml(base_dir: str | None = None) -> Config:
        """Errors are ignored and default values are used instead"""
        if base_dir is None or base_dir == "":
            base_dir = "."

        pyproject = get_pyproject_toml(base_dir)
        if pyproject is None:
            pyproject = {}

        config = pyproject.get("tool", {})
        if not isinstance(
            config, dict
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            config: dict[str, Any] = {}

        config = config.get("flask-livetw", {})
        if not isinstance(
            config, dict
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            config = {}

        return Config.from_dict_with_defaults(config, base_dir)


def add_field(
    pyproject: dict[str, Any],
    key: str,
    new_config: Config,
    default: Any,
    acc: str,
) -> str:
    value = pyproject.get(key, getattr(new_config, key))
    if value == default:
        return acc

    value_type = type(value)
    if value_type == str:
        return f'{acc}\n{key} = "{value}"'

    return f"{acc}\n{key} = {value}"


def update_pyproject_toml(config: Config) -> int:
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

    new_config = """\n[tool.flask-livetw]"""
    new_config = add_field(
        ppconfig, "flask_root", config, DEFAULT_FLASK_ROOT, new_config
    )
    new_config = add_field(
        ppconfig, "static_folder", config, DEFAULT_FOLDER_STATIC, new_config
    )
    new_config = add_field(
        ppconfig,
        "templates_folder",
        config,
        DEFAULT_FOLDER_TEMPLATE,
        new_config,
    )
    new_config = add_field(
        ppconfig, "templates_glob", config, DEFAULT_TEMPLATES_GLOB, new_config
    )
    new_config = add_field(
        ppconfig,
        "root_layout_file",
        config,
        DEFAULT_FILE_ROOT_LAYOUT,
        new_config,
    )
    new_config = add_field(
        ppconfig,
        "live_reload_file",
        config,
        DEFAULT_FILE_LIVE_RELOAD,
        new_config,
    )
    new_config = add_field(
        ppconfig, "globalcss_file", config, DEFAULT_FILE_GLOBALCSS, new_config
    )
    new_config = add_field(
        ppconfig, "tailwind_file", config, DEFAULT_FILE_TAILWIND, new_config
    )
    new_config = add_field(
        ppconfig,
        "tailwind_minified_file",
        config,
        DEFAULT_FILE_MINIFIED_TAILWIND,
        new_config,
    )
    new_config = add_field(
        ppconfig,
        "live_reload_host",
        config,
        DEFAULT_LIVERELOAD_HOST,
        new_config,
    )
    new_config = add_field(
        ppconfig,
        "live_reload_port",
        config,
        DEFAULT_LIVERELOAD_PORT,
        new_config,
    )
    new_config = add_field(
        ppconfig, "flask_host", config, DEFAULT_FLASK_HOST, new_config
    )
    new_config = add_field(
        ppconfig, "flask_port", config, DEFAULT_FLASK_PORT, new_config
    )
    new_config = add_field(
        ppconfig,
        "flask_exclude_patterns",
        config,
        DEFAULT_FLASK_EXCLUDE_PATTERNS,
        new_config,
    )
    new_config += "\n"

    try:
        with open("pyproject.toml", "r") as f:
            pyproject_toml = f.read()
            if "[tool.flask-livetw]" in pyproject_toml:
                pyproject_toml = re.sub(
                    r"\[tool\.flask-livetw\][^[]*", new_config, pyproject_toml
                )
            else:
                pyproject_toml += new_config

        with open("pyproject.toml", "w") as f:
            f.write(pyproject_toml)
    except FileNotFoundError:
        Term.info("Could not find pyproject.toml")
        Term.info("Creating pyproject.toml...")
        with open("pyproject.toml", "w") as f:
            f.write(new_config)

    return 0


def ask_project_layout(app_source: str | None = None) -> Config:
    flask_root = app_source
    if flask_root is None or flask_root == "":
        flask_root = Term.ask_dir(
            f"{PKG_PP} Flask app root (relative to {Term.C}cwd/{Term.END}) [{DEFAULT_FLASK_ROOT}] ",
            default=DEFAULT_FLASK_ROOT,
        )

    static_folder = Term.ask_dir(
        f"{PKG_PP} Static folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_FOLDER_STATIC}] ",
        flask_root,
        DEFAULT_FOLDER_STATIC,
    )

    templates_folder = Term.ask_dir(
        f"{PKG_PP} Templates folder (relative to {Term.C}cwd/{flask_root}/{Term.END}) [{DEFAULT_FOLDER_TEMPLATE}] ",
        flask_root,
        DEFAULT_FOLDER_TEMPLATE,
    )

    templates_glob = (
        Term.ask(
            f"{PKG_PP} Templates glob (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_TEMPLATES_GLOB}] ",
        )
        or DEFAULT_TEMPLATES_GLOB
    )

    root_layout_file = (
        Term.ask(
            f"{PKG_PP} Root layout file (relative to {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END}) [{DEFAULT_FILE_ROOT_LAYOUT}] ",
        )
        or DEFAULT_FILE_ROOT_LAYOUT
    )

    live_reload_file = (
        Term.ask(
            f"{PKG_PP} Live reload file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_LIVE_RELOAD}] ",
        )
        or DEFAULT_FILE_LIVE_RELOAD
    )

    globalcss_file = (
        Term.ask(
            f"{PKG_PP} Global css file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_GLOBALCSS}] ",
        )
        or DEFAULT_FILE_GLOBALCSS
    )

    tailwind_file = (
        Term.ask(
            f"{PKG_PP} TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_TAILWIND}] ",
        )
        or DEFAULT_FILE_TAILWIND
    )

    tailwind_minified_file = (
        Term.ask(
            f"{PKG_PP} Minified TailwindCSS file (relative to {Term.C}cwd/{flask_root}/{static_folder}/{Term.END}) [{DEFAULT_FILE_MINIFIED_TAILWIND}] ",
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
        flask_host=DEFAULT_FLASK_HOST,
        flask_port=DEFAULT_FLASK_PORT,
        flask_exclude_patterns=DEFAULT_FLASK_EXCLUDE_PATTERNS,
    )


def main() -> int:
    config = Config.from_pyproject_toml()
    print(config)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
