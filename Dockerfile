FROM python:3.8.7-slim

# DEFAULT USER & GROUP CONFIGURATION
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance

# OS DEPENDENCY CONFIGURAITON
RUN apt-get update -y && apt-get install -y curl wait-for-it postgresql-client-11 libpq-dev build-essential

# APPLICATION DEPENDENCY CONFIGURATION
WORKDIR /home/
COPY /requirements-docker.txt /home/requirements.txt
RUN pip install -r requirements.txt

# APPLICATION CONFIGURATION
COPY /app/ /home/app/
COPY /server/ /home/server/
COPY /scripts/ /home/scripts/
COPY /util/ /home/util/
COPY /main.py /home/main.py
RUN mkdir ./cache/ && mkdir ./static/
RUN chown -R pynance:pyadmin /home/ && chmod -R 770 /home/

# ENTRYPOINT CONFIGURATION
VOLUME /home/cache/ /home/static/
WORKDIR /home/server/pynance_api/
USER pynance
ENTRYPOINT [ "/home/scripts/docker/pynance-entrypoint.sh" ]