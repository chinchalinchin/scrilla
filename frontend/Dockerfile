#####################
# DOCKER BUILD STEP 1
FROM python:3.8.8-slim AS docs
RUN apt-get update -y && apt-get install -y build-essential
COPY /docs /home/docs
WORKDIR /home/docs
RUN pip install -r requirements.txt && make html

#####################
# DOCKER BUILD STEP 2
FROM node:latest AS frontend
# VERSION CONTROLS
ENV NODE_VERSION=14
ENV ANGULAR_VERSION=11

# DEPENDENCIES & CONFIGURATION
RUN apt-get update -y && apt-get install -y curl moreutils && \ 
    curl -sL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs && npm install -g @angular/cli@${ANGULAR_VERSION} \ 
    && mkdir /home/build/ && mkdir /home/frontend/ && mkdir /home/docs
COPY /pynance-web/ /home/frontend/
COPY --from=docs /home/docs/build/html/ /home/frontend/src/assets/docs/
WORKDIR /home/frontend/
RUN npm install && ng build --prod --output-hashing none


#####################
# DOCKER BUILD STEP 3
FROM nginx:latest

# DEFAULT USER & GROUP
RUN useradd -ms /bin/bash pynance && groupadd pyadmin && usermod -a -G pyadmin pynance && \ 
    mkdir -p /home/build && mkdir -p /home/build/docs

# NGINX CONFIGURATION
COPY --chown=pynance:pyadmin /server/nginx.conf /etc/nginx/nginx.conf
COPY --chown=pynance:pyadmin /server/mime.types /etc/nginx/mime.types
COPY --from=frontend --chown=pynance:pyadmin /home/build/ /home/build/

# PERMISSION CONFIGURATOIN
RUN chown -R pynance:pyadmin /home/ /etc/nginx/nginx.conf /var/cache/nginx/ /var/run/ /var/log/nginx/ && \
    chmod -R 770 /home/

# ENTRYPOINT CONFIGURATION
EXPOSE 8080
RUN mkdir /home/scripts/
COPY /scripts/web-entrypoint.sh /home/scripts/web-entrypoint.sh
COPY /scripts/logging.sh /home/scripts/util/logging.sh
USER pynance
ENTRYPOINT [ "bash", "/home/scripts/web-entrypoint.sh" ]