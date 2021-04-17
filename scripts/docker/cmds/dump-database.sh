SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='dump-database'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="This script will dump a containerized database table specifed by the first argument \
into a local zip file ${nl}${ind} in the \e[3m/data/sql/\e[0m directory. For example,${nl}${nl}\
${tab}${tab}\e[2mbash $SCRIPT_NAME.sh data_equitymarket\e[0m${nl}${nl}${ind} will dump the database table \
\e[1mdata_equitymarket\e[0m into the file \e[3m/data/sql/data_equitymarket.gz\e[0m." 

source "$SCRIPT_DIR/../../util/logging.sh"

if [ "$1" == "--help" ] || [ "$1" == "--h" ] || [ "$1" == "-help" ] || [ "$1" == "-h" ]
then
    help "$SCRIPT_DES" $SCRIPT_NAME
else
    LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/zips"

    source "$SCRIPT_DIR/../../util/env-vars.sh" container

    if [ "$1" == "--data" ] || [ "$1" == "-data" ]
    then
        DUMP_PATH="/home/$(POSTGRES_DB)_data_$(date +'%m-%d-%Y').gz"
        DUMP_CMD="PGPASSWORD=$POSTGRES_PASSWORD pg_dump --data-only --username=$POSTGRES_USER --dbname=$POSTGRES_DB | gzip > $DUMP_PATH"

    fi
    if [ "$1" == "--schema" ] || [ "$1" == " -schema" ]
    then
        DUMP_PATH="/home/$(POSTGRES_DB)_schema_$(date +'%m-%d-%Y').gz"
        DUMP_CMD="PGPASSWORD=$POSTGRES_PASSWORD pg_dump --schema-only --username=$POSTGRES_USER --dbname=$POSTGRES_DB | gzip > $DUMP_PATH"
    fi
   
    CONTAINER_ID="$(docker container ps --filter name=$POSTGRES_HOST --quiet)"

    log "Executing dump command within Container ID # $CONTAINER_ID" $SCRIPT_NAME
    docker exec $CONTAINER_ID bash -c "$DUMP_CMD"

    log "Copying container dump file to local filesytem at $LOCAL_PATH/$(POSTGRES_DB)_data_$(date +'%m-%d-%Y').gz" $SCRIPT_NAME
        # the cp command may or may not need quotes...
    docker cp "$CONTAINER_ID:$DUMP_PATH" "$LOCAL_PATH"

fi