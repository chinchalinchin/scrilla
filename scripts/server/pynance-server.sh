SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-server'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="Execute this script to launch a Django server. Change APP_PORT in\
\e[3m/env/.env\e[0m to modify the port ${nl}${ind}the server will run on. If no argument\
is provided, the script will default to \e[3mlocal\e[0m${nl}${nl}\
${tab}${tab}OPTIONS: ${nl}${tab}${tab}${ind}--local/-l = Invokes \e[2mpython manage.py \
runserver\e[0m from the \e[3m/server/\e[0m directory.${nl}${tab}${tab}${ind}--container/-c\
 = Builds and runs a Docker image of the application.${nl}${tab}${tab}${ind}--help/-h = \
Displays this help message." 

source $SCRIPT_DIR/../util/logging.sh

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    # DIRECTORIES
    ROOT_DIR=$SCRIPT_DIR/../..
    UTIL_DIR=$SCRIPT_DIR/../util
    DOCKER_DIR=$SCRIPT_DIR/../docker
    SERVER_DIR=$ROOT_DIR/server/pynance_api
    APP_DIR=$ROOT_DIR/app
    ENV_DIR=$ROOT_DIR/env
    CACHE_DIR=$ROOT_DIR/data/cache
    STATIC_DIR=$ROOT_DIR/data/static
    # PYTHON SCRIPTS
    LOG_DJANGO_SETTINGS="import server.pynance_api.core.settings as settings; from util.outputter import Logger; \
        logger=Logger('scripts.server.pynance-server','$LOG_LEVEL'); logger.log_django_settings(settings=settings);"
    CLEAR_CACHE="import app.settings as settings; import app.files as files; \
        files.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=True)"
    
    LOG_DJANGO_SETTINGS="import server.pynance_api.core.settings as settings; from util.outputter import Logger; \
        logger=Logger('scripts.server.pynance-server','info'); logger.log_django_settings(settings);"
    CLEAR_CACHE="import app.settings as settings; import app.files as files; \
        files.clear_directory(directory=settings.CACHE_DIR, retain=True, outdated_only=True)"

    # Run in local mode
    if [ "$1" == "--local" ] || [ "$1" == "-local" ] || [ "$1"  == "--l" ] || [ "$1" == "-l" ] || [ $# -eq 0 ]
    then
        log "Invoking \e[3menv-vars\e[0m script." $SCRIPT_NAME
        source $UTIL_DIR/env-vars.sh local

        cd $ROOT_DIR
        log "Logging non-sensitive Django settings." $SCRIPT_NAME
        python3 -c "$LOG_DJANGO_SETTINGS"
   
        log "Clearing \e[3m/cache/\e[0m directory of outdated price histories." $SCRIPT_NAME
        python3 -c "$CLEAR_CACHE"

        cd $SERVER_DIR
        log "Verifying migrations are up-to-date." $SCRIPT_NAME
        python3 manage.py makemigrations

        log 'Migrating Django database models.' $SCRIPT_NAME
        python3 manage.py migrate

        log 'Creating Django Admin from environment variables.' $SCRIPT_NAME
        python3 manage.py createsuperuser --no-input --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
                
        HOST=localhost:$APP_PORT        
        log "Starting Django Development server On \e[3m$HOST\e[0m." $SCRIPT_NAME
        python3 manage.py runserver $HOST
    fi

    # Run in container mode
    if [ "$1" == "--container" ] || [ "$1" = "-container" ] || [ "$1" == "--c" ] || [ "$1" == "-c" ]
    then
        log "Invoking \e[3menv-vars\e[0m script." $SCRIPT_NAME
        source $UTIL_DIR/env-vars.sh container

        log "Checking if \e[3m$APP_CONTAINER_NAME\e[0m container is currently running." $SCRIPT_NAME
        if [ "$(docker ps -q -f name=$APP_CONTAINER_NAME)" ]
        then
            log "Stopping \e[3m$APP_CONTAINER_NAME\e[0m container." $SCRIPT_NAME
            docker container stop $APP_CONTAINER_NAME

            log "Removing \e[3m$APP_CONTAINER_NAME\e[0m container." $SCRIPT_NAME
            docker rm $APP_CONTAINER_NAME
        fi

        log "Invoking \e[3mbuild-container\e[0m script with an argument of \e[1mapplication\e[0m." $SCRIPT_NAME
        bash $DOCKER_DIR/build-container.sh application

        log "Publishing \e[3m$APP_IMG_NAME:$APP_TAG_NAME\e[0m with container name \e[3m$APP_CONTAINER_NAME\e[0m on \e[3mlocalhost:$APP_PORT\e[0m." $SCRIPT_NAME
        docker run \
        --name $APP_CONTAINER_NAME \
        --publish $APP_PORT:$APP_PORT \
        --env-file $ENV_DIR/container.env \
        --mount type=bind,source=$CACHE_DIR,target=/home/cache/ \
        --mount type=bind,source=$STATIC_DIR,target=/home/static/ \
        $APP_IMG_NAME:$APP_TAG_NAME
    fi
fi