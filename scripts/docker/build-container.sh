# TODOSCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-server'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="Execute this script to build a Docker image of the application." 

source "$SCRIPT_DIR/../util/logging.sh"

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

    log "Invoking \e[3menv-vars\e[0m script" $SCRIPT_NAME
    source "$UTIL_DIR/env-vars.sh" container
        
    cd $ROOT_DIR
    docker build -t $IMG_NAME:$IMG_TAG
    log "Build Docker image here" $SCRIPT_NAME


fi