# Flask live tailwindcss

A simple package for adding a dev server to your flask app that automatically compiles the tailwindcss of the templates on file save and triggers a browser reload to sync the changes on the fly.


## Installation

This package is available on PyPI, you can install it using `pip` or other package manager of your choice.

```bash
pip install flask-livetw
```

Its a good practice to add as a development dependency. You can do this by adding the package to your `requirements-dev.txt` file or the "dev dependencies" of your package manager.

```txt
flask-livetw
```


## Initialization

To start using this package, go to your project folder or the folder where you want to develop. Then run the following command to initialize the package.

```bash
livetw init
```

> For default values use the `-d` or `--default` flag.

Then where you have your flask app add the following configuration to enable the live reload feature.

```py
import os

...

app.config["LIVETW_DEV"] = os.getenv("LIVETW_ENV") == "development"
```

When running the flask server separately during development remember to set the `LIVETW_DEV` to `True` in your flask app configuration to enable the live reload feature.

```py
app.config["LIVETW_DEV"] = True
```

For more information on the configuration options see the [Configuration](#configuration) section.


## Commands

Each command has its own help page, you can use the `-h` or `--help` flag to see the available options.

### dev

```bash
livetw dev
```

By default the command starts:

- a flask server in debug mode
- a live reload websocket server
- a tailwindcss in watch mode

This command sets the enviroment variable `LIVETW_ENV` to `development`. This is useful for conditional code execution.

### build

Builds the Tailwind CSS for the templates into a single CSS file.

```bash
livetw build
```

By default, the built Tailwind CSS file will be minified to reduce the file size. You can disable this feature by using the `--no-minify` flag.

```bash
livetw build --no-minify
```

### init

Initializes the package in the current directory. Its the command used in [Initialization](#initialization).

```bash
livetw init
```


## Configuration

After initialization, a `pyproject.toml` file will be created if it does not exist. In this file under the `[tool.flask-livetw]` section

This is an example of a configuration file with the default values:

```toml
[tool.flask-livetw]
flask_root = "src"
static_folder = "static"
template_folder = "templates"
template_glob = "**/*.html"
base_layout = "layout.html"
livetw_folder = ".dev"
flask_app = "app"
```

As a file tree, the configuration would look like this:

```txt
🌳 project_folder/
┣ 📁 src/
┃ ┣ 📁 static/
┃ ┃ ┣ 📁 .dev/
┃ ┃ ┗ ...
┃ ┣ 📁 templates/
┃ ┃ ┣ 📄 layout.html
┃ ┃ ┗ ...
┃ ┗ ...
┃ 📄 app.py
┣ 📄 pyproject.toml
┗ ...
```

### Main options

#### flask_root

The root folder of the flask application. All paths are relative to this folder.

Default is `"src"`.

#### flask_app

The argument `--app` passed to flask to discover the application. For more information see the [Flask Application Discovery](https://flask.palletsprojects.com/en/3.0.x/cli/) documentation.

Default is `"app"`.

#### static_folder

The folder where the static files are stored relative to the `flask_root`.

Default is `"static"`.

#### template_folder

The folder where the templates are stored relative to the `flask_root`.

Default is `"templates"`.

#### template_glob

The glob pattern to search for templates to build the Tailwind CSS. Must be relative to the `template_folder`.

Default is `"**/*.html"`.

For more information see the [Tailwindcss configuring source paths](https://tailwindcss.com/docs/content-configuration) documentation.

#### base_layout

The layout that is shared among all templates. This file is used to inject the Tailwind CSS and the live reload script. If it isn't shared among all templates, the Tailwind CSS and the live reload script won't be injected into the templates.

Default is `"layout.html"`.

#### livetw_folder

The folder where flask-livetw stores the related files.

It contains:

- `global.css`: The global CSS file for the application.
- `live_reload.js`: The live reload script for the application.
- `tailwind_development.css`: The Tailwind CSS file for the application during development.

Default is `".dev"`.

### Other options

#### global_css

The global CSS file for the application relative to the `livetw_folder`.

Default is `"global.css"`.

#### tailwind_prod

The production CSS file for the application relative to the `static_folder`.

Default is `"tailwind_production.css"`.

#### live_reload_host

The host for websocket server for the live reload functionality. If set must be manually sync on the live reload script for the client.

Default is `"127.0.0.1"`.

#### live_reload_port

The port for websocket server for the live reload functionality. If set must be manually sync on the live reload script for the client.

Default is `5678`.

#### flask_host

The host for the Flask application.

Default is `"127.0.0.1"`.

#### flask_port

The port for the Flask application.

Default is `5000`.

#### flask_exclude_patterns

The patterns to exclude python scripts from the Flask application. This is useful to exclude files from triggering the flask server to reload.


## Contributing

Contributions are welcome, feel free to submit a pull request or an issue.


## Packages used

- [pytailwindcss](https://github.com/timonweb/pytailwindcss)
- [tomli](https://github.com/hukkin/tomli)
- [websockets](https://github.com/python-websockets/websockets)


## License

[MIT](./LICENSE)
