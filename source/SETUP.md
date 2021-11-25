# Setup

## Dependencies

You will need Python3.8 or greater. This application depends on the following <b>Python</b> libraries: 

### Required
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)>=2.8.2<br>
- [holidays](https://pypi.org/project/holidays/)>=0.10.4<br>
- [matplotlib](https://pypi.org/project/matplotlib/)>=3.3.3<br>
- [numpy](https://pypi.org/project/numpy/)>=1.19.3<br>
- [python-dotenv](https://pypi.org/project/python-dotenv/)>=0.17.0<br>
- [requests](https://pypi.org/project/requests/)>=2.25.0<br>
- [scipy](https://pypi.org/project/scipy/)>=1.5.4<br>

### Optional
- [PySide6](https://wiki.qt.io/Qt_for_Python)>=6.2.0<br>

### Development

**Testing**
- [pytest]()
- [coverage]()
- [httmock]()

**Documentation**
- [sphinx]()
- [pdoc3]()

**Build**
- [setuptools]()
- [twine]()
- [build]()

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

If you are on Windows, you may need to add your Python scripts bin to the $PATH. To keep the installation as minimal as possible, the base package does not include the GUI libraries. You can install the optional GUI dependency with,

```shell
pip install scrilla[gui]
```

Note, the GUI has a different CLI entrypoint, namely,

```shell
scrilla-gui
```

### Source

If you prefer, you can build from source. `git clone` the [repository](https://github.com/chinchalinchin/scrilla) and then from the root directory install the project dependencies and build the library,

```shell
pip3 install -r requirements
python3 -m build
```

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

```
pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl
```