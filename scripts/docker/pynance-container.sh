SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-container'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="Execute this script to build a Docker image of the application.\
Make sure to initialize your environment file${nl}${ind}before invoking this script. \
To initialize your environment execute from your shell session,${nl}${nl}${tab}${tab}source PROJECT_ROOT/scripts/util\
/env-vars.sh${nl}${nl}${ind}You may provider the \e[3menv-var\e[0m script an argument to specify\
 which environment file to initialize, i.e.${nl}${nl}${tab}${tab}source PROJECT_ROOT/scripts/\
util/env-vars.sh container${nl}${nl}${ind}to initialize the \e[3mcontainer.env\e[0m file." 

source "$SCRIPT_DIR/../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    # DIRECTORIES
    ROOT_DIR=$SCRIPT_DIR/../..

    source "$SCRIPT_DIR/../util/env-vars.sh" container 

    log 'Clearing Docker Cache' $SCRIPT_NAME
    docker system prune -f

    cd $ROOT_DIR
    log "Building \e[3m$IMG_NAME:$TAG_NAME\e[0m Docker image" $SCRIPT_NAME
    docker build -t $IMG_NAME:$TAG_NAME .

    DANGLERS=$(docker images --filter "dangling=true" -q)
    if [ "$DANGLERS" != "" ]
    then 
        log 'Deleting Dangling Images' $SCRIPT_NAME
        docker rmi -f $DANGLERS
    fi
fi