# Setup

This application was built and tested on Python 3.9. 

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
If you are on Windows, you may need to add your Python scripts bin to the **$PATH**.

To keep the installation as minimal as possible, the base package does not include the GUI libraries. You can install the optional GUI with,

```shell
pip install scrilla[gui]
```

The GUI has a different CLI entrypoint, namely,

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