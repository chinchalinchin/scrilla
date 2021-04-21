# Command Line Interface Setup

## Load Environment

See [Environment](/configuration/ENVIRONMENT.md) for more info

You will want to export the environment variables defined in the <i>/env/<b>environment</b>.env</i> file into your current terminal session while using and developing the application. You can `source` the <i>scripts/util/env-vars.sh</i> shell script to load these variables,

`source ./scripts/util/env-vars.sh $ENVIRONMENT`

## CLI Application

### Building From Source Code 

- Note : the first time the CLI application is invoked, it loads a huge amount of data into the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.

First, from the project root directory, (activate your virtual environment, if using one, and) install all of the requirements,

`pip install -r requirements.txt`

For the application to retrieve data, it must be able to connect to <b>AlphaVantage</b>, <b>IEX</b> and <b>Quandl</b>. Register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). The application searches for environment variables called <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> that contain the respective API keys. These variables are loaded in through the <i>/env/local.env</i> environment file. There are several other environment variables that configure various aspects of the application. A <i>.sample.env</i> file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

`cp .sample.env local.env`

And then change the <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> variables to the values you received when you registered on their respective site. Once the API keys have been set, execute the `python main.py` script. Supply this script an argument preceded by a dash that specifies the function you wish to execute and the ticker symbols to which you wish to apply the function. 

You can add the <i>/scripts/</i> directory to your path to provide access to a BASH script for invoking the application with a python wrapper, i.e. if <i>/scripts/</i> is on your path, then

`pynance -help`

will execute the same function as 

`python $PATH_TO_PROJECT/main.py -help`

from any directory on your computer.

## PyPi Module

### Installation

TODO: Explain how to install package from PyPi.

TODO: Explain how to set API Key environment variables before using pynance.

TODO: actually do this.

The application module can also be installed through <b>pip</b> by installing its <i>Pypi</i> package,

`pip install pynance`

Before using the package, make sure to register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). Store your keys in environment keys named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b> respectively. 