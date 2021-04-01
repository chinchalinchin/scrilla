# Setup

## Prerequisites
- [Python 3.8 +](https://www.python.org/downloads/) <br>
- [Docker](https://www.docker.com/products/docker-desktop) (Not required, but recommended for deploying application as a microservice.)<br>

## Load Environment

See [Environment](/configuration/ENVIRONMENT.md) for more info

You will want to export the environment variables defined in the <i>/env/<b>environment</b>.env</i> file into your current terminal session while using and developing the application. You can `source` the <i>scripts/util/env-vars.sh</i> shell script to load these variables,

`source ./scripts/util/env-vars.sh $ENVIRONMENT`

## PyPi Package

The application module can also be installed through <b>pip</b> by installing its <i>Pypi</i> package,

`pip install pynance`

Before using the package, make sure to register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). Store your keys in environment keys named <b>ALPHA_VANTAGE_KEY</b>, <b>QUANDL_KEY</b> and <b>IEX_KEY</b> respectively. 


## CLI Application

### Building From Source Code 

- Note : the first time the CLI application is invoked, it loads a huge amount of data into the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.

First, from the project root directory, (activate your virtual environment, if using one, and) install all of the requirements,

`pip install -r requirements.txt`

For the application to retrieve data, it must be able to connect to <b>AlphaVantage</b>, <b>IEX</b> and <b>Quandl</b>. Register for API keys at [AlphaVantage](https://www.alphavantage.co), [IEX](https://iexcloud.io/) and [Quandl](https://www.quandl.com/). The application searches for environment variables called <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> that contain the respective API keys. These variables are loaded in through the <i>/env/local.env</i> environment file. There are several other environment variables that configure various aspects of the application. A <i>.sample.env</i> file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

`cp .sample.env local.env`

And then change the <b>ALPHA_VANTAGE_KEY</b>, <b>IEX_KEY</b> and <b>QUANDL_KEY</b> variables to the values you received when you registered on their respective site. Once the API keys have been set, execute the `python main.py` script. Supply this script an argument preceded by a dash that specifies the function you wish to execute and the ticker symbols to which you wish to apply the function. 

You can add the <i>/scripts/</i> directory to your path to provide access to a BASH script for invoking the application with a python wrapper, i.e. if <i>/scripts/</i> is on your path, then

> pynance -help

will execute the same function as 

> python $PATH_TO_PROJECT/main.py -help

from any directory on your computer.

## PyPi Module

### Installation

TODO: Explain how to install package from PyPi.

TODO: Explain how to set API Key environment variables before using pynance.

## WSGI Application

### Local Setup

The application's functions can also be exposed through an API (a work in progress). To launch the API on your <i>localhost</i>, first configure the <b>APP_PORT</b> in the <i>/env/local.env</i> file. Then, from the <i>/server/pynance_api</i> directory execute,

> python manage.py runserver $APP_PORT

Alternatively, you can run the <i>/scripts/server/launch-server.sh</i> script with an argument of <i>-local</i>,

>./scripts/server/launch-server.sh -local

This will launch the Django app and expose it on your <i>localhost</i>.

### Container Setup

First create a new environment file,

> cp .sample.env container.env

and make sure the <b>APP_ENV</b> variable is set to <i>container</i>. Initialize your environment in your current shell session by executing from the project root directory,

> source ./scripts/util/env-vars.sh container

After you have your environment file initialized, note the <b>IMG_NAME</b>, <b>TAG_NAME</b> and <b>APP_CONTAINER_NAME</b> environment variables will set the image, tag and container name respectively (if that wasn't obvious). 

To start up the server in a container, execute the <i>launch-server</i> script, but provide it an argument of `-container`,

>./scripts/server/pynance-server.sh -container

Or, if you want to build the image without spinning up the container,

>./scripts/docker/pynance-container.sh

Once the image has been built, you can spin up the container using (assuming your environment file has been initialized and loaded into your shell session),

> docker run 
> --publish $APP_PORT:$APP_PORT \\ <br>
> --env-file /path/to/env/file $IMG_NAME:$IMG_TAG

Note, the image will need an environment file to function properly. The application container also supports the CLI functionality, which can be accessed by providing the `docker run` command with the function you wish to execute (you do not need to publish the container on port in this case),

> docker run --env-file /path/to/env/file \\ <br>
> $IMG_NAME:$IMG_TAG -rr BX AMC BB

The <i>Dockerfile</i> defines the container <i>/cache/</i> and <i>/static/</i> directories as volumes, so that you can mount your local directories onto the container. The first time the CLI is ever run, it loads in a substantial amount of static data. Because of this, it is recommended that you mount atleast the <i>/static/</i> directory onto its containerized counterpart,

> docker run --env-file /path/to/env/file \\ <br>
> --mount type=bind,source=/path/to/project/static/,target=/home/static/ \\ <br>
> $IMG_NAME:$IMG_TAG -min SPY QQQ 

The same applies for publishing the application over a <i>localhost</i> port. To run the container in as efficient as manner as possible, execute the following,

> docker run --publish $APP_PORT:$APP_PORT \\ <br>
> --env-file /path/to/env/file \\ <br>
> --mount type=bind,source=/path/to/project/static/,target=/home/static/ --mount type=bind,source=/path/to/project/cache/,target=/home/cache/ \\ <br>
> $IMG_NAME:$IMG_TAG

NOTE: if the <b>APP_ENV</b> in the environment file is set to <i>container</i>, then the application will search for a <b>postgres</b> database on the connection defined by <b>POSTGRES_\*</b> environment variables. If <b>APP_ENV</b> is set to <i>local</i> or not set at all, then the Django app will default to a <b>SQLite</b> database. If running the application as a container, it is recommended you spin up the container with the <i>docker-compose.yml</i> to launch a postgres container (unless you have a postgres service running on your <i>localhost</i>; configure the <b>POSTGRES_*</b> environment variables accordingly). After building the application image, execute from the project root directory,

> docker-compose up

to orchestrate the application with a <b>postgres</b> container. Verify the environment variable <b>POSTGRES_HOST</b> is set to the name of the database service defined in the <i>docker-compose.yml</i>, i.e. <b>POSTGRES_HOST</b> = <i>datasource</i>, if you are running the application as a container through <i>docker-compose</i>.
