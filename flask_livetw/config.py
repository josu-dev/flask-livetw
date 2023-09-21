from __future__ import annotations

import dataclasses
from typing import Any

import tomli

from flask_livetw.util import Term

PKG_PREFIX = "livetw"

DEFAULT_FLASK_ROOT = "src"

DEFAULT_STATIC_FOLDER = "static"

DEFAULT_TEMPLATE_FOLDER = "templates"
DEFAULT_TEMPLATE_GLOB = "**/*.html"

DEFAULT_FILE_ROOT_LAYOUT = "layout.html"
DEFAULT_FILE_LIVE_RELOAD = ".dev/live_reload.js"
DEFAULT_FILE_GLOBALCSS = ".dev/global.css"
DEFAULT_FILE_TWCSS = ".dev/tailwindcss.css"
DEFAULT_FILE_MINIFIED_TWCSS = "tailwindcss_min.css"


LRWS_HOST = "127.0.0.1"
LRWS_PORT = 5678

DEFAULT_UPDATE_GITIGNORE = False


def get_pyproject_toml(base_dir: str = "") -> dict[str, Any] | None:
    path = f"{base_dir}/pyproject.toml" if base_dir else "pyproject.toml"
    try:
        with open(path, "rb") as f:
            return tomli.load(f)
    except tomli.TOMLDecodeError as e:
        Term.warn(f"Malformed pyproject.toml: {e}")
        return None


@dataclasses.dataclass
class Config:
    base_dir: str
    templates_glob: str
    live_reload_file: str
    globalcss_file: str
    twcss_file: str
    minified_twcss_file: str
    root_layout_file: str
    full_templates_glob: str
    full_live_reload_file: str
    full_globalcss_file: str
    full_twcss_file: str
    full_minified_twcss_file: str
    full_root_layout_file: str

    @staticmethod
    def default(base_dir: str = ""):
        return Config(
            base_dir=base_dir,
            templates_glob=DEFAULT_TEMPLATE_GLOB,
            live_reload_file=DEFAULT_FILE_LIVE_RELOAD,
            globalcss_file=DEFAULT_FILE_GLOBALCSS,
            twcss_file=DEFAULT_FILE_TWCSS,
            minified_twcss_file=DEFAULT_FILE_MINIFIED_TWCSS,
            root_layout_file=DEFAULT_FILE_ROOT_LAYOUT,
            full_templates_glob=f"{base_dir}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_TEMPLATE_GLOB}",
            full_live_reload_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_LIVE_RELOAD}",
            full_globalcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_GLOBALCSS}",
            full_twcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_TWCSS}",
            full_minified_twcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_MINIFIED_TWCSS}",
            full_root_layout_file=f"{base_dir}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_FILE_ROOT_LAYOUT}",
        )

    @staticmethod
    def from_pyproject_toml(base_dir: str = ""):
        pyproject_toml = get_pyproject_toml(base_dir)
        if (
            pyproject_toml is None
            or ("tool" not in pyproject_toml)
            or ("flask-livetw" not in pyproject_toml["tool"])
        ):
            return Config.default(base_dir)

        config: dict[str, Any] = pyproject_toml["tool"]["flask-livetw"]

        return Config(
            base_dir=base_dir,
            templates_glob=config.get("templates_glob", DEFAULT_TEMPLATE_GLOB),
            live_reload_file=config.get(
                "live_reload_file", DEFAULT_FILE_LIVE_RELOAD
            ),
            globalcss_file=config.get(
                "globalcss_file", DEFAULT_FILE_GLOBALCSS
            ),
            twcss_file=config.get("twcss_file", DEFAULT_FILE_TWCSS),
            minified_twcss_file=config.get(
                "minified_twcss_file", DEFAULT_FILE_MINIFIED_TWCSS
            ),
            root_layout_file=config.get(
                "root_layout_file", DEFAULT_FILE_ROOT_LAYOUT
            ),
            full_templates_glob=f"{base_dir}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_TEMPLATE_GLOB}",
            full_live_reload_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_LIVE_RELOAD}",
            full_globalcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_GLOBALCSS}",
            full_twcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_TWCSS}",
            full_minified_twcss_file=f"{base_dir}/{DEFAULT_STATIC_FOLDER}/{DEFAULT_FILE_MINIFIED_TWCSS}",
            full_root_layout_file=f"{base_dir}/{DEFAULT_TEMPLATE_FOLDER}/{DEFAULT_FILE_ROOT_LAYOUT}",
        )


def main() -> int:
    config = Config.from_pyproject_toml()
    print(config)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
