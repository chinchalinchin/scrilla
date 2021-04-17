SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='dump-data'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="This script will dump the containerized database schema." 

source "$SCRIPT_DIR/../../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/dumps/zips"

    source "$SCRIPT_DIR/../../util/env-vars.sh" container

    DUMP_PATH="/home/$(POSTGRES_DB)_schema_$(date +'%m-%d-%Y').gz"
    DUMP_CMD="PGPASSWORD=$POSTGRES_PASSWORD pg_dump --schema-only --username=$POSTGRES_USER --dbname=$POSTGRES_DB| gzip > $DUMP_PATH"
    CONTAINER_ID="$(docker container ps --filter name=$POSTGRES_HOST --quiet)"

    log "Executing dump command within Container ID # $CONTAINER_ID" $SCRIPT_NAME
    docker exec $CONTAINER_ID bash -c "$DUMP_CMD"

    log "Copying container dump file to local filesytem at $LOCAL_PATH/$(POSTGRES_DB)_schema_$(date +'%m-%d-%Y').gz" $SCRIPT_NAME
        # the cp command may or may not need quotes...
    docker cp "$CONTAINER_ID:$DUMP_PATH" "$LOCAL_PATH"
    
fi