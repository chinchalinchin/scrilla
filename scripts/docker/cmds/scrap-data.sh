SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='scrap-data'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="This script will dump the containerized database into a local zip file \
defined by the path passed as the first argument.${nl}${ind}For example,${nl}${nl}${tab}\
${tab}bash $SCRIPT_NAME.sh $(pwd)${nl}${nl}${ind}will dump the database into a file\
within your present working directory." 

source "$SCRIPT_DIR/../../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    if [ ! $# -eq 0 ]
    then
        SCRAP_CMD="cd /home/server/pynance_api && python scrap.py"
        CONTAINER_ID="$(docker container ps --filter name=$CONTAINER_NAME --quiet)"

        log "Executing dump command within Container ID# $CONTAINER_ID" $SCRIPT_NAME
        docker exec $CONTAINER_ID bash -c "$SCRAP_CMD"
    else
        log "No argument provided, unable to execute script. Please see help message below and try again." $SCRIPT_NAME
        help "$SCRIPT_DES" $SCRIPT_NAME
    fi
fi