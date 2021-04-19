SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='web-server'
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
    FRONTEND_DIR=$ROOT_DIR/frontend/pynance-web
    UTIL_DIR=$ROOT_DIR/scripts/util
    ENV_DIR=$ROOT_DIR/env

    # Run in local mode
    if [ "$1" == "--local" ] || [ "$1" == "-local" ] || [ "$1"  == "--l" ] || [ "$1" == "-l" ] || [ $# -eq 0 ]
    then
        log "Invoking \e[3menv-vars\e[0m script." $SCRIPT_NAME
        source $UTIL_DIR/env-vars.sh local

        # TODO: build documentation pages
        
        cd $FRONTEND_DIR
        log "Installing Node dependencies." $SCRIPT_NAME
        npm install 

        log "Launching Angular Development server on \e[3mlocalhost:$WEB_PORT\e[0m." $SCRIPT_NAME
        ng serve --port $WEB_PORT
    fi

    # Run in container mode
    if [ "$1" == "--container" ] || [ "$1" = "-container" ] || [ "$1" == "--c" ] || [ "$1" == "-c" ]
    then
        log "Invoking \e[3menv-vars\e[0m script." $SCRIPT_NAME
        source $UTIL_DIR/env-vars.sh container

        log "Checking if \e[3m$WEB_CONTAINER_NAME\e[0m container is currently running." $SCRIPT_NAME
        if [ "$(docker ps -q -f name=$WEB_CONTAINER_NAME)" ]
        then
            log "Stopping \e[3m$WEB_CONTAINER_NAME\e[0m container." $SCRIPT_NAME
            docker container stop $WEB_CONTAINER_NAME

            log "Removing \e[3m$WEB_CONTAINER_NAME\e[0m container." $SCRIPT_NAME
            docker rm $WEB_CONTAINER_NAME
        fi

        log "Invoking \e[3mweb-container\e[0m script." $SCRIPT_NAME
        bash $DOCKER_DIR/build-container.sh frontend

        log "Publishing \e[3m$WEB_IMG_NAME:$WEB_TAG_NAME\e[0m with container name \e[3m$WEB_CONTAINER_NAME\e[0m on \e[3mlocalhost:$APP_PORT\e[0m." $SCRIPT_NAME
        docker run \
        --name $WEB_CONTAINER_NAME \
        --publish $WEB_PORT:$WEB_PORT \
        --env-file $ENV_DIR/container.env \
        $WEB_IMG_NAME:$WEB_TAG_NAME
    fi
fi