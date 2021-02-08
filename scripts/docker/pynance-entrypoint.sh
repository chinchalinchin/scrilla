#!/bin/bash
# Entrypoint script for Dockerfile that will deploy the application onto a gunicorn web server.
# If the user provides arguments, the entrypoint will switch to CLI mode and execute the given
# function and output results to the terminal.
# 
# NOTE: Dockerfile sets WORKDIR to /home/server/

SCRIPT_NAME='pynance-entrypoint'
source /home/scripts/util/logging.sh

log "Executing from $(pwd)" $SCRIPT_NAME

if [ $# -eq 0 ]
then
    cd /home/
    log "Invoking \e[2mpynance CLI\e[0m to initalize \e[3m/static/\e[0m directory; This may take a while!"
    python main.py -init

    cd /home/server/pynance_api/
    log "Logging Non-sensitive Django settings" $SCRIPT_NAME
    python debug.py

    log 'Migrating Django database models' $SCRIPT_NAME
    python manage.py migrate

    if [ "$APP_ENV" == "container" ]
    then
        log "Binding WSGI app To \e[2mgunicorn\e[0m Web Server On 0.0.0.0:8000" $SCRIPT_NAME 
        gunicorn core.wsgi:application --bind=0.0.0.0:$SERVER_PORT --workers 3
    fi

    # OTHER IMAGE DEPLOYMENTS GO HERE

else
    log "Argument(s) Provided: ${@}" $SCRIPT_NAME
    log "Switching to CLI Mode" $SCRIPT_NAME
    cd /home/
    python main.py $@
fi