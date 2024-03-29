# scrilla: A Financial Optimization Application

_scrilla_ is an open-source financial analysis application written in **Python**. It can optimize portfolios, calculate statistics using a variety of methods and algorithms, generate graphical plots and much more. It uses historical data retrieved from various sources, such as the US Treasury RSS Feed, AlphaVantage, IEX and Quandl, to calibrate models. 

**NOTE**: None of the results of _scrilla_ should be interpretted as financial advice. All results assume past trends will continue indefinitely into the future, which is usually never the case in reality.

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
| pypi/minor-update | [![CircleCI](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update.svg?style=svg)](https://circleci.com/gh/chinchalinchin/scrilla/tree/pypi%2Fminor-update) |
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

You may need to add your Python scripts _/bin/_ to the $PATH if this command is not found. 

To keep the installation as minimal as possible, the base package does not include the GUI libraries. You can install the optional GUI dependency ([PySide6](https://pypi.org/project/PySide6/)) with,

```shell
pip install scrilla[gui]
```

Note, the GUI has a different CLI entrypoint, namely,

```shell
scrilla-gui
```

### Source

If you are developing, you can build from source. `git clone` the [repository](https://github.com/chinchalinchin/scrilla) and then from the root directory install the project dependencies and build the library,

```shell
pip3 install -r requirements.txt
python3 -m build
```

`cd` into the generated <i>/dist/</i>  to manually install the packaged code,

```
pip install scrilla-<major>.<minor>.<micro>-py3-none-any.whl
```

## Configuration

In order to use this application, you will need to register for API keys with [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl/Nasdaq](https://www.quandl.com/). The program will need to be made aware of these keys somehow. The best option is storing these credentials in environment variables. You can add the following lines to your <i>.bashrc</i> profile or corresponding configuration file for whatever shell you are using,

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

If no API keys are found through either of these methods, the application will raise an exception.

**NOTE**: The **Quandl**/**Nasdaq** key is technically no required for the majority of the application to function, as interest rates are now retrieved directly from the **US Treasury** RSS feed. However, it is still recommended that you register for an API key, as **Quandl**/**Nasdaq** is still the only source of economic statistics, like GDP or inflation rates. 

### Environment File

A sample environment file has been included in _/env/.sample.env_. To configure the application environment, copy this file into a new environment, adjust the values and load it into your session,

```shell
cp ./env/.sample.env ./env/.env
# adjust .env values
source ./env/.env
# the values loaded into your session will now configure scrilla's execution environment
scrilla risk-profile GD LMT 
```
## Usage

### Portfolio Optimization

The following command will optimize a portfolio of consisting of *ALLY*, *BX*, *GLD*, *BTC* and *ETH* over the specified date range and save the result to a JSON file,

```shell
scrilla optimize-portfolio ALLY BX GLD BTC ETH \
    -start <YYYY-MM-DD> \
    -end <YYYY-MM-DD> \
    -save <absolute path to json file> 
```

### Efficient Frontier

The following command will calculaate the efficient frontier for a portfolio consisting of *SPY*, *GLD* and *USO* over the specified date range and save the result to a JSON file,

```shell
scrilla efficient-frontier SPY GLD USO \
    --start <YYYY-MM-DD> \
    --end <YYYY-MM-DD> \
    --save <absolute path to json file>
```

The following command will generate a plot of this frontier in the return-volatility plane,

```shell
scrilla plot-ef SPY GLD USO \
    --start <YYYY-MM-DD> \ 
    --end <YYYY-MM-DD> 
```

_scrilla_ has lots of other functions. See [usage](https://chinchalinchin.github.io/scrilla/USAGE.html) for more information.


## Cloud

TODO

currently working on a DynamoDB-based cache and Dockerfiles for lambda functions wrapped around scrilla's main features. will update this section once everything is completed.