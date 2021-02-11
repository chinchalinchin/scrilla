SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='dump-scrapped-data'
nl=$'\n'
tab="     "
ind="   "
SCRIPT_DES="" 

source "$SCRIPT_DIR/../../util/logging.sh"


# TODO: after scrapping, dump database into sql file
# TODO: copy file from container virtual file system to local file system

# docker cp CONTAINER_PATH LOCAL_PATH