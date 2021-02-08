#!/bin/bash

# Dockerfile sets WORKDIR to /home/server/
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SCRIPT_NAME='pynance-entrypoint'
source $SCRIPT_DIR/../util/logging.sh

PROJECT_DIR=$SCRIPT_DIR/../../

log "Executing from $(pwd)" $SCRIPT_NAME

log "Logging Non-sensitive Django settings" $SCRIPT_NAME
python debug.py

log 'Migrating Django database models' $SCRIPT_NAME
python manage.py migrate

if [ $# -eq 0 ]
then
    cd /home/
    log "Invoking \e[2mpynance CLI\e[0m to initalize \e[3m/static/\e[0m directory; This may take a while!"
    python main.py -init

    if [ "$APP_ENV" == "container" ]
    then
        cd /home/server/pynance_api/
        echo "$(pwd)"
        log "Binding WSGI app To \e[2mgunicorn\e[0m Web Server On 0.0.0.0:8000" $SCRIPT_NAME 
        gunicorn core.wsgi:application --bind=0.0.0.0:$SERVER_PORT --workers 3
    fi

else
    log "Argument(s) Provided: $@" $SCRIPT_NAME
    log "Switching to CLI Mode" $SCRIPT_NAME
    cd $PROJECT_DIR
    python ./main.py $@
fi