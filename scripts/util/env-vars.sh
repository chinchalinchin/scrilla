SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$SCRIPT_DIR/logging.sh"

# ARGUMENT: whatever environment's env vars you initializing. Must have a 
# corresponding .env file in the /env/ directory. 

log "Checking \e[3m$1.env\e[0m File Configuration" "env-vars"
if [ -f "$SCRIPT_DIR/../../env/$1.env" ]
then
    log 'Initializing Environment...' "env-vars"
    set -o allexport
    source $SCRIPT_DIR/../../env/$1.env
    set +o allexport
    log 'Environment Initialized' "env-vars"
else
    touch $SCRIPT_DIR/../../env/$1.env
    cp $SCRIPT_DIR/../../env/.sample.env $SCRIPT_DIR/../../env/$1.env
    log "Please configure the \e[3m$1.env\e[0m file and then re-invoke this script. \n \
                    See documentation for more information" "env-vars"
    exit 0
fi