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

DEFAULT_FILE_BASE_LAYOUT = "layout.html"

DEFAULT_FOLDER_LIVETW = ".dev"
DEFAULT_FILE_LIVE_RELOAD = "live_reload.js"
DEFAULT_FILE_GLOBAL_CSS = "global.css"
DEFAULT_FILE_DEV_CSS = "tailwind_development.css"
DEFAULT_FILE_PROD_CSS = "tailwind_production.css"

DEFAULT_LIVE_RELOAD_HOST = "127.0.0.1"
DEFAULT_LIVE_RELOAD_PORT = 5678

DEFAULT_FLASK_APP = "app"
DEFAULT_FLASK_HOST = None
DEFAULT_FLASK_PORT = None
DEFAULT_FLASK_EXCLUDE_PATTERNS: list[str] = []

DEFAULT_CONFIG_BASE = {
    "flask_root": DEFAULT_FLASK_ROOT,
    "static_folder": DEFAULT_FOLDER_STATIC,
    "templates_folder": DEFAULT_FOLDER_TEMPLATE,
    "templates_glob": DEFAULT_TEMPLATES_GLOB,
    "base_layout": DEFAULT_FILE_BASE_LAYOUT,
    "livetw_folder": DEFAULT_FOLDER_LIVETW,
    "flask_app": DEFAULT_FLASK_APP,
}

DEFAULT_CONFIG = {
    **DEFAULT_CONFIG_BASE,
    "global_css": DEFAULT_FILE_GLOBAL_CSS,
    "tailwind_dev": DEFAULT_FILE_DEV_CSS,
    "tailwind_prod": DEFAULT_FILE_PROD_CSS,
    "live_reload": DEFAULT_FILE_LIVE_RELOAD,
    "live_reload_host": DEFAULT_LIVE_RELOAD_HOST,
    "live_reload_port": DEFAULT_LIVE_RELOAD_PORT,
    "flask_host": DEFAULT_FLASK_HOST,
    "flask_port": DEFAULT_FLASK_PORT,
    "flask_exclude_patterns": DEFAULT_FLASK_EXCLUDE_PATTERNS,
}


def get_pyproject_toml(base_dir: str | None = None) -> dict[str, Any] | None:
    path = "pyproject.toml"
    if base_dir is not None and base_dir.strip():
        path = f"{base_dir.strip()}/{path}"

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
    templates_folder: str
    templates_glob: str
    base_layout: str
    livetw_folder: str
    global_css: str
    tailwind_dev: str
    tailwind_prod: str
    live_reload: str
    live_reload_host: str
    live_reload_port: int
    flask_app: str | None
    flask_host: str | None
    flask_port: int | None
    flask_exclude_patterns: list[str] | None

    full_static_folder: str = dataclasses.field(init=False)
    full_templates_folder: str = dataclasses.field(init=False)
    full_templates_glob: str = dataclasses.field(init=False)
    full_base_layout: str = dataclasses.field(init=False)
    full_livetw_folder: str = dataclasses.field(init=False)
    full_live_reload: str = dataclasses.field(init=False)
    full_global_css: str = dataclasses.field(init=False)
    full_tailwind_dev: str = dataclasses.field(init=False)
    full_tailwind_prod: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.full_static_folder = f"{self.flask_root}/{self.static_folder}"
        self.full_templates_folder = (
            f"{self.flask_root}/{self.templates_folder}"
        )
        self.full_templates_glob = (
            f"{self.full_templates_folder}/{self.templates_glob}"
        )
        self.full_base_layout = (
            f"{self.full_templates_folder}/{self.base_layout}"
        )
        self.full_livetw_folder = (
            f"{self.full_static_folder}/{self.livetw_folder}"
        )
        self.full_live_reload = f"{self.full_livetw_folder}/{self.live_reload}"
        self.full_global_css = f"{self.full_livetw_folder}/{self.global_css}"
        self.full_tailwind_dev = (
            f"{self.full_livetw_folder}/{self.tailwind_dev}"
        )
        self.full_tailwind_prod = (
            f"{self.full_static_folder}/{self.tailwind_prod}"
        )

    @staticmethod
    def from_dict_with_defaults(
        src_dict: dict[str, Any], base_dir: str | None = None
    ) -> Config:
        flask_root = src_dict.get("flask_root", DEFAULT_FLASK_ROOT)
        if isinstance(base_dir, str) and base_dir != "":
            base_dir = base_dir.rstrip("/")
            flask_root = f"{base_dir}/{flask_root}"

        config_args: dict[str, Any] = {}
        for key in DEFAULT_CONFIG:
            value = src_dict.get(key)
            if value is None or type(value) is not type(DEFAULT_CONFIG[key]):
                value = DEFAULT_CONFIG[key]

            config_args[key] = value

        config_args["flask_root"] = flask_root

        return Config(**config_args)

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


