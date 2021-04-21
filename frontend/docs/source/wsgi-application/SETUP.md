# WSGI Application Setup

## Local Setup

The application's functions can also be exposed through an API (a work in progress). To launch the API on your <i>localhost</i>, first configure the <b>APP_PORT</b> in the <i>/env/local.env</i> file. Then, from the <i>/server/pynance_api</i> directory execute,

`python manage.py runserver $APP_PORT`

If running directly through the Django admin, you must make sure all the model migrations are up to date to and have been migrated to your choice of database. Alternatively, you can run the <i>/scripts/server/pynance-server.sh</i> script,

`./scripts/server/pynance-server.sh`

This script will ensure all the dependencies have been installed, the database migrations have been created and migrated, and then it will launch the Django app and expose it on your <i>localhost</i>.

## Container Setup

First create a new environment file,

`cp .sample.env container.env`

and make sure the <b>APP_ENV</b> variable is set to <i>container</i>. Initialize your environment in your current shell session by executing from the project root directory,

`source ./scripts/util/env-vars.sh container`

After you have your environment file initialized, note the <b>IMG_NAME</b>, <b>TAG_NAME</b> and <b>APP_CONTAINER_NAME</b> environment variables will set the image, tag and container name respectively (if that wasn't obvious). 

To start up the server in a container, execute the <i>pynance-server</i> script, but provide it an argument of `-container`,

`./scripts/server/pynance-server.sh --container`

Or, if you want to build the image without spinning up the container,

`./scripts/docker/build-container.sh application`

Once the image has been built, you can spin up the container using (assuming your environment file has been initialized and loaded into your shell session),

`docker run --publish $APP_PORT:$APP_PORT \` <br>
`--env-file /path/to/env/file $IMG_NAME:$IMG_TAG`

Note, the image will need an environment file to function properly. 

The application container also supports the CLI functionality, which can be accessed by providing the `docker run` command with the function you wish to execute (you do not need to publish the container on port in this case),

`docker run --env-file /path/to/env/file \` <br>
`$IMG_NAME:$IMG_TAG -rr BX AMC BB`

The <i>Dockerfile</i> defines the container <i>/cache/</i> and <i>/static/</i> directories as volumes, so that you can mount your local directories onto the container. The first time the CLI is ever run, it loads in a substantial amount of static data. Because of this, it is recommended that you mount atleast the <i>/static/</i> directory onto its containerized counterpart,

`docker run --env-file /path/to/env/file \` <br>
`--mount type=bind,source=/path/to/project/static/,target=/home/static/ \` <br>
`$IMG_NAME:$IMG_TAG -min SPY QQQ` 

The same applies for publishing the application over a <i>localhost</i> port. To run the container in as efficient as manner as possible, execute the following,

`docker run --publish $APP_PORT:$APP_PORT \` <br>
`--env-file /path/to/env/file \` <br>
`--mount type=bind,source=/path/to/project/static/,target=/home/static/`<br>
`--mount type=bind,source=/path/to/project/cache/,target=/home/cache/ \` <br>
`$IMG_NAME:$IMG_TAG`

NOTE: if the <b>APP_ENV</b> in the environment file is set to <i>container</i> or <i>local</i>, then the application will search for a <b>postgres</b> database on the connection defined by <b>POSTGRES_\*</b> environment variables. If <b>APP_ENV</b> is not set at all, then the Django app will default to a <b>SQLite</b> database. If running the application as a container, it is recommended you spin up the container with the <i>docker-compose.yml</i> to launch a postgres container (unless you have a postgres service running on your <i>localhost</i>; configure the <b>POSTGRES_*</b> environment variables accordingly). After building the application image, execute from the project root directory,

`docker-compose up`

to orchestrate the application with a <b>postgres</b> container. Verify the environment variable <b>POSTGRES_HOST</b> is set to the name of the database service defined in the <i>docker-compose.yml</i>, i.e. <b>POSTGRES_HOST</b> = <i>datasource</i>, if you are running the application as a container through <i>docker-compose</i>.

## Frontend Application

The frontend runs as a service separate from the backend Django application. As such, the frontend server can run and serve up assets without the backend running (although some of the functionality will not work). The frontend can be run locally or within a container. See [Frontend](./FRONTEND.md) for more information on setting up the frontend.