SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-server'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="Execute this script to launch a Django server. Change SERVER_PORT in\
\e[3m/env/.env\e[0m to modify the port ${nl}${ind}the server will run on. If no argument\
is provided, the script will default to \e[3mlocal\e[0m${nl}${nl}\
${tab}${tab}OPTIONS: ${nl}${tab}${tab}${ind}--local/-l = Invokes \e[2mpython manage.py \
runserver\e[0m from the \e[3m/server/\e[0m directory.${nl}${tab}${tab}${ind}--container/-c\
 = Builds and runs a Docker image of the application.${nl}${tab}${tab}${ind}--help/-h = \
Displays this help message." 

source "$SCRIPT_DIR/../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    # DIRECTORIES
    ROOT_DIR=$SCRIPT_DIR/../..
    UTIL_DIR=$SCRIPT_DIR/../util
    SERVER_DIR=$ROOT_DIR/server/pynance_api
    APP_DIR=$ROOT_DIR/app
    ENV_DIR=$ROOT_DIR/env

    log "Invoking \e[3menv-vars\e[0m script" $SCRIPT_NAME

    if [ "$1" == "--local" ] || [ "$1" == "-local" ] || [ "$1"  == "--l" ] || [ "$1" == "-l" ] || [ $# -eq 0 ]
    then
        source "$UTIL_DIR/env-vars.sh"

        cd $SERVER_DIR
        log "Logging Non-sensitive Django Settings" $SCRIPT_NAME
        python debug.py
        
        log "Starting Server On \e[3mlocalhost:$SERVER_PORT\e[0m" $SCRIPT_NAME
        python manage.py runserver $SERVER_PORT
    fi
    if [ "$1" == "--container" ] || [ "$1" = "-container" ] || [ "$1" == "--c" ] || [ "$1" == "-c" ]
    then
        source "$UTIL_DIR/env-vars.sh" container
        log "Build Docker image here" $SCRIPT_NAME
    fi
fi