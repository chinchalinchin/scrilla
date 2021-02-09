FROM python:latest

# DEFAULT USER & GROUP CONFIGURATION
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance

# OS DEPENDENCY CONFIGURAITON
RUN apt-get update -y && apt-get install -y curl wait-for-it

# APPLICATION DEPENDENCY CONFIGURATION
WORKDIR /home/
COPY /requirements_docker.txt /home/requirements.txt
RUN pip install -r requirements.txt

# APPLICATION CONFIGURATION
COPY /app/ /home/app/
COPY /server/ /home/server/
COPY /scripts/ /home/scripts/
COPY /util/ /home/util/
COPY /main.py /home/main.py
RUN mkdir ./cache/ && mkdir ./static/
VOLUME /home/cache/ /home/static/
RUN chown -R pynance:pyadmin /home/app/ /home/server/ /home/util/ /home/scripts/ /home/cache/ /home/static/
RUN chmod -R 770 /home/app/ /home/server/ /home/scripts/ /home/util/

# ENTRYPOINT CONFIGURATION
WORKDIR /home/server/pynance_api/
USER pynance
ENTRYPOINT [ "/home/scripts/docker/pynance-entrypoint.sh" ]