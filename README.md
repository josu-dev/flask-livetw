# Flask live tailwindcss

A simple package for adding a dev server to your flask app that automatically compiles your tailwindcss of the templates on save and reloads your browser to sync the changes.

> **Note:** This package is intended to use with [poetry](https://python-poetry.org/). If you are not using poetry, you can still use this package by installing the dependencies manually.


## Integrate with poetry

### Installation

```bash
poetry add --group=dev flask-livetw
```

### Initialization

Simply go to your project root folder, run the following command and follow along the steps.

```bash
poetry run flask-livetw
```

> **Note 1:** If want to skip the questions, you can use the `-Y` or `--yes` flag.
>
> **Note 2:** If you want to use default values for the setup, you can use the `-D` or `--default` flag.
>
> **Note 3:** You can use the `-h` or `--help` flag to see the available options.

## Integrate with pip

### Installation

```bash
pip install flask-livetw
```

### Initialization

Simply go to your project root folder, run the following command and follow along the steps.

```bash
python -m flask_livetw
```

After the initialization, you need to install the dependencies manually.

```bash
pip install pytailwindcss python-dotenv websockets
```



## Usage

### Development

When developing your app, you can use the following command to start the dev server.

```bash
./dev.py dev
```

> **Note:** You can use the `-h` or `--help` flag to see the available options.

### Building

When you are done developing, you can use the following command to build your app.

```bash
./dev.py build
```

> **Note:** You can use the `-h` or `--help` flag to see the available options.


## Default values

### Package cli

```py
DEFAULT_FLASK_ROOT = 'src'

DEFAULT_STATIC_FOLDER = 'src/static'

DEFAULT_TEMPLATE_FOLDER = 'src/templates'
DEFAULT_TEMPLATE_GLOB = 'src/templates/**/*.html'

DEFAULT_ROOT_LAYOUT_FILE = 'src/templates/layout.html'
DEFAULT_LIVE_RELOAD_FILE = 'src/static/.dev/live_reload.js'
DEFAULT_TWCSS_FILE = 'src/static/.dev/tailwindcss.css'
DEFAULT_MINIFIED_TWCSS_FILE = 'src/static/tailwindcss_min.css'

DEFAULT_UPDATE_GITIGNORE = False
```

Example as file system tree:

```txt
project_root
├── src
│   ├── static
│   │   ├── .dev
│   │   │   ├── live_reload.js
│   │   │   └── tailwindcss.css
│   │   └── tailwindcss_min.css
│   └── templates
│       ├── layout.html
│       └── ...
├── .gitignore
├── dev.py
├── pyproject.toml
└── ...
```

### Dev server

```py
LRWS_HOST = '127.0.0.1'
LRWS_PORT = 5678
TW_OUTPUT_PATH = 'src/static/.dev/tailwindcss.css'
TW_OUTPUT_PATH_BUILD = 'src/static/tailwindcss_min.css'
```

## Contributing

Contributions are welcome, feel free to submit a pull request or an issue.

## Credits

- [pytailwindcss](https://github.com/timonweb/pytailwindcss)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [websockets](https://github.com/python-websockets/websockets)

## License

[MIT](./LICENSE)
