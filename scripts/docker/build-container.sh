SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-container'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="Execute this script to build a Docker image of the application or frontend.\
Provide this script either${nl}${ind}an argument of 'application' to build the WSGI \
application server image or an argument of 'frontend' to build the Angular-nginx ${nl}\
${ind}web container. For example,${nl}${nl}${tab}\e[1m./scripts/docker/build-container.sh \
application\e[0m ${nl}${nl}${ind}Or,${nl}${nl}${tab}\e[1m./scripts/docker/build-container.sh \
frontend" 

source "$SCRIPT_DIR/../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    # DIRECTORIES
    ROOT_DIR=$SCRIPT_DIR/../..
    FRONTEND_DIR=$ROOT_DIR/frontend/

    source "$SCRIPT_DIR/../util/env-vars.sh" container 

    log 'Clearing Docker Cache' $SCRIPT_NAME
    docker system prune -f

    if [ "$1" == "application" ]
    then
        cd $ROOT_DIR
        log "Building \e[3m$APP_IMG_NAME:$APP_TAG_NAME\e[0m Docker image" $SCRIPT_NAME
        docker build -t $APP_IMG_NAME:$APP_TAG_NAME .
    elif [ "$1" == "frontend" ]
    then
        cd $FRONTEND_DIR
        log "Building \e[3m$WEB_IMG_NAME:$WEB_TAG_NAME\e[0m Docker image" $SCRIPT_NAME
        docker build -t $WEB_IMG_NAME:$WEB_TAG_NAME . 
    fi

    DANGLERS=$(docker images --filter "dangling=true" -q)
    if [ "$DANGLERS" != "" ]
    then 
        log 'Deleting dangling images' $SCRIPT_NAME
        docker rmi -f $DANGLERS
    fi
fi