# Setup

## Dependencies

You will need Python3.8 or greater. If you are building from source, you will need to install the libraries in the following sections. The versions have been frozen in the `requirements.txt` file, so they can be installed via,

```shell
pip install -r requirements.txtss
```

### Required
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
- [holidays](https://pypi.org/project/holidays/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [numpy](https://pypi.org/project/numpy/)>
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)>
- [scipy](https://pypi.org/project/scipy/)

### Optional
- [PySide6](https://pypi.org/project/PySide6/)

### Development

**Testing**
- [pytest](https://pypi.org/project/pytest/)
- [coverage](https://pypi.org/project/coverage/)
- [httmock](https://pypi.org/project/httmock/)

**Documentation**
- [sphinx](https://pypi.org/project/Sphinx/)
- [pdoc3](https://pypi.org/project/pdoc3/)

**Build**
- [setuptools](https://pypi.org/project/setuptools/)
- [twine](https://pypi.org/project/twine/)
- [build](https://pypi.org/project/build/)

## Installation

### PyPi Distribution

Install the package with the <b>Python</b> package manager,

```shell
pip install scrilla
``` 

This will install a command line interface on your path under the name `scrilla`. Confirm your installation with with the `version` command,

```shell
scrilla version
```

.. warning::
    If you are on Windows, you may need to add your Python scripts bin to the **$PATH**.

To keep the installation as minimal as possible, the base package does not include the GUI libraries. You can install the optional GUI dependency with,

```shell
pip install scrilla[gui]
```

Note, the GUI has a different CLI entrypoint, namely,

```shell
scrilla-gui
```

### Source

If you prefer, you can build from source. `git clone` the [repository](https://github.com/chinchalinchin/scrilla),

```shell
git clone https://github.com/chinchalinchin/scrilla.git
```

Then from the root directory install the project dependencies and build the library,

```shell
pip3 install -r requirements
python3 -m build
```

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

```
pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl
```