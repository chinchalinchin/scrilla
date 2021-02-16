SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='dump-data'
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
    if [ ! $# -eq 0 ]
    then        
        source "$SCRIPT_DIR/../../util/env-vars.sh" container
            # reset SCRIPT_DIR since sourcing overwrites it.
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
        DUMP_PATH="/home/$POSTGRES_DB-$1.gz"
        LOCAL_PATH="$SCRIPT_DIR/../../../data/sql/"
        DUMP_CMD="PGPASSWORD=$POSTGRES_PASSWORD pg_dump --username=$POSTGRES_USER --dbname=$POSTGRES_DB --table=$1| gzip > $DUMP_PATH"
        CONTAINER_ID="$(docker container ps --filter name=datasource --quiet)"

        log "Executing dump command within Container ID# $CONTAINER_ID" $SCRIPT_NAME
        echo "$DUMP_CMD"
        docker exec $CONTAINER_ID bash -c "$DUMP_CMD"

        log "Copying dump file to local filesytem at $LOCAL_PATH" $SCRIPT_NAME
        docker cp $CONTAINER_ID:$DUMP_PATH $LOCAL_PATH
    else
        log "No argument provided, unable to execute script. Please see help message below and try again." $SCRIPT_NAME
        help "$SCRIPT_DES" $SCRIPT_NAME
    fi
fi