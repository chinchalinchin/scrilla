SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='restore-data'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="This script restore the table specifed by the first argument to the containerized database \
from the unzipped dump file ${nl}${ind} in the \e[3m/data/sql/\e[0m directory. For example,${nl}${nl}\
${tab}${tab}\e[2mbash $SCRIPT_NAME.sh data_equitymarket\e[0m${nl}${nl}${ind} will restore the database table \
\e[1mdata_equitymarket\e[0m into the \e[1mpostgres\e[0m database service." 

source "$SCRIPT_DIR/../../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    if [ ! $# -eq 0 ]
    then        
        source "$SCRIPT_DIR/../../util/env-vars.sh" container
            # reset SCRIPT_DIR since sourcing overwrites it.
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
        LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/unzipped/$POSTGRES_DB-$1"
        DUMP_PATH="/home/"
        CONTAINER_ID="$(docker container ps --filter name=$POSTGRES_HOST --quiet)"
        RESTORE_CMD="PGPASSWORD=$POSTGRES_PASSWORD psql --username=$POSTGRES_USER --dbname=$POSTGRES_DB -f $LOCAL_PATH"

        log "Copying dump file from local filestem at $LOCAL_PATH/$POSTGRES_DB-$1 to container file system" $SCRIPT_NAME
        docker cp "$LOCAL_PATH" "$CONTAINER_ID:$DUMP_PATH"

        log "Executing restoration command within Container ID # $CONTAINER_ID" $SCRIPT_NAME
        docker exec $CONTAINER_ID bash -c "$RESTORE_CMD"
    else
        log "No argument provided, unable to execute script. Please see help message below and try again." $SCRIPT_NAME
        help "$SCRIPT_DES" $SCRIPT_NAME
    fi
fi