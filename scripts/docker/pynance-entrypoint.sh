#!/bin/bash
# Entrypoint script for Dockerfile that will deploy the application onto a gunicorn web server.
# If the user provides arguments, the entrypoint will switch to CLI mode and execute the given
# function and output results to the terminal.
# 
# NOTE: Dockerfile sets WORKDIR to /home/server/
SCRIPT_NAME='pynance-entrypoint'
source /home/scripts/util/logging.sh


log "Entrypoint Argument(s): \e[3m$(concat_args $@)\e[0m" $SCRIPT_NAME
log "Executing from $(pwd)" $SCRIPT_NAME

if [ $# -eq 0 ] || [ "$1" == "wait-for-it" ] || [ "$1" == "bash" ] || [ "$1" == "psql" ]
then
    cd /home/
    log "Invoking \e[2mpynance CLI\e[0m to initalize \e[3m/static/\e[0m directory; This may take a while!" $SCRIPT_NAME
    python main.py -init

    log "Logging Non-sensitive Django settings" $SCRIPT_NAME
    python -c "import server.pynance_api.core.settings as settings; from util.logger import Logger; \
        logger=Logger('scripts.server.pynance-server', '$LOG_LEVEL'); logger.log_django_settings(settings);"

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

    cd /home/server/pynance_api/
    log 'Checking for new migrations' $SCRIPT_NAME
    python manage.py makemigrations
    
    log 'Migrating Django database models' $SCRIPT_NAME
    python manage.py migrate

        # SCRAPPER_ENABLED to lower case
    if [ "${SCRAPPER_ENABLED,,}" == "true" ]
    then
        log "Scrapping price histories into $POSTGRES_HOST; this may take a while!" $SCRIPT_NAME
        cd /home/server/pynance_api/data/
        python scrapper.py 
    fi

    if [ "$1" == "psql" ]
    then
        PGPASSWORD=$POSTGRES_PASSWORD psql --host=$POSTGRES_HOST --port=$POSTGRES_PORT --username=$POSTGRES_USER 
        exit 0
    fi

    if [ "$APP_ENV" == "container" ]
    then
        cd /home/server/pynance_api/
        log "Binding WSGI app To \e[2mgunicorn\e[0m Web Server On 0.0.0.0:8000" $SCRIPT_NAME 
        gunicorn core.wsgi:application --bind=0.0.0.0:$SERVER_PORT --workers 1
    fi

    # OTHER IMAGE DEPLOYMENTS GO HERE

else
    log "Argument(s) Provided: $(concat_args $@)" $SCRIPT_NAME
    log "Switching to CLI Mode" $SCRIPT_NAME
    cd /home/
    python main.py $@
fi