#!/bin/bash
# Entrypoint script for Dockerfile that will deploy the application onto a gunicorn web server.
# If the user provides arguments, the entrypoint will switch to CLI mode and execute the given
# function and output results to the terminal.
# 
# NOTE: Dockerfile sets WORKDIR to /home/server/
SCRIPT_NAME='pynance-entrypoint'
source /home/scripts/util/logging.sh

if [ ! $# -eq 0 ]
then
    for arg in $@
    do
        log "Entrypoint Argument: $arg" $SCRIPT_NAME
    done
fi
log "Executing from $(pwd)" $SCRIPT_NAME

# TODO: need to modify entrypoint to execute BASH commands for 'wait-for-it' in docker-compose.

if [ $# -eq 0 ] || [ "$1" == "wait-for-it" ] || [ "$1" == "bash" ] || [ "$1" == "--scrap" ] || [ "$1" == "--sc" ] || [ "$1" == "-scrap" ] || [ "$1" = "-sc" ]
then
    cd /home/
    log "Invoking \e[2mpynance CLI\e[0m to initalize \e[3m/static/\e[0m directory; This may take a while!" $SCRIPT_NAME
    python main.py -init

    cd /home/server/pynance_api/
    log "Logging Non-sensitive Django settings" $SCRIPT_NAME
    python debug.py

    if [ "$1" == "wait-for-it" ]
    then
        log "Waiting for database service connection..." $SCRIPT_NAME
        $@
    elif [ "$1" == "bash" ]
    then
        log "Starting BASH shell session..." $SCRIPT_NAME
        $@
        exit 0
    fi

    log 'Checking for new migrations' $SCRIPT_NAME
    python manage.py makemigrations
    
    log 'Migrating Django database models' $SCRIPT_NAME
    python manage.py migrate

    if [ "$1" == "--scrap" ] || [ "$1" == "--sc" ] || [ "$1" == "-scrap" ] || [ "$1" == "-sc" ]
    then
        log "TODO: Data scrapping goes here" $SCRIPT_NAME
    fi

    if [ "$APP_ENV" == "container" ]
    then
        log "Binding WSGI app To \e[2mgunicorn\e[0m Web Server On 0.0.0.0:8000" $SCRIPT_NAME 
        gunicorn core.wsgi:application --bind=0.0.0.0:$SERVER_PORT --workers 3
    fi

    # OTHER IMAGE DEPLOYMENTS GO HERE

else
    log "Argument(s) Provided: $(concat_args $@)" $SCRIPT_NAME
    log "Switching to CLI Mode" $SCRIPT_NAME
    cd /home/
    python main.py $@
fi