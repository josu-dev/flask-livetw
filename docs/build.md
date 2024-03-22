# Build


## Setup

To avoid having to copy and paste the token every time you upload, you can create a $HOME/.pypirc file:

```ini
[pypi]
username = __token__
password = <the token value, including the `pypi-` prefix>
```

For more details, see the specification for [.pypirc](https://packaging.python.org/en/latest/specifications/pypirc/).

Update `twine`:

```bash
python -m pip install --upgrade twine
```


## Upload

First, build the package:

```bash
python -m build
```

Second, upload the package:

```bash
twine upload dist/*
```


## References

- [Example](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Setuptools data files](https://setuptools.pypa.io/en/latest/userguide/datafiles.html)
