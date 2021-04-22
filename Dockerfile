FROM python:3.8.8-slim

USER root
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance && \ 
     apt-get update -y && apt-get install -y curl wait-for-it postgresql-client-11 libpq-dev \
     build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# APPLICATION DEPENDENCY CONFIGURATION
WORKDIR /home/
COPY /requirements-docker.txt /home/requirements.txt
RUN pip install -r requirements.txt

# APPLICATION CONFIGURATION
COPY --chown=pynance:pyadmin /app/ /home/app/
COPY --chown=pynance:pyadmin /server/ /home/server/
COPY --chown=pynance:pyadmin /main.py /home/main.py
COPY --chown=pynance:pyadmin /scripts/ /home/scripts/
RUN mkdir -p /home/data/cache/ && mkdir -p /home/data/static/ && mkdir -p /home/data/common/ && \
     chown -R pynance:pyadmin /home/ && chmod -R 770 /home/

# ENTRYPOINT CONFIGURATION
VOLUME /home/data/cache/ /home/data/static/
USER pynance
ENTRYPOINT [ "/home/scripts/docker/pynance-entrypoint.sh" ]