def add_toml_field(
    key: str,
    value: Any,
    acc: str,
) -> str:
    if type(value) is str:
        return f'{acc}\n{key} = "{value}"'

    return f"{acc}\n{key} = {value}"


def update_pyproject_toml(
    config: Config, keys: list[str] | None = None
) -> int:
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

    user_config = pyproject.get("tool", {}).get("flask-livetw", {})  # type: ignore # noqa: F841

    livetw_config = "[tool.flask-livetw]"
    for key in keys or DEFAULT_CONFIG:
        livetw_config = add_toml_field(
            key, getattr(config, key, DEFAULT_CONFIG[key]), livetw_config
        )

    livetw_config += "\n"

    try:
        with open("pyproject.toml", "r") as f:
            pyproject_toml = f.read()
            if "[tool.flask-livetw]" in pyproject_toml:
                pyproject_toml = re.sub(
                    r"\[tool\.flask-livetw\][^[]*",
                    livetw_config,
                    pyproject_toml,
                )
            else:
                pyproject_toml = pyproject_toml.rstrip()
                if len(pyproject_toml):
                    pyproject_toml += "\n\n"
                pyproject_toml += livetw_config

        with open("pyproject.toml", "w") as f:
            f.write(pyproject_toml)
    except FileNotFoundError:
        Term.info("Could not find pyproject.toml")
        Term.info("Creating pyproject.toml...")
        with open("pyproject.toml", "w") as f:
            f.write(livetw_config)

    return 0


def ask_project_layout(app_source: str | None = None) -> Config:
    flask_root = app_source
    if flask_root is None or flask_root == "":
        flask_root = Term.ask_dir(
            f"{PKG_PP} Flask app root {Term.C}cwd/{Term.END} [{DEFAULT_FLASK_ROOT}] ",
            default=DEFAULT_FLASK_ROOT,
        )

    static_folder = Term.ask_dir(
        f"{PKG_PP} Static folder {Term.C}cwd/{flask_root}/{Term.END} [{DEFAULT_FOLDER_STATIC}] ",
        flask_root,
        DEFAULT_FOLDER_STATIC,
    )

    templates_folder = Term.ask_dir(
        f"{PKG_PP} Templates folder {Term.C}cwd/{flask_root}/{Term.END} [{DEFAULT_FOLDER_TEMPLATE}] ",
        flask_root,
        DEFAULT_FOLDER_TEMPLATE,
    )

    templates_glob = (
        Term.ask(
            f"{PKG_PP} Templates glob {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END} [{DEFAULT_TEMPLATES_GLOB}] ",
        )
        or DEFAULT_TEMPLATES_GLOB
    )

    base_layout = (
        Term.ask(
            f"{PKG_PP} Base layout {Term.C}cwd/{flask_root}/{templates_folder}/{Term.END} [{DEFAULT_FILE_BASE_LAYOUT}] ",
        )
        or DEFAULT_FILE_BASE_LAYOUT
    )

    livetw_folder = (
        Term.ask(
            f"{PKG_PP} Livetw folder {Term.C}cwd/{flask_root}/{static_folder}/{Term.END} [{DEFAULT_FOLDER_LIVETW}] ",
        )
        or DEFAULT_FOLDER_LIVETW
    )

    flask_app = (
        Term.ask(
            f"{PKG_PP} Flask entry point {Term.C}cwd/{Term.END} [{DEFAULT_FLASK_APP}] ",
        )
        or DEFAULT_FLASK_APP
    )

    if not flask_root:
        flask_root = "."

    return Config(
        flask_root=flask_root,
        static_folder=static_folder,
        templates_folder=templates_folder,
        templates_glob=templates_glob,
        base_layout=base_layout,
        livetw_folder=livetw_folder,
        live_reload=DEFAULT_FILE_LIVE_RELOAD,
        global_css=DEFAULT_FILE_GLOBAL_CSS,
        tailwind_dev=DEFAULT_FILE_DEV_CSS,
        tailwind_prod=DEFAULT_FILE_PROD_CSS,
        live_reload_host=DEFAULT_LIVE_RELOAD_HOST,
        live_reload_port=DEFAULT_LIVE_RELOAD_PORT,
        flask_app=flask_app,
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
