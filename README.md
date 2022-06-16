**NOTE**: Quandl was acquired by Nasdaq and their APIs were incorporated into the existing data.nasdaq APIs. The support for some of the feeds was dropped in the reshuffling. In particular, the free feed for the yield curve (USTREASURY/YIELD) is no longer refreshed daily and, in fact, hasn't been refreshed since February of this year. This was the feed this application used to determine the latest interest rate. As a result, any calculations involving interest rate since approximately 02-01-2022 (which is virtually every calculation in this application...) will fail, since there is no interest rate to retrieve. 

Currently working on directly parsing the treasury.gov's XML feed for the yield curve instead of Nasdaq/Quandl's Rest API. 

# scrilla: A Financial Optimization Application

![](https://github.com/chinchalinchin/chinchalinchin/blob/main/assets/scrilla_gui_ii.png)

Documentation
---
- [Overview](https://chinchalinchin.github.io/scrilla/)
- [Packages](https://chinchalinchin.github.io/scrilla/package/index.html)

Coverage
---
- [Unit Tests](https://chinchalinchin.github.io/scrilla/coverage/index.html)

Code Analysis
---
[![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=active+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)<br/>
[![DeepSource](https://deepsource.io/gh/chinchalinchin/scrilla.svg/?label=resolved+issues&show_trend=true&token=tD25pyXAL4uIvrccqjlwzXIU)](https://deepsource.io/gh/chinchalinchin/scrilla/?ref=repository-badge)<br/>

Pipelines
---
| Branch | Status |
| ------ | ------ |
| pypi/micro-update | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fmicro-update.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fmicro-update) |
| pypi/micro-update | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update) |
| develop/main | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/develop%2Fmain.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/develop%2Fmain)| 


## Quick Start

Refer to the [documentation](https://chinchalinchin.github.io/scrilla/) for more detailed information on installation and usage.

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
pip3 install -r requirements.txt
python3 -m build
```

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

```
pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl
```

## Configuration

In order to use this application, you will need to register for API keys with [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). The program will need to be made aware of these keys somehow. The best option is storing these credentials in environment variables. You can add the following lines to your <i>.bashrc</i> profile or corresponding configuration file for whatever shell you are using,

```shell
export ALPHA_VANTAGE_KEY=<key goes here>
export QUANDL_KEY=<key goes here>
export IEX_KEY=<key goes here>
```

You can also invoke the CLI function `store` to store the credentials in the local installation <i>/data/common/</i> directory. To do so,

```shell
scrilla store -key <key> -value <value>
```

where `<key>` is one of the values: **ALPHA_VANTAGE_KEY**, **QUANDL_KEY** or **IEX_KEY**. `<value>` is the corresponding key itself given to you after registration. Obviously, `<value>` is case-sensitive

Keep in mind if using this method to store the API keys, the keys will be stored unencrypted in the local installation's <i>/data/common/</i> directory. The recommended method is storing the credentials in the environment. 

If no API keys are found through either of these methods, the application will not function properly.

## Usage

The following command will optimize a portfolio of consisting of *ALLY*, *BX*, *GLD*, *BTC* and *ETH* over the specified date range and save the result to a JSON file.

```shell
scrilla optimize-portfolio ALLY BX GLD BTC ETH \
    -start <YYYY-MM-DD> \
    -end <YYYY-MM-DD> \
    -save <absolute path to json file> 
```

See [usage](https://chinchalinchin.github.io/scrilla/USAGE.html) for more information.