#!/bin/bash

SCRIPT_NAME='pynance-entrypoint'
source "/home/scripts/util/logging.sh"
# Entrypoint script for Dockerfile that will deploy the application onto a gunicorn web server.
# If the user provides arguments, the entrypoint will switch to CLI mode and execute the given
# function and output results to the terminal.
# 
# NOTE: Dockerfile sets WORKDIR to /home/server/
# DIRECTORIES

ROOT_DIR="/home/"
APP_DIR="/home/app/"
SERVER_DIR="/home/server/pynance_api/"

# PYTHON SCRIPTS
LOG_DJANGO_SETTINGS="import server.pynance_api.core.settings as settings; from app.util.outputter import Logger; \
        logger=Logger('scripts.server.pynance-server','$LOG_LEVEL'); logger.log_django_settings(settings=settings);"
CLEAR_CACHE="import app.settings as settings; import app.files as files; \
        files.clear_directory(directory=settings.CACHE_DIR, retain=True)"

log "Entrypoint Argument(s): \e[3m$(concat_args $@)\e[0m" $SCRIPT_NAME
log "Executing from \e[3m$(pwd)\e[0m" $SCRIPT_NAME

if [ $# -eq 0 ] || [ "$1" == "wait-for-it" ] || [ "$1" == "bash" ] || [ "$1" == "psql" ]
then
    cd $ROOT_DIR
    log "Invoking \e[2mpynance CLI\e[0m to initalize \e[3m/static/\e[0m directory; This may take a while!" $SCRIPT_NAME
    python main.py -init-static

    # TODO: argument to clear cache.
    # log "Clearing \e[3m/cache/\e[0m directory of outdated price histories." $SCRIPT_NAME
    # python -c "$CLEAR_CACHE"

    log "Logging Non-sensitive Django settings" "$SCRIPT_NAME"
    python -c "$LOG_DJANGO_SETTINGS"

    # 
    if [ "$1" == "wait-for-it" ]
    then
        log "Waiting for \e[3m$POSTGRES_HOST:$POSTGRES_PORT\e[0m database service connection." "$SCRIPT_NAME"
        wait-for-it "$POSTGRES_HOST:$POSTGRES_PORT"
    fi

    cd $SERVER_DIR
    log "Checking for new migrations" "$SCRIPT_NAME"
    python manage.py makemigrations
    
    log "Migrating Django database models" "$SCRIPT_NAME"
    python manage.py migrate

    python manage.py createsuperuser --no-input --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"

    # SHELL ENTRYPOINTS
    if [ "${SCRAPPER_ENABLED,,}" == "true" ] # SCRAPPER_ENABLED to lower case
    then
        log "Scrapping price histories into $POSTGRES_HOST/$POSTGRES_DB; this may take a while!" "$SCRIPT_NAME"
        cd "$SERVER_DIR"
        python scrap.py 
    fi
    if [ "$1" == "bash" ]
    then
        log "Starting \e[3mBASH\e[0m shell session." $SCRIPT_NAME
        $@
        exit 0
    fi
    if [ "$1" == "psql" ]
    then
        log "Starting \e[3mpsql\e[0m shell session"
        PGPASSWORD=$POSTGRES_PASSWORD psql --host=$POSTGRES_HOST --port=$POSTGRES_PORT --username=$POSTGRES_USER 
        exit 0
    fi
    # TODO: start Django shell inside of container

    if [ "$APP_ENV" == "container" ]
    then
        cd "$SERVER_DIR"
        log "Binding WSGI app To \e[2mgunicorn\e[0m Web Server On 0.0.0.0:8000" "$SCRIPT_NAME" 
        gunicorn core.wsgi:application --bind="0.0.0.0:$APP_PORT" --workers 1
    fi

    # OTHER IMAGE DEPLOYMENTS GO HERE

else
    log "Argument(s) Provided: $(concat_args $@)" "$SCRIPT_NAME"
    log "Switching to CLI Mode" "$SCRIPT_NAME"
    cd $ROOT_DIR
    python main.py $@
fi