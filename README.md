# Flask live tailwindcss

A simple package for adding a dev server to your flask app that automatically compiles the tailwindcss of the templates on file save and triggers a browser reload to sync the changes on the fly.


## Installation

```bash
# using poetry
poetry add --group=dev flask-livetw

# using pip
pip install flask-livetw
```


## Initialization

To start using this package, simply go to your project root folder, run the following command and follow along the steps.

```bash
# using poetry
poetry shell
flask-livetw init

# using pip
"activate your virtual environment like you normally do"
flask-livetw init
```

> **Note 1:** To skip requirements check use the `-Y` or `--yes` flag.
>
> **Note 2:** To use default values for the initialization use the `-D` or `--default` flag.

### Default values

```py
FLASK_ROOT = "src"

STATIC_FOLDER = "src/static"

TEMPLATE_FOLDER = "src/templates"
TEMPLATE_GLOB = "src/templates/**/*.html"
ROOT_LAYOUT_FILE = "src/templates/layout.html"

LIVE_RELOAD_FILE = "src/static/.dev/live_reload.js"

GLOBALCSS_FILE = "src/static/.dev/global.css"
TAILWIND_FILE = "src/static/.dev/tailwind.css"
MINIFIED_TAILWIND_FILE = "src/static/tailwind_min.css"

UPDATE_GITIGNORE = False
```

Example as file system tree:

```txt
project_root
├── src
│   ├── static
│   │   ├── .dev
│   │   │   ├── global.css
│   │   │   ├── live_reload.js
│   │   │   └── tailwind.css
│   │   ├── tailwind_min.css
│   │   ...
│   └── templates
│       ├── layout.html
│       ...
├── .gitignore
├── pyproject.toml
...
```


## Commands

In order to use the commands, you need to activate your virtual environment first.

```bash
# using poetry
poetry shell

# using pip
"activate your virtual environment like you normally do"
```

Each command has its own help page, you can use the `-h` or `--help` flag to see the available options.

### dev

```bash
flask-livetw dev
```

By default the command starts:

- a flask server in debug mode
- a live reload websocket server
- a tailwindcss in watch mode

During development time the enviroment variable `LIVETW_DEV` is set to `TRUE`, `os.environ["LIVETW_DEV"] == "TRUE"`. This is useful for conditional code execution.

### build

Builds the tailwindcss of the templates as a single css file.

```bash
flask-livetw build
```

By default the builded tailwindcss file will be minified.

During building time the enviroment variable `LIVETW_BUILD` is set to `TRUE`, `os.environ["LIVETW_BUILD"] == "TRUE"`. This is useful for conditional code execution.

### local-install

```bash
flask-livetw local-install
```

This command creates a local script that mimics the `flask-livetw` command and adds the necessary dependencies to your project in order to use the `dev` and `build` commands.

After the installation, you can use the `dev` and `build` commands as follows:

```bash
./dev.py dev
./dev.py build
```


## Contributing

Contributions are welcome, feel free to submit a pull request or an issue.


## Packages used

- [pytailwindcss](https://github.com/timonweb/pytailwindcss)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [tomli](https://github.com/hukkin/tomli)
- [websockets](https://github.com/python-websockets/websockets)


## License

[MIT](./LICENSE)
