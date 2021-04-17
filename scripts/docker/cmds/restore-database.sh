SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='restore-database'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="This script restores the dump specifed by the date provided as an argument. The available dump files \
are located${nl}${ind} in the \e[3m/data/sql/dumps\e[0m directory. For example,${nl}${nl}\
${tab}${tab}\e[2mbash $SCRIPT_NAME.sh --data 03-30-2021\e[0m${nl}${nl}${ind} will restore the database dump\
generated on 03-30-2021 into the \e[1mpostgres\e[0m database service, whereas ${nl}${nl}${tab}${tab}\
\e2mbash $SCRIPT_NAME.sh --schema 03-30-201\e[0m${nl}${nl}${ind} will restore the schema dump generated\
on 03-30-2021. The indicated dump files must exist in \e[3m/data/sql/dumps/\e[0m before invoking\ 
this script." 

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

        if [ "$1" == "--data" ] || [ "$1" == "-data" ]
        then
            LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/dumps/$(POSTGRES_DB)_data_$2"
            DUMP_PATH="/home/$(POSTGRES_DB)_data_$2"
        fi
        if [ "$1" == "--schema" ] || [ "$1" == " -schema" ]
        then
            LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/dumps/$(POSTGRES_DB)_schema_$2"
            DUMP_PATH="/home/$(POSTGRES_DB)_schema_$2"
        fi
        CONTAINER_ID="$(docker container ps --filter name=$POSTGRES_HOST --quiet)"
        RESTORE_CMD="PGPASSWORD=$POSTGRES_PASSWORD psql --username=$POSTGRES_USER --dbname=$POSTGRES_DB -f $DUMP_PATH"

        log "Copying dump file from local filestem at \e[3m$LOCAL_PATH/$(POSTGRES_DB)_data_$1\e[0m to container file \e[3m/$DUMP_PATH\[e0m" $SCRIPT_NAME
        docker cp "$LOCAL_PATH" "$CONTAINER_ID:$DUMP_PATH"

        log "Executing restoration command within Container ID # $CONTAINER_ID" $SCRIPT_NAME
        docker exec $CONTAINER_ID bash -c "$RESTORE_CMD"
    else
        log "No argument provided, unable to execute script. Please see help message below and try again." $SCRIPT_NAME
        help "$SCRIPT_DES" $SCRIPT_NAME
    fi
fi